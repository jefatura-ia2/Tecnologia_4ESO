# Archivos para las placas

| Archivo | Para qué |
|---|---|
| `taller.py` | Biblioteca del banco neumático: `Electrovalvula`, `CilindroDE` (con enclavamiento), `Entrada`, `Seta`, `esperar()` y `estado_seguro()`. Detecta la placa y usa los pines del curso. Ejecútala sola para probar el cableado. Úsala a partir de la misión 10 (antes, el alumnado escribe estas clases en las misiones 6-8). |
| `pn532_i2c.py` | Librería del lector **PN532 NFC V3 por I2C** (interruptores 1 = ON, 2 = OFF): `PN532(i2c)`, `version_firmware()`, `configurar()`, `leer_uid()`, `uid_hex()`. Misión 3. Autor: José I. Sánchez Castaño. |
| `pn532_i2c_main.py` | Programa de prueba del PN532 por I2C en la Pico W (SDA GP6, SCL GP7) con indicaciones del LED. Se guarda en la placa como **`main.py`**. |
| `tira_colores.py` | Tira WS2812 de 8 LED en una **ESP32-C3 SuperMini** (DIN → IO3): verde, rojo, naranja y azul. Misión 3. |
| `pn532_uart.py` | Alternativa: el PN532 por puerto serie (modo HSU, interruptores en OFF): `PN532(uart).leer_uid()`. |
| `secretos.py` | Plantilla con el nombre y la contraseña de la WiFi (misión 11). Se sube a la placa. |

## Instalar MicroPython

- **Raspberry Pi Pico W** → https://micropython.org/download/RPI_PICO_W/
  Mantén pulsado BOOTSEL al conectar el USB y arrastra el `.uf2` a la unidad `RPI-RP2`.
- **ESP32-S3-DevKit** → https://micropython.org/download/ESP32_GENERIC_S3/
  En Thonny: *Ejecutar → Configurar intérprete → MicroPython (ESP32) → Instalar o actualizar MicroPython (esptool)*, familia ESP32-S3, puerto USB marcado UART/COM.
  Si tu placa tiene 8 MB de PSRAM (N8R8/N16R8), elige la variante **SPIRAM_OCT**.

Recomendado: MicroPython **1.22 o posterior** en ambas placas.

Todos estos archivos se publican también en la web, en `/descargas/` (enlaces dentro de las lecciones de la misión 3).
