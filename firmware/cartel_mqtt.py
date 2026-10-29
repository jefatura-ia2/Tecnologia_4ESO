# cartel_mqtt.py · Smart Sign IoT (misiones 4-6) · ESP32-C3 SuperMini
# Guárdalo en la placa como main.py. Cartel de aula que escucha el topic aula/<AULA>/status
# en el broker Mosquitto del servidor del instituto y pinta la tira WS2812 del color recibido.
#
# Mejoras respecto al código base del proyecto:
#   - Tira en IO3 (IO8 es pin de arranque y lleva el LED de la placa).
#   - Brillo por software (MicroPython no tiene np.brightness): se escala el color.
#   - Reconexión automática de WiFi y MQTT, keepalive y último testamento (LWT) "offline".
#   - Un único programa para todos los carteles: solo cambia AULA.

import time
import network
from machine import Pin, reset
from neopixel import NeoPixel
from umqtt.simple import MQTTClient

# ------------------------------------------------------------ configuración
SSID = "SSID_INSTITUTO"
CLAVE = "PASSWORD"
SERVIDOR = "192.168.X.X"        # IP del servidor con Mosquitto
PUERTO = 1883
USUARIO = "cartel"              # None si el broker admite anónimos (solo en pruebas)
CONTRASENA = "*****"
AULA = "203"

PIN_TIRA = 3
NUM_LEDS = 12
BRILLO = 0.25                   # 0-1

TOPIC_ESTADO = "aula/{}/status".format(AULA).encode()
TOPIC_CONEXION = "aula/{}/conexion".format(AULA).encode()
CLIENT_ID = "cartel_aula" + AULA

COLORES = {
    b"verde": (0, 255, 0),       # libre
    b"rojo": (255, 0, 0),        # ocupada
    b"azul": (0, 0, 255),        # reservada
    b"amarillo": (255, 160, 0),
    b"apagado": (0, 0, 0),
}

# ------------------------------------------------------------ tira LED
tira = NeoPixel(Pin(PIN_TIRA, Pin.OUT), NUM_LEDS)


def pintar(rgb, brillo=BRILLO):
    tira.fill(tuple(int(c * brillo) for c in rgb))
    tira.write()


def parpadeo(rgb, veces=2):
    for _ in range(veces):
        pintar(rgb)
        time.sleep(0.15)
        pintar((0, 0, 0))
        time.sleep(0.15)


# ------------------------------------------------------------ red
wlan = network.WLAN(network.STA_IF)


def conectar_wifi(timeout=20):
    wlan.active(True)
    if wlan.isconnected():
        return True
    wlan.connect(SSID, CLAVE)
    t0 = time.time()
    while not wlan.isconnected():
        tira[0] = (0, 0, 20)            # LED 0 azul tenue: buscando WiFi
        tira.write()
        time.sleep(0.5)
        if time.time() - t0 > timeout:
            return False
    print("WiFi:", wlan.ifconfig()[0])
    return True


def al_llegar(topic, msg):
    msg = msg.strip().lower()
    print(topic, msg)
    if msg in COLORES:
        pintar(COLORES[msg])


def conectar_mqtt():
    c = MQTTClient(CLIENT_ID, SERVIDOR, port=PUERTO, user=USUARIO, password=CONTRASENA, keepalive=60)
    c.set_callback(al_llegar)
    c.set_last_will(TOPIC_CONEXION, b"offline", retain=True)
    c.connect()
    c.publish(TOPIC_CONEXION, b"online", retain=True)
    c.subscribe(TOPIC_ESTADO)         # el broker nos envía el último estado retenido
    print("Escuchando", TOPIC_ESTADO)
    return c


# ------------------------------------------------------------ programa principal
parpadeo((255, 255, 255))
cliente = None
ultimo_ping = time.time()
fallos = 0

while True:
    try:
        if not wlan.isconnected():
            cliente = None
            if not conectar_wifi():
                raise OSError("sin WiFi")
        if cliente is None:
            cliente = conectar_mqtt()
            fallos = 0
        cliente.check_msg()
        if time.time() - ultimo_ping > 30:
            cliente.ping()
            ultimo_ping = time.time()
        time.sleep(0.2)
    except OSError as e:
        print("Error de red:", e)
        cliente = None
        fallos += 1
        parpadeo((255, 120, 0), 1)       # naranja: problema de conexión
        if fallos > 20:                  # unos minutos sin conexión: reinicio limpio
            reset()
        time.sleep(min(30, 2 * fallos))
