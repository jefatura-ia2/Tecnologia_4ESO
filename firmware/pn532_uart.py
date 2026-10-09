# pn532_uart.py — Controlador mínimo del PN532 NFC RFID Module V3 por puerto serie (modo HSU)
# TEC_IVJP_lab27 · 4º ESO. Funciona en Raspberry Pi Pico W y ESP32-S3 con MicroPython.
#
# Interruptores del módulo en HSU: SEL0 = OFF, SEL1 = OFF (cámbialos sin alimentación).
# Conexión:  VCC→3V3 · GND→GND · SDA/TXD→RX de la placa · SCL/RXD→TX de la placa
#   Pico W:   UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
#   ESP32-S3: UART(1, baudrate=115200, tx=10, rx=11)
#
# Uso:
#   from pn532_uart import PN532
#   nfc = PN532(uart)
#   uid = nfc.leer_uid()      # bytes con el UID, o None si no hay tarjeta
import time

ACK = b"\x00\x00\xff\x00\xff\x00"


class PN532:
    def __init__(self, uart):
        self.uart = uart
        self._despertar()
        # SAMConfiguration: modo normal, sin tiempo límite, con IRQ
        if self._comando(0x14, [0x01, 0x14, 0x01]) is None:
            raise OSError("El PN532 no responde: revisa cables (TX↔RX), alimentación e interruptores en HSU")
        # RFConfiguration: reintentos limitados para que leer_uid() no se quede esperando
        self._comando(0x32, [0x05, 0xFF, 0x01, 0x02])

    def _despertar(self):
        # En modo HSU el PN532 se despierta con un preámbulo largo
        self.uart.write(b"\x55\x55" + b"\x00" * 14)
        time.sleep_ms(50)
        while self.uart.any():
            self.uart.read()

    @staticmethod
    def _trama(datos):
        n = len(datos)
        lcs = (256 - n) % 256
        dcs = (256 - sum(datos) % 256) % 256
        return bytes([0x00, 0x00, 0xFF, n, lcs] + datos + [dcs, 0x00])

    def _leer(self, n, timeout_ms):
        buf = b""
        t0 = time.ticks_ms()
        while len(buf) < n and time.ticks_diff(time.ticks_ms(), t0) < timeout_ms:
            if self.uart.any():
                trozo = self.uart.read(n - len(buf))
                if trozo:
                    buf += trozo
            else:
                time.sleep_ms(2)
        return buf

    def _comando(self, cmd, parametros=(), timeout_ms=500):
        self.uart.write(self._trama([0xD4, cmd] + list(parametros)))
        if self._leer(6, 100) != ACK:
            return None
        cab = self._leer(5, timeout_ms)                 # 00 00 FF LEN LCS
        if len(cab) < 5 or cab[2] != 0xFF or (cab[3] + cab[4]) % 256:
            return None
        n = cab[3]
        resto = self._leer(n + 2, timeout_ms)           # datos + DCS + 00
        if len(resto) < n + 1:
            return None
        datos = resto[:n]
        if (sum(datos) + resto[n]) % 256 or datos[0] != 0xD5 or datos[1] != cmd + 1:
            return None
        return datos[2:]

    def version(self):
        r = self._comando(0x02)
        if not r:
            return None
        return "PN5%02X v%d.%d" % (r[0], r[1], r[2])

    def leer_uid(self, timeout_ms=500):
        """Devuelve el UID (bytes) de la tarjeta que haya cerca, o None."""
        r = self._comando(0x4A, [0x01, 0x00], timeout_ms)   # InListPassiveTarget, 106 kbps tipo A
        if not r or r[0] < 1:
            return None
        n = r[5]
        return bytes(r[6:6 + n])
