# AI-Powered Business Enquiry Automation

## 1. Project Overview

This system automates the first-level handling of business enquiries for Curd Rice Business Studio. It receives an enquiry through an API or a CSV file, understands it, classifies it, extracts the key details, scores the lead, prepares a draft reply, flags enquiries that need a human, and stores everything in a database.

A locally hosted AI model (Llama 3.2 1B through Ollama) is used together with Python rules. Nothing is ever sent to a customer automatically. Every reply is only a draft that a human must approve.

## 2. Key Features

- Accept enquiries through a REST API or a CSV upload.
- Service category chosen from a fixed list of business categories.
- Extraction of requirement, budget, timeline and urgency.
- Lead score from 0 to 100 with High / Medium / Low priority, and the reasons behind every score.
- Draft reply generated from a fixed template, marked as a draft.
- Human review flag with reasons (complaints, pricing questions, partnership requests, sensitive topics, unclear enquiries, high priority leads).
- Anti-hallucination checks on budget, timeline and requirement.
- Storage in a SQLite database.
- Input validation and error handling, including CSV validation.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API and Swagger documentation |
| Ollama + Llama 3.2 (1B) | Local AI model (no API key needed) |
| SQLite | Database |
| Pydantic | Input validation |
| Uvicorn | API server |

## 4. Project Architecture

Customer Enquiry (API / CSV)  
↓  
Input Validation  
↓  
AI Extraction (requirement, budget, timeline, urgency)  
↓  
Python Verification (rules check the AI output)  
↓  
Rule-based Category Decision  
↓  
Lead Scoring with Reasons  
↓  
Human Review Check  
↓  
Draft Response (fixed template)  
↓  
SQLite Storage  
↓  
API Response

## 5. Project Structure

```text
ai-business-enquiry-automation/
│
├── data/
│   └── sample_enquiries.csv
│
├── frontend/               # Interactive enquiry automation dashboard
│   ├── index.html          # Web UI for enquiry processing
│   ├── styles.css          # Curd Rice design system & styling
│   ├── app.js              # Client logic & API connector
│   ├── server.py           # Dev server with API reverse proxy
│   └── README.md           # Frontend guide
│
├── main.py                 # FastAPI app and endpoints
├── ai_processor.py         # AI extraction + verification rules
├── lead_scoring.py         # Score, priority and reasons
├── human_review.py         # Human review flag
├── response_generator.py   # Draft reply template
├── database.py             # SQLite storage
├── run_samples.py          # Runs the 12 sample enquiries
│
├── requirements.txt
├── PROJECT_PROGRESS.md
├── README.md
└── .gitignore
```

> The SQLite database (`data/enquiries.db`) is created automatically when the app first runs. It is excluded from Git through `.gitignore`.

## 6. Installation and Setup

### Required API keys / environment variables

None. The AI model runs locally through Ollama.

### Step 1: Clone the repository

```bash
git clone https://github.com/Naveenjoahn26/ai-business-enquiry-automation.git
cd ai-business-enquiry-automation
```

### Step 2: Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Ollama and download the model

Download Ollama from https://ollama.com/ and run:

```bash
ollama pull llama3.2:1b
```

Keep Ollama running.

### Step 5: Start the application

```bash
uvicorn main:app --reload
```

### Step 6: Open the API documentation

http://127.0.0.1:8000/docs

### Step 7 (optional): Run all 12 sample enquiries

Open a second terminal, activate the virtual environment and run:

```bash
python run_samples.py
```

### Step 8 (optional): Launch the Frontend Dashboard

To use the interactive Curd Rice Business Studio web dashboard:

```bash
python frontend/server.py
```

Then visit http://localhost:3000 in your browser, or open `frontend/index.html` directly.

## 7. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check application status |
| GET | `/health` | Health check |
| POST | `/enquiries` | Save a new enquiry without AI analysis |
| POST | `/analyse` | Full pipeline: analyse, score, flag, draft and save |
| GET | `/enquiries` | Retrieve saved enquiries |
| POST | `/upload-csv` | Upload and process a CSV of enquiries |

Request body for `/enquiries` and `/analyse`:

```json
{
  "customer_name": "Test Customer",
  "email": "test@example.com",
  "message": "Need a website for our company."
}
```

## 8. Lead Scoring Logic

The score is rule-based, so every score can be explained.

| Rule | Points |
|---|---|
| Base score | +30 |
| Customer showed urgency | +30 |
| Budget was mentioned | +20 |
| Relevant business category | +20 |

Maximum score is 100.

| Score | Priority |
|---|---|
| 70–100 | High |
| 40–69 | Medium |
| Below 40 | Low |

Business categories that earn the category points: Business Consulting, AI Automation, Website & App Development, Operational Systems / ERP, Branding & Marketing. "General Enquiry" and "Job / Internship" do not.

Every response includes a `reasons` list, for example:

```json
"lead_score": {
  "score": 70,
  "priority": "High",
  "reasons": [
    "Base score: +30",
    "Budget was mentioned: +20",
    "Relevant business category (Website & App Development): +20"
  ]
}
```

## 9. Human Review Flag

`/analyse` returns a `human_review` object with `needs_human_review` and the reasons. An enquiry is flagged when it contains:

- a possible complaint or unhappy customer,
- a pricing or quotation request (prices must never be invented),
- a partnership request,
- a sensitive topic (legal, fraud and similar),
- an unclear or general enquiry,
- or when the lead is High priority.

## 10. Error Handling and Validation

- Customer name, email format and message length validation.
- CSV file type, required columns, empty file, invalid row and 5 MB size validation.
- If the AI service fails or returns invalid output, `/analyse` returns HTTP 503 with a clear message. Nothing is saved for that enquiry.
- Database errors are caught and returned as clean errors.

## 11. Technical Explanation

### Why did you choose this technology stack?

- **Python** has the strongest ecosystem for AI and data work.
- **FastAPI** gives quick API development, automatic Swagger documentation, and works with Pydantic validation.
- **Ollama with Llama 3.2 (1B)** runs fully on a local laptop. It is free, needs no API key, and keeps enquiry data on the local machine.
- **SQLite** needs no installation, which suits a prototype.

### How does your system decide the lead priority?

With fixed rules: base 30, plus 30 for urgency, plus 20 for a mentioned budget, plus 20 for a relevant business category. The total maps to High (70–100), Medium (40–69) or Low (below 40). The API returns the reasons for every score.

### How do you prevent the AI from generating incorrect business information?

During testing the small 1B model invented budgets and timelines and copied text from the prompt example. I fixed this by not trusting the AI blindly:

- **Budget:** the number the AI returns must really appear in the customer's message, otherwise it becomes "Not mentioned". If the AI misses a real budget (such as "₹2 lakh"), a regular expression finds it.
- **Timeline:** same approach, with checks against the customer's own words.
- **Urgency:** decided only by keyword rules on the original message.
- **Category:** decided by keyword rules from a fixed list, because the small model was not reliable here.
- **Requirement:** the AI sentence is used only if it shares words with the customer's message. Otherwise the customer's own words are used.
- **Draft reply:** built from a fixed template that only inserts the checked values. The AI never writes free text to the customer, so no prices, services or delivery dates can be invented. Drafts are marked "DRAFT - Pending human approval".

### What happens when the AI model fails or returns invalid output?

The AI call is wrapped in error handling. If Ollama is not running, times out, or returns invalid or incomplete JSON, the pipeline stops and `/analyse` returns HTTP 503 with a clear message. Nothing is saved for that enquiry, so the database never holds half-processed data. A future improvement is to fall back to rules-only processing and send the enquiry to human review instead of failing.

### How would you scale this system to process 10,000 enquiries per day?

10,000 per day is roughly 7 per minute on average, with higher peaks. I would:

- Put incoming enquiries into a queue (for example Redis with Celery or RQ) and process them with several background workers.
- Replace SQLite with PostgreSQL.
- Run the model on a GPU server or use a hosted model API.
- Add retries, rate limiting, caching and monitoring.

### What would you improve if you had another two days?

- Build a dashboard where the team can review, edit and approve drafts.
- Fall back to rules-only processing when the AI fails.
- Add the human review flag to CSV results and keep processing the other rows if one row fails.
- Use a stronger model and compare accuracy.
- Handle complaints separately from sales leads in scoring.
- Add automated tests and Docker.

## 12. Sample Enquiry Test Results

All 12 sample enquiries from the assessment were tested with `run_samples.py`.

| ID | Category | Score | Human review |
|---|---|---|---|
| 001 | AI Automation | 50 Medium | No |
| 002 | Website & App Development (₹2 lakh, this week) | 70 High | Yes (high priority) |
| 003 | General Enquiry | 30 Low | Yes (unclear) |
| 004 | Operational Systems / ERP | 50 Medium | No |
| 005 | Job / Internship | 30 Low | No |
| 006 | Operational Systems / ERP | 50 Medium | No |
| 007 | General Enquiry | 30 Low | Yes (pricing) |
| 008 | AI Automation (immediately) | 80 High | Yes (high priority) |
| 009 | Job / Internship | 30 Low | No |
| 010 | AI Automation | 50 Medium | No |
| 011 | General Enquiry | 30 Low | Yes (partnership) |
| 012 | General Enquiry (urgent) | 60 Medium | Yes (complaint) |

## 13. Known Limitations

- The 1B model is small. It is used for the requirement summary, and Python rules verify or replace its other outputs.
- Category and review flags use keywords, so unusual wording can be missed.
- A complaint (012) is scored like any urgent enquiry (Medium). It is flagged for human review, but the score does not treat it separately from sales leads.
- The CSV upload does not return the human review flag, and if the AI fails on one row, rows before it are already saved.
- There is no dashboard. Swagger UI is the interface.
- SQLite is for a prototype only.

## 14. AI Usage Disclosure

**AI inside the application:** the locally hosted Llama 3.2 1B model (through Ollama) extracts the requirement, budget, timeline and urgency from a message. Python rules verify or replace its output and decide the category, score, review flag and draft reply.

**AI tools used while developing:**

- Claude (Anthropic): step-by-step guidance, writing and fixing code during testing, debugging, and drafting this README.
- Antigravity: IDE used to work on the project and push it to GitHub.

**What I implemented and decided myself:** I set up and ran the project on my own computer (Python virtual environment, Ollama, FastAPI), applied and tested every code change, ran all 12 sample enquiries and checked the results to find wrong outputs (for example an invented budget for enquiry 001 and a wrong requirement for enquiry 007) so they could be fixed, and managed the project on GitHub.

I can explain and modify every important part of this project.

## 15. Author

NAVEENJOAHN S A

Developed for the Curd Rice Business Studio AI Intern technical assessment.