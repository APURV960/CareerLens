# AI Job Agent

An **AI-powered career assistant** that analyzes a user's resume, discovers relevant job opportunities, identifies skill gaps, and automatically generates tailored cover letters.

The system combines **AI agents, semantic search, Retrieval-Augmented Generation (RAG), and persistent memory** to automate the job discovery workflow.

---

# Features

### Resume Intelligence

* Parses and analyzes resumes
* Extracts relevant skills using NLP
* Understands user expertise and experience

### Automated Job Discovery

* Searches job portals using skill-based queries
* Filters and ranks jobs based on resume similarity
* Uses semantic similarity for better matching

### Skill Gap Analysis

* Compares job requirements with resume skills
* Identifies missing or in-demand skills
* Provides career improvement suggestions

### AI Cover Letter Generation

* Generates tailored cover letters for each job
* Uses Gemini API with fallback template support

### Career Knowledge Assistant (RAG)

* Uses vector search over curated career knowledge documents
* Provides grounded career advice instead of hallucinated answers

### Persistent Agent Memory

* Stores results and user data using PostgreSQL
* Tracks job recommendations and generated applications

### Structured Job Export

* Saves ranked job results to Excel
* Easy to review and track opportunities

---

# System Architecture

```
User Resume
      ↓
Resume Parser
      ↓
Skill Extraction
      ↓
Job Search Engine
      ↓
Semantic Job Ranking
      ↓
Skill Gap Analysis
      ↓
AI Agent Tools
   ├ Cover Letter Generator
   └ Career Advice (RAG)
      ↓
Results Export + Memory Storage
```

---

# Project Structure

```
AI-Job-Agent
│
├ data
│   └ career_docs/           # Knowledge base for RAG
│
├ output
│   ├ cover_letters/         # Generated cover letters
│   └ job_matches.xlsx       # Ranked job results
│
├ src
│
│   ├ agent
│   │   ├ executor.py
│   │   ├ planner.py
│   │   └ tools_registry.py
│
│   ├ rag
│   │   ├ rag_agent.py
│   │   ├ vector_store.py
│   │   └ ingest_docs.py
│
│   ├ memory
│   │   ├ database.py
│   │   └ memory_store.py
│
│   ├ tools
│   │   ├ resume_tool.py
│   │   ├ job_search_tool.py
│   │   ├ ranking_tool.py
│   │   ├ skill_gap_tool.py
│   │   └ cover_letter_tool.py
│
│   ├ main_agent.py
│   └ excel_writer.py
│
├ requirements.txt
└ README.md
```

---

# Tech Stack

* Python
* Sentence Transformers
* FAISS (vector search)
* spaCy (NLP)
* Gemini API
* PostgreSQL
* Pandas

---

# Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/AI-Job-Agent.git
cd AI-Job-Agent
```

Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Download spaCy model:

```bash
python -m spacy download en_core_web_sm
```

---

# Environment Variables

Create a `.env` file in the project root.

```
APP_ID=your_adzuna_app_id
APP_KEY=your_adzuna_app_key

GEMINI_API_KEY=your_gemini_api_key

DB_PASSWORD=your_postgres_password
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
