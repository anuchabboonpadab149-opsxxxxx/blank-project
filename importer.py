import json
import requests


def fetch_texts_from_url(url: str, fmt: str = "lines") -> list:
    """
    Fetch tweet texts from an external source.
    fmt:
      - "lines": treat response body as UTF-8 text, one post per line
      - "json": response is a JSON array of strings
    """
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    if fmt == "json":
        data = resp.json()
        if not isinstance(data, list):
            raise ValueError("JSON import must be a list of strings")
        return [str(x).strip() for x in data if str(x).strip()]
    # default: lines
    text = resp.text
    return [line.strip() for line in text.splitlines() if line.strip()]