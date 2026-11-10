import base64
import os
from openai import OpenAI

def inspect_screenshot(image_path: str, question: str = "Describe the visible interactive elements.") -> str:
    """Optional multimodal screenshot interpretation using an OpenAI vision model."""
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return "Vision analysis is disabled. Add OPENAI_API_KEY to .env to enable it."
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    client = OpenAI(api_key=key)
    result = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role":"user","content":[
            {"type":"text","text":question},
            {"type":"image_url","image_url":{"url":f"data:image/png;base64,{encoded}"}}
        ]}],
        max_tokens=350,
    )
    return result.choices[0].message.content or "No visual description returned."
