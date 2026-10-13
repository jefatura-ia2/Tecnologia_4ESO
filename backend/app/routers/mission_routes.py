from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import config
from ..anticheat import check_timing, plagiarism_check
from ..auth import current_user
from ..content import calendar, get_section, load_missions, mission_summary, public_section
from ..db import get_db
from ..evaluator import grade_section
from ..feedback import summary_message
from ..models import SectionPhoto, SectionProgress, Submission, User, now
from ..photos import needs_photo, photo_meta, validate_photo
from ..progress import unlock_state

router = APIRouter(prefix="/api", tags=["misiones"])

HARDWARE = [
    {
        "id": "pico_w", "name": "Raspberry Pi Pico W", "chip": "RP2040 · 2 núcleos Cortex-M0+ a 133 MHz",
        "ram": "264 KB", "flash": "2 MB", "wifi": "Sí (CYW43439, 2,4 GHz)", "bluetooth": "BLE en el chip CYW43439 (MicroPython ≥ 1.20); el curso usa BLE sobre todo con la ESP32-S3",
        "usb": "Micro-USB", "adc": "3 canales de 12 bits: GPIO 26, 27, 28 (+ sensor de temperatura interno)",
        "led": 'Pin("LED") — conectado al chip WiFi', "button": "BOOTSEL (solo para cargar firmware)",
        "ml": "GPIO a 3,3 V y máx. ~12 mA por pin: las electroválvulas de 12 V se mandan siempre a través de un módulo MOSFET",
        "spi": "Electroválvulas EV1-EV4: GP10-GP13 · Finales de carrera: GP18-GP21",
        "firmware": "https://micropython.org/download/RPI_PICO_W/",
    },
    {
        "id": "esp32_s3", "name": "ESP32-S3-DevKit", "chip": "ESP32-S3-WROOM-1 · 2 núcleos Xtensa LX7 a 240 MHz",
        "ram": "512 KB (+ PSRAM según modelo)", "flash": "8-16 MB", "wifi": "Sí (802.11 b/g/n, 2,4 GHz)",
        "bluetooth": "BLE 5.0", "usb": "USB-C doble (UART + USB-OTG nativo)",
        "adc": "20 canales de 12 bits (ADC1: GPIO 1-10 · ADC2: GPIO 11-20; ADC2 no funciona con WiFi activo)",
        "led": "LED RGB direccionable (WS2812) en GPIO 48 (GPIO 38 en algunas revisiones v1.1)",
        "button": "BOOT (GPIO 0); algunas placas incluyen KEY en IO45",
        "ml": "GPIO a 3,3 V (máx. ~20-40 mA por pin): las electroválvulas de 12 V se mandan siempre a través de un módulo MOSFET",
        "spi": "Electroválvulas EV1-EV4: GPIO 4-7 · Finales de carrera: GPIO 17, 18, 8, 9",
        "firmware": "https://micropython.org/download/ESP32_GENERIC_S3/",
    },
]


class SubmitIn(BaseModel):
    answers: dict


class PhotoIn(BaseModel):
    image: str
    note: str = ""


def _get_progress(db: Session, user: User, mission_id: str, section_id: str) -> SectionProgress:
    p = db.query(SectionProgress).filter_by(user_id=user.id, section_id=section_id).first()
    if p is None:
        p = SectionProgress(user_id=user.id, mission_id=mission_id, section_id=section_id)
        db.add(p)
        db.flush()
    return p


@router.get("/hardware")
def hardware():
    return HARDWARE


@router.get("/calendar")
def get_calendar(user: User = Depends(current_user)):
    return {"start": config.COURSE_START_DATE.isoformat(), "weeks": calendar(),
            "hours_per_week": config.HOURS_PER_WEEK}


@router.get("/missions")
def list_missions(user: User = Depends(current_user), db: Session = Depends(get_db)):
    state = unlock_state(db, user)
    out = []
    for m in load_missions():
        summary = mission_summary(m)
        summary["state"] = state["missions"][m["id"]]
        for s in summary["sections"]:
            s["state"] = state["sections"][s["id"]]
        out.append(summary)
    return out


@router.get("/sections/{section_id}")
def get_section_view(section_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    mission, section = get_section(section_id)
    if section is None:
        raise HTTPException(404, "Sección no encontrada")
    state = unlock_state(db, user)
    if not state["sections"][section_id]["unlocked"]:
        raise HTTPException(403, "Sección bloqueada: supera antes las anteriores.")
    if user.role == "student":
        p = _get_progress(db, user, mission["id"], section_id)
        if p.started_at is None:
            p.started_at = now()
        db.commit()
    last = (db.query(Submission).filter_by(user_id=user.id, section_id=section_id)
            .order_by(Submission.created_at.desc()).first())
    idx = [s["id"] for s in mission["sections"]].index(section_id)
    nav = {
        "prev": mission["sections"][idx - 1]["id"] if idx > 0 else None,
        "next": mission["sections"][idx + 1]["id"] if idx + 1 < len(mission["sections"]) else None,
    }
    return {
        "mission": {"id": mission["id"], "number": mission["number"], "title": mission["title"],
                    "icon": mission.get("icon", ""), "passing_score": mission["passing_score"]},
        "section": public_section(section),
        "state": state["sections"][section_id],
        "nav": nav,
        "last_submission": {
            "answers": last.answers, "score": last.score, "passed": last.passed, "feedback": last.feedback,
            "created_at": last.created_at.isoformat(),
        } if last else None,
    }


@router.post("/sections/{section_id}/submit")
def submit(section_id: str, data: SubmitIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    mission, section = get_section(section_id)
    if section is None:
        raise HTTPException(404, "Sección no encontrada")
    state = unlock_state(db, user)
    if not state["sections"][section_id]["unlocked"]:
        raise HTTPException(403, "Sección bloqueada.")

    is_student = user.role == "student"
    elapsed = 0
    if is_student:
        p = _get_progress(db, user, mission["id"], section_id)
        allowed, msg, elapsed = check_timing(p)
        if not allowed:
            db.commit()
            raise HTTPException(429, msg)

    result = grade_section(section, data.answers)
    passing = mission["passing_score"]
    passed = result["score"] >= passing - 1e-9
    result["passing_score"] = passing
    result["passed"] = passed
    result["message"] = summary_message(result["score"], passing, passed)

    if not is_student:  # el profesor puede probar sin guardar
        result["preview"] = True
        return result

    flags = plagiarism_check(db, user.id, section, data.answers)
    p.attempts += 1
    p.last_attempt_at = now()
    if passed:
        p.failed_streak = 0
        if not p.passed:
            p.passed, p.passed_at = True, now()
    else:
        p.failed_streak += 1
    p.best_score = max(p.best_score, result["score"])
    sub = Submission(user_id=user.id, mission_id=mission["id"], section_id=section_id, answers=data.answers,
                     score=result["score"], passed=passed, feedback=result, elapsed_seconds=elapsed,
                     flagged=bool(flags), flag_reason="\n".join(flags))
    db.add(sub)
    db.commit()

    new_state = unlock_state(db, user)
    result["attempts"] = p.attempts
    result["mission_completed"] = new_state["missions"][mission["id"]]["completed"]
    result["next_unlocked"] = None
    sec_state = new_state["sections"][section_id]
    photo_pending = passed and needs_photo(section) and sec_state["photo"] is None
    result["photo_pending"] = photo_pending
    if photo_pending:
        result["message"] += " 📷 Para completar la sección, sube la foto de tu montaje."
    idx = [s["id"] for s in mission["sections"]].index(section_id)
    if passed and not photo_pending and idx + 1 < len(mission["sections"]):
        result["next_unlocked"] = mission["sections"][idx + 1]["id"]
    return result


@router.post("/sections/{section_id}/photo")
def upload_photo(section_id: str, data: PhotoIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role != "student":
        raise HTTPException(400, "Solo el alumnado sube fotos de sus montajes.")
    mission, section = get_section(section_id)
    if section is None:
        raise HTTPException(404, "Sección no encontrada")
    if not needs_photo(section):
        raise HTTPException(400, "Esta sección no pide foto.")
    if not unlock_state(db, user)["sections"][section_id]["unlocked"]:
        raise HTTPException(403, "Sección bloqueada.")
    ok, msg, size = validate_photo(data.image)
    if not ok:
        raise HTTPException(400, msg)
    ph = db.query(SectionPhoto).filter_by(user_id=user.id, section_id=section_id).first()
    if ph is None:
        ph = SectionPhoto(user_id=user.id, section_id=section_id, image="")
        db.add(ph)
    ph.image, ph.bytes, ph.note = data.image, size, data.note[:300]
    ph.status, ph.comment, ph.uploaded_at, ph.reviewed_at = "pendiente", "", now(), None
    db.commit()
    state = unlock_state(db, user)
    idx = [s["id"] for s in mission["sections"]].index(section_id)
    sec_state = state["sections"][section_id]
    return {"ok": True, "photo": photo_meta(ph), "state": sec_state,
            "mission_completed": state["missions"][mission["id"]]["completed"],
            "next_unlocked": mission["sections"][idx + 1]["id"]
            if sec_state["passed"] and idx + 1 < len(mission["sections"]) else None}


@router.get("/sections/{section_id}/photo")
def my_photo(section_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    ph = db.query(SectionPhoto).filter_by(user_id=user.id, section_id=section_id).first()
    if ph is None:
        raise HTTPException(404, "Todavía no has subido foto.")
    return {"image": ph.image, "uploaded_at": ph.uploaded_at.isoformat()}
