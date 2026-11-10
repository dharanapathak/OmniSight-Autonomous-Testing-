from urllib.parse import urlparse

ALLOWED_ACTIONS = {"navigate", "click", "fill", "select", "wait", "extract", "screenshot"}

def validate_action(action: dict) -> None:
    kind = action.get("action")
    if kind not in ALLOWED_ACTIONS:
        raise ValueError(f"Unsupported action: {kind!r}")
    if kind == "navigate":
        url = action.get("url", "")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Navigation requires a valid http:// or https:// URL.")
    if kind in {"click", "fill", "select"} and not action.get("target"):
        raise ValueError(f"{kind} requires a target.")
    if kind == "fill" and "value" not in action:
        raise ValueError("fill requires a value.")
    if kind == "select" and "value" not in action:
        raise ValueError("select requires a value.")
    if kind == "wait":
        seconds = float(action.get("seconds", 1))
        if not 0 <= seconds <= 10:
            raise ValueError("wait must be between 0 and 10 seconds.")
