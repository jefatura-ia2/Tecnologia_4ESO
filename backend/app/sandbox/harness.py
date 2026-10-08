"""Arnés que se ejecuta en un proceso aislado para corregir código del alumnado.

Uso: python3 -I harness.py <nonce>   (recibe JSON por stdin)

Simula los módulos de MicroPython (machine, time, neopixel, network, bluetooth...)
para que el código pensado para Pico W / ESP32-S3 pueda probarse en el servidor.
El resultado se escribe en stdout precedido del nonce, de modo que el alumno no
pueda falsificarlo con print().
"""
import ast
import builtins
import io
import json
import math
import random
import re
import sys
import types
import traceback

ALLOWED_IMPORTS = {
    "machine", "time", "utime", "math", "random", "urandom", "neopixel", "network",
    "bluetooth", "ubluetooth", "micropython", "esp32", "rp2", "gc", "json", "ujson",
    "struct", "ustruct", "array", "collections",
}
FORBIDDEN_NAMES = {
    "open", "exec", "eval", "compile", "__import__", "globals", "locals", "vars",
    "getattr", "setattr", "delattr", "breakpoint", "help", "memoryview", "exit", "quit",
    "__builtins__", "__loader__", "__spec__",
}


DUNDER_RE = re.compile(r"__\w+__")


class SecurityError(Exception):
    pass


def check_ast(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in ALLOWED_IMPORTS:
                    raise SecurityError(f"No se permite importar '{alias.name}' en este ejercicio")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] not in ALLOWED_IMPORTS:
                raise SecurityError(f"No se permite importar '{node.module}' en este ejercicio")
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise SecurityError("No se permite acceder a atributos especiales (__algo__)")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            raise SecurityError(f"No se permite usar '{node.id}' en este ejercicio")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and DUNDER_RE.search(node.value):
            raise SecurityError("No se permiten cadenas con nombres especiales (__algo__)")


# ----------------------------------------------------------------- simuladores
class Clock:
    def __init__(self):
        self.us = 0
        self.sleeps = []

    def advance_us(self, us):
        self.us += int(us)
        if self.us > 3_600_000_000:  # 1 h simulada: casi seguro un bucle sin fin
            raise TimeoutError("Tu programa 'esperó' más de una hora simulada: ¿bucle infinito?")


CLOCK = Clock()
LOG = []          # registro de acciones sobre el hardware: (componente, id, acción, valor)
ADC_VALUES = {}   # pin -> lista de valores (se recorren en bucle)
PIN_INPUTS = {}   # pin -> lista de valores leídos


def make_time():
    t = types.ModuleType("time")

    def sleep(s):
        CLOCK.sleeps.append(float(s))
        CLOCK.advance_us(float(s) * 1_000_000)

    def sleep_ms(ms):
        CLOCK.sleeps.append(ms / 1000)
        CLOCK.advance_us(ms * 1000)

    def sleep_us(us):
        CLOCK.sleeps.append(us / 1_000_000)
        CLOCK.advance_us(us)

    t.sleep, t.sleep_ms, t.sleep_us = sleep, sleep_ms, sleep_us
    t.ticks_us = lambda: CLOCK.us
    t.ticks_ms = lambda: CLOCK.us // 1000
    t.ticks_diff = lambda a, b: a - b
    t.ticks_add = lambda a, b: a + b
    t.time = lambda: 1_700_000_000 + CLOCK.us // 1_000_000
    t.localtime = lambda *a: (2026, 10, 13, 9, 0, 0, 0, 286)
    t._clock = CLOCK
    return t


def make_machine():
    m = types.ModuleType("machine")

    class Pin:
        IN, OUT, OPEN_DRAIN = 0, 1, 2
        PULL_UP, PULL_DOWN = 1, 2
        IRQ_FALLING, IRQ_RISING = 4, 8

        def __init__(self, id, mode=-1, pull=-1, value=None):
            self.id = id
            self.mode = mode
            # una entrada con pull-up sin nada conectado lee 1 (como en la placa real)
            self._v = int(bool(value)) if value is not None else (1 if pull == Pin.PULL_UP and mode == Pin.IN else 0)
            self._reads = 0
            LOG.append(("pin", id, "init", mode))

        def value(self, v=None):
            if v is None:
                seq = PIN_INPUTS.get(self.id)
                if seq:
                    val = seq[self._reads % len(seq)]
                    self._reads += 1
                    return val
                return self._v
            self._v = int(bool(v))
            LOG.append(("pin", self.id, "value", self._v))

        def __call__(self, v=None):
            return self.value(v)

        def on(self):
            self.value(1)

        def off(self):
            self.value(0)

        def high(self):
            self.value(1)

        def low(self):
            self.value(0)

        def toggle(self):
            self._v = 1 - self._v
            LOG.append(("pin", self.id, "toggle", self._v))

        def irq(self, handler=None, trigger=None):
            LOG.append(("pin", self.id, "irq", trigger))
            self._handler = handler

        def init(self, *a, **k):
            pass

    class ADC:
        ATTN_0DB, ATTN_2_5DB, ATTN_6DB, ATTN_11DB = 0, 1, 2, 3
        WIDTH_12BIT = 3
        CORE_TEMP = 4

        def __init__(self, pin, atten=None):
            self.id = pin.id if isinstance(pin, Pin) else pin
            self._i = 0
            LOG.append(("adc", self.id, "init", None))

        def _next(self):
            seq = ADC_VALUES.get(self.id, [32768])
            v = seq[self._i % len(seq)]
            self._i += 1
            return int(v)

        def read_u16(self):
            v = self._next()
            LOG.append(("adc", self.id, "read", v))
            return v

        def read(self):
            return self.read_u16() >> 4

        def read_uv(self):
            return int(self.read_u16() * 3_300_000 / 65535)

        def atten(self, a):
            LOG.append(("adc", self.id, "atten", a))

        def width(self, w):
            pass

    class PWM:
        def __init__(self, pin, freq=None, duty_u16=None):
            self.id = pin.id if isinstance(pin, Pin) else pin
            self._f, self._d = freq or 1000, duty_u16 or 0

        def freq(self, f=None):
            if f is None:
                return self._f
            self._f = f
            LOG.append(("pwm", self.id, "freq", f))

        def duty_u16(self, d=None):
            if d is None:
                return self._d
            self._d = d
            LOG.append(("pwm", self.id, "duty", d))

        def deinit(self):
            pass

    class Timer:
        PERIODIC, ONE_SHOT = 1, 0

        def __init__(self, *a, **k):
            pass

        def init(self, *a, **k):
            LOG.append(("timer", 0, "init", k.get("period")))

        def deinit(self):
            pass

    m.Pin, m.ADC, m.PWM, m.Timer = Pin, ADC, PWM, Timer
    m.freq = lambda *a: 133_000_000
    m.reset = lambda: LOG.append(("machine", 0, "reset", None))
    m.unique_id = lambda: b"\x01\x02\x03\x04"
    m._log = LOG
    return m


def make_neopixel(machine):
    mod = types.ModuleType("neopixel")

    class NeoPixel:
        def __init__(self, pin, n, bpp=3, timing=1):
            self.pin = pin.id if isinstance(pin, machine.Pin) else pin
            self.n = n
            self.buf = [(0, 0, 0)] * n

        def __setitem__(self, i, c):
            self.buf[i] = tuple(c)

        def __getitem__(self, i):
            return self.buf[i]

        def __len__(self):
            return self.n

        def fill(self, c):
            self.buf = [tuple(c)] * self.n

        def write(self):
            LOG.append(("neopixel", self.pin, "write", list(self.buf)))

    mod.NeoPixel = NeoPixel
    return mod


def make_network():
    net = types.ModuleType("network")
    net.STA_IF, net.AP_IF = 0, 1
    net.STAT_GOT_IP = 3

    class WLAN:
        def __init__(self, iface=0):
            self.iface = iface
            self._active = False
            self._connected = False
            self.ssid = None

        def active(self, v=None):
            if v is None:
                return self._active
            self._active = bool(v)
            LOG.append(("wifi", self.iface, "active", self._active))

        def connect(self, ssid=None, key=None, **k):
            self.ssid = ssid
            self._connected = self._active
            LOG.append(("wifi", self.iface, "connect", ssid))

        def isconnected(self):
            return self._connected

        def status(self, *a):
            return 3 if self._connected else 0

        def ifconfig(self, *a):
            return ("192.168.1.50", "255.255.255.0", "192.168.1.1", "8.8.8.8")

        def config(self, *a, **k):
            if a and a[0] == "mac":
                return b"\x28\xcd\xc1\x00\x00\x01"
            LOG.append(("wifi", self.iface, "config", k))

        def scan(self):
            return [(b"aula-tecnologia", b"\x00" * 6, 6, -50, 3, False)]

        def disconnect(self):
            self._connected = False

    net.WLAN = WLAN
    return net


def make_bluetooth():
    bt = types.ModuleType("bluetooth")

    class BLE:
        def __init__(self):
            self._active = False
            self.adv = None

        def active(self, v=None):
            if v is None:
                return self._active
            self._active = bool(v)
            LOG.append(("ble", 0, "active", self._active))

        def gap_advertise(self, interval_us, adv_data=None, **k):
            self.adv = bytes(adv_data) if adv_data is not None else None
            LOG.append(("ble", 0, "advertise", self.adv))

        def irq(self, h):
            pass

        def config(self, *a, **k):
            if a and a[0] == "mac":
                return (0, b"\x28\xcd\xc1\x00\x00\x02")
            LOG.append(("ble", 0, "config", k))

    bt.BLE = BLE
    bt.UUID = lambda x: x
    bt.FLAG_READ, bt.FLAG_WRITE, bt.FLAG_NOTIFY = 2, 8, 16
    return bt


def make_simple():
    mp = types.ModuleType("micropython")
    mp.native = lambda f: f
    mp.viper = lambda f: f
    mp.const = lambda x: x
    mp.mem_info = lambda *a: None

    gc = types.ModuleType("gc")
    gc.collect = lambda: None
    gc.mem_free = lambda: 180_000
    gc.mem_alloc = lambda: 20_000

    esp32 = types.ModuleType("esp32")
    esp32.mcu_temperature = lambda: 38
    esp32.raw_temperature = lambda: 100

    rp2 = types.ModuleType("rp2")
    rp2.country = lambda *a: LOG.append(("rp2", 0, "country", a[0] if a else None))
    return mp, gc, esp32, rp2


# --------------------------------------------------------------- utilidades
def same(a, b, tol):
    if isinstance(b, bool) or isinstance(a, bool):
        return a == b
    if isinstance(b, (int, float)) and isinstance(a, (int, float)):
        return math.isclose(a, b, rel_tol=tol, abs_tol=tol)
    if isinstance(b, (list, tuple)) and isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(same(x, y, tol) for x, y in zip(a, b))
    if isinstance(b, dict) and isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k], tol) for k in b)
    return a == b


def short(v, n=200):
    s = repr(v)
    return s if len(s) <= n else s[:n] + "…"


def error_info(exc):
    tb = traceback.extract_tb(exc.__traceback__)
    line = None
    for frame in tb:
        if frame.filename == "<alumno>":
            line = frame.lineno
    if isinstance(exc, SyntaxError) and exc.filename == "<alumno>":
        line = exc.lineno
    return {"type": type(exc).__name__, "message": str(exc), "line": line}


def reset_state():
    LOG.clear()
    ADC_VALUES.clear()
    PIN_INPUTS.clear()
    CLOCK.us = 0
    CLOCK.sleeps.clear()


def evaluate(req: dict) -> dict:
    """Ejecuta el código del alumno y sus pruebas. Lo usan el servidor (subproceso)
    y el navegador (Pyodide, en un Web Worker)."""
    reset_state()
    real_stdout = sys.stdout
    code, tests = req["code"], req.get("tests", [])
    random.seed(0)

    result = {"ok": False, "error": None, "tests": [], "stdout": ""}

    machine = make_machine()
    time_mod = make_time()
    neopixel = make_neopixel(machine)
    network = make_network()
    bluetooth = make_bluetooth()
    mp, gc, esp32, rp2 = make_simple()
    fake = {
        "machine": machine, "time": time_mod, "utime": time_mod, "neopixel": neopixel,
        "network": network, "bluetooth": bluetooth, "ubluetooth": bluetooth,
        "micropython": mp, "gc": gc, "esp32": esp32, "rp2": rp2,
        "json": json, "ujson": json, "math": math, "random": random, "urandom": random,
    }
    real_import = builtins.__import__

    def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
        root = name.split(".")[0]
        if root not in ALLOWED_IMPORTS:
            raise ImportError(f"No se permite importar '{name}'")
        if root in fake:
            return fake[root]
        return real_import(name, globals, locals, fromlist, level)

    for name in ("struct", "array", "collections"):
        fake.setdefault(name, real_import(name))
    fake["ustruct"] = fake["struct"]

    safe_builtins = {k: getattr(builtins, k) for k in dir(builtins)
                     if k not in FORBIDDEN_NAMES and not k.startswith("_")}
    safe_builtins["__import__"] = safe_import
    safe_builtins["__build_class__"] = builtins.__build_class__
    safe_builtins["input"] = lambda *a: "0"

    captured = io.StringIO()
    ns = {"__builtins__": safe_builtins, "__name__": "__main__"}

    try:
        for stmt in req.get("setup", []):  # preparación de confianza (del profesor)
            exec(stmt, {"machine": machine, "ADC_VALUES": ADC_VALUES, "PIN_INPUTS": PIN_INPUTS})
        tree = ast.parse(code, filename="<alumno>")
        check_ast(tree)
        compiled = compile(tree, "<alumno>", "exec")
        sys.stdout = captured
        try:
            exec(compiled, ns)
        finally:
            sys.stdout = real_stdout
        result["ok"] = True
    except SecurityError as exc:
        result["error"] = {"type": "SecurityError", "message": str(exc), "line": None}
    except BaseException as exc:  # noqa: BLE001 — cualquier fallo del alumno
        sys.stdout = real_stdout
        result["error"] = error_info(exc)

    if result["ok"]:
        test_ns = dict(ns)
        test_ns.update({
            "_machine": machine, "_time": time_mod, "_log": LOG, "_clock": CLOCK,
            "_out": captured.getvalue(), "_json": json, "_neopixel": neopixel, "_network": network, "_ble": bluetooth,
        })
        for t in tests:
            entry = {"desc": t.get("desc", "Prueba"), "passed": False}
            try:
                for stmt in t.get("before", []):
                    exec(stmt, test_ns)
                sys.stdout = captured
                try:
                    if "call" in t:
                        got = eval(t["call"], test_ns)
                    else:
                        got = eval(t["check"], test_ns)
                finally:
                    sys.stdout = real_stdout
                test_ns["_out"] = captured.getvalue()
                if "call" in t:
                    entry["passed"] = same(got, t["expected"], t.get("tol", 1e-6))
                    entry["got"] = short(got)
                    entry["expected"] = short(t["expected"])
                else:
                    entry["passed"] = bool(got)
            except BaseException as exc:  # noqa: BLE001
                sys.stdout = real_stdout
                entry["error"] = error_info(exc)
            result["tests"].append(entry)

    result["stdout"] = captured.getvalue()[:4000]
    return result


def evaluate_json(text: str) -> str:
    return json.dumps(evaluate(json.loads(text)), default=repr)


def main():
    nonce = sys.argv[1]
    result = evaluate(json.loads(sys.stdin.read()))
    sys.stdout.write(nonce + json.dumps(result, default=repr) + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
