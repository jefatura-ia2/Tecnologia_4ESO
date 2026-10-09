"""Pequeña librería para dibujar las ilustraciones técnicas (SVG) de TEC_IVJP_lab27."""
import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "frontend", "public", "img")
os.makedirs(OUT, exist_ok=True)

FONT = "font-family:'Inter','Segoe UI',Arial,sans-serif"
C = {
    "ink": "#1f2937", "muted": "#6b7280", "line": "#cbd5e1", "bg": "#ffffff", "panel": "#f1f5f9",
    "scope": "#2b3038", "scope2": "#3a414c", "screen": "#0b1220", "grid": "#2c3a52", "grid2": "#3e5272",
    "ch1": "#facc15", "ch2": "#22d3ee", "red": "#dc2626", "black": "#111827", "yellow": "#eab308",
    "blue": "#2563eb", "green": "#16a34a", "orange": "#ea580c", "pcb": "#1d6b3a", "pcb_esp": "#20242b",
    "pn532": "#b91c1c", "copper": "#d4a017", "air": "#0ea5e9", "accent": "#0f766e",
}


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h, self.items = w, h, []
        self.title = title

    def add(self, s):
        self.items.append(s)
        return self

    # --- primitivas -------------------------------------------------
    def rect(self, x, y, w, h, fill="none", stroke=C["ink"], sw=2, rx=0, extra=""):
        return self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def line(self, x1, y1, x2, y2, stroke=C["ink"], sw=2, dash=None, extra=""):
        d = f'stroke-dasharray="{dash}"' if dash else ""
        return self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" {d} {extra}/>')

    def path(self, d, stroke=C["ink"], sw=2, fill="none", dash=None, extra=""):
        ds = f'stroke-dasharray="{dash}"' if dash else ""
        return self.add(f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}" stroke-linejoin="round" stroke-linecap="round" {ds} {extra}/>')

    def poly(self, pts, stroke=C["ink"], sw=2, fill="none", dash=None):
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        return self.path(d, stroke, sw, fill, dash)

    def circle(self, cx, cy, r, fill="none", stroke=C["ink"], sw=2):
        return self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, s, size=14, fill=C["ink"], anchor="start", weight="normal", extra=""):
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return self.add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" style="{FONT}" {extra}>{s}</text>')

    def _head(self, x1, y1, x2, y2, color, size):
        a = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2 - size * math.cos(a - 0.45), y2 - size * math.sin(a - 0.45))
        p2 = (x2 - size * math.cos(a + 0.45), y2 - size * math.sin(a + 0.45))
        self.add(f'<path d="M{x2:.1f},{y2:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} Z" fill="{color}" stroke="{color}" stroke-width="1"/>')

    def arrow(self, x1, y1, x2, y2, color=C["ink"], sw=2, both=False):
        size = 6 + sw * 2
        self.line(x1, y1, x2, y2, color, sw)
        self._head(x1, y1, x2, y2, color, size)
        if both:
            self._head(x2, y2, x1, y1, color, size)
        return self

    def badge(self, x, y, n, color=C["accent"]):
        self.circle(x, y, 13, fill=color, stroke="white", sw=2)
        return self.text(x, y + 5, str(n), 14, "white", "middle", "bold")

    def wire(self, pts, color, sw=4):
        self.poly(pts, C["black"] if color != C["black"] else "#4b5563", sw + 2)
        return self.poly(pts, color, sw)

    def dot(self, x, y, color=C["ink"], r=4):
        return self.circle(x, y, r, fill=color, stroke=color, sw=1)

    def label_box(self, x, y, w, h, title, lines, color=C["accent"]):
        self.rect(x, y, w, h, fill="#f8fafc", stroke=color, sw=1.5, rx=8)
        self.text(x + 12, y + 22, title, 14, color, weight="bold")
        for i, l in enumerate(lines):
            self.text(x + 12, y + 44 + i * 19, l, 13, C["ink"])
        return self

    def save(self, name):
        defs = ""
        body = "\n".join(self.items)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" role="img" aria-label="{self.title}">'
               f'<title>{self.title}</title>{defs}<rect width="100%" height="100%" fill="#ffffff"/>{body}</svg>')
        with open(os.path.join(OUT, name), "w") as f:
            f.write(svg)
        return name


# --- bloques reutilizables -------------------------------------------

def screen(s, x, y, w, h, divx=10, divy=8, header=None, footer=None):
    """Pantalla de osciloscopio con cuadrícula. Devuelve (x0, y0, dx, dy)."""
    s.rect(x - 6, y - 6, w + 12, h + 12, fill=C["screen"], stroke="#000", sw=2, rx=6)
    dx, dy = w / divx, h / divy
    for i in range(divx + 1):
        s.line(x + i * dx, y, x + i * dx, y + h, C["grid2"] if i == divx // 2 else C["grid"], 1, None if i in (0, divx) else "2,3")
    for j in range(divy + 1):
        s.line(x, y + j * dy, x + w, y + j * dy, C["grid2"] if j == divy // 2 else C["grid"], 1, None if j in (0, divy) else "2,3")
    # marcas finas en los ejes centrales
    for i in range(divx * 5):
        xx = x + i * dx / 5
        s.line(xx, y + h / 2 - 3, xx, y + h / 2 + 3, C["grid2"], 1)
    for j in range(divy * 5):
        yy = y + j * dy / 5
        s.line(x + w / 2 - 3, yy, x + w / 2 + 3, yy, C["grid2"], 1)
    if header:
        s.text(x + 4, y - 12, header, 12, "#e5e7eb")
    if footer:
        s.text(x + 4, y + h + 22, footer, 12, "#e5e7eb")
    return x, y, dx, dy


def square_wave(s, x0, y_base, dx, dy, period_div, duty, high_div, start_div, end_div, color, sw=3, phase_div=0.0):
    pts = []
    t = start_div - phase_div
    level_hi = y_base - high_div * dy
    x = x0 + start_div * dx
    # recorrer tramos
    cur = start_div
    k = math.floor((start_div - phase_div) / period_div)
    while cur < end_div:
        p0 = phase_div + k * period_div
        rise, fall, nxt = p0, p0 + duty * period_div, p0 + period_div
        for a, b, lvl in ((rise, fall, level_hi), (fall, nxt, y_base)):
            a2, b2 = max(a, cur), min(b, end_div)
            if b2 > a2:
                if pts and abs(pts[-1][1] - lvl) > 0.1:
                    pts.append((x0 + a2 * dx, lvl))
                elif not pts:
                    pass
                pts.append((x0 + a2 * dx, lvl))
                pts.append((x0 + b2 * dx, lvl))
                cur = b2
        k += 1
    s.poly(pts, color, sw)
    return pts


def pico(s, x, y, highlight=(), w=150, h=360, label="Raspberry Pi Pico W"):
    """Pico W vista superior (USB arriba). Devuelve dict pin -> (x, y)."""
    s.rect(x, y, w, h, fill=C["pcb"], stroke="#0f3d22", sw=2, rx=10)
    s.rect(x + w / 2 - 22, y - 12, 44, 26, fill="#c0c4c8", stroke="#6b7280", sw=1.5, rx=3)  # USB
    s.rect(x + w / 2 - 30, y + 120, 60, 60, fill="#111", stroke="#333", sw=1, rx=3)          # RP2040
    s.text(x + w / 2, y + 155, "RP2040", 10, "#9ca3af", "middle")
    s.rect(x + w / 2 - 34, y + 220, 68, 50, fill="#c8ccd0", stroke="#6b7280", sw=1, rx=3)     # módulo WiFi
    s.text(x + w / 2, y + 250, "WiFi", 10, "#374151", "middle")
    s.text(x + w / 2, y + h - 14, label, 11, "#e5e7eb", "middle", "bold")
    left = ["GP0", "GP1", "GND", "GP2", "GP3", "GP4", "GP5", "GND", "GP6", "GP7", "GP8", "GP9", "GND", "GP10",
            "GP11", "GP12", "GP13", "GND", "GP14", "GP15"]
    right = ["VBUS", "VSYS", "GND", "3V3_EN", "3V3", "VREF", "GP28", "GND", "GP27", "GP26", "RUN", "GP22", "GND",
             "GP21", "GP20", "GP19", "GP18", "GND", "GP17", "GP16"]
    pins = {}
    step = (h - 40) / 20
    for i, n in enumerate(left):
        py = y + 22 + i * step
        hl = n in highlight
        s.circle(x + 10, py, 4.5, fill="#facc15" if hl else "#d4a017", stroke="#7c5e0b", sw=1)
        if hl:
            s.text(x + 20, py + 4, n, 10, "#ffffff", weight="bold")
        pins.setdefault(n, (x + 10, py))
        pins[f"L{i}"] = (x + 10, py)
    for i, n in enumerate(right):
        py = y + 22 + i * step
        hl = n in highlight
        s.circle(x + w - 10, py, 4.5, fill="#facc15" if hl else "#d4a017", stroke="#7c5e0b", sw=1)
        if hl:
            s.text(x + w - 20, py + 4, n, 10, "#ffffff", "end", "bold")
        pins.setdefault("R:" + n, (x + w - 10, py))
        if n not in pins:
            pins[n] = (x + w - 10, py)
    return pins


def resistor(s, x1, y, x2, label=None):
    mid = (x1 + x2) / 2
    s.line(x1, y, mid - 20, y, C["ink"], 2)
    s.line(mid + 20, y, x2, y, C["ink"], 2)
    s.rect(mid - 20, y - 7, 40, 14, fill="#e8d5b0", stroke=C["ink"], sw=1.5, rx=4)
    for i, col in enumerate(("#dc2626", "#dc2626", "#7c2d12")):
        s.rect(mid - 12 + i * 7, y - 7, 3.5, 14, fill=col, stroke="none", sw=0)
    if label:
        s.text(mid, y - 12, label, 11, C["muted"], "middle")


def led(s, x, y, color):
    """LED vertical: ánodo arriba (x, y), cátodo abajo (x, y+40)."""
    s.line(x, y, x, y + 10, C["ink"], 2)
    s.path(f"M{x-10},{y+10} L{x+10},{y+10} L{x},{y+26} Z", C["ink"], 1.5, color)
    s.line(x - 10, y + 26, x + 10, y + 26, C["ink"], 2)
    s.line(x, y + 26, x, y + 40, C["ink"], 2)
    s.arrow(x + 12, y + 14, x + 24, y + 6, color, 1.5)
    s.arrow(x + 14, y + 20, x + 26, y + 12, color, 1.5)


def diode_v(s, x, y1, y2, label="1N4007"):
    """Diodo vertical: cátodo (banda) arriba (y1), ánodo abajo (y2)."""
    mid = (y1 + y2) / 2
    s.line(x, y1, x, mid - 10, C["ink"], 2)
    s.line(x, mid + 10, x, y2, C["ink"], 2)
    s.path(f"M{x-10},{mid+10} L{x+10},{mid+10} L{x},{mid-8} Z", C["ink"], 1.5, "#374151")
    s.line(x - 11, mid - 10, x + 11, mid - 10, C["ink"], 3)
    if label:
        s.text(x + 16, mid + 4, label, 11, C["muted"])


def mosfet_module(s, x, y, w=190, h=120, title="Módulo MOSFET", mirror=False):
    """mirror=True: bornes de señal a la derecha y de potencia a la izquierda."""
    s.rect(x, y, w, h, fill="#1e3a8a", stroke="#172554", sw=2, rx=8)
    s.text(x + w / 2, y + 22, title, 13, "white", "middle", "bold")
    s.rect(x + w / 2 - 18, y + 40, 36, 44, fill="#111", stroke="#000", sw=1, rx=2)
    s.text(x + w / 2, y + 66, "FET", 10, "#9ca3af", "middle")
    sig_x, pow_x = (x + w, x) if mirror else (x, x + w)
    pts = {}
    for i, n in enumerate(("SIG", "GND")):
        py = y + 52 + i * 34
        s.rect(sig_x - 8, py - 8, 16, 16, fill="#e5e7eb", stroke="#374151", sw=1.5, rx=2)
        s.text(sig_x + (-14 if mirror else 14), py + 4, n, 11, "white", "end" if mirror else "start")
        pts[n] = (sig_x + (8 if mirror else -8), py)
    for i, n in enumerate(("V+", "V−", "OUT+", "OUT−")):
        py = y + 30 + i * 24
        s.rect(pow_x - 8, py - 8, 16, 16, fill="#16a34a", stroke="#14532d", sw=1.5, rx=2)
        s.text(pow_x + (14 if mirror else -14), py + 4, n, 11, "white", "start" if mirror else "end")
        pts[n] = (pow_x + (-8 if mirror else 8), py)
    return pts


def supply12(s, x, y, w=150, h=80):
    s.rect(x, y, w, h, fill="#374151", stroke="#111", sw=2, rx=8)
    s.text(x + w / 2, y + 30, "Fuente 12 V DC", 13, "white", "middle", "bold")
    s.text(x + w / 2, y + 50, "≥ 2 A", 12, "#d1d5db", "middle")
    s.circle(x + w - 40, y + h - 14, 7, fill=C["red"], stroke="#7f1d1d", sw=1.5)
    s.circle(x + 40, y + h - 14, 7, fill=C["black"], stroke="#000", sw=1.5)
    s.text(x + w - 40, y + h + 14, "+12 V", 12, C["red"], "middle", "bold")
    s.text(x + 40, y + h + 14, "0 V", 12, C["ink"], "middle", "bold")
    return {"+": (x + w - 40, y + h - 14), "-": (x + 40, y + h - 14)}


def caption(s, text, y=None):
    s.text(s.w / 2, (y or s.h - 14), text, 13, C["muted"], "middle")
