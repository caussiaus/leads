-- Enable vectors and trigram for fuzzy name / email lookups
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Only needed if the environment doesn't auto-create this
CREATE ROLE leads_user WITH LOGIN PASSWORD 'pass';
GRANT ALL PRIVILEGES ON DATABASE leadsdb TO leads_user;


------------------------------------------------------------
-- 1. People / Leads
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS person (
    id            SERIAL PRIMARY KEY,
    full_name     TEXT                NOT NULL,
    first_name    TEXT,
    last_name     TEXT,
    current_title TEXT,                        -- e.g. Professor, CEO
    location      TEXT,                        -- city / country string
    bio           TEXT,
    summary       TEXT,                        -- Mistral‑7B output
    quality_score NUMERIC,                     -- 1‑10 (writing quality)
    embedding     VECTOR(768),                 -- from E5‑large
    created_at    TIMESTAMPTZ DEFAULT now()
);

-- Fast name search
CREATE INDEX IF NOT EXISTS idx_person_full_name_trgm
          ON person USING gin (full_name gin_trgm_ops);

------------------------------------------------------------
-- 2. Emails  (1‑to‑many)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS email (
    id         SERIAL PRIMARY KEY,
    person_id  INT REFERENCES person(id) ON DELETE CASCADE,
    address    TEXT UNIQUE NOT NULL,
    confidence NUMERIC DEFAULT 1.0            -- heuristics/probability
);

------------------------------------------------------------
-- 3. Organizations (company / university / NPO)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS organization (
    id      SERIAL PRIMARY KEY,
    name    TEXT UNIQUE NOT NULL,
    org_type TEXT,                            -- 'company' | 'university' …
    country  TEXT
);

------------------------------------------------------------
-- 4. Affiliations  (many‑to‑many person↔org)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS affiliation (
    person_id INT REFERENCES person(id) ON DELETE CASCADE,
    org_id    INT REFERENCES organization(id) ON DELETE CASCADE,
    role      TEXT,                           -- 'Professor', 'Alumnus', …
    PRIMARY KEY(person_id, org_id, role)
);

------------------------------------------------------------
-- 5. Source URLs  (traceability / RAG provenance)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS source (
    id         SERIAL PRIMARY KEY,
    person_id  INT REFERENCES person(id) ON DELETE CASCADE,
    url        TEXT,
    snippet    TEXT,      -- first 300‑500 chars of cleaned page
    source_rank SMALLINT, -- order of appearance
    fetched_at TIMESTAMPTZ
);

------------------------------------------------------------
-- 6. Person‑to‑Person edges (co‑author, co‑worker, etc.)
------------------------------------------------------------
CREATE TABLE IF NOT EXISTS edge (
    from_id  INT REFERENCES person(id) ON DELETE CASCADE,
    to_id    INT REFERENCES person(id) ON DELETE CASCADE,
    rel_type TEXT,                            -- 'coauthor' | 'colleague'
    weight   NUMERIC DEFAULT 1,
    PRIMARY KEY(from_id, to_id, rel_type)
);
