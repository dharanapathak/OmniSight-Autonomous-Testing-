from omnisight.planner import _fallback_plan

def test_fallback_plan_includes_start_url():
    plan = _fallback_plan("Open the demo page and take a screenshot", "http://localhost:8000")
    assert plan["actions"][0] == {"action":"navigate","url":"http://localhost:8000"}

def test_fallback_plan_parses_fill():
    plan = _fallback_plan("fill the name field with Dharana", None)
    assert any(a.get("action") == "fill" and a.get("value") == "Dharana" for a in plan["actions"])
