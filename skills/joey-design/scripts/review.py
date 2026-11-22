"""Exercise a local HTML deliverable in two fresh, offline Chromium contexts."""
import json
import tempfile
from pathlib import Path

VIEWPORTS = {"desktop": (1280, 800), "phone": (390, 844)}
ACTIONS = {"click", "press", "reload", "visible", "disabled", "text"}
PAGE_CHECK = """() => ({
  overflow: document.documentElement.scrollWidth > innerWidth + 1,
  images: [...document.images].filter(i => i.getClientRects().length && i.complete && !i.naturalWidth)
    .map(i => (i.alt || i.getAttribute('src') || 'image').slice(0, 90)),
  unnamed: [...document.querySelectorAll('button, a[href], [role="button"]')].filter(e => {
    if (!e.getClientRects().length) return false;
    const ids = (e.getAttribute('aria-labelledby') || '').trim().split(/\\s+/);
    const labels = ids.map(id => document.getElementById(id)?.textContent || '').join('');
    const named = [labels, e.innerText, e.getAttribute('aria-label'), e.title,
      ...[...e.querySelectorAll('img')].map(i => i.alt)].some(s => s && s.trim());
    return !named;
  }).map(e => e.tagName.toLowerCase())
})"""


def read_steps(path):
    if path is None:
        return []
    steps = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(steps, list):
        raise ValueError("A journey must be a JSON array")
    for index, step in enumerate(steps, 1):
        if not isinstance(step, dict) or step.get("action") not in ACTIONS:
            raise ValueError(f"Unknown action at step {index}")
        action = step["action"]
        keys = {"action"}
        if action != "reload":
            keys.add("selector")
        if action in ("press", "text"):
            keys.add("value")
        if set(step) != keys or any(not isinstance(step[k], str) or not step[k].strip() for k in keys):
            raise ValueError(f"Step {index} requires {', '.join(sorted(keys))}")
    return steps


def exercise(page, step, expect):
    action = step["action"]
    if action == "reload":
        page.reload(wait_until="load")
        return
    element = page.locator(step["selector"])
    if action == "click":
        element.click()
    elif action == "press":
        element.press(step["value"])
    elif action == "visible":
        expect(element).to_be_visible(timeout=3000)
    elif action == "disabled":
        expect(element).to_be_disabled(timeout=3000)
    else:
        expect(element).to_be_visible(timeout=3000)
        expect(element).to_contain_text(step["value"], timeout=3000)


def review_page(source, destination, journey=None):
    from playwright.sync_api import Error, expect, sync_playwright

    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_file() or source.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("Pass a local HTML file")
    steps = read_steps(journey)
    if destination.exists():
        raise ValueError("Choose a fresh review directory")
    destination.parent.mkdir(parents=True, exist_ok=True)
    results = {}
    with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
        stage = Path(temporary) / "review"
        stage.mkdir()
        with sync_playwright() as engine:
            try:
                browser = engine.chromium.launch()
            except Error as error:
                raise ValueError(f"Chromium could not start: {str(error).splitlines()[0]}. Check browser installation and launch permissions.") from error
            for name, (width, height) in VIEWPORTS.items():
                context = browser.new_context(viewport={"width": width, "height": height},
                                              has_touch=name == "phone", reduced_motion="reduce",
                                              service_workers="block", offline=True)
                page = context.new_page()
                page.set_default_timeout(3500)
                issues = []
                page.on("pageerror", lambda exc: issues.append(f"Script error: {exc}"))
                def inspect_state(label):
                    check = page.evaluate(PAGE_CHECK)
                    if check["overflow"]:
                        issues.append(f"{label}: document exceeds viewport")
                    if check["images"]:
                        issues.append(f"{label}: broken images: {check['images']}")
                    if check["unnamed"]:
                        issues.append(f"{label}: controls without a visible or accessible name: {check['unnamed']}")
                completed = 0
                try:
                    page.goto(source.as_uri(), wait_until="load")
                    inspect_state("opening")
                    page.screenshot(path=stage / f"{name}.png", animations="disabled")
                    for index, step in enumerate(steps, 1):
                        exercise(page, step, expect)
                        inspect_state(f"step {index}")
                        completed = index
                except (Error, AssertionError) as error:
                    issues.append(f"After {completed} completed steps: {str(error)[:700]}")
                if steps:
                    page.screenshot(path=stage / f"{name}-end.png", animations="disabled")
                for issue in dict.fromkeys(issues):
                    print(f"{name}: {issue}")
                results[name] = {"size": [width, height], "completed": completed, "issues": issues}
                context.close()
            browser.close()
        report = {"page": source.name, "steps": len(steps), "viewports": results}
        (stage / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        stage.rename(destination)
    return all(not item["issues"] for item in results.values())
