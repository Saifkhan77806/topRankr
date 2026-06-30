CREATE TABLE IF NOT EXISTS candidate_security (
    id SERIAL PRIMARY KEY,
    candidate_email VARCHAR,
    resume_hash VARCHAR,
    spam_score INTEGER NOT NULL DEFAULT 0,
    prompt_injection BOOLEAN NOT NULL DEFAULT FALSE,
    duplicate_resume BOOLEAN NOT NULL DEFAULT FALSE,
    virus_scan VARCHAR NOT NULL DEFAULT 'not_scanned',
    allowed BOOLEAN NOT NULL DEFAULT FALSE,
    rejection_reason VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_candidate_security_id
    ON candidate_security (id);

CREATE INDEX IF NOT EXISTS ix_candidate_security_candidate_email
    ON candidate_security (candidate_email);

CREATE INDEX IF NOT EXISTS ix_candidate_security_resume_hash
    ON candidate_security (resume_hash);
