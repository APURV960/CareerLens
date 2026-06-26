# 🎯 CareerLens

## **AI-Powered Career Discovery, Resume Intelligence & Job Matching Platform**

> **Upload your resume → Discover relevant jobs → Identify skill gaps → Generate AI-powered cover letters → Track your applications**

---

## 📖 Overview

**CareerLens** is an end-to-end AI-powered career assistant that helps job seekers streamline the entire job search process.

Instead of manually searching job portals and comparing job descriptions, CareerLens intelligently:

* 📄 Analyzes resumes
* 🔍 Discovers relevant job opportunities
* 🎯 Ranks jobs using semantic similarity
* 📊 Identifies missing skills
* 📚 Recommends learning paths
* ✉️ Generates personalized cover letters
* 📈 Tracks job applications and previous searches

---

# ✨ Features

## 📄 Resume Analysis

* PDF Resume Upload
* Automatic Resume Parsing
* AI-powered Skill Extraction
* Resume Versioning
* Session-based User Management

---

## 🔍 AI Job Discovery

* Semantic Job Search
* Intelligent Query Generation
* AI-based Job Ranking
* Company & Location Matching
* Experience Level Matching
* Salary Information
* Employment Type Detection
* Direct Job Application Links

---

## 🧠 Skill Gap Analysis

* Missing Skill Detection
* Market Demand Analysis
* Skill Frequency Visualization
* Learning Roadmap
* Curated Learning Resources
* Career Guidance Dashboard

---

## ✉️ AI Cover Letter Generator

* Personalized Cover Letters
* Editable Before Download
* Copy to Clipboard
* Download as Text
* Automatic Fallback Generation

---

## 📈 Search History

* Resume Version History
* Previous Search Runs
* Historical Job Matches
* Historical Skill Analysis
* Generated Cover Letters Archive

---

## 📂 Application Tracking

Track every application through its lifecycle:

* 🟡 Generated
* 🔵 Applied
* 🟠 Interview
* 🟢 Offer
* 🔴 Rejected

---

# 🛠 Tech Stack

## **Frontend**

* HTML5
* CSS3
* Vanilla JavaScript

### **Backend**

* FastAPI
* Python
* Uvicorn

### **Database**

* PostgreSQL
* Neon PostgreSQL
* psycopg2 Connection Pool

### **AI & NLP**

* Google Gemini API
* Sentence Transformers
* spaCy
* FAISS Vector Search
* Scikit-learn

### **Job Search**

* Adzuna Jobs API

### **Production Stack**

* Google Cloud Run
* Docker
* Neon PostgreSQL

---

# 🏗 System Architecture

```text
                           User Uploads Resume (PDF)
                                       │
                                       ▼
                    Resume Parsing & Text Extraction Engine
                                       │
                                       ▼
                     NLP-Based Skill Extraction (spaCy)
                                       │
                                       ▼
          Semantic Resume Embedding (Sentence Transformers)
                                       │
                     ┌─────────────────┴─────────────────┐
                     │                                   │
                     ▼                                   ▼
         Intelligent Query Generator         Resume Embedding Cache
                     │                                   │
                     └─────────────────┬─────────────────┘
                                       ▼
                          Adzuna Job Search API
                                       │
                                       ▼
                     Semantic Job Ranking Engine
                 (Cosine Similarity + Embeddings)
                                       │
             ┌─────────────────────────┼────────────────────────┐
             │                         │                        │
             ▼                         ▼                        ▼
      Skill Gap Analysis      Market Demand Analysis   Job Match Analytics
             │                         │                        │
             └──────────────┬──────────┴──────────────┬─────────┘
                            ▼                         ▼
             AI Cover Letter Generator      Application Tracker
                     (Google Gemini)                │
                            └──────────────┬────────┘
                                           ▼
                        PostgreSQL (Neon) Data Persistence
                                           │
                                           ▼
                     FastAPI REST API + Interactive Dashboard
```

---

# 📂 Project Structure

```text
CareerLens/
│
├── backend/
│   ├── auth/
│   ├── repositories/
│   ├── routes/
│   ├── services/
│   ├── schema.sql
│   └── main.py
│
├── frontend/
│   ├── css/
│   ├── js/
│   ├── index.html
│   ├── upload.html
│   ├── dashboard.html
│   ├── results.html
│   └── history.html
│
├── src/
│   ├── agent/
│   ├── rag/
│   ├── services/
│   ├── memory/
│   ├── tools/
│   └── main_agent.py
│
├── data/
├── output/
├── storage/
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# ⚡ Installation

### Clone the Repository

```bash
git clone https://github.com/APURV960/CareerLens.git

cd CareerLens
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ⚙ Configuration

Create a **.env** file:

```env
APP_ID=YOUR_ADZUNA_APP_ID
APP_KEY=YOUR_ADZUNA_APP_KEY

GEMINI_API_KEY=YOUR_GEMINI_API_KEY

DATABASE_URL=YOUR_NEON_DATABASE_URL

JWT_SECRET=YOUR_SECRET_KEY

STORAGE_PROVIDER=local
```

---

# ▶ Running the Application

### Apply Database Schema

```bash
python -m backend.apply_schema
```

### Start Backend

```bash
python backend/main.py
```

Open:

```text
http://localhost:8000
```

---

# 📸 Screenshots

> Add screenshots for:

* Landing Page
  <img width="1897" height="863" alt="image" src="https://github.com/user-attachments/assets/29f5a3e7-b671-4d9d-ae1e-2dcd19974831" />

* Resume Upload
  <img width="1894" height="860" alt="image" src="https://github.com/user-attachments/assets/5aa3b6a7-8378-41cd-a772-53d41065e2af" />

* Dashboard
  <img width="1899" height="863" alt="image" src="https://github.com/user-attachments/assets/a3080ae9-b1a6-450f-80ff-6631c4cab60c" />


* Results Page
  <img width="1891" height="868" alt="image" src="https://github.com/user-attachments/assets/697fabaa-3ddb-4703-8b1d-950c8a4fbaf1" />


---

# 🔮 Future Improvements

* ATS Resume Score
* Resume Optimizer
* AI Interview Preparation
* LinkedIn Profile Analysis
* Company Insights
* Salary Prediction
* Email Automation
* Cloud Storage Integration
* Authentication & User Accounts
* Background Job Queue
* Recruiter Dashboard
* Multi-language Resume Support

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new feature branch
3. Commit your changes
4. Push your branch
5. Open a Pull Request

---

# 📄 License

Licensed under the **MIT License**.

---

# 👨‍💻 Author

**Apurva Anand**

**B.Tech Computer Science Engineering**

Passionate about **Artificial Intelligence**, **Full-Stack Development**, **Natural Language Processing**, and building intelligent software systems.

* **GitHub:** https://github.com/APURV960
* **LinkedIn:** https://www.linkedin.com/in/apurva-anand-2313a0249/

---

## ⭐ If you found this project useful, consider giving it a Star!

It helps others discover the project and supports future development.
