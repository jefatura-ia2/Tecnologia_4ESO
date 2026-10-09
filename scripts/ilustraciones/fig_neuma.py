from neuma_simbolos import *

# A ─ Cilindro de simple efecto con electroválvula 3/2 -----------------------
s = SVG(900, 520, "Cilindro de simple efecto gobernado por una electroválvula 3/2 NC")
c_out = compresor(s, 80, 380)
fin, fout = frl(s, 160, 380)
air(s, [c_out, fin])
v = valve32(s, 470, 250)
air(s, [fout, (v["1"][0], fout[1]), v["1"]])
cyl = cylinder(s, 400, 70, single=True, piston=0.2)
air(s, [v["2"], (v["2"][0], 175), (cyl["rear"][0], 175), cyl["rear"]])
s.text(400 + 110, 58, "Cilindro de simple efecto (retorno por muelle)", 12, C["ink"], "middle", "bold")
# parte eléctrica
s.label_box(640, 210, 240, 150, "Mando eléctrico", ["Placa GP10 → módulo MOSFET", "MOSFET → bobina EV1 (12 V)", "Diodo 1N4007 en la bobina", "EV1 = 1 → el cilindro avanza", "EV1 = 0 → vuelve por el muelle"], C["orange"])
s.poly([(640, 340), (459, 340), (459, 292)], C["orange"], 2, dash="6,4")
s.text(410, 402, "3-4 bar en el aula", 11, C["muted"], "middle")
caption(s, "En reposo la vía 2 está unida al escape 3: el muelle mantiene el vástago dentro.")
s.save("neum_simple_efecto.svg")


# B ─ Doble efecto con dos 3/2 ----------------------------------------------
s = SVG(900, 560, "Cilindro de doble efecto con dos electroválvulas 3/2 NC y enclavamiento")
fin, fout = frl(s, 60, 430)
v1 = valve32(s, 290, 300, label="EV1 (A+)")
v2 = valve32(s, 560, 300, label="EV2 (A−)")
air(s, [fout, (v1["1"][0], fout[1]), v1["1"]])
air(s, [(v1["1"][0], fout[1]), (v2["1"][0], fout[1]), v2["1"]])
s.dot(v1["1"][0], fout[1], AIR, 5)
cyl = cylinder(s, 300, 90, w=300, piston=0.3, rod_ext=110)
air(s, [v1["2"], (v1["2"][0], 220), (cyl["rear"][0], 220), cyl["rear"]])
air(s, [v2["2"], (v2["2"][0], 220), (cyl["front"][0], 220), cyl["front"]])
s.text(450, 76, "Cilindro de doble efecto", 13, C["ink"], "middle", "bold")
s.text(cyl["rear"][0] - 6, 205, "cámara trasera", 11, C["muted"], "end")
s.text(cyl["front"][0] + 6, 205, "cámara delantera", 11, C["muted"])
# tabla de estados
tx, ty = 40, 70
s.rect(tx, ty, 190, 150, fill="#f8fafc", stroke=C["line"], sw=1.5, rx=8)
s.text(tx + 12, ty + 22, "EV1  EV2   Cilindro", 13, C["ink"], weight="bold")
rows = [("1", "0", "avanza", C["green"]), ("0", "1", "retrocede", C["green"]), ("0", "0", "libre", C["muted"]), ("1", "1", "¡PROHIBIDO!", C["red"])]
for i, (a, b, t, col) in enumerate(rows):
    yy = ty + 50 + i * 24
    s.text(tx + 22, yy, a, 13, C["ink"], "middle")
    s.text(tx + 62, yy, b, 13, C["ink"], "middle")
    s.text(tx + 92, yy, t, 13, col, weight="bold")
caption(s, "Enclavamiento por software: antes de activar una electroválvula, desactiva siempre la contraria.")
s.save("neum_doble_efecto.svg")


# C ─ Finales de carrera ------------------------------------------------------
s = SVG(900, 470, "Finales de carrera a0 y a1 conectados a la placa")
cyl = cylinder(s, 120, 90, w=300, piston=0.85, rod_ext=150)
s.text(270, 76, "Cilindro A (vástago fuera)", 13, C["ink"], "middle", "bold")
cam_x = cyl["tip"][0] - 10
s.rect(cam_x - 8, 108, 18, 24, fill=C["orange"], stroke=C["ink"], sw=1.5, rx=3)      # leva
def limit_switch(x, y, name, pressed):
    s.rect(x - 22, y, 44, 34, fill="#e5e7eb", stroke=C["ink"], sw=2, rx=4)
    ang = -1 if pressed else 1
    s.line(x, y, x + 10, y - 18, C["ink"], 3)
    s.circle(x + 12, y - 22, 6, fill="white", stroke=C["ink"], sw=2)
    s.text(x - 30, y + 24, name, 14, C["accent"], "end", "bold")
    return (x - 10, y + 34), (x + 10, y + 34)
a0 = limit_switch(250, 150, "a0 (dentro)", False)
a1 = limit_switch(cam_x + 4, 150, "a1 (fuera)", True)
s.text(cam_x + 30, 150, "← la leva pisa a1", 11, C["orange"])
# cableado
gy = 420
s.line(120, gy, 760, gy, C["blue"], 3)
s.text(116, gy + 5, "GND", 13, C["blue"], "end", "bold")
s.wire([a0[0], (a0[0][0], 300), (640, 300)], C["green"], 2.5)
s.wire([a1[0], (a1[0][0], 330), (640, 330)], C["green"], 2.5)
s.line(a0[1][0], a0[1][1], a0[1][0], gy, C["ink"], 2); s.dot(a0[1][0], gy, C["blue"])
s.line(a1[1][0], a1[1][1], a1[1][0], gy, C["ink"], 2); s.dot(a1[1][0], gy, C["blue"])
s.rect(640, 270, 140, 90, fill=C["pcb"], stroke="#0f3d22", sw=2, rx=8)
s.text(710, 290, "Placa", 12, "white", "middle", "bold")
s.text(650, 304, "GP18 / GPIO 17", 11, "#fde68a")
s.text(650, 334, "GP19 / GPIO 18", 11, "#fde68a")
s.text(650, 352, "GND", 11, "#bfdbfe")
s.wire([(700, 360), (700, gy)], C["black"], 2.5)
s.label_box(620, 170, 260, 64, "Contacto NA a GND + Pin.PULL_UP", ["pisado = 0 · libre = 1"], C["accent"])
caption(s, "Con el vástago fuera, a1 está pisado (0) y a0 libre (1). ESP32-S3: GPIO 17 y 18.")
s.save("finales_carrera.svg")
print("ok")
