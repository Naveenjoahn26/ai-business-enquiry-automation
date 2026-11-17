import csv
import io
import sqlite3

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field, ValidationError

from database import create_table, save_enquiry
from response_generator import generate_response
from lead_scoring import calculate_lead_score
from ai_processor import classify_enquiry
from human_review import check_human_review


app = FastAPI(
    title="AI Business Enquiry Automation",
    description="AI-powered business enquiry processing system",
    version="1.0.0"
)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@app.on_event("startup")
def startup():
    create_table()


class Enquiry(BaseModel):
    customer_name: str = Field(min_length=2)
    email: str = Field(
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )
    message: str = Field(min_length=10)


@app.get("/")
def home():
    return {
        "message": "AI Business Enquiry Automation API is running!",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/enquiries")
def create_new_enquiry(enquiry: Enquiry):
    try:
        enquiry_id = save_enquiry(
            enquiry.customer_name,
            enquiry.email,
            enquiry.message
        )

        return {
            "message": "Enquiry saved successfully!",
            "enquiry_id": enquiry_id,
            "customer_name": enquiry.customer_name,
            "email": enquiry.email,
            "status": "received"
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Database error while saving enquiry."
        )


@app.post("/analyse")
def analyse_enquiry(enquiry: Enquiry):
    try:
        result = classify_enquiry(enquiry.message)
        lead_score = calculate_lead_score(result)
        review = check_human_review(enquiry.message, result, lead_score)

        response_draft = generate_response(
            enquiry.customer_name,
            result
        )

        enquiry_id = save_enquiry(
            enquiry.customer_name,
            enquiry.email,
            enquiry.message,
            result["category"],
            lead_score["score"],
            response_draft
        )

        return {
            "enquiry_id": enquiry_id,
            "customer_name": enquiry.customer_name,
            "email": enquiry.email,
            "analysis": result,
            "lead_score": lead_score,
            "human_review": review,
            "response_draft": response_draft
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="AI analysis or database service failed. Please try again."
        )


@app.get("/enquiries")
def get_enquiries():
    connection = None

    try:
        connection = sqlite3.connect("data/enquiries.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM enquiries")
        records = cursor.fetchall()

        return {"enquiries": records}

    except sqlite3.Error:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve enquiries from database."
        )

    finally:
        if connection:
            connection.close()


@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):

    try:
        if not file.filename or not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=400,
                detail="Please upload a CSV file only."
            )

        content = await file.read(MAX_FILE_SIZE + 1)

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="CSV file size exceeds the 5 MB limit."
            )

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded CSV file is empty."
            )

        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid file encoding. Please use UTF-8 CSV."
            )

        reader = csv.DictReader(io.StringIO(text))
        required_columns = ["customer_name", "email", "message"]

        if not reader.fieldnames:
            raise HTTPException(
                status_code=400,
                detail="CSV file has no column headers."
            )

        missing_columns = [
            column for column in required_columns
            if column not in reader.fieldnames
        ]

        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns: {missing_columns}"
            )

        rows = list(reader)

        if not rows:
            raise HTTPException(
                status_code=400,
                detail="CSV file has no enquiry records."
            )

        # Validate all rows before processing
        for row_number, row in enumerate(rows, start=2):

            for column in required_columns:
                if not row.get(column) or not row[column].strip():
                    raise HTTPException(
                        status_code=400,
                        detail=f"Missing {column} in CSV row {row_number}."
                    )

            try:
                Enquiry(
                    customer_name=row["customer_name"],
                    email=row["email"],
                    message=row["message"]
                )

            except ValidationError as error:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": f"Invalid data in CSV row {row_number}.",
                        "errors": error.errors()
                    }
                )

        processed = 0

        for row in rows:
            result = classify_enquiry(row["message"])
            lead_score = calculate_lead_score(result)

            response_draft = generate_response(
                row["customer_name"],
                result
            )

            save_enquiry(
                row["customer_name"],
                row["email"],
                row["message"],
                result["category"],
                lead_score["score"],
                response_draft
            )

            processed += 1

        return {
            "message": "CSV processed successfully",
            "total_enquiries": processed
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="CSV processing or AI service failed. Please try again."
        )

    finally:
        await file.close()