import csv
import io
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import hash_password, teacher_required
from ..content import get_section, load_missions
from ..db import get_db
from ..models import MissionOverride, SectionProgress, Submission, TeacherGrade, User
from ..progress import unlock_state

router = APIRouter(prefix="/api/teacher", tags=["profesor"], dependencies=[Depends(teacher_required)])


class SectionRef(BaseModel):
    section_id: str


class MissionRef(BaseModel):
    mission_id: str


class GradeIn(BaseModel):
    mission_id: str
    grade: float | None = Field(default=None, ge=0, le=10)
    notes: str = ""


class PasswordIn(BaseModel):
    password: str = Field(min_length=6)


def _student(db: Session, student_id: int) -> User:
    u = db.get(User, student_id)
    if not u or u.role != "student":
        raise HTTPException(404, "Alumno no encontrado")
    return u


def _student_row(db: Session, u: User, missions: list[dict], flags_by_user: dict) -> dict:
    state = unlock_state(db, u)
    pmap = {p.section_id: p for p in u.progress}
    per_mission = []
    total_sections = passed_sections = 0
    score_sum = 0.0
    for m in missions:
        ms = state["missions"][m["id"]]
        scores = [pmap[s["id"]].best_score for s in m["sections"] if s["id"] in pmap]
        per_mission.append({
            "mission_id": m["id"], "passed": ms["passed_sections"], "total": ms["total_sections"],
            "completed": ms["completed"], "unlocked": ms["unlocked"],
            "avg_score": round(sum(scores) / len(m["sections"]), 3) if scores else 0.0,
        })
        total_sections += ms["total_sections"]
        passed_sections += ms["passed_sections"]
        score_sum += sum(scores)
    last = max((p.last_attempt_at for p in u.progress if p.last_attempt_at), default=None)
    return {
        "id": u.id, "username": u.username, "full_name": u.full_name, "group_name": u.group_name, "board": u.board,
        "missions": per_mission, "passed_sections": passed_sections, "total_sections": total_sections,
        "avg_score": round(score_sum / total_sections, 3) if total_sections else 0.0,
        "attempts": sum(p.attempts for p in u.progress), "flags": flags_by_user.get(u.id, 0),
        "last_activity": last.isoformat() if last else None,
    }


@router.get("/info")
def info():
    from .. import config
    return {"class_code": config.CLASS_CODE, "course_start": config.COURSE_START_DATE.isoformat(),
            "min_seconds": config.MIN_SECONDS_BEFORE_SUBMIT, "free_attempts": config.FREE_ATTEMPTS,
            "plagiarism_threshold": config.PLAGIARISM_THRESHOLD}


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    missions = load_missions()
    students = db.query(User).filter(User.role == "student").order_by(User.group_name, User.full_name).all()
    flags = defaultdict(int)
    for sub in db.query(Submission).filter(Submission.flagged.is_(True)):
        flags[sub.user_id] += 1
    rows = [_student_row(db, u, missions, flags) for u in students]
    mission_stats = []
    for i, m in enumerate(missions):
        done = sum(1 for r in rows if r["missions"][i]["completed"])
        mission_stats.append({"mission_id": m["id"], "number": m["number"], "title": m["title"],
                              "icon": m.get("icon", ""), "completed": done, "students": len(rows)})
    return {
        "students": rows,
        "missions": mission_stats,
        "totals": {
            "students": len(rows),
            "avg_progress": round(sum(r["passed_sections"] / r["total_sections"] for r in rows) / len(rows), 3) if rows else 0,
            "flags": sum(flags.values()),
            "submissions": db.query(Submission).count(),
        },
    }


@router.get("/students/{student_id}")
def student_detail(student_id: int, db: Session = Depends(get_db)):
    u = _student(db, student_id)
    state = unlock_state(db, u)
    pmap = {p.section_id: p for p in u.progress}
    grades = {g.mission_id: g for g in db.query(TeacherGrade).filter_by(user_id=u.id)}
    missions = []
    for m in load_missions():
        secs = []
        for s in m["sections"]:
            p = pmap.get(s["id"])
            secs.append({
                "id": s["id"], "title": s["title"], **state["sections"][s["id"]],
                "started_at": p.started_at.isoformat() if p and p.started_at else None,
                "passed_at": p.passed_at.isoformat() if p and p.passed_at else None,
                "failed_streak": p.failed_streak if p else 0,
            })
        g = grades.get(m["id"])
        missions.append({"id": m["id"], "number": m["number"], "title": m["title"], "icon": m.get("icon", ""),
                         **state["missions"][m["id"]], "sections": secs,
                         "grade": g.grade if g else None, "notes": g.notes if g else ""})
    subs = (db.query(Submission).filter_by(user_id=u.id).order_by(Submission.created_at.desc()).limit(200).all())
    return {
        "student": {"id": u.id, "username": u.username, "full_name": u.full_name, "group_name": u.group_name,
                    "board": u.board},
        "missions": missions,
        "submissions": [{
            "id": s.id, "section_id": s.section_id, "score": s.score, "passed": s.passed,
            "elapsed_seconds": s.elapsed_seconds, "flagged": s.flagged, "flag_reason": s.flag_reason,
            "created_at": s.created_at.isoformat(), "answers": s.answers, "feedback": s.feedback,
        } for s in subs],
    }


@router.get("/flags")
def flags(db: Session = Depends(get_db)):
    subs = db.query(Submission).filter(Submission.flagged.is_(True)).order_by(Submission.created_at.desc()).all()
    return [{"id": s.id, "student_id": s.user_id, "student": s.user.full_name, "username": s.user.username,
             "section_id": s.section_id, "score": s.score, "reason": s.flag_reason,
             "elapsed_seconds": s.elapsed_seconds, "created_at": s.created_at.isoformat()} for s in subs]


@router.post("/flags/{submission_id}/dismiss")
def dismiss_flag(submission_id: int, db: Session = Depends(get_db)):
    s = db.get(Submission, submission_id)
    if not s:
        raise HTTPException(404, "Entrega no encontrada")
    s.flagged = False
    s.flag_reason = (s.flag_reason + "\n[Revisado por el profesor]").strip()
    db.commit()
    return {"ok": True}


@router.post("/students/{student_id}/reset-attempts")
def reset_attempts(student_id: int, data: SectionRef, db: Session = Depends(get_db)):
    _student(db, student_id)
    p = db.query(SectionProgress).filter_by(user_id=student_id, section_id=data.section_id).first()
    if p:
        p.failed_streak = 0
        p.last_attempt_at = None
        db.commit()
    return {"ok": True}


@router.post("/students/{student_id}/unlock")
def unlock(student_id: int, data: MissionRef, db: Session = Depends(get_db)):
    _student(db, student_id)
    if not db.query(MissionOverride).filter_by(user_id=student_id, mission_id=data.mission_id).first():
        db.add(MissionOverride(user_id=student_id, mission_id=data.mission_id))
        db.commit()
    return {"ok": True}


@router.post("/unlock-all")
def unlock_all(data: MissionRef, db: Session = Depends(get_db)):
    """Desbloquea una misión para toda la clase (p. ej., al empezar su semana en el calendario)."""
    n = 0
    for u in db.query(User).filter(User.role == "student"):
        if not db.query(MissionOverride).filter_by(user_id=u.id, mission_id=data.mission_id).first():
            db.add(MissionOverride(user_id=u.id, mission_id=data.mission_id))
            n += 1
    db.commit()
    return {"ok": True, "unlocked": n}


@router.put("/students/{student_id}/grade")
def set_grade(student_id: int, data: GradeIn, db: Session = Depends(get_db)):
    _student(db, student_id)
    g = db.query(TeacherGrade).filter_by(user_id=student_id, mission_id=data.mission_id).first()
    if not g:
        g = TeacherGrade(user_id=student_id, mission_id=data.mission_id)
        db.add(g)
    g.grade, g.notes = data.grade, data.notes
    db.commit()
    return {"ok": True}


@router.post("/students/{student_id}/password")
def set_password(student_id: int, data: PasswordIn, db: Session = Depends(get_db)):
    u = _student(db, student_id)
    u.password_hash = hash_password(data.password)
    db.commit()
    return {"ok": True}


@router.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    u = _student(db, student_id)
    db.query(Submission).filter_by(user_id=u.id).delete()
    db.query(MissionOverride).filter_by(user_id=u.id).delete()
    db.query(TeacherGrade).filter_by(user_id=u.id).delete()
    db.delete(u)
    db.commit()
    return {"ok": True}


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    """Dificultad por sección e ítem (último intento de cada alumno)."""
    latest: dict[tuple, Submission] = {}
    for s in db.query(Submission).order_by(Submission.created_at):
        latest[(s.user_id, s.section_id)] = s
    attempts = defaultdict(list)
    for p in db.query(SectionProgress):
        attempts[p.section_id].append(p)
    out = []
    for m in load_missions():
        for sec in m["sections"]:
            subs = [v for (uid, sid), v in latest.items() if sid == sec["id"]]
            items = []
            for item in sec["evaluation"]["items"]:
                vals = []
                for sub in subs:
                    fb = next((i for i in sub.feedback.get("items", []) if i["id"] == item["id"]), None)
                    if fb:
                        vals.append(fb["earned"] / fb["points"] if fb["points"] else 0)
                items.append({"id": item["id"], "type": item["type"],
                              "label": (item.get("question") or item.get("prompt") or item.get("text") or "")[:90],
                              "avg": round(sum(vals) / len(vals), 3) if vals else None, "n": len(vals)})
            ps = attempts.get(sec["id"], [])
            out.append({
                "mission_id": m["id"], "section_id": sec["id"], "title": sec["title"],
                "students_started": len(ps), "students_passed": sum(1 for p in ps if p.passed),
                "avg_attempts": round(sum(p.attempts for p in ps) / len(ps), 2) if ps else 0,
                "avg_best": round(sum(p.best_score for p in ps) / len(ps), 3) if ps else 0, "items": items,
            })
    return out


@router.get("/sections/{section_id}/solutions")
def solutions(section_id: str):
    mission, section = get_section(section_id)
    if not section:
        raise HTTPException(404, "Sección no encontrada")
    return {"mission_id": mission["id"], "section": section}


@router.get("/export.csv")
def export_csv(db: Session = Depends(get_db)):
    missions = load_missions()
    grades = {(g.user_id, g.mission_id): g for g in db.query(TeacherGrade)}
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    header = ["usuario", "nombre", "grupo", "placa"]
    for m in missions:
        header += [f"M{m['number']} secciones", f"M{m['number']} nota auto (0-10)", f"M{m['number']} nota profesor"]
    header += ["media auto (0-10)", "intentos", "alertas"]
    w.writerow(header)
    flags = defaultdict(int)
    for sub in db.query(Submission).filter(Submission.flagged.is_(True)):
        flags[sub.user_id] += 1
    for u in db.query(User).filter(User.role == "student").order_by(User.group_name, User.full_name):
        row = _student_row(db, u, missions, flags)
        line = [u.username, u.full_name, u.group_name, u.board]
        for pm, m in zip(row["missions"], missions):
            g = grades.get((u.id, m["id"]))
            line += [f"{pm['passed']}/{pm['total']}", f"{pm['avg_score'] * 10:.1f}".replace(".", ","),
                     "" if not g or g.grade is None else f"{g.grade:.1f}".replace(".", ",")]
        line += [f"{row['avg_score'] * 10:.1f}".replace(".", ","), row["attempts"], row["flags"]]
        w.writerow(line)
    data = "﻿" + buf.getvalue()  # BOM para que Excel abra bien las tildes
    return StreamingResponse(iter([data]), media_type="text/csv; charset=utf-8",
                             headers={"Content-Disposition": "attachment; filename=notas_neumalab.csv"})
