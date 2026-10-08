"""Medidas anti-trampa: tiempo mínimo, espera progresiva entre intentos y similitud de código."""
import builtins
import io
import keyword
import re
import tokenize
from datetime import datetime

from sqlalchemy.orm import Session

from . import config
from .models import SectionProgress, Submission, now

_KEEP = set(keyword.kwlist) | set(dir(builtins)) | {
    "Pin", "ADC", "PWM", "machine", "time", "sleep", "sleep_ms", "network", "neopixel", "WLAN",
    "value", "toggle", "on", "off", "read_u16", "append", "len", "range", "sum", "min", "max",
}


def check_timing(progress: SectionProgress, at: datetime | None = None) -> tuple[bool, str, int]:
    """Devuelve (permitido, mensaje, segundos_transcurridos)."""
    at = at or now()
    if progress.started_at is None:
        return False, "Abre primero la sección y estudia la teoría.", 0
    elapsed = int((at - progress.started_at).total_seconds())
    if progress.attempts == 0 and elapsed < config.MIN_SECONDS_BEFORE_SUBMIT:
        wait = config.MIN_SECONDS_BEFORE_SUBMIT - elapsed
        return False, f"Dedica un poco más de tiempo a la sección antes de entregar (faltan {wait} s).", elapsed
    if progress.failed_streak >= config.FREE_ATTEMPTS and progress.last_attempt_at:
        extra = progress.failed_streak - config.FREE_ATTEMPTS + 1
        cooldown = config.COOLDOWN_BASE_SECONDS * extra
        since = int((at - progress.last_attempt_at).total_seconds())
        if since < cooldown:
            return False, (f"Llevas {progress.failed_streak} intentos fallidos seguidos. Repasa la teoría: "
                           f"podrás reintentar en {cooldown - since} s."), elapsed
    return True, "", elapsed


def normalize_code(code: str) -> str:
    """Quita comentarios y renombra identificadores para comparar estructura, no nombres."""
    out = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(code).readline):
            if tok.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                            tokenize.DEDENT, tokenize.ENDMARKER):
                continue
            if tok.type == tokenize.NAME and tok.string not in _KEEP:
                out.append("ID")
            elif tok.type == tokenize.STRING:
                out.append("STR")
            else:
                out.append(tok.string)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return re.sub(r"\s+", " ", code)
    return " ".join(out)


def _shingles(text: str, k: int = 4) -> set:
    toks = text.split()
    if len(toks) < k:
        return {" ".join(toks)}
    return {" ".join(toks[i:i + k]) for i in range(len(toks) - k + 1)}


def similarity(a: str, b: str) -> float:
    sa, sb = _shingles(normalize_code(a)), _shingles(normalize_code(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def plagiarism_check(db: Session, user_id: int, section: dict, answers: dict) -> list[str]:
    """Compara el código con las entregas de otros alumnos en la misma sección."""
    reasons = []
    code_items = [i for i in section["evaluation"]["items"] if i["type"] == "code"]
    if not code_items:
        return reasons
    others = (
        db.query(Submission)
        .filter(Submission.section_id == section["id"], Submission.user_id != user_id)
        .order_by(Submission.created_at.desc())
        .limit(400)
        .all()
    )
    for item in code_items:
        mine = answers.get(item["id"]) or ""
        size = len(normalize_code(mine).split())
        if size < 40:  # en ejercicios cortos es normal que todos escriban casi lo mismo
            continue
        if size >= 60 and item.get("solution") and similarity(mine, item["solution"]) >= 0.999:
            reasons.append(f"[{item['id']}] Idéntico estructuralmente a la solución de referencia")
        best, who = 0.0, None
        for sub in others:
            other = (sub.answers or {}).get(item["id"]) or ""
            if not other:
                continue
            s = similarity(mine, other)
            if s > best:
                best, who = s, sub.user.username
        if best >= config.PLAGIARISM_THRESHOLD:
            reasons.append(f"[{item['id']}] Similitud {round(best * 100)}% con la entrega de {who}")
    return reasons
