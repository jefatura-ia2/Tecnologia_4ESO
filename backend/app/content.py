"""Carga del temario (misiones en YAML) y vistas públicas sin soluciones."""
import copy
from datetime import timedelta
from functools import lru_cache
from pathlib import Path

import yaml

from . import config

CONTENT_DIR = Path(__file__).parent / "content" / "missions"


@lru_cache(maxsize=1)
def load_missions() -> list[dict]:
    missions = []
    for path in sorted(CONTENT_DIR.glob("*.yml")):
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        missions.append(data)
    missions.sort(key=lambda m: m["number"])
    for m in missions:
        m["passing_score"] = config.passing_score(m["number"])
        for s in m["sections"]:
            s["mission_id"] = m["id"]
            s["max_points"] = sum(item.get("points", 1) for item in s["evaluation"]["items"])
    return missions


def get_mission(mission_id: str) -> dict | None:
    return next((m for m in load_missions() if m["id"] == mission_id), None)


def get_section(section_id: str) -> tuple[dict, dict] | tuple[None, None]:
    for m in load_missions():
        for s in m["sections"]:
            if s["id"] == section_id:
                return m, s
    return None, None


_PRIVATE_ITEM_KEYS = {"answer", "accept", "accept_regex", "solution", "explanation", "hints", "tests", "required", "forbidden"}


def public_item(item: dict) -> dict:
    out = {k: v for k, v in item.items() if k not in _PRIVATE_ITEM_KEYS}
    if item["type"] == "quiz":
        out["options"] = [{"id": o["id"], "text": o["text"]} for o in item["options"]]
    if item["type"] == "fill_blank":
        out["blanks"] = [{"hint": b.get("hint", "")} for b in item.get("blanks", [])]
    if item["type"] == "code":
        out["tests"] = [t.get("desc", "Prueba") for t in item.get("tests", [])]
    return out


def public_section(section: dict) -> dict:
    s = copy.deepcopy(section)
    s["evaluation"] = {
        "intro": section["evaluation"].get("intro", ""),
        "items": [public_item(i) for i in section["evaluation"]["items"]],
    }
    return s


def mission_summary(m: dict) -> dict:
    return {
        "id": m["id"],
        "number": m["number"],
        "title": m["title"],
        "subtitle": m.get("subtitle", ""),
        "icon": m.get("icon", ""),
        "weeks": m.get("weeks", []),
        "hours": m.get("hours", 0),
        "objectives": m.get("objectives", []),
        "materials": m.get("materials", []),
        "criteria": m.get("criteria", []),
        "passing_score": m["passing_score"],
        "extra": bool(m.get("extra")),
        "trimestre": m.get("trimestre"),
        "sections": [
            {"id": s["id"], "title": s["title"], "hours": s.get("hours", 0), "kind": s.get("kind", "lesson"),
             "foto": bool(s.get("foto"))}
            for s in m["sections"]
        ],
    }


def calendar() -> list[dict]:
    """Temporalización semana a semana a partir de las misiones."""
    weeks = []
    last = max([config.WEEKS] + [s["week"] for m in load_missions() for s in m.get("schedule", [])])
    for w in range(1, last + 1):
        start = config.COURSE_START_DATE + timedelta(weeks=w - 1)
        weeks.append({
            "week": w,
            "start": start.isoformat(),
            "end": (start + timedelta(days=4)).isoformat(),
            "extra": w > config.WEEKS,
            "sessions": [],
        })
    for m in load_missions():
        for sess in m.get("schedule", []):
            w = sess["week"]
            if 1 <= w <= len(weeks):
                weeks[w - 1]["sessions"].append({
                    "mission_id": m["id"],
                    "mission_title": m["title"],
                    "icon": m.get("icon", ""),
                    "session": sess["session"],
                    "title": sess["title"],
                    "section_id": sess.get("section"),
                })
    for w in weeks:
        w["sessions"].sort(key=lambda s: s["session"])
    return weeks
