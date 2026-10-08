# taller.py — Biblioteca del banco neumático de NeumaLab (4º ESO)
# Súbela a la placa con Thonny y úsala con:  from taller import *
# Funciona igual en Raspberry Pi Pico W y ESP32-S3 (solo cambian los números de pin).
#
# Conexiones del curso
#   Señal                     Pico W              ESP32-S3
#   EV1..EV4 (módulo MOSFET)  GP10..GP13          GPIO 4..7
#   MARCHA / PARO / SETA(NC)  GP14 / GP15 / GP16  GPIO 14 / 15 / 16
#   a0 / a1 / b0 / b1         GP18..GP21          GPIO 17 / 18 / 8 / 9
from machine import Pin
import sys
import time

if "rp2" in sys.platform:
    PINES = {"EV": (10, 11, 12, 13), "MARCHA": 14, "PARO": 15, "SETA": 16,
             "a0": 18, "a1": 19, "b0": 20, "b1": 21}
else:  # ESP32-S3
    PINES = {"EV": (4, 5, 6, 7), "MARCHA": 14, "PARO": 15, "SETA": 16,
             "a0": 17, "a1": 18, "b0": 8, "b1": 9}


class Electrovalvula:
    """Electroválvula de 12 V mandada por un canal del módulo MOSFET (1 = activada)."""

    def __init__(self, pin):
        self.pin = Pin(pin, Pin.OUT, value=0)   # arranca SIEMPRE desactivada
        self.activaciones = 0

    def activar(self):
        if not self.pin.value():
            self.activaciones += 1
        self.pin.value(1)

    def desactivar(self):
        self.pin.value(0)

    def activa(self):
        return self.pin.value() == 1


class CilindroDE:
    """Cilindro de doble efecto con dos 3/2 NC: A = avance, B = retroceso.
    Enclavamiento: nunca están las dos activadas a la vez."""

    def __init__(self, pin_a, pin_b):
        self.ev_a = Electrovalvula(pin_a)
        self.ev_b = Electrovalvula(pin_b)

    def avanzar(self):
        self.ev_b.desactivar()      # primero se quita la contraria
        self.ev_a.activar()

    def retroceder(self):
        self.ev_a.desactivar()
        self.ev_b.activar()

    def liberar(self):
        self.ev_a.desactivar()
        self.ev_b.desactivar()

    def estado(self):
        if self.ev_a.activa():
            return "AVANZANDO"
        if self.ev_b.activa():
            return "RETROCEDIENDO"
        return "LIBRE"


class Entrada:
    """Pulsador o final de carrera a GND con pull-up interno: activo = 0 V."""

    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self._antes = self.activa()

    def activa(self):
        return self.pin.value() == 0

    def flanco(self):
        """True solo en el instante en que se pulsa (no mientras se mantiene)."""
        ahora = self.activa()
        f = ahora and not self._antes
        self._antes = ahora
        return f


class Seta:
    """Seta de emergencia con contacto NC: 0 = reposo; 1 = pulsada o cable roto."""

    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)

    def pulsada(self):
        return self.pin.value() == 1


def esperar(entrada, timeout_ms, paso_ms=5):
    """Espera a que la entrada se active. Devuelve True o False si se agota el tiempo."""
    t0 = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t0) < timeout_ms:
        if entrada.activa():
            return True
        time.sleep_ms(paso_ms)
    return False


def estado_seguro(*actuadores):
    """Desactiva electroválvulas y libera cilindros."""
    for a in actuadores:
        if hasattr(a, "liberar"):
            a.liberar()
        else:
            a.desactivar()


if __name__ == "__main__":
    # Prueba rápida: cada electroválvula 0,5 s y estado de las entradas
    evs = [Electrovalvula(p) for p in PINES["EV"]]
    for i, ev in enumerate(evs, 1):
        print("EV%d" % i)
        ev.activar(); time.sleep(0.5); ev.desactivar(); time.sleep(0.3)
    for nombre in ("MARCHA", "PARO", "a0", "a1", "b0", "b1"):
        print(nombre, "activa" if Entrada(PINES[nombre]).activa() else "-")
    print("SETA", "PULSADA" if Seta(PINES["SETA"]).pulsada() else "ok")
