"""Ilustraciones de las misiones 9-12: secuencias, seguridad, panel WiFi y GRAFCET."""
from lib import *
from neuma_simbolos import cylinder, valve32  # noqa: F401


# 1 ─ Diagrama espacio-fase A+ B+ B- A- ------------------------------------
s = SVG(900, 400, "Diagrama espacio-fase de la estampadora A+ B+ B- A-")
x0, y0, fw = 150, 70, 150
s.text(x0 - 10, y0 - 20, "fase", 12, C["muted"], "end")
for i in range(5):
    x = x0 + i * fw
    s.line(x, y0 - 10, x, 330, C["line"], 1.5, "4,4")
    s.text(x, y0 - 20, str(i + 1 if i < 4 else 1), 14, C["ink"], "middle", "bold")
rows = [("A", 120, [0, 1, 1, 1, 0], C["blue"]), ("B", 250, [0, 0, 1, 0, 0], C["orange"])]
for name, yb, pos, col in rows:
    s.text(60, yb - 18, f"Cilindro {name}", 14, col, "middle", "bold")
    s.text(118, yb - 46, "1", 12, C["muted"], "end"); s.text(118, yb + 4, "0", 12, C["muted"], "end")
    s.line(x0, yb, x0 + 4 * fw, yb, C["line"], 1)
    s.line(x0, yb - 50, x0 + 4 * fw, yb - 50, C["line"], 1)
    pts = []
    for i in range(4):
        a, b = pos[i], pos[i + 1]
        xa, xb = x0 + i * fw, x0 + (i + 1) * fw
        pts += [(xa, yb - 50 * a), (xb, yb - 50 * b)]
    s.poly(pts, col, 4)
moves = ["A+", "B+", "B−", "A−"]
for i, m in enumerate(moves):
    s.text(x0 + i * fw + fw / 2, 350, m, 15, C["accent"], "middle", "bold")
s.text(x0 + 2 * fw, 380, "movimiento de cada fase", 12, C["muted"], "middle")
s.save("espacio_fase.svg")


# 2 ─ La estampadora ---------------------------------------------------------
s = SVG(900, 500, "Estampadora: el cilindro A sujeta la pieza y el cilindro B la marca")
s.rect(80, 380, 740, 24, fill="#cbd5e1", stroke=C["ink"], sw=2)                # bancada
s.rect(520, 330, 120, 50, fill="#fcd34d", stroke=C["ink"], sw=2, rx=4)         # pieza
s.text(580, 360, "pieza", 13, C["ink"], "middle", "bold")
s.rect(660, 300, 26, 80, fill="#94a3b8", stroke=C["ink"], sw=2)                # tope fijo
cA = cylinder(s, 120, 320, w=260, h=56, piston=0.8, rod_ext=120)
s.rect(cA["tip"][0] - 4, 326, 16, 50, fill="#64748b", stroke=C["ink"], sw=2)    # mordaza
s.text(250, 306, "Cilindro A (sujeta)", 13, C["blue"], "middle", "bold")
# cilindro B vertical
bx, by = 552, 60
s.rect(bx, by, 56, 170, fill="white", stroke=C["ink"], sw=2.5)
s.rect(bx + 2, by + 150, 52, 10, fill=C["ink"], stroke=C["ink"], sw=1)
s.rect(bx + 22, by + 160, 12, 94, fill="#e5e7eb", stroke=C["ink"], sw=2)
s.rect(bx + 6, by + 254, 44, 16, fill="#64748b", stroke=C["ink"], sw=2)           # punzón
s.text(bx - 70, by + 110, "Cilindro B (marca)", 13, C["orange"], "end", "bold")
# finales de carrera
def fc(x, y, name, on):
    s.rect(x - 12, y - 10, 24, 20, fill="#16a34a" if on else "#e5e7eb", stroke=C["ink"], sw=1.5, rx=3)
    s.text(x, y + 30, name, 12, C["accent"], "middle", "bold")
fc(150, 440, "a0", False); fc(470, 440, "a1", True)
fc(bx - 40, by + 20, "b0", False); fc(bx - 40, by + 230, "b1", True)
s.label_box(660, 60, 220, 150, "Salidas y entradas", ["EV1/EV2 → cilindro A", "EV3/EV4 → cilindro B", "a0 GP18 · a1 GP19", "b0 GP20 · b1 GP21", "verde = pisado"], C["accent"])
caption(s, "Fase 2 de la secuencia A+ B+ B− A−: A sujeta la pieza (a1 pisado) y B baja a marcarla (b1 pisado).", 488)
s.save("estampadora.svg")


# 3 ─ Seta de emergencia con contacto NC ------------------------------------
s = SVG(900, 330, "Seta de emergencia con contacto NC: reposo, pulsada y cable cortado")
cases = [("Reposo", "contacto cerrado", "lee 0 · normal", False, False, C["green"]),
         ("Seta pulsada", "contacto abierto", "lee 1 · EMERGENCIA", True, False, C["red"]),
         ("Cable cortado", "circuito abierto", "lee 1 · EMERGENCIA", False, True, C["red"])]
for k, (t, sub, res, pressed, broken, col) in enumerate(cases):
    X = 40 + k * 285
    s.rect(X, 30, 260, 250, fill="#f8fafc", stroke=C["line"], sw=1.5, rx=10)
    s.text(X + 130, 58, t, 15, C["ink"], "middle", "bold")
    # seta
    s.circle(X + 60, 120, 30, fill="#facc15", stroke=C["ink"], sw=2)
    s.circle(X + 60, 120 + (4 if pressed else 0), 20, fill=C["red"], stroke="#7f1d1d", sw=2)
    # circuito: pin GP16 → contacto NC → GND
    s.text(X + 120, 100, "GP16", 12, C["accent"], weight="bold")
    s.line(X + 160, 96, X + 200, 96, C["ink"], 2)
    s.line(X + 200, 96, X + 200, 140, C["ink"], 2)
    # contacto NC
    if pressed:
        s.line(X + 200, 140, X + 214, 160, C["ink"], 2.5)
    else:
        s.line(X + 200, 140, X + 200, 166, C["ink"], 2.5)
    s.line(X + 200, 166, X + 200, 190 if not broken else 182, C["ink"], 2)
    if broken:
        s.line(X + 200, 196, X + 200, 214, C["ink"], 2)
        s.text(X + 210, 194, "✂", 16, C["red"])
    else:
        s.line(X + 200, 190, X + 200, 214, C["ink"], 2)
    s.line(X + 186, 214, X + 214, 214, C["ink"], 3)
    s.line(X + 191, 220, X + 209, 220, C["ink"], 2)
    s.text(X + 222, 219, "GND", 11, C["muted"])
    s.text(X + 130, 252, sub, 12, C["muted"], "middle")
    s.text(X + 130, 272, res, 14, col, "middle", "bold")
caption(s, "Con contacto NC y Pin.PULL_UP, cualquier fallo del cable para la máquina: seguridad positiva.", 312)
s.save("seta_nc.svg")


# 4 ─ Mando bimanual: diagrama de tiempos -----------------------------------
s = SVG(900, 400, "Diagrama de tiempos del mando bimanual con ventana de 0,5 s")
def trace(y, label, edges, col, t0=150, scale=120):
    s.text(130, y - 6, label, 13, col, "end", "bold")
    pts, lvl = [(t0, y)], 0
    for t, v in edges:
        x = t0 + t * scale
        pts += [(x, y - 30 * lvl), (x, y - 30 * v)]
        lvl = v
    pts.append((440, y - 30 * lvl))
    s.poly(pts, col, 3)
s.text(295, 34, "Caso correcto", 14, C["green"], "middle", "bold")
s.text(670, 34, "Caso incorrecto", 14, C["red"], "middle", "bold")
s.line(450, 50, 450, 340, C["line"], 1.5, "5,5")
trace(110, "P1", [(0.5, 1), (2.2, 0)], C["blue"], 150, 120)
trace(180, "P2", [(0.8, 1), (2.2, 0)], C["blue"], 150, 120)
trace(260, "Prensa baja", [(0.8, 1), (2.2, 0)], C["green"], 150, 120)
s.arrow(150 + 0.5 * 120, 196, 150 + 0.8 * 120, 196, C["orange"], 2, both=True)
s.text(150 + 0.65 * 120, 214, "0,3 s ✓", 12, C["orange"], "middle", "bold")
# caso incorrecto (a la derecha)
def trace2(y, edges, col):
    t0, scale = 480, 70
    pts, lvl = [(t0, y)], 0
    for t, v in edges:
        x = t0 + t * scale
        pts += [(x, y - 30 * lvl), (x, y - 30 * v)]
        lvl = v
    pts.append((860, y - 30 * lvl))
    s.poly(pts, col, 3)
trace2(110, [(0.4, 1), (4.5, 0)], C["blue"])
trace2(180, [(1.6, 1), (4.5, 0)], C["blue"])
trace2(260, [], C["red"])
s.arrow(480 + 0.4 * 70, 196, 480 + 1.6 * 70, 196, C["red"], 2, both=True)
s.text(480 + 1.0 * 70, 214, "1,2 s ✗", 12, C["red"], "middle", "bold")
s.text(680, 252, "no baja: fuera de la ventana", 12, C["red"], "middle")
caption(s, "La prensa solo baja si los dos pulsadores se pulsan con menos de 0,5 s de diferencia y se mantienen pulsados.", 380)
s.save("bimanual.svg")


# 5 ─ Panel WiFi y seguridad local -----------------------------------------
s = SVG(900, 340, "Panel de control por WiFi: el móvil manda, la seguridad local decide")
s.rect(50, 90, 110, 190, fill="#111827", stroke="#000", sw=2, rx=18)
s.rect(62, 112, 86, 140, fill="#f8fafc", stroke="none", sw=0, rx=4)
s.text(105, 132, "Panel", 11, C["ink"], "middle", "bold")
for i, (t, col) in enumerate((("CICLO", C["green"]), ("PARO", C["red"]), ("ESTADO", C["blue"]))):
    s.rect(72, 142 + i * 34, 66, 24, fill=col, stroke="none", sw=0, rx=5)
    s.text(105, 158 + i * 34, t, 11, "white", "middle", "bold")
s.text(105, 305, "Móvil", 13, C["ink"], "middle", "bold")
for r in (16, 28, 40):
    s.path(f"M{250-r},{170-r*0.2} A{r},{r} 0 0 1 {250+r},{170-r*0.2}", C["blue"], 2.5)
s.circle(250, 172, 4, fill=C["blue"], stroke=C["blue"])
s.text(250, 210, "WiFi 2,4 GHz", 12, C["blue"], "middle")
s.arrow(170, 185, 330, 185, C["ink"], 2)
s.text(250, 232, "GET /ciclo", 12, C["muted"], "middle")
s.rect(340, 120, 200, 130, fill=C["pcb"], stroke="#0f3d22", sw=2, rx=10)
s.text(440, 146, "Placa (servidor web)", 12, "white", "middle", "bold")
s.text(440, 172, "atender(ruta, estado)", 12, "#fde68a", "middle")
s.rect(360, 186, 160, 50, fill="#0b3b20", stroke="#86efac", sw=1, rx=6)
s.text(440, 206, "¿emergencia? → DENEGADO", 11, "#fecaca", "middle")
s.text(440, 224, "¿REPOSO? → CICLO", 11, "#bbf7d0", "middle")
s.arrow(545, 185, 650, 185, C["ink"], 2)
s.rect(660, 120, 200, 130, fill="#f8fafc", stroke=C["line"], sw=1.5, rx=10)
s.text(760, 146, "Máquina", 13, C["ink"], "middle", "bold")
s.text(760, 172, "electroválvulas", 12, C["muted"], "middle")
s.circle(720, 214, 18, fill="#facc15", stroke=C["ink"], sw=2)
s.circle(720, 214, 11, fill=C["red"], stroke="#7f1d1d", sw=1.5)
s.text(746, 210, "seta local", 12, C["red"], weight="bold")
s.text(746, 226, "manda siempre", 11, C["muted"])
s.arrow(700, 254, 470, 254, C["red"], 2)
caption(s, "El panel remoto nunca anula la seguridad local: con la seta pulsada, /ciclo se deniega.", 320)
s.save("panel_wifi.svg")


# 6 ─ GRAFCET de la estampadora ---------------------------------------------
s = SVG(900, 620, "GRAFCET de la estampadora A+ B+ B- A-")
X, Y, B, G = 300, 40, 56, 100
steps = [("0", None, "reposo"), ("1", "A+  (EV1)", None), ("2", "B+  (EV3)", None), ("3", "B−  (EV4)", None), ("4", "A−  (EV2)", None)]
trans = ["MARCHA · a0 · b0", "a1", "b1", "b0", "a0"]
for i, (n, act, note) in enumerate(steps):
    y = Y + i * G
    s.rect(X, y, B, B, fill="white", stroke=C["ink"], sw=2.5)
    if i == 0:
        s.rect(X + 6, y + 6, B - 12, B - 12, fill="none", stroke=C["ink"], sw=2)
    s.text(X + B / 2, y + B / 2 + 7, n, 20, C["ink"], "middle", "bold")
    if act:
        s.line(X + B, y + B / 2, X + B + 40, y + B / 2, C["ink"], 2)
        s.rect(X + B + 40, y + B / 2 - 20, 150, 40, fill="#fff7ed", stroke=C["orange"], sw=2)
        s.text(X + B + 115, y + B / 2 + 6, act, 15, C["orange"], "middle", "bold")
    if note:
        s.text(X + B + 20, y + B / 2 + 6, note, 13, C["muted"])
    # enlace y transición hacia la etapa siguiente
    ty = y + B + (G - B) / 2
    s.line(X + B / 2, y + B, X + B / 2, y + G if i < 4 else ty + 10, C["ink"], 2)
    s.line(X + B / 2 - 14, ty, X + B / 2 + 14, ty, C["ink"], 3.5)
    s.text(X + B / 2 - 24, ty + 5, trans[i], 14, C["accent"], "end", "bold")
# retorno de la etapa 4 a la 0
yb = Y + 4 * G + B + (G - B) / 2 + 10
s.poly([(X + B / 2, yb), (X + B / 2, yb + 12), (X - 90, yb + 12), (X - 90, Y - 14), (X + B / 2, Y - 14), (X + B / 2, Y)], C["ink"], 2)
s.path(f"M{X-90},{(Y + yb)/2 - 8} l-7,14 h14 z", C["ink"], 1, C["ink"])
s.label_box(600, 60, 260, 168, "Cómo se lee", ["Etapa = situación estable", "Doble cuadrado = etapa inicial", "Rectángulo = acción (salida)", "Rayita = transición (condición)", "Se pasa de etapa cuando la", "condición se cumple"], C["accent"])
caption(s, "Etapa 0 → (MARCHA con A y B dentro) → 1 A+ → (a1) → 2 B+ → (b1) → 3 B− → (b0) → 4 A− → (a0) → vuelta a 0.", 600)
s.save("grafcet_estampadora.svg")
print("ok")
