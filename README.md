
# AI-Powered Business Enquiry Automation

## 1. Project Overview

The AI-Powered Business Enquiry Automation system automates the process of analysing and managing business enquiries.

It uses a locally hosted AI model to understand customer messages, extract important business information, classify enquiries, calculate lead scores, and generate personalised response drafts.

## 2. Key Features

- Accept business enquiries through REST API.
- Upload and process multiple enquiries using CSV files.
- AI-powered enquiry classification.
- Extract customer requirements, budget, and timeline.
- Detect enquiry urgency.
- Automatic lead scoring (0–100).
- Classify leads into High, Medium, and Low priority.
- Generate personalised response drafts.
- Store enquiry information in SQLite database.
- Input validation and error handling.
- CSV file type and file size validation.
- Human review before sending customer responses.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| Ollama | Local AI model execution |
| Llama 3.2 (1B) | Enquiry classification |
| SQLite | Database |
| Pydantic | Input validation |
| CSV | Bulk enquiry processing |
| Uvicorn | API server |

## 4. Project Architecture

Customer Enquiry (API / CSV)  
↓  
Input Validation  
↓  
AI Enquiry Classification  
↓  
Information Extraction  
↓  
Lead Scoring  
↓  
Response Draft Generation  
↓  
SQLite Database Storage  
↓  
API Response

## 5. Project Structure

```text
ai-business-enquiry-automation/
│
├── data/
│   ├── sample_enquiries.csv
│   └── enquiries.db
│
├── main.py
├── ai_processor.py
├── lead_scoring.py
├── database.py
├── response_generator.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

## 6. Installation and Setup

### Step 1: Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ai-business-enquiry-automation
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
```

### Step 3: Activate the environment

Windows:

```powershell
venv\Scripts\activate
```

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Install and start Ollama

Download Ollama from:

https://ollama.com/

Download the model:

```bash
ollama pull llama3.2:1b
```

Keep the Ollama service running.

### Step 6: Start the FastAPI application

```bash
uvicorn main:app --reload
```

### Step 7: Open API documentation

http://127.0.0.1:8000/docs

## 7. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check application status |
| GET | `/health` | Health check |
| POST | `/enquiries` | Submit a new enquiry |
| POST | `/analyse` | Analyse an enquiry using AI |
| GET | `/enquiries` | Retrieve saved enquiries |
| POST | `/upload-csv` | Upload and process CSV enquiries |

## 8. Lead Scoring Logic

The system calculates a lead score based on:

- Base score: 30 points.
- Urgency: +30 points.
- Budget mentioned: +20 points.
- Recognised business category: +20 points.

Maximum score: 100.

Priority classification:

| Score | Priority |
|---|---|
| 70–100 | High |
| 40–69 | Medium |
| Below 40 | Low |

## 9. Error Handling and Validation

The application includes:

- Customer name validation.
- Email format validation.
- Message length validation.
- CSV file type validation.
- CSV required-column validation.
- Empty CSV validation.
- Invalid CSV row validation.
- 5 MB CSV upload size limit.
- AI service error handling.
- Database error handling.

## 10. AI Safety and Limitations

- Uses a locally hosted Llama 3.2 1B model through Ollama.
- Extracts information from customer messages.
- Urgency is additionally checked using Python keyword rules.
- AI-generated information may require human verification.
- Response drafts are generated but never automatically sent.
- The current system uses SQLite and is intended as a prototype.
- AI accuracy depends on the model and input quality.

## 11. Future Improvements

- Build a web-based dashboard.
- Add advanced lead scoring.
- Improve AI extraction accuracy.
- Add human review and approval workflows.
- Support additional enquiry channels.
- Introduce scalable database infrastructure.

## 12. AI Usage Disclosure

This project uses the locally hosted Llama 3.2 1B model through Ollama for AI-powered business enquiry classification and information extraction.

Python is used for validation, urgency verification, lead scoring, database operations, and response draft generation.

AI-generated results are subject to human review.

## 13. Author

Developed as part of an internship assessment project.
