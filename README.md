# 🎯 CareerLens

> **AI-Powered Career Discovery Platform**
>
> Upload your resume, discover relevant jobs, identify skill gaps, generate personalized cover letters, and track your job search—all in one place.

---

## 📖 Overview

CareerLens is an end-to-end AI-powered career assistant that helps job seekers analyze their resumes, discover matching job opportunities, identify missing skills, and generate tailored application materials.

Unlike traditional job portals, CareerLens combines semantic search, natural language processing, vector embeddings, and large language models to understand a candidate's profile and recommend opportunities based on overall relevance rather than simple keyword matching.

---

## ✨ Features

### 📄 Resume Analysis

* Upload PDF resumes
* Automatic resume parsing
* AI-powered skill extraction
* Resume versioning
* Session-based user management

---

### 🔍 AI Job Discovery

* Semantic job search
* Intelligent query generation
* Job ranking using embedding similarity
* Company, location, salary, and experience matching
* Direct job application links

---

### 📊 Skill Gap Analysis

* Compare resume skills against job market demand
* Identify missing skills
* Market demand visualization
* Learning roadmap
* Curated learning resources

---

### ✉ AI Cover Letter Generator

* Personalized cover letters
* Editable before download
* Copy to clipboard
* Download as text
* Automatic fallback generation if LLM services are unavailable

---

### 📈 Search History

* Store previous searches
* Resume version history
* View historical job matches
* Revisit previous analyses

---

### 📂 Application Tracking

Track the status of each application:

* Generated
* Applied
* Interview
* Offer
* Rejected

---

## 🛠 Tech Stack

### Frontend

* HTML5
* CSS3
* Vanilla JavaScript

### Backend

* FastAPI
* Python

### Database

* PostgreSQL

### AI & NLP

* Google Gemini API
* SentenceTransformers
* spaCy
* FAISS Vector Search

### Job Search

* Adzuna Jobs API

### Storage

* PostgreSQL
* Local file storage (development)

---

## 🏗 Project Structure

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
│   ├── tools/
│   ├── memory/
│   └── main_agent.py
│
├── data/
├── output/
├── requirements.txt
└── README.md
```

---

## 🚀 Workflow

```text
Upload Resume
        │
        ▼
Resume Parsing
        │
        ▼
Skill Extraction
        │
        ▼
Semantic Job Search
        │
        ▼
Job Ranking
        │
        ▼
Skill Gap Analysis
        │
        ▼
Cover Letter Generation
        │
        ▼
Results Dashboard
        │
        ▼
Application Tracking
```

---

## ⚡ Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/CareerLens.git
cd CareerLens
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment:

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙ Configuration

Create a `.env` file:

```env
APP_ID=YOUR_ADZUNA_APP_ID
APP_KEY=YOUR_ADZUNA_APP_KEY

GEMINI_API_KEY=YOUR_GEMINI_API_KEY

DB_PASSWORD=YOUR_POSTGRES_PASSWORD
```

Configure PostgreSQL and execute the schema before running the application.

---

## ▶ Running the Application

Start the backend:

```bash
python backend/main.py
```

Open the application:

```
http://localhost:8000
```

---

# Setup PostgreSQL

Create database:

```sql
CREATE DATABASE ai_agent;
```

Create tables:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT
);

CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    user_id INT,
    content TEXT
);

CREATE TABLE job_results (
    id SERIAL PRIMARY KEY,
    user_id INT,
    job_title TEXT,
    company TEXT,
    match_score FLOAT
);

CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    user_id INT,
    company TEXT,
    role TEXT,
    cover_letter TEXT
);
```

---

# Prepare RAG Knowledge Base

Add career documents inside:

```
data/career_docs/
```

Example files:

```
ml_engineer.txt
data_scientist.txt
backend_developer.txt
devops_engineer.txt
```

Then run:

```bash
python -m src.rag.ingest_docs
```

---

# Run the AI Agent

```bash
python src/main_agent.py
```

Example output:

```
Goal: Find best jobs and prepare applications

Agent action: analyze_resume
Agent action: search_jobs
Agent action: rank_jobs
Agent action: analyze_skill_gap
Agent action: generate_cover_letters
```

Generated files:

```
output/job_matches.xlsx
output/cover_letters/*.txt
```

---

# Example Workflow

1. Upload resume
2. Extract skills
3. Discover relevant jobs
4. Rank opportunities using embeddings
5. Detect missing skills
6. Generate tailored cover letters
7. Export job matches

---

# Future Improvements

* Web dashboard (FastAPI + React)
* Resume optimization suggestions
* Application tracking system
* Scheduled job alerts
* Advanced agent planning
* Cached LLM responses to reduce API usage
