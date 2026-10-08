"""Reglas de desbloqueo y cálculo de progreso."""
from sqlalchemy.orm import Session

from .content import load_missions
from .models import MissionOverride, SectionProgress, User


def progress_map(db: Session, user: User) -> dict[str, SectionProgress]:
    rows = db.query(SectionProgress).filter(SectionProgress.user_id == user.id).all()
    return {r.section_id: r for r in rows}


def overrides(db: Session, user: User) -> set[str]:
    return {o.mission_id for o in db.query(MissionOverride).filter(MissionOverride.user_id == user.id)}


def mission_completed(mission: dict, pmap: dict) -> bool:
    return all(pmap.get(s["id"]) is not None and pmap[s["id"]].passed for s in mission["sections"])


def unlock_state(db: Session, user: User) -> dict:
    """Devuelve {mission_id: {...}, section_id: {...}} con estados de bloqueo y progreso."""
    pmap = progress_map(db, user)
    ov = overrides(db, user)
    missions = load_missions()
    state = {"missions": {}, "sections": {}}
    prev_done = True
    for m in missions:
        unlocked = user.role == "teacher" or prev_done or m["id"] in ov
        done = mission_completed(m, pmap)
        passed_count = sum(1 for s in m["sections"] if pmap.get(s["id"]) and pmap[s["id"]].passed)
        state["missions"][m["id"]] = {
            "unlocked": unlocked,
            "completed": done,
            "passed_sections": passed_count,
            "total_sections": len(m["sections"]),
        }
        prev_section_ok = True
        for s in m["sections"]:
            p = pmap.get(s["id"])
            s_unlocked = unlocked and (prev_section_ok or user.role == "teacher")
            state["sections"][s["id"]] = {
                "unlocked": s_unlocked,
                "passed": bool(p and p.passed),
                "best_score": p.best_score if p else 0.0,
                "attempts": p.attempts if p else 0,
            }
            prev_section_ok = bool(p and p.passed)
        prev_done = done
    return state
