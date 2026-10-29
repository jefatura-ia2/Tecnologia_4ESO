"""Valida el temario: cada solución de referencia saca el 100 % y los ítems están bien formados."""
import pytest

from app.content import load_missions
from app.evaluator import grade_code

MISSIONS = load_missions()
CODE_ITEMS = [(s["id"], i) for m in MISSIONS for s in m["sections"] for i in s["evaluation"]["items"] if i["type"] == "code"]


def test_structure():
    assert len(MISSIONS) == 15
    ids = set()
    for m in MISSIONS:
        assert m["schedule"], m["id"]
        for s in m["sections"]:
            assert s["id"] not in ids
            ids.add(s["id"])
            assert s["theory"].strip()
            for ex in s.get("examples", []):
                # Ejemplo de placa (Pico W + ESP32-S3, opcionalmente ESP32-C3) o ejemplo genérico (codigo + lenguaje)
                assert ex.get("codigo") or (ex.get("pico_w") and ex.get("esp32_s3")) or ex.get("esp32_c3"), (s["id"], ex["title"])
            item_ids = [i["id"] for i in s["evaluation"]["items"]]
            assert len(item_ids) == len(set(item_ids)), s["id"]
            for item in s["evaluation"]["items"]:
                if item["type"] == "quiz":
                    assert item["answer"] in [o["id"] for o in item["options"]], (s["id"], item["id"])
                if item["type"] == "fill_blank":
                    assert item["text"].count("___") == len(item["blanks"]), (s["id"], item["id"])
                if item["type"] == "code":
                    assert item.get("solution") and item.get("tests"), (s["id"], item["id"])


def test_schedule_covers_135_sessions():
    assert not any(m.get("extra") for m in MISSIONS)
    sessions = [(x["week"], x["session"]) for m in MISSIONS for x in m["schedule"]]
    assert len(sessions) == len(set(sessions)) == 135
    assert {w for w, _ in sessions} == set(range(1, 46))
    for m in MISSIONS:
        assert m.get("trimestre") in (1, 2, 3), m["id"]
        assert sum(s["hours"] for s in m["sections"]) == m["hours"] == 9, m["id"]
        sec_ids = {s["id"] for s in m["sections"]}
        assert all(x["section"] in sec_ids for x in m["schedule"]), m["id"]


@pytest.mark.parametrize("section_id,item", CODE_ITEMS, ids=[f"{s}-{i['id']}" for s, i in CODE_ITEMS])
def test_solution_passes(section_id, item):
    fb = grade_code(item, item["solution"])
    assert fb["correct"], fb


@pytest.mark.parametrize("section_id,item", CODE_ITEMS, ids=[f"{s}-{i['id']}" for s, i in CODE_ITEMS])
def test_starter_fails(section_id, item):
    fb = grade_code(item, item.get("starter", ""))
    assert not fb["correct"]
