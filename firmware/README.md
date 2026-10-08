# Archivos para las placas

| Archivo | Para qué |
|---|---|
| `taller.py` | Biblioteca del banco neumático: `Electrovalvula`, `CilindroDE` (con enclavamiento), `Entrada`, `Seta`, `esperar()` y `estado_seguro()`. Detecta la placa y usa los pines del curso. Ejecútala sola para probar el cableado. Úsala a partir de la misión 9 (antes, el alumnado escribe estas clases en las misiones 5-7). |
| `secretos.py` | Plantilla con el nombre y la contraseña de la WiFi (misión 10). Se sube a la placa. |

## Instalar MicroPython

- **Raspberry Pi Pico W** → https://micropython.org/download/RPI_PICO_W/
  Mantén pulsado BOOTSEL al conectar el USB y arrastra el `.uf2` a la unidad `RPI-RP2`.
- **ESP32-S3-DevKit** → https://micropython.org/download/ESP32_GENERIC_S3/
  En Thonny: *Ejecutar → Configurar intérprete → MicroPython (ESP32) → Instalar o actualizar MicroPython (esptool)*, familia ESP32-S3, puerto USB marcado UART/COM.
  Si tu placa tiene 8 MB de PSRAM (N8R8/N16R8), elige la variante **SPIRAM_OCT**.

Recomendado: MicroPython **1.22 o posterior** en ambas placas.
