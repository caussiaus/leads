# stub: call your Mistral-7B summarizer here
def mistral_summarize(snippets: list, context: str) -> str:
    # For now, return the first snippet or a placeholder
    return snippets[0] if snippets else "No summary available."

async def run_phase3(people: dict, context: str = ""):
    for rec in people.values():
        rec["summary"] = mistral_summarize(rec["snips"], context)
    return people