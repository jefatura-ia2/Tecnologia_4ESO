# ---------------------------------------------------------------------------
#  pn532_i2c.py  ·  Libreria para el lector NFC PN532 por I2C en MicroPython
#  Autor: Jose Ignacio Sanchez Castano
#
#  Este archivo NO se ejecuta solo: se importa desde el programa principal.
#  Copialo en la raiz del Pico (o en la carpeta /lib).
#
#  Uso minimo:
#
#      from machine import Pin, I2C
#      from pn532_i2c import PN532, uid_hex
#
#      i2c = I2C(1, sda=Pin(6), scl=Pin(7), freq=100_000)
#      nfc = PN532(i2c)
#      nfc.configurar()
#      print(uid_hex(nfc.leer_uid()))
#
#  El modulo debe tener los micro-interruptores en modo I2C:
#      SEL0 (1) = ON        SEL1 (2) = OFF
# ---------------------------------------------------------------------------

import time

DIR_PN532 = 0x24          # direccion I2C de 7 bits del modulo

TFI_ENVIO = 0xD4          # identificador de trama: host -> PN532
ACK = b'\x00\x00\xFF\x00\xFF\x00'


def uid_hex(uid, separador=":"):
    """Convierte un UID en bytes a texto legible: b'\\xaa\\xbb' -> 'AA:BB'."""
    if not uid:
        return ""
    return separador.join("{:02X}".format(b) for b in uid)


class PN532:
    """Driver minimo del PN532 por I2C: detectar el modulo y leer UIDs."""

    def __init__(self, i2c, direccion=DIR_PN532):
        self.i2c = i2c
        self.dir = direccion
        time.sleep_ms(100)          # el modulo tarda en arrancar

    # ------------------------------------------------- nivel bajo: tramas
    def _enviar(self, comando):
        """Monta y envia una trama normal de informacion."""
        longitud = len(comando) + 1                   # +1 por el TFI
        suma = TFI_ENVIO + sum(comando)
        trama = bytearray([0x00, 0x00, 0xFF,
                           longitud, (-longitud) & 0xFF, TFI_ENVIO])
        trama += comando
        trama.append((-suma) & 0xFF)                  # checksum de datos
        trama.append(0x00)                            # postambulo
        self.i2c.writeto(self.dir, trama)

    def _listo(self):
        """El primer byte que devuelve el modulo indica si tiene respuesta."""
        try:
            return self.i2c.readfrom(self.dir, 1)[0] & 0x01
        except OSError:
            return 0

    def _esperar(self, ms=1000):
        t0 = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), t0) < ms:
            if self._listo():
                return True
            time.sleep_ms(5)
        return False

    def _leer(self, n, ms=1000):
        """Devuelve n bytes de respuesta (sin el byte de estado) o None."""
        if not self._esperar(ms):
            return None
        try:
            buf = self.i2c.readfrom(self.dir, n + 1)
        except OSError:
            return None
        return buf[1:] if buf[0] & 0x01 else None

    def _leer_ack(self):
        return self._leer(6) == ACK

    def _leer_respuesta(self, ms=1000):
        """Devuelve solo los datos utiles de la trama (sin TFI ni checksum)."""
        d = self._leer(32, ms)
        if not d:
            return None
        i = d.find(b'\x00\xFF')                       # inicio de trama
        if i < 0:
            return None
        longitud = d[i + 2]
        return d[i + 5: i + 4 + longitud]             # tras el TFI (0xD5)

    def _comando(self, comando, ms=1000):
        self._enviar(comando)
        if not self._leer_ack():
            return None
        return self._leer_respuesta(ms)

    # ------------------------------------------- nivel alto: uso habitual
    def version_firmware(self):
        """Devuelve (version, revision) o None si el modulo no responde."""
        for _ in range(3):                            # el 1er intento lo despierta
            r = self._comando(b'\x02')                # GetFirmwareVersion
            if r and len(r) >= 5:
                return r[2], r[3]
            time.sleep_ms(100)
        return None

    def configurar(self):
        """SAMConfiguration: modo normal, imprescindible antes de leer."""
        return self._comando(b'\x14\x01\x14\x01') is not None

    def leer_uid(self, ms=1000):
        """Busca una tarjeta ISO14443-A y devuelve su UID (bytes) o None."""
        r = self._comando(b'\x4A\x01\x00', ms)        # InListPassiveTarget
        if not r or len(r) < 8 or r[1] != 1:          # r[1] = tarjetas halladas
            return None
        n = r[6]                                      # longitud del UID
        return r[7:7 + n]
