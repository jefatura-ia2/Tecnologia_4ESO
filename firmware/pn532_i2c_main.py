# ---------------------------------------------------------------------------
#  main.py  ·  Prueba del lector NFC PN532 por I2C en Raspberry Pi Pico W
#  Autor: Jose Ignacio Sanchez Castano
#
#  Necesita el archivo pn532_i2c.py copiado tambien en el Pico.
#
#  CONEXIONES  (I2C1 del Pico W)
#     PN532 SDA -> GP6   (pin fisico 9)
#     PN532 SCL -> GP7   (pin fisico 10)
#     PN532 VCC -> 3V3   (pin fisico 36)
#     PN532 GND -> GND   (pin fisico 8, 38, 3, 13...)
#
#  QUE HACE EL LED (el integrado de la placa):
#     3 parpadeos lentos al arrancar ... el programa ha empezado
#     parpadeo rapido y continuo ...... no encuentra el PN532
#     2 parpadeos cortos .............. ha leido una tarjeta nueva
#     encendido fijo .................. hay una tarjeta sobre la antena
# ---------------------------------------------------------------------------

from machine import Pin, I2C
import time

from pn532_i2c import PN532, uid_hex

# --------------------------------------------------------------- ajustes
PIN_SDA = 6
PIN_SCL = 7
BUS_I2C = 1               # GP6 y GP7 pertenecen al bus I2C1
FRECUENCIA = 100_000

led = Pin("LED", Pin.OUT)


def parpadeo(veces, ms=120):
    """Enciende y apaga el LED las veces indicadas."""
    for _ in range(veces):
        led.on()
        time.sleep_ms(ms)
        led.off()
        time.sleep_ms(ms)


def error(mensaje):
    """Muestra el fallo y deja el LED parpadeando rapido para siempre."""
    print("ERROR:", mensaje)
    while True:
        parpadeo(1, 60)


# ------------------------------------------------------------- arranque
parpadeo(3, 200)                      # senal visual de que el script corre

i2c = I2C(BUS_I2C, sda=Pin(PIN_SDA), scl=Pin(PIN_SCL), freq=FRECUENCIA)

encontrados = i2c.scan()
print("Dispositivos en el bus I2C:", [hex(d) for d in encontrados])
if not encontrados:
    error("el bus I2C esta vacio. Revisa SDA, SCL, VCC y GND.")

nfc = PN532(i2c)

version = nfc.version_firmware()
if version is None:
    error("PN532 no responde. Revisa los switches: 1 = ON, 2 = OFF.")

print("PN532 detectado - firmware {}.{}".format(version[0], version[1]))

if not nfc.configurar():
    error("fallo en la configuracion del PN532 (SAMConfiguration).")

print("Listo. Acerca una tarjeta a la antena...")

# ----------------------------------------------------------- bucle principal
ultimo = None
try:
    while True:
        uid = nfc.leer_uid(500)

        if uid:
            if uid != ultimo:                  # tarjeta nueva
                print("Tarjeta:", uid_hex(uid))
                parpadeo(2, 60)
                ultimo = uid
            led.on()                           # sigue encima de la antena
        else:
            if ultimo is not None:
                print("Tarjeta retirada")
            ultimo = None
            led.off()

        time.sleep_ms(200)

except KeyboardInterrupt:                      # al pulsar Stop en Thonny
    led.off()
    print("Programa detenido.")
