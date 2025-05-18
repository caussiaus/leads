def run(people: dict):
    out = []
    for name, rec in people.items():
        out.append({
          "name": name,
          "emails": list(rec["emails"]),
          "score": len(rec["emails"])*10 + len(rec["urls"]),
          "summary": rec.get("summary",""),
          "sources": list(rec["urls"])
        })
    return sorted(out, key=lambda x: x["score"], reverse=True)
