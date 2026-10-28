# ---------------------------------------------------------------------------
#  tira_colores.py  ·  Tira WS2812 de 8 LEDs en ESP32-C3 SuperMini
#  Autor: Jose Ignacio Sanchez Castano
#
#  CONEXIONES
#     Tira DIN -> IO3   (del modulo ESP32-C3)
#     Tira 5V  -> 5V
#     Tira GND -> GND
#
#  Se usa el extremo de la tira marcado DIN. El otro extremo, DOUT, solo
#  sirve para encadenar una segunda tira.
# ---------------------------------------------------------------------------

from machine import Pin
from neopixel import NeoPixel
import time

# --------------------------------------------------------------- ajustes
PIN_DATOS = 3          # IO3
NUM_LEDS  = 8
BRILLO    = 0.25       # de 0.0 a 1.0. Ver la nota del final sobre consumo.

tira = NeoPixel(Pin(PIN_DATOS, Pin.OUT), NUM_LEDS)

COLORES = {
    "verde":   (0, 255, 0),
    "rojo":    (255, 0, 0),
    "naranja": (255, 70, 0),
    "azul":    (0, 0, 255),
    "apagado": (0, 0, 0),
}


def color(nombre):
    """Pinta toda la tira del color indicado."""
    r, g, b = COLORES[nombre]
    valor = (int(r * BRILLO), int(g * BRILLO), int(b * BRILLO))
    for i in range(NUM_LEDS):
        tira[i] = valor
    tira.write()


def apagar():
    color("apagado")


# ====================  DEMOSTRACION  ====================
# Recorre los cuatro colores en bucle. Para probar uno suelto, detén el
# programa y escribe en la consola de Thonny:   color("azul")

try:
    while True:
        for nombre in ("verde", "rojo", "naranja", "azul"):
            print(nombre)
            color(nombre)
            time.sleep(1)

except KeyboardInterrupt:          # al pulsar Stop en Thonny
    apagar()
    print("Tira apagada.")


# ---------------------------------------------------------------------------
#  NOTA SOBRE EL CONSUMO
#  Cada LED puede llegar a 60 mA en blanco pleno: 8 LEDs son casi 0,5 A.
#  Con BRILLO = 0.25 y un solo color primario te quedas sobre los 120 mA,
#  que el pin de 5V del modulo aguanta sin problema alimentado por USB.
#  Si subes BRILLO a 1.0, alimenta la tira con una fuente de 5V aparte
#  y une las masas.
# ---------------------------------------------------------------------------
