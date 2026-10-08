"""Corrección automática de las evaluaciones de cada sección."""
import re
import unicodedata

from .feedback import explain_error
from .sandbox.runner import run_code


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    text = text.strip().lower().replace("'", '"')
    return re.sub(r"\s+", "", text)


def grade_quiz(item: dict, answer) -> dict:
    points = item.get("points", 1)
    correct = answer is not None and str(answer) == str(item["answer"])
    fb = {"id": item["id"], "type": "quiz", "points": points, "earned": points if correct else 0, "correct": correct}
    if correct:
        fb["message"] = "✅ Correcto. " + item.get("explanation", "")
    elif answer in (None, ""):
        fb["message"] = "Sin responder."
    else:
        chosen = next((o for o in item["options"] if str(o["id"]) == str(answer)), None)
        fb["message"] = "❌ " + ((chosen or {}).get("feedback") or "No es correcta. Vuelve a leer la teoría de esta sección.")
    return fb


def grade_fill_blank(item: dict, answer) -> dict:
    blanks = item.get("blanks", [])
    answers = answer if isinstance(answer, list) else []
    per_blank, details = (item.get("points", 1) / max(len(blanks), 1)), []
    earned = 0.0
    for i, blank in enumerate(blanks):
        given = answers[i] if i < len(answers) else ""
        ok = any(_norm(given) == _norm(acc) for acc in blank.get("accept", []))
        if not ok and blank.get("accept_regex"):
            ok = re.fullmatch(blank["accept_regex"], str(given).strip(), flags=re.IGNORECASE) is not None
        if ok:
            earned += per_blank
            details.append({"ok": True, "message": "✅"})
        else:
            details.append({"ok": False, "message": "❌ " + (blank.get("hint") or "Revisa este hueco.")})
    earned = round(earned, 2)
    return {
        "id": item["id"], "type": "fill_blank", "points": item.get("points", 1), "earned": earned,
        "correct": earned >= item.get("points", 1) - 1e-9, "blanks": details,
        "message": "✅ Todo correcto. " + item.get("explanation", "") if earned >= item.get("points", 1) - 1e-9
        else "Algunos huecos no son correctos.",
    }


def grade_code(item: dict, code) -> dict:
    points = item.get("points", 3)
    code = code if isinstance(code, str) else ""
    fb = {"id": item["id"], "type": "code", "points": points, "earned": 0, "correct": False, "tests": [], "messages": []}
    if not code.strip() or code.strip() == (item.get("starter") or "").strip():
        fb["messages"].append("Todavía no has escrito tu solución.")
        return fb

    for rule in item.get("forbidden", []):
        if re.search(rule["pattern"], code):
            fb["messages"].append("🚫 " + rule["message"])
            return fb

    result = run_code(code, item.get("tests", []), item.get("setup"))
    hints = item.get("hints", {})
    if result.get("error"):
        fb["messages"].append(explain_error(result["error"], hints))
        return fb

    tests = result.get("tests", [])
    passed = 0
    for t in tests:
        row = {"desc": t["desc"], "passed": t["passed"]}
        if t.get("error"):
            row["message"] = explain_error(t["error"], hints)
        elif not t["passed"] and "got" in t:
            row["message"] = f"Tu código devuelve {t['got']} y se esperaba {t['expected']}."
        if t["passed"]:
            passed += 1
        fb["tests"].append(row)
    ratio = passed / len(tests) if tests else 1.0

    missing = [r for r in item.get("required", []) if not re.search(r["pattern"], code)]
    for r in missing:
        fb["messages"].append("⚠️ " + r["message"])
    if missing:
        ratio *= 0.5

    if ratio < 1 and hints.get("wrong_result") and passed < len(tests):
        fb["messages"].append("💡 " + hints["wrong_result"])
    if result.get("stdout"):
        fb["stdout"] = result["stdout"][-1500:]

    fb["earned"] = round(points * ratio, 2)
    fb["correct"] = ratio >= 1 - 1e-9
    if fb["correct"]:
        fb["messages"].insert(0, "✅ Todas las pruebas superadas. " + item.get("explanation", ""))
    return fb


GRADERS = {"quiz": grade_quiz, "fill_blank": grade_fill_blank, "code": grade_code}


def grade_section(section: dict, answers: dict) -> dict:
    items_fb, earned, total = [], 0.0, 0.0
    for item in section["evaluation"]["items"]:
        fb = GRADERS[item["type"]](item, answers.get(item["id"]))
        items_fb.append(fb)
        earned += fb["earned"]
        total += fb["points"]
    return {"score": round(earned / total, 4) if total else 0.0, "earned": round(earned, 2), "total": total, "items": items_fb}
