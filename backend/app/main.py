from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .auth import hash_password
from .content import load_missions
from .db import Base, SessionLocal, engine
from .models import User
from .routers import auth_routes, mission_routes, teacher_routes


def ensure_teacher():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == config.TEACHER_USERNAME).first():
            db.add(User(username=config.TEACHER_USERNAME, full_name=config.TEACHER_FULLNAME, role="teacher",
                        password_hash=hash_password(config.TEACHER_PASSWORD)))
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    load_missions()  # valida el temario al arrancar
    ensure_teacher()
    yield


app = FastAPI(title="TEC_IVJP_lab27 4º ESO — MicroPython, electrónica y neumática", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_routes.router)
app.include_router(mission_routes.router)
app.include_router(teacher_routes.router)


@app.get("/api/health")
def health():
    return {"ok": True, "missions": len(load_missions())}


# Si existe el frontend compilado (modo "todo en uno" sin Docker), se sirve desde aquí.
STATIC = Path(__file__).resolve().parent.parent / "static"
if STATIC.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        target = STATIC / full_path
        if full_path and target.is_file():
            return FileResponse(target)
        return FileResponse(STATIC / "index.html")
