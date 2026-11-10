from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

def _attempt(locator, timeout_ms):
    locator.first.wait_for(state="visible", timeout=timeout_ms)
    return locator.first

def resolve_locator(page, target: str, timeout_ms: int = 2500):
    """Try semantic and normalized locator strategies; return (locator, strategy)."""
    target = target.strip()
    cleaned = target
    for suffix in (" text field", " input field", " field", " dropdown", " textbox", " input"):
        cleaned = cleaned.replace(suffix, "")
    cleaned = cleaned.strip()
    candidates = [
        ("role-button", lambda: page.get_by_role("button", name=cleaned, exact=False)),
        ("role-link", lambda: page.get_by_role("link", name=cleaned, exact=False)),
        ("label", lambda: page.get_by_label(cleaned, exact=False)),
        ("placeholder", lambda: page.get_by_placeholder(cleaned, exact=False)),
        ("text", lambda: page.get_by_text(cleaned, exact=False)),
        ("test-id", lambda: page.get_by_test_id(cleaned)),
        ("name-attribute", lambda: page.locator(f'[name="{cleaned}"]')),
        ("id-attribute", lambda: page.locator(f'#{cleaned}')),
    ]
    errors = []
    for strategy, factory in candidates:
        try:
            return _attempt(factory(), timeout_ms), strategy
        except Exception as exc:
            errors.append(f"{strategy}: {str(exc).splitlines()[0][:160]}")
    raise LookupError(f"Could not locate '{target}'. Tried: " + " | ".join(errors))
