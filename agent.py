from .planner import create_plan
from .browser import BrowserSession
from .safety import validate_action

def run_task(task: str, start_url: str | None = None, progress=None):
    session = BrowserSession().start()
    log, extracted = [], ""
    try:
        context = session.page_context()
        plan = create_plan(task, start_url, context)
        log.append(f"Planner: {plan.get('planner', 'unknown')}")
        log.append(f"Goal: {plan.get('goal', task)}")
        for index, action in enumerate(plan["actions"], 1):
            try:
                validate_action(action)
                result = session.execute(action)
                log.append(f"Step {index}: {action['action']} — {result}")
                if action["action"] == "extract":
                    extracted = result
                if progress:
                    progress(index, len(plan["actions"]), log[-1])
            except Exception as exc:
                log.append(f"Step {index} failed: {type(exc).__name__}: {exc}")
                # One safe recovery: wait briefly and retry the same constrained action.
                if action.get("action") in {"click", "fill", "select"}:
                    try:
                        session.page.wait_for_timeout(700)
                        result = session.execute(action)
                        log.append(f"Step {index} recovered: {result}")
                    except Exception as retry_exc:
                        log.append(f"Recovery failed: {retry_exc}")
        screenshot = session.take_screenshot() if session.page else None
        if not extracted and session.page:
            extracted = session.page_context()
        return {"plan": plan, "log": log, "extracted": extracted, "screenshot": screenshot}
    finally:
        session.close()
