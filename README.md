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
│   └── sample_enquiries.csv
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

> Note: The SQLite database file (`data/enquiries.db`) is created automatically the first time the application runs. It is excluded from Git through `.gitignore`.

## 6. Installation and Setup

### Required API keys / environment variables

None. The AI model runs locally through Ollama, so no paid API key or `.env` file is needed.

### Step 1: Clone the repository

```bash
git clone https://github.com/Naveenjoahn26/ai-business-enquiry-automation.git
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
- The 1B model is small, so classification and extraction can be less accurate on vague or unusual enquiries.

## 11. Technical Explanation

### Why did you choose this technology stack?

- **Python** has the strongest ecosystem for AI and data work.
- **FastAPI** gives fast API development, automatic Swagger documentation, and works with Pydantic for input validation.
- **Ollama with Llama 3.2 (1B)** runs fully on a local machine. It is free, needs no API key, and keeps enquiry data on the local computer.
- **SQLite** needs no installation or server, which suits a prototype.

### How does your system decide the lead priority?

The score is rule-based, not random. It starts at 30 points. Urgency adds 30, a mentioned budget adds 20, and a recognised business category adds 20. The total (maximum 100) maps to High (70–100), Medium (40–69) or Low (below 40). Because every score is a sum of fixed rules, it can be explained and adjusted.

### How do you prevent the AI from generating incorrect business information?

- [VERIFY against response_generator.py before submitting] The AI is used for classification and extraction. Response drafts are built only from the business information given in the assessment, with no invented services, prices or delivery dates.
- Urgency is double-checked with Python keyword rules instead of relying only on the model.
- Drafts are never sent automatically. A human must review them first.

### What happens when the AI model fails or returns invalid output?

- [VERIFY against ai_processor.py before submitting] AI service errors are caught so the API does not crash, and an error response is returned instead.
- Input is validated before it reaches the model, and CSV rows that fail validation are reported.
- [Add here what your code does with invalid or non-JSON model output, for example a default category or sending the enquiry to human review.]

### How would you scale this system to process 10,000 enquiries per day?

10,000 per day is roughly 7 per minute on average, with higher peaks. I would:

- Put enquiries into a queue (for example Redis with Celery or RQ) and process them with several background workers.
- Replace SQLite with PostgreSQL.
- Run the model on a GPU server or use a hosted model API, since a 1B model on a laptop would be slow.
- Add retries, rate limiting, caching for repeated enquiries, and monitoring with logs.

### What would you improve if you had another two days?

- Build a simple dashboard where the team can review, edit and approve response drafts.
- Add a clear "needs human review" flag for unclear or sensitive enquiries (complaints, partnership requests).
- Show the reasons behind each lead score in the API response.
- Test with a stronger model and compare accuracy on the 12 sample enquiries.
- Add automated tests and Docker setup.

## 12. AI Usage Disclosure

**AI inside the application:** The project uses the locally hosted Llama 3.2 1B model through Ollama for enquiry classification and information extraction. Python code handles validation, urgency verification, lead scoring, database operations and response draft generation. AI-generated results are subject to human review.

**AI tools used while developing:**

- [FILL IN: tool names, for example Claude, Antigravity, etc.]
- Used for: [FILL IN: for example, step-by-step guidance, debugging errors, README writing, etc.]

**What I implemented and decided myself:** [FILL IN honestly: for example, the project idea, the scoring rules, testing the enquiries, running and fixing the project.]

I can explain and modify every important part of this project.

## 13. Author

[FILL IN: Your full name]

Developed as part of the Curd Rice Business Studio AI Intern technical assessment.