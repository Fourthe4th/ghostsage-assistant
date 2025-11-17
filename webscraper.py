import requests
from bs4 import BeautifulSoup


def fetch_url(url: str, max_chars: int = 4000) -> str:
    """
    Fetch the given URL and return cleaned text content.
    - Limits output length with max_chars.
    - Strips script/style/noscript tags.
    """

    try:
        resp = requests.get(
            url,
            headers={
                "User-Agent": "GhostSageBot/1.0 (+https://localhost)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            timeout=10,
        )
        resp.raise_for_status()
    except Exception as e:
        return f"Error fetching URL {url}: {e}"

    content_type = resp.headers.get("content-type", "")
    text = resp.text

    # If not HTML, just return first chunk of raw text
    if "text/html" not in content_type.lower():
        return text[:max_chars]

    soup = BeautifulSoup(text, "html.parser")

    # Remove non-content tags
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Try to grab title
    title = soup.title.string.strip() if soup.title and soup.title.string else url

    # Get visible text
    lines = soup.get_text(separator="\n").splitlines()
    cleaned_lines = [ln.strip() for ln in lines if ln.strip()]
    body_text = "\n".join(cleaned_lines)

    if not body_text:
        return f"No readable text found at {url}."

    if len(body_text) > max_chars:
        body_text = body_text[:max_chars]

    return f"Title: {title}\n\n{body_text}"
