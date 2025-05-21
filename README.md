# LeadsProject

A fully modular, end-to-end pipeline for scraping, enriching, summarizing, and storing "lead" profiles (people) into a PostgreSQL + pgvector database, designed to run locally with an NVIDIA RTX 4090 and a dedicated NVMe drive.

---

## 📂 Directory Structure

```
~/leads
├── Dockerfile                    # Container definition for the orchestrator
├── docker-compose.yml            # Compose file for PostgreSQL + (optionally) the app
├── envs
│   └── scraper_env.yml           # Conda environment spec for scraper dependencies
├── models                        # All task-specific model folders (via manifest)
│   ├── manifest.json             # JSON listing all models to download
│   ├── ner_model/                # NER model (Davlan/bert…)
│   ├── summarizer_model/         # Summarization model (e.g. OpenHermes 7B)
│   ├── bio_generator_model/      # Bio/expertise generation model (e.g. Llama2-chat)
│   ├── quality_scorer/           # Writing quality classifier (DeBERTa)
│   └── embedder_model/           # Embeddings (E5-large-v2)
├── db
│   ├── init.sql                  # DDL: create tables & extensions
│   ├── seed.sql                  # Optional starter data
│   ├── cfg.py                    # SQLAlchemy connection config
│   └── models.py                 # SQLAlchemy ORM definitions
├── scr                           # Scraper code & orchestrator
│   ├── orch.py                   # Flask API / orchestrator entrypoint
│   ├── config.py                 # API keys & defaults (dotenv)
│   ├── phases                    # Four sequential pipeline modules
│   │   ├── p1_initial.py         # Phase 1: Google CSE + NER extraction
│   │   ├── p2_tangential.py      # Phase 2: drill‐down search & email extraction
│   │   ├── p3_summarizer.py      # Phase 3: summarization (Mistral‐7B or stub)
│   │   └── p4_sorter.py          # Phase 4: normalize fields & call DB insert
│   └── utils                     # Shared utilities
│       ├── ner.py                # NER extraction pipeline
│       ├── email_extractor.py    # Regex & obfuscated email parsing
│       ├── fetcher.py            # Async HTTP + Playwright fetchers
│       ├── google_cse.py         # Google Custom Search JSON API wrapper
│       ├── html_parser.py        # BeautifulSoup-based HTML→text
│       └── download_models.py    # Manifest-driven model downloader
└── README.md                     # This documentation
```

---

## 🔄 Architecture Overview

1. **Orchestration (`scr/orch.py`)**

   * Provides a Flask endpoint (`POST /run`) or CLI entrypoint
   * Invokes four phases sequentially (async where appropriate)
   * After Phase 4, pushes data into PostgreSQL via SQLAlchemy helpers

2. **Phase 1: Initial Search & NER**

   * Query Google Custom Search (CX JSON API) for `industry + location` or free-text prompts
   * Fetch each landing page concurrently
   * Run Hugging Face `Davlan/bert-base-multilingual-cased-ner-hrl` for PERSON & ORG entities
   * Collect names, contexts, and URLs for drill-down

3. **Phase 2: Tangential Searches & Email Extraction**

   * For each candidate name: query Google CSE for `"Name" email` and `"Name" profile`
   * If the URL domain requires JS (LinkedIn, RocketReach), use Playwright; else use aiohttp
   * Parse page text → extract emails (raw + obfuscated) and context snippets

4. **Phase 3: Summarizer**

   * Summarize cleaned HTML/text using Mistral-7B (`models/summarizer_model`) via 4-bit quantization
   * Generate a concise summary relevant to the original prompt
   * (During testing, you can stub this step to use the first snippet)

5. **Phase 4: Sorter & DB Insertion**

   * Normalize each profile into standard fields: `name`, `summary`, `bio`, `emails`, `affiliations`, `sources`, `quality` score, `embedding`
   * Compute embeddings via E5-large-v2 for vector similarity searches
   * Score quality using writing-quality classifier (DeBERTa) or heuristic formula
   * Call `db/db_ops.insert_lead()` to insert into PostgreSQL tables

6. **Database (PostgreSQL + pgvector)**

   * Data directory: `/data/ldb/pgdata` (bind-mounted to `/data/bookproject/ldb/pgdata` on the Kingston NVMe)
   * Tables:

     * `person` (int PK, full\_name, first/last, title, location, bio, summary, quality\_score, embedding)
     * `email` (int PK, person\_id FK, address, confidence, is\_primary)
     * `organization` (int PK, name, org\_type, country)
     * `affiliation` (person\_id, org\_id, role)
     * `source` (person\_id, url, snippet, source\_rank, fetched\_at)
     * `edge` (from\_id, to\_id, rel\_type, weight)
   * Extensions: `vector` (pgvector), `pg_trgm` (fuzzy search)

---

## ⚙️ Getting Started

1. **Clone & scaffold**

   ```bash
   cd ~
   git clone <your-repo-url> leads
   cd leads
   ./scr/utils/download_models.py   # download all models via manifest.json
   ```

2. **Create Conda env**

   ```bash
   conda env create -f envs/scraper_env.yml
   conda activate scraper
   ```

3. **Start the database**

   ```bash
   # ensure /data/bookproject/ldb/pgdata is bind-mounted to /data/ldb
   docker compose up -d db
   docker logs -f leads_postgres
   # confirm tables created
   psql -h localhost -U leads_user -d leadsdb -c '\dt'
   ```

4. **Run the pipeline**

   ```bash
   # CLI mode
   python scr/orch.py "quantitative researchers Canada"

   # or Flask API mode
   flask run --app scr/app.py
   curl -X POST http://127.0.0.1:5000/run -H 'Content-Type: application/json' \
        -d '{"query":"AI ethics researchers"}'
   ```

5. **Verify results**

   ```sql
   SELECT full_name, summary, quality_score FROM person ORDER BY created_at DESC LIMIT 5;
   SELECT p.full_name, e.address FROM person p JOIN email e ON p.id=e.person_id;
   ```

---

## 🔧 Tips & Next Steps

* **Stub summarizer** during dev: have Phase 3 return snippets to avoid VRAM issues.
* **Swap models** by editing `models/manifest.json` and rerunning `download_models.py`.
* **Scale**: containerize the `app` by providing a Dockerfile and uncommenting the `app:` service in `docker-compose.yml`.
* **Backups**: snapshot `/data/ldb/pgdata` regularly; your code sits on WD\_BLACK.
* **UI**: build a front-end or integrate into your book-editor agent under `ui/app.py`.

---

Casey Jussaume
