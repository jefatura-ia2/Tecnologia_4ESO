# Módulos — Actuadores

Referencia de actuadores y módulos de salida para ESP32 + MicroPython.

## Relés

| Módulo | Canales | Voltaje bobina | Carga máx | Trigger | Notas |
|--------|---------|----------------|-----------|---------|-------|
| Relé 5V SRD-05VDC | 1/2/4/8 | 5V | 10A@250VAC | LOW activo | Necesita 5V externo |
| Relé 3.3V | 1/2 | 3.3V | 10A@250VAC | LOW activo | Directo desde ESP32 |
| SSR (estado sólido) | 1 | 3-32VDC | 2-40A@AC | HIGH activo | Sin partes mecánicas |
| MOSFET IRF520 | 1 | 3.3-5V | 24V/5A | HIGH activo | Solo DC, PWM compatible |

### Conexión relé 5V con optoacoplador
```
ESP32 GPIO26 ──── IN1 (activo LOW)
ESP32 GND    ──── GND
5V externo   ──── VCC
             ──── JD-VCC (alimenta bobina independiente)
```

⚠️ **Seguridad**: siempre usar relé con optoacoplador para aislar ESP32 de alta tensión.

## Motores DC

| Driver | Voltaje motor | Corriente máx | Canales | PWM | Notas |
|--------|--------------|---------------|---------|-----|-------|
| L298N | 5-35V | 2A/canal | 2 | Sí | Clásico, ineficiente |
| TB6612FNG | 2.5-13.5V | 1.2A/canal | 2 | Sí | Eficiente, recomendado |
| L293D | 4.5-36V | 600mA/canal | 2 | Sí | Económico |
| BTS7960 | 5.5-27V | 43A | 1 | Sí | Alta potencia |
| DRV8833 | 2.7-10.8V | 1.5A/canal | 2 | Sí | Compacto |

### Conexión TB6612FNG
```
ESP32 GPIO25 ──── AIN1     ESP32 GPIO14 ──── BIN1
ESP32 GPIO26 ──── AIN2     ESP32 GPIO27 ──── BIN2
ESP32 GPIO32 ──── PWMA     ESP32 GPIO33 ──── PWMB
ESP32 GPIO13 ──── STBY (HIGH = activo)
ESP32 3.3V   ──── VCC
Motor VCC    ──── VM (5-13.5V)
GND común    ──── GND
```

## Servomotores

| Tipo | Ángulo | Torque | Voltaje | Señal |
|------|--------|--------|---------|-------|
| SG90 | 0-180° | 1.8kg·cm | 4.8-6V | PWM 50Hz |
| MG996R | 0-180° | 11kg·cm | 4.8-7.2V | PWM 50Hz |
| MG90S | 0-180° | 2.2kg·cm | 4.8-6V | PWM 50Hz (metal) |
| Servo continuo | 360° | Variable | 4.8-6V | PWM 50Hz |

### Control PWM servo en MicroPython
```python
from machine import Pin, PWM
servo = PWM(Pin(15), freq=50)
# duty: 26 (0°) — 51 (90°) — 77 (180°) para 10-bit
# duty_ns: 500000 (0°) — 1500000 (90°) — 2500000 (180°)
servo.duty_ns(1500000)  # Centro (90°)
```

⚠️ Alimentar servos desde fuente externa, nunca desde 3.3V del ESP32.

## Motores paso a paso (Stepper)

| Driver | Voltaje | Corriente | Microstepping | Notas |
|--------|---------|-----------|---------------|-------|
| A4988 | 8-35V | 2A | 1/2/4/8/16 | Estándar para impresoras 3D |
| DRV8825 | 8.2-45V | 2.5A | Hasta 1/32 | Mayor resolución |
| TMC2209 | 4.75-28V | 2A | Hasta 1/256 | Silencioso (StealthChop) |
| ULN2003 | 5-12V | 500mA | Onda completa | Para 28BYJ-48 |

### Conexión A4988
```
ESP32 GPIO16 ──── STEP
ESP32 GPIO17 ──── DIR
ESP32 GPIO5  ──── ENABLE (LOW = activo)
VCC lógica   ──── VDD (3.3V)
Motor VCC    ──── VMOT (8-35V)
GND común    ──── GND
Capacitor 100µF electrolítico entre VMOT y GND
```

## Displays

| Módulo | Interface | Resolución | Color | Librería |
|--------|-----------|------------|-------|----------|
| SSD1306 OLED | I2C/SPI | 128x64 | Mono | `ssd1306` (builtin) |
| SH1106 OLED | I2C/SPI | 128x64 | Mono | `sh1106` |
| ST7789 TFT | SPI | 240x240 / 240x320 | 65K | `st7789` |
| ILI9341 TFT | SPI | 320x240 | 65K | `ili9341` |
| LCD 16x2 I2C | I2C (PCF8574) | 16x2 chars | Mono | `lcd_i2c` |
| MAX7219 matriz LED | SPI | 8x8 por módulo | Mono | `max7219` |
| NeoPixel WS2812B | 1-Wire | — | RGB | `neopixel` (builtin) |

### Conexión SSD1306 OLED I2C
```
ESP32 GPIO21 (SDA) ──── SDA
ESP32 GPIO22 (SCL) ──── SCL
ESP32 3.3V         ──── VCC
ESP32 GND          ──── GND
Dirección: 0x3C (por defecto)
```

## Sonido

| Módulo | Interface | Voltaje | Notas |
|--------|-----------|---------|-------|
| Buzzer activo | Digital | 3.3-5V | Tono fijo, solo ON/OFF |
| Buzzer pasivo | PWM | 3.3-5V | Frecuencia variable |
| DFPlayer Mini | UART | 3.3-5V | Reproduce MP3 desde SD |
| MAX98357A I2S | I2S | 3.3V | Amplificador 3W |

## Comunicación

| Módulo | Interface | Voltaje | Protocolo | Librería |
|--------|-----------|---------|-----------|----------|
| MCP2515 | SPI | 5V | CAN Bus | `mcp2515` |
| MAX485 | UART | 5V | RS-485 | UART directo |
| nRF24L01 | SPI | 3.3V | 2.4GHz propietario | `nrf24l01` |
| LoRa SX1276/78 | SPI | 3.3V | LoRa | `sx127x` |
| GPS NEO-6M | UART | 3.3-5V | NMEA | `micropyGPS` |
