"""Pruebas de extremo a extremo de la API (registro, desbloqueo, entrega, anti-trampa, profesor)."""
import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["SECRET_KEY"] = "test"
os.environ["TEACHER_PASSWORD"] = "profe123"

from datetime import timedelta  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import config  # noqa: E402
from app.content import get_section, load_missions  # noqa: E402
from app.db import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models import SectionProgress  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def register(client, username, code=None):
    r = client.post("/api/auth/register", json={
        "username": username, "full_name": username.title(), "password": "secreto1",
        "class_code": code or config.CLASS_CODE, "group_name": "4ºA", "board": "esp32_s3"})
    return r


def correct_answers(section_id):
    _, s = get_section(section_id)
    ans = {}
    for item in s["evaluation"]["items"]:
        if item["type"] == "quiz":
            ans[item["id"]] = item["answer"]
        elif item["type"] == "fill_blank":
            ans[item["id"]] = [b["accept"][0] for b in item["blanks"]]
        else:
            ans[item["id"]] = item["solution"]
    return ans


def backdate(username, section_id, seconds=600):
    db = SessionLocal()
    from app.models import User
    u = db.query(User).filter_by(username=username).first()
    p = db.query(SectionProgress).filter_by(user_id=u.id, section_id=section_id).first()
    p.started_at = p.started_at - timedelta(seconds=seconds)
    if p.last_attempt_at:
        p.last_attempt_at = p.last_attempt_at - timedelta(seconds=seconds)
    db.commit()
    db.close()


def test_register_and_login(client):
    assert register(client, "ana", code="MALO").status_code == 400
    r = register(client, "ana")
    assert r.status_code == 200
    assert register(client, "ana").status_code == 400  # duplicado
    r = client.post("/api/auth/login", json={"username": "ana", "password": "secreto1"})
    assert r.status_code == 200 and r.json()["user"]["board"] == "esp32_s3"
    assert client.post("/api/auth/login", json={"username": "ana", "password": "x"}).status_code == 401


def test_missions_locked_and_no_answers_leak(client):
    tok = client.post("/api/auth/login", json={"username": "ana", "password": "secreto1"}).json()["token"]
    ms = client.get("/api/missions", headers=auth(tok)).json()
    assert len(ms) == 15
    assert ms[0]["state"]["unlocked"] and not ms[1]["state"]["unlocked"]
    assert ms[0]["sections"][0]["state"]["unlocked"] and not ms[0]["sections"][1]["state"]["unlocked"]
    assert client.get("/api/sections/m1s2", headers=auth(tok)).status_code == 403
    r = client.get("/api/sections/m1s1", headers=auth(tok))
    assert r.status_code == 200
    text = r.text
    assert '"answer"' not in text and '"solution"' not in text and '"accept"' not in text
    assert "estados[valvula] = estado" not in text


def test_submit_flow_and_anticheat(client):
    tok = client.post("/api/auth/login", json={"username": "ana", "password": "secreto1"}).json()["token"]
    # demasiado rápido
    r = client.post("/api/sections/m1s1/submit", json={"answers": {}}, headers=auth(tok))
    assert r.status_code == 429
    backdate("ana", "m1s1")
    # intento fallido
    r = client.post("/api/sections/m1s1/submit", json={"answers": {"q1": "b"}}, headers=auth(tok))
    assert r.status_code == 200
    body = r.json()
    assert not body["passed"] and body["score"] < 0.7
    q1 = next(i for i in body["items"] if i["id"] == "q1")
    assert "archivo de Python" in q1["message"]  # feedback específico del distractor
    # aprobado
    r = client.post("/api/sections/m1s1/submit", json={"answers": correct_answers("m1s1")}, headers=auth(tok))
    body = r.json()
    assert body["passed"] and body["score"] == 1.0 and body["next_unlocked"] == "m1s2"
    assert client.get("/api/sections/m1s2", headers=auth(tok)).status_code == 200


def test_cooldown_after_failures(client):
    tok = client.post("/api/auth/login", json={"username": "ana", "password": "secreto1"}).json()["token"]
    backdate("ana", "m1s2")
    for _ in range(config.FREE_ATTEMPTS):
        r = client.post("/api/sections/m1s2/submit", json={"answers": {}}, headers=auth(tok))
        assert r.status_code == 200
    r = client.post("/api/sections/m1s2/submit", json={"answers": {}}, headers=auth(tok))
    assert r.status_code == 429 and "intentos fallidos" in r.json()["detail"]


FOTO = "data:image/jpeg;base64," + __import__("base64").b64encode(b"\x07" * 6000).decode()


def subir_foto(client, tok, sid, image=FOTO):
    return client.post(f"/api/sections/{sid}/photo", json={"image": image, "note": "montaje"}, headers=auth(tok))


def test_photo_validation(client):
    tok = client.post("/api/auth/login", json={"username": "ana", "password": "secreto1"}).json()["token"]
    ms = client.get("/api/missions", headers=auth(tok)).json()
    secs = {s["id"]: s for s in ms[0]["sections"]}
    assert secs["m1s2"]["foto"] and not secs["m1s1"]["foto"]
    assert subir_foto(client, tok, "m1s1").status_code == 400
    assert subir_foto(client, tok, "m1s2", "data:text/plain;base64,QUJD").status_code == 400
    assert subir_foto(client, tok, "m1s2", "data:image/jpeg;base64,QUJD").status_code == 400
    big = "data:image/jpeg;base64," + __import__("base64").b64encode(b"\x01" * 2_600_000).decode()
    assert subir_foto(client, tok, "m1s2", big).status_code == 400
    assert subir_foto(client, tok, "m5s2").status_code == 403
    assert client.get("/api/sections/m1s2/photo", headers=auth(tok)).status_code == 404


def test_mission_unlock_and_plagiarism(client):
    tok = client.post("/api/auth/login", json={"username": "ana", "password": "secreto1"}).json()["token"]
    for sid in ["m1s2", "m1s3", "m1s4"]:
        client.get(f"/api/sections/{sid}", headers=auth(tok))
        backdate("ana", sid, 3600)
        r = client.post(f"/api/sections/{sid}/submit", json={"answers": correct_answers(sid)}, headers=auth(tok))
        assert r.json()["passed"], r.json()
        # aprobada, pero falta la foto del montaje: la siguiente sigue bloqueada
        assert r.json()["photo_pending"] and r.json()["next_unlocked"] is None and not r.json()["mission_completed"]
        f = subir_foto(client, tok, sid)
        assert f.status_code == 200, f.json()
        assert f.json()["photo"]["status"] == "pendiente"
    assert f.json()["mission_completed"]
    ms = client.get("/api/missions", headers=auth(tok)).json()
    assert ms[1]["state"]["unlocked"] and ms[0]["state"]["completed"]

    # Otro alumno copia el código de ana (con nombres cambiados) → alerta
    register(client, "beto")
    tok2 = client.post("/api/auth/login", json={"username": "beto", "password": "secreto1"}).json()["token"]
    client.get("/api/sections/m1s1", headers=auth(tok2))
    backdate("beto", "m1s1")
    client.post("/api/sections/m1s1/submit", json={"answers": correct_answers("m1s1")}, headers=auth(tok2))
    for sid in ["m1s2", "m1s3"]:
        client.get(f"/api/sections/{sid}", headers=auth(tok2))
        backdate("beto", sid)
        client.post(f"/api/sections/{sid}/submit", json={"answers": correct_answers(sid)}, headers=auth(tok2))
        subir_foto(client, tok2, sid)
    client.get("/api/sections/m1s4", headers=auth(tok2))
    backdate("beto", "m1s4")
    ans = correct_answers("m1s4")
    ans["c1"] = ans["c1"].replace("lecturas", "datos").replace("salida", "res") + "\n# mío\n"
    client.post("/api/sections/m1s4/submit", json={"answers": ans}, headers=auth(tok2))


def test_teacher_dashboard(client):
    r = client.post("/api/auth/login", json={"username": "profesor", "password": "profe123"})
    tok = r.json()["token"]
    stu = client.post("/api/auth/login", json={"username": "ana", "password": "secreto1"}).json()["token"]
    assert client.get("/api/teacher/overview", headers=auth(stu)).status_code == 403
    ov = client.get("/api/teacher/overview", headers=auth(tok)).json()
    assert ov["totals"]["students"] == 2
    ana = next(s for s in ov["students"] if s["username"] == "ana")
    assert ana["missions"][0]["completed"] and ana["passed_sections"] == 4
    assert ana["photos"]["uploaded"] == 3 and ov["totals"]["photos_pending"] >= 3
    flags = client.get("/api/teacher/flags", headers=auth(tok)).json()
    assert any("Similitud" in f["reason"] for f in flags), flags
    # revisión de fotos: rechazar quita la sección de superadas sin bloquear la siguiente
    pend = client.get("/api/teacher/photos?status=pendiente", headers=auth(tok)).json()
    assert any(f["username"] == "ana" and f["section_id"] == "m1s3" for f in pend)
    assert client.get("/api/teacher/photos", headers=auth(stu)).status_code == 403
    assert client.get("/api/teacher/photos/ana/m1s3", headers=auth(tok)).json()["image"] == FOTO
    assert client.get(f"/api/teacher/photos/{ana['id']}/m1s3", headers=auth(tok)).json()["image"] == FOTO
    r = client.put("/api/teacher/photos/ana/m1s3", json={"status": "rechazada", "comment": "No se ve el cableado"}, headers=auth(tok))
    assert r.json()["photo"]["status"] == "rechazada"
    assert client.put("/api/teacher/photos/ana/m1s3", json={"status": "otra"}, headers=auth(tok)).status_code == 400
    m1 = client.get("/api/missions", headers=auth(stu)).json()[0]
    s3 = next(s for s in m1["sections"] if s["id"] == "m1s3")
    assert not s3["state"]["passed"] and s3["state"]["score_passed"] and s3["state"]["photo"]["comment"] == "No se ve el cableado"
    assert not m1["state"]["completed"] and next(s for s in m1["sections"] if s["id"] == "m1s4")["state"]["unlocked"]
    assert subir_foto(client, stu, "m1s3").json()["photo"]["status"] == "pendiente"
    assert client.put("/api/teacher/photos/ana/m1s3", json={"status": "aceptada"}, headers=auth(tok)).json()["ok"]
    assert client.get("/api/missions", headers=auth(stu)).json()[0]["state"]["completed"]
    assert client.get("/api/sections/m1s3/photo", headers=auth(stu)).json()["image"] == FOTO
    detail = client.get(f"/api/teacher/students/{ana['id']}", headers=auth(tok)).json()
    assert detail["submissions"]
    assert client.post(f"/api/teacher/students/{ana['id']}/unlock", json={"mission_id": "m4"}, headers=auth(tok)).json()["ok"]
    ms = client.get("/api/missions", headers=auth(stu)).json()
    assert ms[3]["state"]["unlocked"] and not ms[2]["state"]["unlocked"]
    assert client.put(f"/api/teacher/students/{ana['id']}/grade", json={"mission_id": "m6", "grade": 8.5, "notes": "Buen proyecto"},
                      headers=auth(tok)).json()["ok"]
    csv = client.get("/api/teacher/export.csv", headers=auth(tok))
    assert csv.status_code == 200 and "ana" in csv.text and "8,5" in csv.text
    assert "fotos subidas" in csv.text and "3/44" in csv.text
    stats = client.get("/api/teacher/stats", headers=auth(tok)).json()
    assert len(stats) == sum(len(m["sections"]) for m in load_missions())
    sol = client.get("/api/teacher/sections/m1s1/solutions", headers=auth(tok)).json()
    assert sol["section"]["evaluation"]["items"][0]["answer"] == "a"
    # el profesor puede probar entregas sin que cuenten
    r = client.post("/api/sections/m6s4/submit", json={"answers": correct_answers("m6s4")}, headers=auth(tok))
    assert r.json()["preview"] and r.json()["passed"]


def test_calendar(client):
    tok = client.post("/api/auth/login", json={"username": "ana", "password": "secreto1"}).json()["token"]
    cal = client.get("/api/calendar", headers=auth(tok)).json()
    assert len(cal["weeks"]) == 45
    assert all(len(w["sessions"]) == 3 for w in cal["weeks"])
