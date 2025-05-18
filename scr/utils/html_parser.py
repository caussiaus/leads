from bs4 import BeautifulSoup

def html_to_text(html: str) -> str:
    soup  = BeautifulSoup(html, "html.parser")
    nodes = soup.find_all(["p","li","span","div","h1","h2","h3"])
    return " ".join(n.get_text(" ",strip=True) for n in nodes)
