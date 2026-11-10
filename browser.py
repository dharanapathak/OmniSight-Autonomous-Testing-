import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from .self_healing import resolve_locator
from .safety import validate_action

class BrowserSession:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.timeout = int(os.getenv("BROWSER_TIMEOUT_MS", "12000"))
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)

    def start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=os.getenv("HEADLESS", "false").lower() == "true")
        self.page = self.browser.new_page(viewport={"width": 1365, "height": 900})
        self.page.set_default_timeout(self.timeout)
        return self

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def page_context(self):
        if not self.page:
            return ""
        try:
            return self.page.locator("body").inner_text(timeout=2500)[:9000]
        except Exception:
            return ""

    def take_screenshot(self):
        path = self.screenshot_dir / "latest.png"
        self.page.screenshot(path=str(path), full_page=True)
        return str(path)

    def execute(self, action: dict):
        validate_action(action)
        kind = action["action"]
        if kind == "navigate":
            self.page.goto(action["url"], wait_until="domcontentloaded")
            return f"Opened {action['url']}"
        if kind in {"click", "fill", "select"}:
            locator, strategy = resolve_locator(self.page, action["target"])
            if kind == "click":
                locator.click()
                return f"Clicked '{action['target']}' using {strategy}"
            if kind == "fill":
                locator.fill(str(action["value"]))
                return f"Filled '{action['target']}' using {strategy}"
            locator.select_option(label=str(action["value"]))
            return f"Selected '{action['value']}' in '{action['target']}' using {strategy}"
        if kind == "wait":
            self.page.wait_for_timeout(int(float(action.get("seconds", 1)) * 1000))
            return f"Waited {action.get('seconds', 1)} second(s)"
        if kind == "extract":
            target = action.get("target", "main")
            try:
                text = self.page.locator(target).inner_text(timeout=3000)
            except Exception:
                text = self.page.locator("body").inner_text(timeout=3000)
            return text[:6000]
        if kind == "screenshot":
            return f"Screenshot saved: {self.take_screenshot()}"
        raise ValueError(f"Unsupported action: {kind}")
