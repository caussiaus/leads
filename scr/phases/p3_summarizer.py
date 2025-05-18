# stub: call your Mistral-7B summarizer here
def run(people: dict, context: str):
    for rec in people.values():
        rec["summary"] = mistral_summarize(rec["snips"], context)
    return people
