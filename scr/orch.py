#!/usr/bin/env python3
import argparse
import logging
import sys
import traceback
from flask import Flask, request, jsonify
import asyncio

# -- Import actual phases (assumed async-compatible, but fallback to sync)
from scr.phases.p1_initial import run_phase1
from scr.phases.p2_tangential import run_phase2
from scr.phases.p3_summarizer import run_phase3
from scr.phases.p4_sorter import run_phase4

# Optional DB integration
# from db.db_ops import insert_leads

# ----------------------------------------------------
# CONFIGURE LOGGING
# ----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------
# Flask App Init
# ----------------------------------------------------
app = Flask(__name__)

# ----------------------------------------------------
# Core Orchestration Logic
# ----------------------------------------------------

async def run_pipeline(query: str):
    logger.info(f"🚀 Starting async pipeline for query: {query}")
    try:
        p1 = await run_phase1(query)
        p2 = await run_phase2(p1)
        p3 = await run_phase3(p2)
        p4 = run_phase4(p3)
        return p4
    except Exception as e:
        logger.exception("❌ Pipeline failed")
        return {"error": str(e)}

    logger.info(f"🚀 Starting pipeline for query: {query}")
    try:
        # Phase 1
        logger.info("🔍 Phase 1: Initial Search & NER")
        phase1_results = run_phase1(query)

        # Phase 2
        logger.info("📧 Phase 2: Tangential Searches & Email Extraction")
        phase2_results = run_phase2(phase1_results)

        # Phase 3
        logger.info("📝 Phase 3: Summarizer")
        phase3_results = run_phase3(phase2_results)

        # Phase 4
        logger.info("📊 Phase 4: Sorter & DB Insertion")
        final_results = run_phase4(phase3_results)

        logger.info("✅ Pipeline completed successfully")
        return final_results

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        traceback.print_exc()
        return {"error": str(e)}

# ----------------------------------------------------
# Flask API Route
# ----------------------------------------------------
@app.route('/run', methods=['POST'])
def run_api():
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    logger.info(f"📥 API triggered for query: {query}")
    results = asyncio.run(run_pipeline(query))
    return jsonify({'results': results})


# ----------------------------------------------------
# CLI Entrypoint
# ----------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Run the leads scraping pipeline.")
    parser.add_argument('query', type=str, nargs='?', help='Search query (e.g. "AI researchers Canada")')
    parser.add_argument('--api', action='store_true', help='Run Flask API server')
    args = parser.parse_args()

    if args.api:
        logger.info("🌐 Starting Flask API server...")
        app.run(debug=True)
    elif args.query:
        results = asyncio.run(run_pipeline(args.query))
        print("\n[🔎 FINAL OUTPUT]")
        print(results)
    else:
        print("❗ Please provide a query or use --api to start the server.")
        sys.exit(1)

# ----------------------------------------------------
# Main Entrypoint
# ----------------------------------------------------
if __name__ == '__main__':
    main()
