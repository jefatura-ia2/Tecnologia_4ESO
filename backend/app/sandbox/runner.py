"""Lanza el arnés en un subproceso con límites de CPU, memoria y tiempo."""
import json
import os
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path

from .. import config

HARNESS = Path(__file__).with_name("harness.py")
MAX_CODE_CHARS = 20_000


def _limits():  # pragma: no cover - se ejecuta en el hijo
    try:
        import resource

        cpu = int(config.SANDBOX_TIMEOUT) + 1
        resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
        mem = config.SANDBOX_MEMORY_MB * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
        resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
    except Exception:
        pass
    os.setsid()


def run_code(code: str, tests: list[dict], setup: list[str] | None = None) -> dict:
    if len(code) > MAX_CODE_CHARS:
        return {"ok": False, "error": {"type": "TooLong", "message": "El código es demasiado largo", "line": None}, "tests": []}
    nonce = "@@RESULT-" + secrets.token_hex(8) + "@@"
    payload = json.dumps({"code": code, "tests": tests, "setup": setup or []})
    with tempfile.TemporaryDirectory(prefix="sbx-") as tmp:
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-S", str(HARNESS), nonce],
                input=payload,
                capture_output=True,
                text=True,
                timeout=config.SANDBOX_TIMEOUT,
                cwd=tmp,
                env={"PATH": "/usr/bin:/bin", "PYTHONHASHSEED": "0"},
                preexec_fn=_limits if os.name == "posix" else None,
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": {"type": "Timeout", "message": "Tiempo agotado", "line": None}, "tests": []}
    for line in proc.stdout.splitlines():
        if line.startswith(nonce):
            return json.loads(line[len(nonce):])
    err = (proc.stderr or "").strip().splitlines()
    msg = err[-1] if err else "El programa terminó de forma inesperada"
    kind = "MemoryError" if "MemoryError" in msg else ("Timeout" if proc.returncode in (-9, -24, 137, 152) else "Crash")
    return {"ok": False, "error": {"type": kind, "message": msg[:300], "line": None}, "tests": []}
