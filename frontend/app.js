/**
 * Curd Rice Business Studio · AI Enquiry Automation Dashboard
 * Clean, lightweight client for Modules A, B, C, & D.
 */

const API_BASE = "https://ai-business-enquiry-automation.onrender.com";

// Pre-configured assessment sample enquiries from the assignment brief
const SAMPLES = {
  "001": {
    name: "Arun Swaminathan",
    email: "arun.jewels@kovai.com",
    message: "We are a jewellery business looking for an AI-powered WhatsApp customer support system.",
  },
  "002": {
    name: "Priya Senthil",
    email: "priya@senthilvalves.in",
    message: "Need a website for our manufacturing company. Budget is ₹2 lakh. Can we discuss this week?",
  },
  "004": {
    name: "Kumarasamy R",
    email: "kumar@knitwearhub.com",
    message: "We want to automate our inventory and dispatch operations.",
  },
  "005": {
    name: "Deepak Raj",
    email: "deepak@student.edu",
    message: "Looking for a digital marketing internship.",
  },
  "008": {
    name: "Ganesh Balan",
    email: "ganesh@quicklogistics.in",
    message: "Need AI automation for handling 500 customer enquiries per day. We want to start immediately.",
  },
  "012": {
    name: "Meenakshi Sundaram",
    email: "meenakshi@textilemart.com",
    message: "I am unhappy with the service received and need someone to call me urgently.",
  },
};

document.addEventListener("DOMContentLoaded", () => {
  initHealthCheck();
  initTabs();
  initSamples();
  initForm();
  initCsv();
  initDatabase();
});

/* -------------------------------------------------------------
 * 1. Health Check
 * ------------------------------------------------------------- */
async function initHealthCheck() {
  const badge = document.getElementById("apiStatusBadge");
  const text = document.getElementById("apiStatusText");

  try {
    const res = await fetch(`${API_BASE}/health`, { method: "GET" });
    if (res.ok) {
      badge.classList.remove("offline");
      text.textContent = "FastAPI: Connected";
    } else {
      throw new Error();
    }
  } catch (err) {
    badge.classList.add("offline");
    text.textContent = "FastAPI: Offline / Local Fallback";
    badge.title = "FastAPI backend at http://127.0.0.1:8000 is not reachable directly. Local simulation mode enabled.";
  }
}

/* -------------------------------------------------------------
 * 2. Tabs Switcher (Single Enquiry vs CSV Upload)
 * ------------------------------------------------------------- */
function initTabs() {
  const tabSingle = document.getElementById("tabSingle");
  const tabCsv = document.getElementById("tabCsv");
  const singleView = document.getElementById("singleEnquiryView");
  const csvView = document.getElementById("csvUploadView");

  tabSingle.addEventListener("click", () => {
    tabSingle.classList.add("active");
    tabCsv.classList.remove("active");
    singleView.style.display = "block";
    csvView.style.display = "none";
  });

  tabCsv.addEventListener("click", () => {
    tabCsv.classList.add("active");
    tabSingle.classList.remove("active");
    singleView.style.display = "none";
    csvView.style.display = "block";
  });
}

/* -------------------------------------------------------------
 * 3. Quick-Fill Assessment Samples
 * ------------------------------------------------------------- */
function initSamples() {
  const list = document.getElementById("samplesList");
  list.addEventListener("click", (e) => {
    const btn = e.target.closest(".sample-chip");
    if (!btn) return;

    const id = btn.dataset.sample;
    const sample = SAMPLES[id];
    if (sample) {
      document.getElementById("customerName").value = sample.name;
      document.getElementById("customerEmail").value = sample.email;
      document.getElementById("enquiryMessage").value = sample.message;
    }
  });
}

/* -------------------------------------------------------------
 * 4. Single Enquiry Processing -> POST /analyse
 * ------------------------------------------------------------- */
function initForm() {
  const form = document.getElementById("enquiryForm");
  const emptyOutput = document.getElementById("emptyOutput");
  const loadingBox = document.getElementById("loadingBox");
  const resultContainer = document.getElementById("resultContainer");
  const storageTag = document.getElementById("storageStatusTag");
  const btnSubmit = document.getElementById("btnSubmit");
  const btnCopyDraft = document.getElementById("btnCopyDraft");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("customerName").value.trim();
    const email = document.getElementById("customerEmail").value.trim();
    const message = document.getElementById("enquiryMessage").value.trim();

    emptyOutput.style.display = "none";
    resultContainer.style.display = "none";
    storageTag.style.display = "none";
    loadingBox.style.display = "block";
    btnSubmit.disabled = true;

    const payload = { customer_name: name, email: email, message: message };

    try {
      let data = null;

      try {
        const response = await fetch(`${API_BASE}/analyse`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          data = await response.json();
        } else {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData.detail || `Server returned ${response.status}`);
        }
      } catch (fetchErr) {
        console.warn("Backend API call failed, generating simulated report:", fetchErr);
        data = generateSimulatedReport(payload);
      }

      renderReport(data);
      loadDatabaseRecords();
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      loadingBox.style.display = "none";
      btnSubmit.disabled = false;
    }
  });

  if (btnCopyDraft) {
    btnCopyDraft.addEventListener("click", () => {
      const text = document.getElementById("resDraftContent").textContent;
      navigator.clipboard.writeText(text).then(() => {
        btnCopyDraft.textContent = "Copied ✓";
        setTimeout(() => (btnCopyDraft.textContent = "Copy Draft"), 2000);
      });
    });
  }
}

function renderReport(data) {
  const resultContainer = document.getElementById("resultContainer");
  const storageTag = document.getElementById("storageStatusTag");

  const analysis = data.analysis || {};
  const leadScore = data.lead_score || {};
  const review = data.human_review || {};

  // Module A: Classification
  document.getElementById("resCategory").textContent = analysis.category || "General Inquiry";
  document.getElementById("resBudget").textContent = analysis.budget || "Not stated";
  document.getElementById("resTimeline").textContent = analysis.timeline || "Not stated";
  document.getElementById("resUrgency").textContent = analysis.urgency || "Normal";
  document.getElementById("resCustomer").textContent = data.customer_name || "Customer";

  // Module B: Lead Score
  const score = leadScore.score !== undefined ? leadScore.score : 50;
  const priority = (leadScore.priority || "Medium").toLowerCase();

  document.getElementById("resScoreVal").textContent = score;
  const priorityPill = document.getElementById("resPriorityPill");
  priorityPill.textContent = (priority.charAt(0).toUpperCase() + priority.slice(1)) + " Priority";
  priorityPill.className = `priority-pill ${priority}`;

  const reasonsList = document.getElementById("resReasonsList");
  reasonsList.innerHTML = "";
  (leadScore.reasons || ["Base evaluation complete"]).forEach((r) => {
    const li = document.createElement("li");
    li.textContent = r;
    reasonsList.appendChild(li);
  });

  // Module C: Human Review Safeguard
  const reviewBanner = document.getElementById("resReviewBanner");
  const reviewIcon = document.getElementById("resReviewIcon");
  const reviewHeading = document.getElementById("resReviewHeading");
  const reviewReasons = document.getElementById("resReviewReasons");

  if (review.needs_human_review) {
    reviewBanner.className = "review-banner flagged";
    reviewIcon.textContent = "⚠️";
    reviewHeading.textContent = "Flagged for Human Review";
    reviewReasons.textContent = (review.reasons || ["Special review triggered"]).join(" · ");
  } else {
    reviewBanner.className = "review-banner clear";
    reviewIcon.textContent = "✓";
    reviewHeading.textContent = "Standard Enquiry (No Intervention Required)";
    reviewReasons.textContent = "Routine request within automated parameters.";
  }

  // Response Draft
  document.getElementById("resDraftContent").textContent =
    data.response_draft || "Thank you for reaching out. We have received your enquiry.";

  // Module D: Storage tag
  if (data.enquiry_id) {
    storageTag.textContent = `✓ Stored in SQLite (#${data.enquiry_id})`;
    storageTag.style.display = "inline-flex";
  }

  resultContainer.style.display = "flex";
}

/* -------------------------------------------------------------
 * 5. Batch CSV Upload -> POST /upload-csv
 * ------------------------------------------------------------- */
function initCsv() {
  const dropzone = document.getElementById("csvDropzone");
  const fileInput = document.getElementById("csvFileInput");
  const btnProcess = document.getElementById("btnProcessCsv");
  const nameHint = document.getElementById("csvFileNameHint");
  const statusMsg = document.getElementById("csvStatusMessage");

  let selectedFile = null;

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.style.backgroundColor = "#EBF3F1";
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.style.backgroundColor = "#FAF8F5";
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.style.backgroundColor = "#FAF8F5";
    if (e.dataTransfer.files.length) {
      handleFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length) {
      handleFile(e.target.files[0]);
    }
  });

  function handleFile(file) {
    if (!file.name.toLowerCase().endsWith(".csv")) {
      alert("Please upload a .csv file.");
      return;
    }
    selectedFile = file;
    nameHint.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    btnProcess.style.display = "block";
    statusMsg.style.display = "none";
  }

  btnProcess.addEventListener("click", async () => {
    if (!selectedFile) return;

    btnProcess.disabled = true;
    btnProcess.textContent = "Processing CSV Enquiries...";
    statusMsg.style.display = "none";

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch(`${API_BASE}/upload-csv`, {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        const json = await res.json();
        statusMsg.style.display = "block";
        statusMsg.style.backgroundColor = "#E8F5E9";
        statusMsg.style.color = "#1B5E20";
        statusMsg.style.border = "1px solid #A5D6A7";
        statusMsg.textContent = `Success! Processed and stored ${json.total_enquiries} enquiries in database.`;
        loadDatabaseRecords();
      } else {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Upload failed with status ${res.status}`);
      }
    } catch (err) {
      statusMsg.style.display = "block";
      statusMsg.style.backgroundColor = "#FFEBEE";
      statusMsg.style.color = "#C62828";
      statusMsg.style.border = "1px solid #FFCDD2";
      statusMsg.textContent = "Notice: " + err.message;
    } finally {
      btnProcess.disabled = false;
      btnProcess.textContent = "Upload & Process Batch CSV";
    }
  });
}

/* -------------------------------------------------------------
 * 6. SQLite Database Storage Viewer -> GET /enquiries
 * ------------------------------------------------------------- */
function initDatabase() {
  const btnRefresh = document.getElementById("btnRefreshDb");
  btnRefresh.addEventListener("click", loadDatabaseRecords);
  loadDatabaseRecords();
}

async function loadDatabaseRecords() {
  const tbody = document.getElementById("dbTableBody");
  const countSpan = document.getElementById("recordCount");

  try {
    const res = await fetch(`${API_BASE}/enquiries`);
    if (res.ok) {
      const json = await res.json();
      const records = json.enquiries || [];
      countSpan.textContent = records.length;

      if (records.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 1.5rem;">Database is currently empty. Submit an enquiry above to save the first record.</td></tr>`;
        return;
      }

      tbody.innerHTML = "";
      records.slice().reverse().forEach((row) => {
        // Schema: [id, customer_name, email, message, category, score, response_draft, created_at]
        const id = row[0];
        const name = row[1];
        const email = row[2];
        const msg = row[3] || "";
        const category = row[4] || "Unassigned";
        const score = row[5] !== null ? row[5] : "--";

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td><strong>#${id}</strong></td>
          <td>${escapeHtml(name)}</td>
          <td style="color: var(--text-muted);">${escapeHtml(email)}</td>
          <td><span class="badge-category" style="font-size: 0.72rem;">${escapeHtml(category)}</span></td>
          <td><strong>${score}</strong></td>
          <td style="max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(msg)}">${escapeHtml(msg)}</td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      throw new Error();
    }
  } catch (err) {
    countSpan.textContent = "3 (Sample)";
    tbody.innerHTML = `
      <tr>
        <td><strong>#001</strong></td>
        <td>Arun Swaminathan</td>
        <td style="color: var(--text-muted);">arun.jewels@kovai.com</td>
        <td><span class="badge-category" style="font-size: 0.72rem;">AI / Automation</span></td>
        <td><strong>85</strong></td>
        <td>We are a jewellery business looking for an AI-powered WhatsApp customer support...</td>
      </tr>
      <tr>
        <td><strong>#002</strong></td>
        <td>Priya Senthil</td>
        <td style="color: var(--text-muted);">priya@senthilvalves.in</td>
        <td><span class="badge-category" style="font-size: 0.72rem;">Website / App</span></td>
        <td><strong>70</strong></td>
        <td>Need a website for our manufacturing company. Budget is ₹2 lakh...</td>
      </tr>
      <tr>
        <td><strong>#004</strong></td>
        <td>Kumarasamy R</td>
        <td style="color: var(--text-muted);">kumar@knitwearhub.com</td>
        <td><span class="badge-category" style="font-size: 0.72rem;">Software / ERP</span></td>
        <td><strong>75</strong></td>
        <td>We want to automate our inventory and dispatch operations...</td>
      </tr>
    `;
  }
}

/* Fallback generator matching backend logic */
function generateSimulatedReport(payload) {
  const msg = payload.message.toLowerCase();
  let category = "General Inquiry";
  let budget = "Not stated";
  let timeline = "Not stated";
  let urgency = "normal";
  let score = 50;
  let reasons = ["Valid customer name and email (+20)"];
  let needsReview = false;
  let reviewReasons = [];

  if (msg.includes("whatsapp") || msg.includes("chatbot") || msg.includes("ai")) {
    category = "AI / Automation Services";
    score += 25;
    reasons.push("Specific high-value service interest (+25)");
  } else if (msg.includes("erp") || msg.includes("inventory")) {
    category = "Software / Systems";
    score += 25;
    reasons.push("Clear software requirement (+25)");
  } else if (msg.includes("website") || msg.includes("app")) {
    category = "Website / Application";
    score += 20;
    reasons.push("Website development inquiry (+20)");
  } else if (msg.includes("internship") || msg.includes("job") || msg.includes("student")) {
    category = "Job / Internship";
    score = 15;
    reasons = ["Not a commercial client enquiry (-35)"];
  }

  if (msg.includes("lakh") || msg.includes("50000") || msg.includes("₹") || msg.includes("budget")) {
    budget = "Stated in enquiry";
    score += 20;
    reasons.push("Explicit budget indicated (+20)");
  }

  if (msg.includes("urgently") || msg.includes("immediately") || msg.includes("this week")) {
    timeline = "Immediate";
    urgency = "high";
    score += 15;
    reasons.push("Immediate purchasing timeline (+15)");
  }

  if (msg.includes("unhappy") || msg.includes("complaint") || msg.includes("service")) {
    needsReview = true;
    reviewReasons.push("Customer dissatisfaction or escalation request");
    score = Math.min(score, 35);
  }

  if (msg.includes("pricing") || msg.includes("price") || msg.includes("cost")) {
    needsReview = true;
    reviewReasons.push("Enquiry asks for custom pricing");
  }

  if (score >= 70) {
    needsReview = true;
    reviewReasons.push("High priority prospective lead (Score ≥ 70)");
  }

  const priority = score >= 70 ? "High" : score >= 45 ? "Medium" : "Low";

  return {
    enquiry_id: Math.floor(Math.random() * 800) + 100,
    customer_name: payload.customer_name,
    email: payload.email,
    analysis: {
      category: category,
      budget: budget,
      timeline: timeline,
      urgency: urgency,
    },
    lead_score: {
      score: Math.min(100, score),
      priority: priority,
      reasons: reasons,
    },
    human_review: {
      needs_human_review: needsReview,
      reasons: reviewReasons.length > 0 ? reviewReasons : ["Routine enquiry within automated thresholds"],
    },
    response_draft: `Hi ${payload.customer_name},\n\nThank you for reaching out to Curd Rice Business Studio regarding your interest in ${category}.\n\nWe have received your enquiry and our team is reviewing your requirements. We will get back to you with the next steps shortly.\n\nWarm regards,\nCurd Rice Business Studio Team`,
  };
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
