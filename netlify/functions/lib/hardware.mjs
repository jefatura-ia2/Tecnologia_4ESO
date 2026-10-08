export const HARDWARE = [
  {
    id: 'pico_w', name: 'Raspberry Pi Pico W', chip: 'RP2040 · 2 núcleos Cortex-M0+ a 133 MHz',
    ram: '264 KB', flash: '2 MB', wifi: 'Sí (CYW43439, 2,4 GHz)',
    bluetooth: 'BLE en el chip CYW43439 (MicroPython ≥ 1.20); el curso usa BLE sobre todo con la ESP32-S3',
    usb: 'Micro-USB', adc: '3 canales de 12 bits: GPIO 26, 27, 28 (+ sensor de temperatura interno)',
    led: 'Pin("LED") — conectado al chip WiFi', button: 'BOOTSEL (solo para cargar firmware)',
    ml: 'GPIO a 3,3 V y máx. ~12 mA por pin: las electroválvulas de 12 V se mandan siempre a través de un módulo MOSFET',
    spi: 'Electroválvulas EV1-EV4: GP10-GP13 · Finales de carrera: GP18-GP21',
    firmware: 'https://micropython.org/download/RPI_PICO_W/',
  },
  {
    id: 'esp32_s3', name: 'ESP32-S3-DevKit', chip: 'ESP32-S3-WROOM-1 · 2 núcleos Xtensa LX7 a 240 MHz',
    ram: '512 KB (+ PSRAM según modelo)', flash: '8-16 MB', wifi: 'Sí (802.11 b/g/n, 2,4 GHz)',
    bluetooth: 'BLE 5.0', usb: 'USB-C doble (UART + USB-OTG nativo)',
    adc: '20 canales de 12 bits (ADC1: GPIO 1-10 · ADC2: GPIO 11-20; ADC2 no funciona con WiFi activo)',
    led: 'LED RGB direccionable (WS2812) en GPIO 48 (GPIO 38 en algunas revisiones v1.1)',
    button: 'BOOT (GPIO 0); algunas placas incluyen KEY en IO45',
    ml: 'GPIO a 3,3 V (máx. ~20-40 mA por pin): las electroválvulas de 12 V se mandan siempre a través de un módulo MOSFET',
    spi: 'Electroválvulas EV1-EV4: GPIO 4-7 · Finales de carrera: GPIO 17, 18, 8, 9',
    firmware: 'https://micropython.org/download/ESP32_GENERIC_S3/',
  },
]
