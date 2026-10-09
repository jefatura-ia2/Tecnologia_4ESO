"""Configuración global leída de variables de entorno."""
import os
import secrets
from datetime import date


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


DATABASE_URL = _env("DATABASE_URL", "sqlite:///./data/neumalab.db")
def _secret_key() -> str:
    """Usa SECRET_KEY o, si no existe, una clave persistente en la carpeta de datos
    (debe ser la misma en todos los procesos del servidor)."""
    key = _env("SECRET_KEY", "")
    if key and not key.startswith("cambia-esto"):
        return key
    folder = os.path.dirname(DATABASE_URL.replace("sqlite:///", "", 1)) if DATABASE_URL.startswith("sqlite:///") else "."
    path = os.path.join(folder or ".", ".secret_key")
    try:
        os.makedirs(folder or ".", exist_ok=True)
        if not os.path.exists(path):
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w") as fh:
                fh.write(secrets.token_hex(32))
        with open(path) as fh:
            return fh.read().strip()
    except FileExistsError:
        with open(path) as fh:
            return fh.read().strip()
    except OSError:
        return secrets.token_hex(32)


SECRET_KEY = _secret_key()
TOKEN_HOURS = int(_env("TOKEN_HOURS", "12"))

# Cuenta de profesor que se crea al arrancar si no existe
TEACHER_USERNAME = _env("TEACHER_USERNAME", "profesor")
TEACHER_PASSWORD = _env("TEACHER_PASSWORD", "cambiame")
TEACHER_FULLNAME = _env("TEACHER_FULLNAME", "Profesor/a")

# Código que el alumnado necesita para registrarse (lo comunica el profesor)
CLASS_CODE = _env("CLASS_CODE", "4ESO-NEUMA")

# Inicio del trimestre (lunes de la semana 1). Se usa para el calendario.
try:
    COURSE_START_DATE = date.fromisoformat(_env("COURSE_START_DATE", "2026-09-14"))
except ValueError:
    COURSE_START_DATE = date(2026, 9, 14)
WEEKS = int(_env("COURSE_WEEKS", "36"))
HOURS_PER_WEEK = int(_env("HOURS_PER_WEEK", "3"))

# Anti-trampa
MIN_SECONDS_BEFORE_SUBMIT = int(_env("MIN_SECONDS_BEFORE_SUBMIT", "120"))
FREE_ATTEMPTS = int(_env("FREE_ATTEMPTS", "3"))          # intentos sin espera
COOLDOWN_BASE_SECONDS = int(_env("COOLDOWN_BASE_SECONDS", "60"))  # espera que crece tras fallos
PLAGIARISM_THRESHOLD = float(_env("PLAGIARISM_THRESHOLD", "0.92"))

# Sandbox
SANDBOX_TIMEOUT = float(_env("SANDBOX_TIMEOUT", "4"))
SANDBOX_MEMORY_MB = int(_env("SANDBOX_MEMORY_MB", "256"))

# Nota mínima por misión (proporción 0-1)
PASSING_SCORES = {
    1: 0.70,
    2: 0.70,
    3: 0.75,
    4: 0.75,
    5: 0.75,
}
PASSING_SCORE_EXTRA = 0.80

CORS_ORIGINS = [o.strip() for o in _env("CORS_ORIGINS", "*").split(",") if o.strip()]


def passing_score(mission_number: int) -> float:
    return PASSING_SCORES.get(mission_number, PASSING_SCORE_EXTRA)
