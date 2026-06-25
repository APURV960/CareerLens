-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table (Supports Mode A: Anonymous Sessions & Mode B: JWT Authenticated Users)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    session_id UUID UNIQUE,                             -- Used for Mode A (Anonymous Session)
    email VARCHAR(255) UNIQUE,                          -- Used for Mode B (Null for Anonymous)
    hashed_password VARCHAR(255),                       -- Null for Anonymous
    is_anonymous BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_session ON users(session_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email) WHERE email IS NOT NULL;

-- 2. Resumes Table (Supports Resume Versioning)
CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    storage_key VARCHAR(512) NOT NULL,                  -- Key used to fetch file from storage provider
    resume_text TEXT NOT NULL,
    extracted_skills JSONB NOT NULL,                    -- Array of string skills
    version INT NOT NULL DEFAULT 1,                     -- Increments per user upload
    is_active BOOLEAN DEFAULT TRUE NOT NULL,            -- Only one active resume per user
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_resumes_user ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_resumes_active ON resumes(user_id) WHERE is_active = TRUE;

-- 3. Agent Jobs Table (Async Execution Tracking)
CREATE TABLE IF NOT EXISTS agent_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'queued' NOT NULL,       -- queued, running, completed, failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_agent_jobs_user ON agent_jobs(user_id);

-- 4. Search Runs Table (Execution History Root)
CREATE TABLE IF NOT EXISTS search_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resume_id INT NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    job_id UUID REFERENCES agent_jobs(id) ON DELETE SET NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'running' NOT NULL       -- running, success, failed
);

CREATE INDEX IF NOT EXISTS idx_search_runs_user ON search_runs(user_id);

-- 5. Job Results Table (Extended for Analytics)
CREATE TABLE IF NOT EXISTS job_results (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    search_run_id UUID NOT NULL REFERENCES search_runs(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    url VARCHAR(1024) NOT NULL,
    match_score DOUBLE PRECISION NOT NULL,
    salary VARCHAR(100),                                -- Analytics Field
    employment_type VARCHAR(100),                       -- Analytics Field
    source VARCHAR(100),                                -- Analytics Field
    experience_level VARCHAR(100),                      -- Analytics Field
    work_setting VARCHAR(100),                          -- Analytics Field
    posted_at VARCHAR(100),                             -- Analytics Field
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_job_results_run ON job_results(search_run_id);
CREATE INDEX IF NOT EXISTS idx_job_results_user_score ON job_results(user_id, match_score DESC);

-- 6. Skill Gaps Table (Linked to Search Run)
CREATE TABLE IF NOT EXISTS skill_gaps (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    search_run_id UUID NOT NULL REFERENCES search_runs(id) ON DELETE CASCADE,
    missing_skills JSONB NOT NULL,                      -- List of strings
    market_demand JSONB NOT NULL,                       -- List of skill frequencies
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_skill_gaps_run ON skill_gaps(search_run_id);

-- 7. Cover Letters Table (Database as Source of Truth)
CREATE TABLE IF NOT EXISTS cover_letters (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    search_run_id UUID NOT NULL REFERENCES search_runs(id) ON DELETE CASCADE,
    company VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,                              -- Full letter content
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cover_letters_run ON cover_letters(search_run_id);

-- 8. Applications Table
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_result_id INT NOT NULL REFERENCES job_results(id) ON DELETE CASCADE,
    cover_letter_id INT REFERENCES cover_letters(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'Generated' NOT NULL,        -- Generated, Applied, Interview, Rejected, Offer
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);
