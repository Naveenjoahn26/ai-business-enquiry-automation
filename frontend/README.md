# Curd Rice Business Studio · AI Enquiry Automation Dashboard

A simple, focused frontend interface built specifically for the Curd Rice Business Studio AI Intern Technical Assessment. It borrows the brand typography (`Plus Jakarta Sans`), colors (Warm Cream `#FAF8F3`, Deep Pine Green `#0B473E`, Honey Mustard `#F5B82E`), and aesthetic without touching the backend code.

---

## Technical Assessment Modules Covered

| Module | What It Does |
|---|---|
| **Module A: Enquiry Classification** | Categorizes business enquiries (AI automation, ERP, website, internship, etc.) and extracts budget, timeline, urgency, and requirement. |
| **Module B: Intelligent Lead Scoring** | Calculates priority score (0–100) with High/Medium/Low priority badges and transparent itemized reasons. |
| **Module C: Human Review & Draft Reply** | Flags sensitive topics, complaints, pricing requests, and high-priority leads with amber warnings; generates safe personalised response drafts with 1-click clipboard copy. |
| **Module D: Automation & Storage** | Saves enquiries to SQLite (`data/enquiries.db`) and provides a live record viewer with automatic table updates. |

---

## How to Run

### Option 1: Direct in Browser
Double-click or open [frontend/index.html](file:///C:/Users/Admin/ai-business-enquiry-automation/frontend/index.html) in your browser.

### Option 2: Local Server with Dev Proxy (Recommended)
While your FastAPI backend is running (`uvicorn main:app --reload` on port 8000):
```powershell
python frontend/server.py
```
Visit **`http://localhost:3000`**. The lightweight server proxies all API calls (`/analyse`, `/enquiries`, `/upload-csv`, `/health`) to `http://127.0.0.1:8000` with zero CORS issues.
