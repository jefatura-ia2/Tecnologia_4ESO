# ESP32 — Referencia de Hardware

## Variantes soportadas

| Variante | Flash | PSRAM | WiFi | BLE | USB | Notas |
|----------|-------|-------|------|-----|-----|-------|
| ESP32-WROOM-32 | 4MB | No | 2.4GHz | 4.2 | No | Clásico, más documentación |
| ESP32-WROVER | 4MB | 8MB | 2.4GHz | 4.2 | No | PSRAM para buffers grandes |
| ESP32-S3 | 8-16MB | 2-8MB | 2.4GHz | 5.0 | Nativo | Recomendado para nuevos proyectos |
| ESP32-C3 | 4MB | No | 2.4GHz | 5.0 | Nativo | RISC-V, bajo consumo, económico |

## Pinout ESP32-WROOM-32 (DevKit v1 — 30 pines)

### Pines seguros para uso general

| GPIO | Función | Notas |
|------|---------|-------|
| 2 | Digital I/O | LED integrado en muchas placas |
| 4 | Digital I/O, ADC2_CH0 | Seguro |
| 5 | Digital I/O, VSPI_SS | Seguro, pull-up interno |
| 12 | Digital I/O, ADC2_CH5 | ⚠️ Debe estar LOW en boot |
| 13 | Digital I/O, ADC2_CH4 | Seguro |
| 14 | Digital I/O, ADC2_CH6 | Seguro |
| 15 | Digital I/O, ADC2_CH3 | ⚠️ Salida PWM en boot |
| 16 | Digital I/O, UART2_RX | Seguro |
| 17 | Digital I/O, UART2_TX | Seguro |
| 18 | Digital I/O, VSPI_CLK | Seguro |
| 19 | Digital I/O, VSPI_MISO | Seguro |
| 21 | Digital I/O, I2C_SDA | I2C por defecto |
| 22 | Digital I/O, I2C_SCL | I2C por defecto |
| 23 | Digital I/O, VSPI_MOSI | Seguro |
| 25 | Digital I/O, DAC1, ADC2_CH8 | DAC disponible |
| 26 | Digital I/O, DAC2, ADC2_CH9 | DAC disponible |
| 27 | Digital I/O, ADC2_CH7 | Seguro |
| 32 | Digital I/O, ADC1_CH4 | ADC disponible con WiFi |
| 33 | Digital I/O, ADC1_CH5 | ADC disponible con WiFi |
| 34 | Solo entrada, ADC1_CH6 | Sin pull-up/down interno |
| 35 | Solo entrada, ADC1_CH7 | Sin pull-up/down interno |
| 36 (VP) | Solo entrada, ADC1_CH0 | Sin pull-up/down interno |
| 39 (VN) | Solo entrada, ADC1_CH3 | Sin pull-up/down interno |

### Pines a evitar

| GPIO | Razón |
|------|-------|
| 0 | Boot mode — pull-up, no usar como entrada |
| 1 | TX0 — consola serial |
| 3 | RX0 — consola serial |
| 6-11 | Conectados a flash SPI — NO USAR |

### Buses de comunicación

| Bus | Pines por defecto | Notas |
|-----|-------------------|-------|
| I2C | SDA=21, SCL=22 | Reasignable a cualquier GPIO |
| SPI (VSPI) | CLK=18, MISO=19, MOSI=23, SS=5 | Bus principal |
| SPI (HSPI) | CLK=14, MISO=12, MOSI=13, SS=15 | Bus secundario |
| UART0 | TX=1, RX=3 | Consola — no usar |
| UART1 | TX=10, RX=9 | ⚠️ Conflicto con flash |
| UART2 | TX=17, RX=16 | Libre para uso |

### Capacidades analógicas

- **ADC1** (GPIOs 32-39): funciona con WiFi activo, resolución 12-bit
- **ADC2** (GPIOs 0,2,4,12-15,25-27): NO funciona con WiFi activo
- **DAC**: GPIO 25 (DAC1) y GPIO 26 (DAC2), 8-bit
- **Canales PWM**: 16 canales independientes, cualquier GPIO de salida
- **Touch**: GPIOs 0,2,4,12-15,27,32,33 — sensores capacitivos

### Límites eléctricos

| Parámetro | Valor |
|-----------|-------|
| Voltaje de operación | 3.3V |
| Corriente máx por GPIO | 40mA (recomendado 20mA) |
| Corriente máx total GPIOs | 1200mA |
| Voltaje entrada máx GPIO | 3.3V (NO tolerante a 5V) |
| Consumo típico WiFi activo | 80-160mA |
| Consumo deep sleep | 10µA |
| Alimentación VIN | 5V (regulador onboard) |

### Consideraciones de diseño

- **Level shifting**: necesario para módulos de 5V (usar divisor resistivo o módulo bidireccional)
- **Decoupling**: capacitor 100nF cerca de VCC de cada módulo
- **Pull-ups I2C**: 4.7kΩ a 3.3V si no están en el módulo
- **Antena WiFi**: no colocar plano de tierra bajo la antena PCB
- **Reset**: capacitor 100nF entre EN y GND para filtrar ruido
