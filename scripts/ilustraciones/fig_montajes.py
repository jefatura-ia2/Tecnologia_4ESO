from lib import *


def probe(s, tip, gnd, end, color, label):
    """Sonda: gancho en tip, pinza de masa en gnd, cable hasta end (x, y)."""
    bx, by = end
    s.rect(bx - 70, by - 14, 120, 28, fill="#374151", stroke="#111", sw=2, rx=12)
    s.rect(bx - 20, by - 9, 26, 18, fill="#6b7280", stroke="#111", sw=1, rx=3)
    s.text(bx - 7, by + 4, "x10", 10, "white", "middle", "bold")
    s.text(bx - 10, by - 22, label, 13, color, "middle", "bold")
    s.path(f"M{bx-70},{by} C{bx-110},{by} {tip[0]+60},{tip[1]} {tip[0]+14},{tip[1]}", "#9ca3af", 4)
    s.path(f"M{tip[0]+14},{tip[1]} L{tip[0]+4},{tip[1]} a5,5 0 1 1 -1,-6", "#e5e7eb", 3)
    s.circle(tip[0], tip[1], 7, fill="none", stroke=color, sw=3)
    s.path(f"M{bx-40},{by+14} C{bx-60},{by+60} {gnd[0]+70},{gnd[1]+10} {gnd[0]+18},{gnd[1]}", C["black"], 3)
    s.rect(gnd[0] + 6, gnd[1] - 7, 22, 14, fill=C["black"], stroke="#000", sw=1, rx=3)
    s.circle(gnd[0], gnd[1], 7, fill="none", stroke="#9ca3af", sw=3)
    s.line(bx + 50, by, bx + 130, by, "#9ca3af", 5)
    s.text(bx + 135, by + 5, "→ osciloscopio", 12, C["muted"])


# 1 ─ Medir la PWM de la placa -----------------------------------------------
s = SVG(900, 470, "Montaje para medir la PWM de la placa con el osciloscopio")
p = pico(s, 120, 60, highlight=("GP22", "GND"))
tip, gnd = p["GP22"], p["R:GND"]
gnd = (gnd[0], gnd[1] + (p["GP22"][1] - p["R:GND"][1]) * 0 )
gnd_pin = [v for k, v in p.items() if k == "R:GND"][0]
# GND de la derecha más cercano a GP22 (fila siguiente)
gnd2 = (p["GP22"][0], p["GP22"][1] + (p["GP21"][1] - p["GP22"][1]) / 2)
probe(s, p["GP22"], (p["GP22"][0], p["GP21"][1] - (p["GP21"][1] - p["GP22"][1]) / 2), (560, 200), C["ch1"], "Sonda CH1")
s.label_box(560, 290, 320, 130, "Conexión", ["Gancho de la sonda → GP22 (salida PWM)", "Pinza de masa → GND (pin junto a GP22)", "Sonda en x10 · menú CH1 en x10", "ESP32-S3: GPIO 21 y GND"], C["accent"])
caption(s, "La pinza de masa va SIEMPRE a GND. La placa se alimenta por el USB del ordenador.")
s.save("montaje_pwm.svg")


# 2 ─ PN532 por I2C -----------------------------------------------------------
s = SVG(900, 520, "Conexión del módulo PN532 NFC V3 a la Pico W por I2C")
X, Y = 40, 110
s.rect(X, Y, 270, 210, fill=C["pn532"], stroke="#7f1d1d", sw=2, rx=10)
for i in range(4):
    s.rect(X + 24 + i * 9, Y + 22 + i * 9, 150 - i * 18, 150 - i * 18, fill="none", stroke=C["copper"], sw=2.5, rx=14)
s.text(X + 99, Y + 101, "antena", 11, "#fde68a", "middle")
s.rect(X + 192, Y + 20, 60, 56, fill="#1d4ed8", stroke="#1e3a8a", sw=1.5, rx=3)
s.text(X + 222, Y + 32, "ON ↑", 9, "white", "middle")
for i in range(2):
    sx = X + 202 + i * 24
    s.rect(sx, Y + 38, 14, 28, fill="#e5e7eb", stroke="#111", sw=1)
    up = i == 0                                            # 1 = ON (arriba), 2 = OFF (abajo)
    s.rect(sx + 2, Y + (40 if up else 52), 10, 12, fill="#111", stroke="none", sw=0)
    s.text(sx + 7, Y + 88, str(i + 1), 10, "white", "middle", "bold")
s.text(X + 222, Y + 104, "1 ON · 2 OFF = I2C", 10, "white", "middle", "bold")
s.text(X + 120, Y + 200, "PN532 NFC RFID Module V3", 12, "white", "middle", "bold")
hdr = {}
for i, n in enumerate(("GND", "VCC", "SDA", "SCL")):
    hy = Y + 122 + i * 18
    s.circle(X + 262, hy, 5, fill="#d4a017", stroke="#7c5e0b", sw=1)
    s.text(X + 252, hy + 4, n, 10, "white", "end", "bold")
    hdr[n] = (X + 262, hy)
p = pico(s, 600, 80, highlight=("GP6", "GP7", "GND", "3V3"))
def route(a, b, color, via_x):
    s.wire([a, (via_x, a[1]), (via_x, b[1]), b], color, 3)
    s.dot(*a, color); s.dot(*b, color)
route(hdr["GND"], p["L7"], C["black"], 430)
route(hdr["SDA"], p["GP6"], C["blue"], 470)
route(hdr["SCL"], p["GP7"], C["yellow"], 510)
v = p["3V3"]
s.wire([hdr["VCC"], (400, hdr["VCC"][1]), (400, 40), (790, 40), (790, v[1]), v], C["red"], 3)
s.dot(*hdr["VCC"], C["red"]); s.dot(*v, C["red"])
s.text(600, 32, "VCC → 3V3 (pin 36)", 12, C["red"], "middle", "bold")
s.label_box(40, 350, 260, 132, "Pico W (bus I2C1)", ["SDA → GP6 (pin 9)", "SCL → GP7 (pin 10)", "VCC → 3V3 (36) · GND → GND (8)", "I2C(1, sda=Pin(6), scl=Pin(7))"], C["blue"])
s.label_box(320, 350, 260, 132, "ESP32-S3", ["SDA → GPIO 10", "SCL → GPIO 11", "VCC → 3V3 · GND → GND", "I2C(0, sda=Pin(10), scl=Pin(11))"], C["accent"])
caption(s, "Dirección I2C del PN532: 0x24. Cambia los interruptores sin alimentación.")
s.save("montaje_pn532.svg")


# 3 ─ Cerradura de solenoide con módulo MOSFET -------------------------------
s = SVG(900, 560, "Montaje de la cerradura de solenoide de 12 V con módulo MOSFET y diodo")
p = pico(s, 700, 110, highlight=("GP10", "GND"), h=360)
m = mosfet_module(s, 380, 250, mirror=True)
sup = supply12(s, 60, 60)
s.wire([p["GP10"], (640, p["GP10"][1]), (640, m["SIG"][1]), m["SIG"]], C["yellow"], 3)
s.wire([p["L12"], (660, p["L12"][1]), (660, m["GND"][1]), m["GND"]], C["black"], 3)
s.text(610, m["SIG"][1] - 8, "señal", 11, C["muted"], "middle")
s.wire([sup["+"], (sup["+"][0], 190), (330, 190), (330, m["V+"][1]), m["V+"]], C["red"], 3)
s.wire([sup["-"], (sup["-"][0], 210), (310, 210), (310, m["V−"][1]), m["V−"]], C["black"], 3)
# cerradura (abajo a la izquierda)
LX, LY = 60, 300
s.rect(LX, LY, 170, 90, fill="#9ca3af", stroke="#374151", sw=2, rx=6)
s.rect(LX + 20, LY + 20, 80, 50, fill="#b45309", stroke="#78350f", sw=1.5, rx=4)
s.text(LX + 60, LY + 50, "bobina", 11, "white", "middle")
s.path(f"M{LX+170},{LY+30} L{LX+205},{LY+30} L{LX+190},{LY+60} L{LX+170},{LY+60} Z", "#374151", 2, "#d1d5db")
s.text(LX + 85, LY - 10, "Cerradura de solenoide 12 V", 12, C["ink"], "middle", "bold")
lp, ln = (LX + 50, LY + 90), (LX + 130, LY + 90)
s.text(lp[0] - 10, lp[1] + 18, "+", 14, C["red"], "end", "bold")
s.text(ln[0] + 10, ln[1] + 18, "−", 14, C["ink"], "start", "bold")
yb = 480
s.wire([m["OUT+"], (290, m["OUT+"][1]), (290, yb + 20), (lp[0], yb + 20), lp], C["red"], 3)
s.wire([m["OUT−"], (270, m["OUT−"][1]), (270, yb - 20), (ln[0], yb - 20), ln], C["black"], 3)
# diodo entre + y − de la bobina, cátodo (banda) en el +
yd = 440
s.line(lp[0], lp[1], lp[0], yd, C["ink"], 2) if False else None
s.line(lp[0] + 0, yd, lp[0] + 25, yd, C["ink"], 2)
s.dot(lp[0], yd, C["ink"], 3)
s.line(lp[0], lp[1], lp[0], yd, C["ink"], 0)
s.path(f"M{lp[0]+50},{yd-11} L{lp[0]+50},{yd+11} L{lp[0]+27},{yd} Z", C["ink"], 1.5, "#374151")
s.line(lp[0] + 26, yd - 12, lp[0] + 26, yd + 12, C["ink"], 3)
s.line(lp[0] + 50, yd, ln[0], yd, C["ink"], 2)
s.dot(ln[0], yd, C["ink"], 3)
s.text(ln[0] + 12, yd + 4, "1N4007", 11, C["muted"])
s.text(ln[0] + 12, yd + 20, "(banda hacia el +)", 11, C["muted"])
# puntos de medida
s.badge(p["GP10"][0] - 34, p["GP10"][1] + 20, "1", "#ca8a04")
s.badge(330, m["OUT−"][1] + 20, "2", "#0891b2")
s.label_box(380, 60, 280, 92, "Puntos de medida (osciloscopio)", ["① CH1: GP10, señal de la placa", "② CH2: OUT−, drenador del MOSFET"], C["accent"])
caption(s, "GND común entre placa, módulo y fuente. ESP32-S3: señal en GPIO 4. Revisión del profesor antes de conectar los 12 V.")
s.save("montaje_cerradura.svg")


# 4 ─ LEDs y pulsador (misión 1) ---------------------------------------------
s = SVG(900, 500, "Montaje de cuatro LEDs y un pulsador con la Pico W")
p = pico(s, 690, 60, highlight=("GP10", "GP11", "GP12", "GP13", "GP14", "GND"))
gy = 440
s.line(60, gy, 640, gy, C["blue"], 3)
s.text(56, gy + 5, "GND", 13, C["blue"], "end", "bold")
s.wire([p["L17"], (650, p["L17"][1]), (650, gy), (640, gy)], C["black"], 3)
cols = ["#ef4444", "#f59e0b", "#22c55e", "#3b82f6"]
for i, gp in enumerate(("GP10", "GP11", "GP12", "GP13")):
    a = p[gp]
    x = 140 + i * 110
    yy = 120 + i * 0
    s.wire([a, (600 - i * 14, a[1]), (600 - i * 14, 90 + i * 20), (x, 90 + i * 20), (x, 180)], C["yellow"], 2.5)
    s.text(x + 8, 86 + i * 20, gp + " · EV" + str(i + 1), 11, C["muted"])
    s.rect(x - 7, 180, 14, 46, fill="#e8d5b0", stroke=C["ink"], sw=1.5, rx=4)
    for k, col in enumerate(("#dc2626", "#dc2626", "#7c2d12")):
        s.rect(x - 7, 188 + k * 8, 14, 3.5, fill=col, stroke="none", sw=0)
    s.text(x + 12, 207, "220 Ω", 11, C["muted"])
    s.line(x, 226, x, 270, C["ink"], 2)
    led(s, x, 270, cols[i])
    s.line(x, 310, x, gy, C["ink"], 2)
    s.dot(x, gy, C["blue"])
b = p["GP14"]
bx = 590
s.wire([b, (630, b[1]), (630, 380), (bx + 20, 380)], C["green"], 2.5)
s.line(bx + 20, 380, bx + 20, 400, C["ink"], 2)
s.line(bx + 20, 400, bx - 20, 392, C["ink"], 2.5)
s.line(bx - 20, 400, bx - 20, gy, C["ink"], 2)
s.line(bx, 375, bx, 393, C["ink"], 2)
s.line(bx - 10, 375, bx + 10, 375, C["ink"], 2.5)
s.dot(bx - 20, gy, C["blue"])
s.text(bx - 30, 368, "MARCHA (GP14)", 11, C["green"], "end", "bold")
caption(s, "Cada LED (con su resistencia de 220 Ω) representa una electroválvula. El pulsador va a GND: usa Pin.PULL_UP.", 488)
s.save("montaje_leds.svg")
print("ok")
