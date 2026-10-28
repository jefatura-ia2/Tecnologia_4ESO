"""Pinout de la tira WS2812 de 8 LED (dibujo propio) y conexión a las placas del aula."""
from lib import *

s = SVG(900, 470, "Tira WS2812 de 8 LED: pads DIN y DOUT y conexión a la placa")
X, Y, W, H = 150, 90, 600, 120
s.rect(X, Y, W, H, fill="#15171a", stroke="#000", sw=2, rx=10)
cols = ["#22c55e", "#ef4444", "#f97316", "#3b82f6", "#22c55e", "#ef4444", "#f97316", "#3b82f6"]
for i in range(8):
    cx = X + 75 + i * 64
    s.rect(cx - 24, Y + 34, 48, 48, fill="#f5f5f4", stroke="#a8a29e", sw=1.5, rx=4)
    s.circle(cx, Y + 58, 15, fill=cols[i], stroke="#e7e5e4", sw=2)
    s.rect(cx - 8, Y + 92, 16, 9, fill="#78716c", stroke="none", sw=0)          # condensador
for x in (X + 205, X + W - 205):
    s.circle(x, Y + 18, 7, fill="#f5f5f4", stroke="#a8a29e", sw=1.5)              # taladros
# pads
pads = ["GND", "DIN", "5V", "GND"]
padso = ["GND", "DOUT", "5V", "GND"]
colp = {"GND": C["blue"], "DIN": C["green"], "DOUT": C["green"], "5V": C["red"]}
pin = {}
for i, (a, b) in enumerate(zip(pads, padso)):
    y = Y + 22 + i * 25
    s.rect(X + 6, y - 7, 22, 14, fill="#d4a017", stroke="#7c5e0b", sw=1, rx=2)
    s.rect(X + W - 28, y - 7, 22, 14, fill="#d4a017", stroke="#7c5e0b", sw=1, rx=2)
    s.rect(X - 70, y - 10, 58, 20, fill=colp[a], stroke="none", sw=0, rx=5)
    s.text(X - 41, y + 5, a, 12, "white", "middle", "bold")
    s.rect(X + W + 12, y - 10, 62, 20, fill=colp[b], stroke="none", sw=0, rx=5)
    s.text(X + W + 43, y + 5, b, 12, "white", "middle", "bold")
    pin[a if a != "GND" else f"GND{i}"] = (X + 6, y)
s.arrow(X + 250, Y + H + 22, X + 350, Y + H + 22, C["accent"], 2.5)
s.text(X + 300, Y + H + 44, "sentido de los datos", 12, C["accent"], "middle", "bold")
s.text(X - 41, Y - 16, "ENTRADA", 12, C["green"], "middle", "bold")
s.text(X + W + 43, Y - 16, "SALIDA", 12, C["green"], "middle", "bold")
s.text(X + W / 2, Y - 16, "Tira WS2812 · 8 LED 5050", 15, C["ink"], "middle", "bold")
# tabla de conexión
s.label_box(40, 300, 260, 130, "Raspberry Pi Pico W", ["DIN → GP22", "5V → VBUS (pin 40)", "GND → GND", "NeoPixel(Pin(22), 8)"], C["blue"])
s.label_box(320, 300, 260, 130, "ESP32-S3-DevKit", ["DIN → GPIO 21", "5V → 5V", "GND → GND", "NeoPixel(Pin(21), 8)"], C["accent"])
s.label_box(600, 300, 260, 130, "ESP32-C3 SuperMini", ["DIN → IO3", "5V → 5V", "GND → GND", "NeoPixel(Pin(3), 8)"], C["orange"])
caption(s, "Conecta siempre el extremo DIN. DOUT solo sirve para encadenar otra tira. Brillo ≤ 0,25 con alimentación USB.", 455)
s.save("tira_ws2812.svg")
print("ok")
