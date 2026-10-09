from lib import *


def sq(x0, y_base, dx, dy, period, duty, high, start, end, phase=0.0):
    """Puntos de una onda cuadrada (unidades en divisiones)."""
    pts = [(start, 0)]
    t = phase
    while t > start:
        t -= period
    lvl = 0
    edges = []
    while t < end:
        edges.append((t, high))
        edges.append((t + duty * period, 0))
        t += period
    cur = 0
    for te, v in edges:
        if te <= start:
            cur = v
    pts = [(start, cur)]
    for te, v in edges:
        if start < te < end:
            pts.append((te, cur))
            pts.append((te, v))
            cur = v
    pts.append((end, cur))
    return [(x0 + a * dx, y_base - b * dy) for a, b in pts]


# 1 ─ Panel del osciloscopio ------------------------------------------------
s = SVG(900, 560, "Panel de un osciloscopio digital y sus mandos principales")
s.rect(20, 20, 860, 430, fill=C["scope"], stroke="#111", sw=2, rx=18)
s.rect(36, 36, 828, 398, fill=C["scope2"], stroke="none", sw=0, rx=12)
s.text(56, 64, "OSCILOSCOPIO DIGITAL · serie OD-600 (esquema)", 13, "#e5e7eb", weight="bold")
x0, y0, dx, dy = screen(s, 64, 96, 440, 300, header=None)
s.text(70, 112, "CH1  1.00 V/div", 12, C["ch1"], weight="bold")
s.text(250, 112, "M 200 µs/div", 12, "#e5e7eb")
s.text(400, 112, "T ↑ 1.60 V", 12, "#e5e7eb")
s.poly(sq(x0, y0 + 6 * dy, dx, dy, 5, 0.5, 3.3, 0, 10, phase=1), C["ch1"], 3)
s.add(f'<path d="M{x0-2},{y0 + 6*dy - 1.6*dy} l-10,-7 v14 z" fill="#f97316"/>')  # nivel de disparo
s.text(x0 - 2, y0 + 6 * dy + 4, "1▸", 11, C["ch1"], "end", "bold")
s.rect(x0, y0 + 300 - 34, 440, 34, fill="#111827", stroke="none", sw=0)
s.text(x0 + 10, y0 + 300 - 12, "Frec 1.000 kHz    Periodo 1.000 ms    Vmax 3.30 V    Duty 50.0 %", 12, "#a7f3d0")
# mandos
def knob(x, y, r, label, color="#9ca3af"):
    s.circle(x, y, r, fill="#4b5563", stroke="#111", sw=2)
    s.circle(x, y, r - 6, fill="#6b7280", stroke="#374151", sw=1)
    s.line(x, y, x, y - r + 4, "#f9fafb", 3)
    s.text(x, y + r + 16, label, 11, "#e5e7eb", "middle", "bold")
def button(x, y, w, label, color="#9ca3af", tc="#111"):
    s.rect(x, y, w, 26, fill=color, stroke="#111", sw=1.5, rx=5)
    s.text(x + w / 2, y + 17, label, 11, tc, "middle", "bold")
button(540, 70, 92, "AUTOSET", "#f59e0b")
button(642, 70, 92, "MEASURE", "#cbd5e1")
button(744, 70, 92, "CURSOR", "#cbd5e1")
button(540, 108, 92, "RUN/STOP", "#cbd5e1")
button(642, 108, 92, "MENU", "#cbd5e1")
button(744, 108, 92, "SAVE", "#cbd5e1")
s.rect(540, 152, 140, 150, fill="none", stroke="#6b7280", sw=1, rx=8)
s.text(610, 170, "VERTICAL", 11, "#d1d5db", "middle", "bold")
button(552, 180, 50, "CH1", C["ch1"])
button(618, 180, 50, "CH2", C["ch2"])
knob(610, 250, 26, "VOLTS/DIV")
s.rect(690, 152, 80, 150, fill="none", stroke="#6b7280", sw=1, rx=8)
s.text(730, 170, "HORIZ.", 11, "#d1d5db", "middle", "bold")
knob(730, 230, 26, "SEC/DIV")
s.rect(780, 152, 76, 150, fill="none", stroke="#6b7280", sw=1, rx=8)
s.text(818, 170, "TRIGGER", 11, "#d1d5db", "middle", "bold")
knob(818, 230, 20, "LEVEL")
# conectores
for i, (lab, col) in enumerate((("CH1", C["ch1"]), ("CH2", C["ch2"]))):
    cx = 580 + i * 90
    s.circle(cx, 360, 18, fill="#9ca3af", stroke="#111", sw=2)
    s.circle(cx, 360, 7, fill="#111", stroke="#000", sw=1)
    s.text(cx, 398, lab, 11, col, "middle", "bold")
s.rect(770, 342, 22, 22, fill="#d4a017", stroke="#111", sw=1.5, rx=3)
s.rect(800, 342, 22, 22, fill="#9ca3af", stroke="#111", sw=1.5, rx=3)
s.text(796, 384, "Calibr. 1 kHz", 10, "#e5e7eb", "middle")
s.text(796, 398, "señal · masa", 10, "#9ca3af", "middle")
# numeración y leyenda
for n, (bx, by) in enumerate([(84, 140), (586, 62), (568, 228), (700, 200), (798, 204), (580, 334), (796, 334)], 1):
    s.badge(bx, by, n)
leg = ["1 Pantalla: 10 × 8 divisiones", "2 AUTOSET y MEASURE (medidas automáticas)", "3 VOLTS/DIV: escala vertical",
       "4 SEC/DIV: escala de tiempo", "5 LEVEL: nivel de disparo (flecha naranja)", "6 Entradas BNC de las sondas", "7 Salida de calibración para compensar la sonda"]
for i, t in enumerate(leg):
    s.text(40 + (i % 2) * 430, 478 + (i // 2) * 20, t, 13, C["ink"])
s.save("osc_panel.svg")


# 2 ─ Lectura de una PWM -----------------------------------------------------
s = SVG(900, 520, "Cómo medir tensión, periodo y ciclo de trabajo en la pantalla")
x0, y0, dx, dy = screen(s, 60, 50, 500, 400)
s.text(66, 38, "CH1 1 V/div · 0,2 ms/div · sonda x10 (menú x10)", 13, C["ink"], weight="bold")
base = y0 + 7 * dy
pts = sq(x0, base, dx, dy, 5, 0.5, 3.3, 0, 10, phase=1)
s.poly(pts, C["ch1"], 3.5)
s.line(x0, base, x0 + 500, base, "#64748b", 1, "6,4")
# cotas
s.arrow(x0 + 1.6 * dx, base, x0 + 1.6 * dx, base - 3.3 * dy, "#f97316", 2.5, both=True)
s.text(x0 + 1.75 * dx, base - 1.5 * dy, "3,3 div", 13, "#fdba74", weight="bold")
yP = base + 0.45 * dy
s.arrow(x0 + 1 * dx, yP, x0 + 6 * dx, yP, "#22d3ee", 2.5, both=True)
s.text(x0 + 3.5 * dx, yP + 20, "T = 5 div", 13, "#67e8f9", "middle", "bold")
yT = base - 3.3 * dy - 14
s.arrow(x0 + 6 * dx, yT, x0 + 8.5 * dx, yT, "#a3e635", 2.5, both=True)
s.text(x0 + 7.25 * dx, yT - 8, "t_on = 2,5 div", 13, "#bef264", "middle", "bold")
# cálculos
s.label_box(600, 60, 280, 120, "Tensión", ["3,3 div × 1 V/div = 3,3 V", "(nivel alto de la salida de la placa)"], "#ea580c")
s.label_box(600, 196, 280, 120, "Periodo y frecuencia", ["T = 5 div × 0,2 ms/div = 1 ms", "f = 1 / T = 1 / 0,001 s = 1000 Hz"], "#0891b2")
s.label_box(600, 332, 280, 120, "Ciclo de trabajo", ["t_on = 2,5 div × 0,2 ms = 0,5 ms", "ciclo = 0,5 / 1 × 100 = 50 %"], "#65a30d")
caption(s, "Cuenta divisiones (cada una tiene 5 subdivisiones) y multiplica por la escala. Después compáralo con MEASURE.")
s.save("osc_lectura_pwm.svg")


# 3 ─ Compensación de la sonda -------------------------------------------------
s = SVG(900, 330, "Compensación de la sonda: subcompensada, correcta y sobrecompensada")
titles = [("Subcompensada", "esquinas redondeadas", "#dc2626"), ("Correcta ✓", "esquinas rectas", "#16a34a"), ("Sobrecompensada", "picos en las esquinas", "#dc2626")]
for k, (t, sub, col) in enumerate(titles):
    X = 30 + k * 290
    x0, y0, dx, dy = screen(s, X + 10, 60, 250, 180, divx=5, divy=4)
    s.text(X + 135, 40, t, 15, col, "middle", "bold")
    pts = []
    hi, lo = y0 + 0.9 * dy, y0 + 3.1 * dy
    per = 2 * dx
    for c in range(3):
        xs = x0 + c * per - 0.5 * dx
        for half, (a, b) in enumerate(((lo, hi), (hi, lo))):
            xa = xs + half * dx
            for i in range(26):
                u = i / 25
                xx = xa + u * dx
                if k == 0:
                    v = b + (a - b) * math.exp(-u * 4)
                elif k == 1:
                    v = b
                else:
                    v = b + (b - a) * 0.35 * math.exp(-u * 9)
                if x0 <= xx <= x0 + 250:
                    pts.append((xx, v))
    s.poly(pts, C["ch1"], 3)
    s.text(X + 135, 272, sub, 13, C["muted"], "middle")
caption(s, "Punta en la salida de calibración (1 kHz). Gira el tornillo de ajuste de la sonda hasta ver la onda del centro.", 310)
s.save("osc_compensacion.svg")


# 4 ─ Dos canales: señal de la placa y drenador del MOSFET ---------------------
s = SVG(900, 470, "Conmutación de la cerradura vista con dos canales")
x0, y0, dx, dy = screen(s, 60, 50, 520, 360)
s.text(66, 38, "CH1 2 V/div · CH2 5 V/div (sonda x10) · 0,5 s/div", 13, C["ink"], weight="bold")
b1 = y0 + 7.4 * dy
s.poly([(x0, b1), (x0 + 2 * dx, b1), (x0 + 2 * dx, b1 - 1.65 * dy), (x0 + 8 * dx, b1 - 1.65 * dy), (x0 + 8 * dx, b1), (x0 + 520, b1)], C["ch1"], 3)
s.text(x0 + 4, b1 - 6, "1", 12, C["ch1"], weight="bold")
b2 = y0 + 5 * dy
hi2 = b2 - 2.4 * dy
pts = [(x0, hi2), (x0 + 2 * dx, hi2), (x0 + 2.03 * dx, b2 - 0.05 * dy), (x0 + 8 * dx, b2 - 0.05 * dy), (x0 + 8.02 * dx, hi2), (x0 + 520, hi2)]
s.poly(pts, C["ch2"], 3)
s.text(x0 + 4, b2 - 6, "2", 12, C["ch2"], weight="bold")
s.poly([(x0 + 8 * dx, b2 - 0.05 * dy), (x0 + 8.01 * dx, y0 + 0.2 * dy), (x0 + 8.06 * dx, hi2)], "#f87171", 2, dash="4,3")
s.text(x0 + 7.85 * dx, y0 + 0.6 * dy, "sin diodo: pico peligroso", 12, "#fca5a5", "end")
s.label_box(610, 60, 270, 104, "CH1 · señal de la placa", ["0 V → 3,3 V durante 3 s", "(orden de abrir)"], "#ca8a04")
s.label_box(610, 180, 270, 124, "CH2 · drenador del MOSFET", ["Cerrada: 12 V (sin corriente)", "Abierta: ≈ 0 V (la bobina", "recibe los 12 V)"], "#0891b2")
s.label_box(610, 320, 270, 92, "Con diodo 1N4007", ["Al cortar no hay pico:", "el MOSFET está protegido"], "#16a34a")
caption(s, "Pinza de masa de las dos sondas a GND. Nunca a +12 V.")
s.save("osc_cerradura.svg")
print("ok")
