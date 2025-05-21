-- db/init.sql

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create role only if it doesn't exist
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'leads_user') THEN
      CREATE ROLE leads_user WITH LOGIN PASSWORD 'secret_pass';
   END IF;
END$$;

GRANT ALL PRIVILEGES ON DATABASE leadsdb TO leads_user;

-- Table 1: person
CREATE TABLE IF NOT EXISTS person (
    id            SERIAL PRIMARY KEY,
    full_name     TEXT NOT NULL,
    first_name    TEXT,
    last_name     TEXT,
    current_title TEXT,
    location      TEXT,
    bio           TEXT,
    summary       TEXT,
    quality_score NUMERIC,
    embedding     VECTOR(768),
    created_at    TIMESTAMPTZ DEFAULT now()
);

-- Index for fast name search
CREATE INDEX IF NOT EXISTS idx_person_full_name_trgm ON person USING gin (full_name gin_trgm_ops);

-- Table 2: email
CREATE TABLE IF NOT EXISTS email (
    id         SERIAL PRIMARY KEY,
    person_id  INT REFERENCES person(id) ON DELETE CASCADE,
    address    TEXT UNIQUE NOT NULL,
    confidence NUMERIC DEFAULT 1.0,
    is_primary BOOLEAN DEFAULT FALSE
);

-- Table 3: organization
CREATE TABLE IF NOT EXISTS organization (
    id       SERIAL PRIMARY KEY,
    name     TEXT UNIQUE NOT NULL,
    org_type TEXT,
    country  TEXT
);

-- Table 4: affiliation
CREATE TABLE IF NOT EXISTS affiliation (
    person_id INT REFERENCES person(id) ON DELETE CASCADE,
    org_id    INT REFERENCES organization(id) ON DELETE CASCADE,
    role      TEXT,
    PRIMARY KEY(person_id, org_id, role)
);

-- Table 5: source (provenance of scraped content)
CREATE TABLE IF NOT EXISTS source (
    id         SERIAL PRIMARY KEY,
    person_id  INT REFERENCES person(id) ON DELETE CASCADE,
    url        TEXT,
    snippet    TEXT,
    source_rank SMALLINT,
    fetched_at TIMESTAMPTZ
);

-- Table 6: edge (person-to-person relationships)
CREATE TABLE IF NOT EXISTS edge (
    from_id  INT REFERENCES person(id) ON DELETE CASCADE,
    to_id    INT REFERENCES person(id) ON DELETE CASCADE,
    rel_type TEXT,
    weight   NUMERIC DEFAULT 1,
    PRIMARY KEY(from_id, to_id, rel_type)
);
