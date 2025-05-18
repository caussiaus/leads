from flask import Flask, request, jsonify
import asyncio
from scr.config import DEFAULT_NUM_LINKS
from scr.phases.p1_initial   import run as phase1
from scr.phases.p2_tangential import run as phase2
from scr.phases.p3_summarizer import run as phase3
from scr.phases.p4_sorter     import run as phase4

app = Flask(__name__)

@app.route("/run", methods=["POST"])
def run_all():
    data  = request.get_json(force=True)
    prompt= data.get("query")
    limit = data.get("limit", DEFAULT_NUM_LINKS)
    if not prompt:
        return jsonify({"error":"no query"}),400

    async def _orchestrate():
        ppl  = await phase1(prompt, limit)
        ppl  = await phase2(ppl)
        ppl  = phase3(ppl, prompt)
        lst  = phase4(ppl)
        return lst

    result = asyncio.run(_orchestrate())
    return jsonify(result)

if __name__=="__main__":
    app.run(debug=True,port=5000)
