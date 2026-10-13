"""Fotos de los montajes prácticos (mismas reglas que la versión de Netlify).

- Una sección con `foto` se considera superada al aprobar la evaluación Y tener foto no rechazada.
- Para desbloquear la siguiente basta con haber subido una foto (aunque luego se rechace).
"""
import re

from sqlalchemy.orm import Session, load_only

from .models import SectionPhoto, User

MAX_PHOTO_BYTES = 2_500_000
PHOTO_STATES = {"pendiente", "aceptada", "rechazada"}
_DATA_URL = re.compile(r"^data:image/(jpeg|png|webp);base64,([A-Za-z0-9+/=]+)$")


def needs_photo(section: dict) -> bool:
    return bool(section.get("foto"))


def photo_meta(ph: SectionPhoto | None) -> dict | None:
    if ph is None:
        return None
    return {"uploaded_at": ph.uploaded_at.isoformat(), "status": ph.status, "comment": ph.comment,
            "bytes": ph.bytes, "note": ph.note,
            "reviewed_at": ph.reviewed_at.isoformat() if ph.reviewed_at else None}


def photo_map(db: Session, user: User) -> dict[str, SectionPhoto]:
    q = (db.query(SectionPhoto)
         .options(load_only(SectionPhoto.section_id, SectionPhoto.status, SectionPhoto.comment, SectionPhoto.bytes,
                            SectionPhoto.note, SectionPhoto.uploaded_at, SectionPhoto.reviewed_at))
         .filter(SectionPhoto.user_id == user.id))
    return {p.section_id: p for p in q}


def photo_ok(section: dict, ph: SectionPhoto | None) -> bool:
    return not needs_photo(section) or (ph is not None and ph.status != "rechazada")


def photo_uploaded(section: dict, ph: SectionPhoto | None) -> bool:
    return not needs_photo(section) or ph is not None


def validate_photo(image) -> tuple[bool, str, int]:
    if not isinstance(image, str):
        return False, "Falta la imagen.", 0
    m = _DATA_URL.match(image)
    if not m:
        return False, "Formato no válido: sube una foto JPG, PNG o WEBP.", 0
    size = len(m.group(2)) * 3 // 4
    if size > MAX_PHOTO_BYTES:
        return False, "La foto es demasiado grande (máximo 2,5 MB).", size
    if size < 2000:
        return False, "La imagen está vacía o es demasiado pequeña.", size
    return True, "", size
