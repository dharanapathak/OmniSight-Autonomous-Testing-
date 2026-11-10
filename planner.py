import json
import os
import re
from openai import OpenAI

SYSTEM_PROMPT = """You are a browser RPA task planner. Return ONLY valid JSON:
{"goal":"short goal","actions":[...]}
Allowed action objects:
- {"action":"navigate","url":"https://..."}
- {"action":"click","target":"visible button/link text or accessible name"}
- {"action":"fill","target":"field label/placeholder/name","value":"..."}
- {"action":"select","target":"dropdown label/name","value":"..."}
- {"action":"wait","seconds":1}
- {"action":"extract","target":"main"}
- {"action":"screenshot"}
Use no more than 12 actions. Never invent a URL if one is not supplied or already present in context. If the user asks to open a page and no URL is given, use the provided start_url. Do not attempt CAPTCHA, payment, credential theft, security bypass, or destructive actions. Do not output code or extra prose."""

def _fallback_plan(task: str, start_url: str | None):
    t = task.strip()
    actions = []
    url_match = re.search(r'https?://[^\s]+', t)
    url = url_match.group(0).rstrip(".,)") if url_match else start_url
    if url and any(w in t.lower() for w in ["open", "go to", "visit", "navigate", "demo"]):
        actions.append({"action": "navigate", "url": url})
    # Parse simple natural language form tasks: "fill [target] with [value]"
    for match in re.finditer(r"(?:fill|enter|type)\s+(?:the\s+)?(.+?)\s+(?:with|as)\s+['\"]?([^,'\".]+)", t, re.I):
        actions.append({"action": "fill", "target": match.group(1).strip(), "value": match.group(2).strip()})
    for match in re.finditer(r"(?:choose|select)\s+(?:the\s+)?(.+?)\s+(?:from|dropdown)\s+(.+?)(?:,| and |$)", t, re.I):
        actions.append({"action": "select", "target": match.group(2).strip(), "value": match.group(1).strip()})
    click_match = re.search(r"(?:click|press|submit)\s+(?:the\s+)?(.+?)(?:\.|$)", t, re.I)
    if click_match:
        click_target = click_match.group(1).strip()
        if "submit" in t.lower() or "form" in click_target.lower():
            click_target = "Submit Application"
        actions.append({"action": "click", "target": click_target})
    if any(w in t.lower() for w in ["extract", "read", "get text", "result"]):
        actions.append({"action": "extract", "target": "main"})
    if not actions:
        actions = [{"action": "screenshot"}]
    return {"goal": t, "actions": actions[:12], "planner": "fallback"}

def create_plan(task: str, start_url: str | None = None, page_context: str = "") -> dict:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return _fallback_plan(task, start_url)
    client = OpenAI(api_key=key)
    prompt = f"Start URL: {start_url or 'not supplied'}\nCurrent page context:\n{page_context[:9000]}\nUser task: {task}"
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":prompt}],
        response_format={"type":"json_object"},
        temperature=0.1,
    )
    data = json.loads(response.choices[0].message.content)
    if not isinstance(data.get("actions"), list):
        raise ValueError("Planner returned an invalid action plan.")
    data["actions"] = data["actions"][:12]
    data["planner"] = "openai"
    return data
