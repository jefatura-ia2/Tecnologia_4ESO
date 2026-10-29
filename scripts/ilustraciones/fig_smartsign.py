"""Ilustraciones del proyecto Smart Sign IoT (misiones 4-6)."""
from lib import SVG, C, caption

ACR = "#cfeff5"      # metacrilato
PLA = "#e5e7eb"      # pieza impresa
PLA2 = "#9ca3af"


def dim_h(s, x1, x2, y, txt, ext_from=None, color=C["muted"]):
    """Cota horizontal con líneas de referencia."""
    if ext_from is not None:
        s.line(x1, ext_from, x1, y + 5, color, 1)
        s.line(x2, ext_from, x2, y + 5, color, 1)
    s.arrow(x1 + (x2 - x1) / 2, y, x1, y, color, 1.2)
    s.arrow(x1 + (x2 - x1) / 2, y, x2, y, color, 1.2)
    s.rect(x1 + (x2 - x1) / 2 - 24, y - 10, 48, 18, fill="white", stroke="none", sw=0)
    s.text(x1 + (x2 - x1) / 2, y + 5, txt, 13, C["ink"], "middle", "bold")


def dim_v(s, x, y1, y2, txt, ext_from=None, color=C["muted"]):
    if ext_from is not None:
        s.line(ext_from, y1, x - 5 if ext_from > x else x + 5, y1, color, 1)
        s.line(ext_from, y2, x - 5 if ext_from > x else x + 5, y2, color, 1)
    m = y1 + (y2 - y1) / 2
    s.arrow(x, m, x, y1, color, 1.2)
    s.arrow(x, m, x, y2, color, 1.2)
    s.rect(x - 18, m - 10, 36, 18, fill="white", stroke="none", sw=0)
    s.text(x, m + 5, txt, 13, C["ink"], "middle", "bold")


def leader(s, x1, y1, x2, y2, lines):
    s.line(x1, y1, x2, y2, C["ink"], 1)
    s.dot(x1, y1, C["ink"], 2.5)
    for i, l in enumerate(lines):
        s.text(x2 + 6, y2 + 4 + i * 16, l, 13 if i == 0 else 12, C["ink"] if i == 0 else C["muted"], weight="bold" if i == 0 else "normal")


# =====================================================================
# 1. Plano acotado: vista frontal + sección A-A
# =====================================================================
def plano():
    s = SVG(1060, 600, "Plano del cartel Smart Sign: vista frontal acotada y sección A-A del soporte")
    s.text(30, 34, "Vista frontal (escala 1:2,5)", 16, C["ink"], weight="bold")
    s.text(600, 34, "Sección A-A del soporte (escala 1:0,6)", 16, C["ink"], weight="bold")

    # ---------- vista frontal: 2 px/mm ----------
    k = 2
    x0, yb = 90, 500
    L, H = 176 * k, 38 * k
    ytop = yb - H
    s.rect(x0, ytop, L, H, fill=PLA, stroke=C["ink"], sw=2, rx=3)
    s.rect(x0, yb, L, 2 * k, fill=PLA2, stroke=C["ink"], sw=1.5)                    # tapa
    px, pw = x0 + 8 * k, 160 * k
    pbot = ytop + 10 * k                                                              # fondo de la ranura
    ptop = pbot - 120 * k
    s.rect(px, ptop, pw, ytop - ptop, fill=ACR, stroke="#0e7490", sw=2)
    s.rect(px, ytop, pw, pbot - ytop, fill="none", stroke="#0e7490", sw=1.2, extra='stroke-dasharray="5,4"')
    # tira LED oculta
    ys = yb - 28 * k
    s.rect(px - 2, ys, pw + 4, 3.6 * k, fill="none", stroke=C["orange"], sw=1.5, extra='stroke-dasharray="4,3"')
    # capuchón
    cw = 164.4 * k
    s.rect(px - 2.2 * k, ptop - 2 * k, cw, 9 * k, fill=PLA, stroke=C["ink"], sw=2, rx=2)
    # texto grabado
    s.text(px + pw / 2, ptop + 120, "AULA 203", 30, "#0e7490", "middle", "bold", 'opacity="0.55"')
    s.text(px + pw / 2, ptop + 150, "metacrilato 5 mm grabado", 13, "#0e7490", "middle")
    # ojales (ocultos, cara trasera)
    for xo in (x0 + L / 2 - 60 * k, x0 + L / 2 + 60 * k):
        s.circle(xo, yb - 7 * k, 4 * k, fill="none", stroke=C["muted"], sw=1.2)
    # USB-C en el lateral
    s.rect(x0 - 3, yb - 9 * k, 6, 6 * k, fill=C["ink"], stroke=C["ink"], sw=1)
    # cotas
    dim_h(s, px, px + pw, ptop - 30, "160", ext_from=ptop - 6)
    dim_v(s, px + pw + 46, ptop, ytop, "120*", ext_from=px + pw + 4)
    dim_h(s, x0, x0 + L, yb + 34, "176", ext_from=yb + 6)
    dim_v(s, x0 - 34, ytop, yb, "38", ext_from=x0 - 4)
    s.text(px + pw + 30, ptop + 130, "* visible: 120 − 10", 11, C["muted"])
    s.text(px + pw + 30, ptop + 145, "  (entra 10 en la ranura)", 11, C["muted"])
    # marca de sección A-A
    xa = x0 + L / 2
    s.line(xa, ytop - 14, xa, ytop + 8, C["red"], 2)
    s.line(xa, yb - 8, xa, yb + 14, C["red"], 2)
    s.arrow(xa, ytop - 14, xa + 22, ytop - 14, C["red"], 2)
    s.arrow(xa, yb + 14, xa + 22, yb + 14, C["red"], 2)
    s.text(xa + 30, ytop - 9, "A", 15, C["red"], weight="bold")
    s.text(xa + 30, yb + 19, "A", 15, C["red"], weight="bold")
    # leyenda
    s.line(30, 560, 60, 560, "#0e7490", 1.5, "5,4"); s.text(66, 565, "parte oculta del metacrilato", 12, C["muted"])
    s.line(250, 560, 280, 560, C["orange"], 1.5, "4,3"); s.text(286, 565, "tira WS2812 (oculta)", 12, C["muted"])
    s.circle(445, 560, 6, stroke=C["muted"], sw=1.2); s.text(457, 565, "ojales de pared (detrás)", 12, C["muted"])

    # ---------- sección A-A: 4 px/mm ----------
    k = 4
    xs, yb = 600, 470
    W, H = 45 * k, 38 * k
    yt = yb - H
    xc = xs + W / 2
    s.rect(xs, yt, W, H, fill=PLA, stroke=C["ink"], sw=2)
    pared = 2.4 * k
    hueco = 22 * k
    s.rect(xs + pared, yb - hueco, W - 2 * pared, hueco, fill="white", stroke=C["ink"], sw=1.5)
    y_canal = yb - hueco - 2.4 * k
    cw, ch = 11.1 * k, 3.6 * k
    s.rect(xc - cw / 2, y_canal - ch, cw, ch, fill="white", stroke=C["ink"], sw=1.5)
    rw = 5.2 * k
    s.rect(xc - rw / 2, yt, rw, y_canal - ch - yt, fill="white", stroke=C["ink"], sw=1.5)
    s.rect(xs, yb, W, 2 * k, fill=PLA2, stroke=C["ink"], sw=1.5)          # tapa
    # rayado de sección (bandas)
    for i in range(0, int(W + H), 14):
        pass
    # tira LED
    s.rect(xc - 10.5 * k / 2, y_canal - 3 * k, 10.5 * k, 1.2 * k, fill="#f8fafc", stroke=C["ink"], sw=1)
    s.rect(xc - 2.5 * k / 2, y_canal - 3 * k - 1.6 * k, 2.5 * k, 1.6 * k, fill=C["yellow"], stroke=C["ink"], sw=1)
    # metacrilato (sale por arriba, con rotura)
    pw = 5 * k
    ptop = yt - 120
    plate_bottom = y_canal - ch
    s.path(f"M{xc - pw/2},{plate_bottom} L{xc - pw/2},{ptop} L{xc - pw/2 + 6},{ptop - 8} L{xc + 2},{ptop + 4} L{xc + pw/2},{ptop - 6} L{xc + pw/2},{plate_bottom} Z",
           stroke="#0e7490", sw=2, fill=ACR)
    for dy in (20, 60, 100):
        s.arrow(xc, plate_bottom - dy + 18, xc, plate_bottom - dy - 6, C["yellow"], 2)
    # batería y módulos en el hueco
    s.circle(xs + pared + 46, yb - 44, 36, fill="#bfdbfe", stroke=C["blue"], sw=1.5)
    s.text(xs + pared + 46, yb - 40, "18650", 12, C["blue"], "middle", "bold")
    s.rect(xs + W - pared - 64, yb - 22, 60, 14, fill=C["pcb"], stroke=C["ink"], sw=1)
    s.text(xs + W - pared - 34, yb - 28, "módulos", 11, C["muted"], "middle")
    # ojal en la cara trasera (derecha = pared)
    s.rect(xs + W - 2, yb - 9 * k, 4, 6 * k, fill="white", stroke="none", sw=0)
    # cotas
    dim_h(s, xs, xs + W, yb + 40, "45", ext_from=yb + 10)
    dim_v(s, xs - 30, yt, yb, "38", ext_from=xs - 4)
    # notas
    lx = xs + W + 46
    leader(s, xc + rw / 2, yt + 18, lx, yt - 70, ["Ranura 5,2 mm", "= 5 (metacrilato) + 0,2 (holgura)", "profundidad 10 mm"])
    leader(s, xc + cw / 2, y_canal - ch / 2, lx, yt - 8, ["Canal de la tira 11,1 × 3,6", "LED mirando hacia arriba"])
    leader(s, xc + 30, y_canal + 4, lx, yt + 44, ["Suelo 2,4 mm", "paso de cables Ø5"])
    leader(s, xs + W - pared - 20, yb - 70, lx, yt + 96, ["Hueco de 22 mm", "batería y módulos"])
    leader(s, xs + W - 6, yb + 4, lx, yb + 4, ["Tapa 2 mm", "4 tornillos M3"])
    s.text(xs + 6, yt + 16, "pared 2,4", 11, C["muted"])
    caption(s, "Cotas en mm. La luz de la tira entra por el canto inferior del metacrilato y sale por las zonas grabadas.", 590)
    s.save("smart_sign_plano.svg")


# =====================================================================
# 2. Bloques de energía
# =====================================================================
def bloque(s, x, y, w, h, titulo, lineas, color):
    s.rect(x, y, w, h, fill="#f8fafc", stroke=color, sw=2, rx=10)
    s.text(x + w / 2, y + 26, titulo, 15, color, "middle", "bold")
    for i, l in enumerate(lineas):
        s.text(x + w / 2, y + 48 + i * 18, l, 12, C["ink"], "middle")


def energia():
    s = SVG(1060, 420, "Esquema de bloques de la energía del cartel: USB-C, TP4056, batería 18650, interruptor, MT3608, ESP32-C3 y tira WS2812")
    s.text(30, 34, "Energía del cartel", 17, C["ink"], weight="bold")
    # bloques
    bloque(s, 30, 80, 110, 80, "USB-C", ["cargador 5 V", "del móvil"], C["muted"])
    bloque(s, 200, 70, 170, 100, "TP4056", ["carga Li-ion 4,2 V", "protección DW01", "OUT+ / OUT−"], C["blue"])
    bloque(s, 200, 260, 170, 100, "Batería 18650", ["3,7 V nominal", "≈ 2500 mAh", "portapilas + JST"], C["green"])
    bloque(s, 430, 80, 100, 80, "Interruptor", ["ON / OFF"], C["ink"])
    bloque(s, 590, 70, 170, 100, "MT3608", ["elevador (boost)", "3,7 V → 5,0 V", "η ≈ 85 %"], C["orange"])
    bloque(s, 840, 50, 190, 100, "ESP32-C3 SuperMini", ["WiFi + MQTT", "pin 5V · IO3 → DIN"], C["accent"])
    bloque(s, 840, 230, 190, 100, "Tira WS2812 × 12", ["5 V · DIN · GND", "≈ 1 mA por LED apagado"], C["red"])
    # conexiones
    s.arrow(140, 120, 200, 120, C["red"], 3)
    s.arrow(285, 170, 285, 260, C["red"], 3, both=True)
    s.text(295, 196, "B+ / B−", 12, C["muted"])
    s.text(295, 212, "carga ⇅ descarga", 12, C["muted"])
    s.arrow(370, 120, 430, 120, C["red"], 3)
    s.arrow(530, 120, 590, 120, C["red"], 3)
    s.text(560, 108, "3,7 V", 12, C["red"], "middle", "bold")
    # bus 5 V
    s.line(760, 120, 800, 120, C["red"], 3)
    s.line(800, 100, 800, 280, C["red"], 3)
    s.arrow(800, 100, 840, 100, C["red"], 3)
    s.arrow(800, 280, 840, 280, C["red"], 3)
    s.text(780, 112, "5 V", 13, C["red"], "middle", "bold")
    # DIN
    s.arrow(935, 150, 935, 230, C["accent"], 2.5)
    s.text(945, 195, "IO3 → DIN", 12, C["accent"], weight="bold")
    # amperímetro en serie
    s.circle(285, 232, 15, fill="white", stroke=C["ink"], sw=2)
    s.text(285, 237, "A", 14, C["ink"], "middle", "bold")
    s.text(268, 237, "polímetro en serie", 11, C["muted"], "end")
    # GND común
    s.line(60, 390, 1000, 390, C["black"], 2, "6,4")
    s.text(1000, 382, "GND común a todos los bloques", 12, C["muted"], "end")
    # aviso
    s.rect(430, 220, 330, 120, fill="#fff7ed", stroke=C["orange"], sw=1.5, rx=8)
    s.text(445, 245, "⚠ Antes de conectar la placa", 13, C["orange"], weight="bold")
    s.text(445, 266, "ajusta la salida del MT3608 a 5,0 V", 12, C["ink"])
    s.text(445, 284, "con su potenciómetro y el polímetro.", 12, C["ink"])
    s.text(445, 308, "I_bat = I_5V · 5 / (3,7 · η)", 13, C["ink"], weight="bold")
    s.text(445, 328, "autonomía = 0,8 · capacidad / I_bat", 13, C["ink"], weight="bold")
    s.save("smart_sign_energia.svg")


# =====================================================================
# 3. Arquitectura MQTT
# =====================================================================
def mqtt():
    s = SVG(1060, 440, "Arquitectura MQTT del Smart Sign: el panel del profesor publica por WebSockets en el puerto 9001 y los carteles se suscriben por TCP en el puerto 1883")
    s.rect(20, 50, 1020, 360, fill="#f8fafc", stroke=C["line"], sw=1.5, rx=14)
    s.text(36, 76, "Red local del instituto (LAN) · el cortafuegos abre 1883 y 9001 solo dentro de la LAN", 13, C["muted"])
    s.text(30, 34, "Publicar / suscribir con MQTT", 17, C["ink"], weight="bold")
    # panel
    s.rect(50, 130, 210, 150, fill="white", stroke=C["ink"], sw=2, rx=10)
    s.rect(64, 146, 182, 92, fill="#eef2ff", stroke=C["line"], sw=1, rx=4)
    for i, (n, col) in enumerate((("Libre", C["green"]), ("Ocupada", C["red"]), ("Reservada", C["blue"]))):
        s.rect(72 + i * 58, 196, 52, 26, fill=col, stroke=col, sw=1, rx=5)
        s.text(98 + i * 58, 213, n, 10, "white", "middle", "bold")
    s.text(155, 176, "Aula 203: OCUPADA", 13, C["ink"], "middle", "bold")
    s.text(155, 258, "Panel del profesor", 14, C["ink"], "middle", "bold")
    s.text(155, 300, "React + mqtt.js", 12, C["muted"], "middle")
    s.text(155, 316, "http://servidor/  (no Netlify)", 12, C["muted"], "middle")
    # broker
    s.rect(400, 120, 260, 190, fill="white", stroke=C["accent"], sw=2.5, rx=12)
    s.text(530, 150, "Servidor Linux del instituto", 14, C["accent"], "middle", "bold")
    s.rect(420, 166, 220, 70, fill="#ecfdf5", stroke=C["accent"], sw=1.5, rx=8)
    s.text(530, 192, "Broker Mosquitto", 15, C["ink"], "middle", "bold")
    s.text(530, 214, ":1883 TCP · :9001 WebSockets", 12, C["ink"], "middle")
    s.text(530, 260, "Nginx :80 → panel_profesor.html", 12, C["muted"], "middle")
    s.text(530, 280, "guarda el último estado (retain)", 12, C["muted"], "middle")
    # panel -> broker
    s.arrow(260, 190, 400, 190, C["blue"], 3)
    s.text(330, 176, "ws://IP:9001", 12, C["blue"], "middle", "bold")
    s.text(330, 212, "publish", 12, C["ink"], "middle", "bold")
    s.text(330, 228, "aula/203/status", 11, C["ink"], "middle")
    s.text(330, 243, "«rojo» · retain", 11, C["ink"], "middle")
    # carteles
    for i, (aula, col) in enumerate((("105", C["green"]), ("106", C["blue"]), ("203", C["red"]))):
        y = 96 + i * 88
        s.rect(830, y, 150, 62, fill=ACR, stroke="#0e7490", sw=1.5, rx=3)
        s.rect(822, y + 62, 166, 16, fill=PLA, stroke=C["ink"], sw=1.5, rx=2)
        s.line(832, y + 60, 978, y + 60, col, 5)
        s.text(905, y + 38, "AULA " + aula, 16, col, "middle", "bold")
        s.arrow(660, 215, 818, y + 40, C["accent"], 2)
        s.text(1000, y + 30, "C3", 11, C["muted"])
    s.text(740, 140, "TCP :1883 (WiFi)", 12, C["accent"], "middle", "bold")
    s.text(905, 384, "subscribe aula/{id}/status", 12, C["ink"], "middle", "bold")
    s.text(905, 400, "cada cartel solo recibe su aula", 11, C["muted"], "middle")
    s.text(155, 380, "Pasillo: el panel se suscribe a aula/+/status", 12, C["ink"], "middle")
    s.save("smart_sign_mqtt.svg")


plano()
energia()
mqtt()
print("ok")
