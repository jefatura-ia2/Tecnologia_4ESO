# Módulos — Sensores

Referencia rápida de sensores compatibles con ESP32 + MicroPython.

## Temperatura y humedad

| Módulo | Interface | Voltaje | Rango | Precisión | Librería MicroPython |
|--------|-----------|---------|-------|-----------|---------------------|
| DHT11 | 1-Wire | 3.3-5V | 0-50°C, 20-80%RH | ±2°C, ±5%RH | `dht` (builtin) |
| DHT22 | 1-Wire | 3.3-5V | -40-80°C, 0-100%RH | ±0.5°C, ±2%RH | `dht` (builtin) |
| BME280 | I2C/SPI | 3.3V | -40-85°C, 0-100%RH, 300-1100hPa | ±1°C, ±3%RH | `bme280` |
| DS18B20 | 1-Wire | 3.3-5V | -55-125°C | ±0.5°C | `ds18x20` (builtin) |
| SHT31 | I2C | 3.3V | -40-125°C, 0-100%RH | ±0.3°C, ±2%RH | `sht31` |

### Conexión típica DHT22
```
ESP32 GPIO4 ──── DATA (pull-up 4.7kΩ a 3.3V)
ESP32 3.3V  ──── VCC
ESP32 GND   ──── GND
```

### Conexión típica BME280 (I2C)
```
ESP32 GPIO21 (SDA) ──── SDA
ESP32 GPIO22 (SCL) ──── SCL
ESP32 3.3V         ──── VCC
ESP32 GND          ──── GND
Dirección I2C: 0x76 (SDO→GND) o 0x77 (SDO→VCC)
```

## Distancia y presencia

| Módulo | Interface | Voltaje | Rango | Precisión | Librería |
|--------|-----------|---------|-------|-----------|----------|
| HC-SR04 | Trigger/Echo | 5V | 2-400cm | ±3mm | `hcsr04` |
| VL53L0X | I2C | 3.3-5V | 3-200cm | ±3% | `vl53l0x` |
| PIR HC-SR501 | Digital | 5V | 3-7m | — | GPIO directo |
| Sharp GP2Y0A21 | Analógico | 5V | 10-80cm | ±5% | ADC directo |

### Conexión HC-SR04 (requiere level shifter para Echo)
```
ESP32 GPIO5  ──── TRIG
ESP32 GPIO18 ──── ECHO (divisor: 1kΩ + 2kΩ para 3.3V)
5V           ──── VCC
GND          ──── GND
```

## Luz y color

| Módulo | Interface | Voltaje | Rango | Librería |
|--------|-----------|---------|-------|----------|
| BH1750 | I2C | 3.3-5V | 1-65535 lux | `bh1750` |
| LDR (fotoresistencia) | Analógico | 3.3V | Variable | ADC directo |
| TCS34725 | I2C | 3.3V | RGB + Clear | `tcs34725` |

## Movimiento e inercia

| Módulo | Interface | Voltaje | Ejes | Librería |
|--------|-----------|---------|------|----------|
| MPU6050 | I2C | 3.3V | 6 DOF (accel+gyro) | `mpu6050` |
| MPU9250 | I2C/SPI | 3.3V | 9 DOF (+mag) | `mpu9250` |
| ADXL345 | I2C/SPI | 3.3V | 3-axis accel | `adxl345` |

### Conexión MPU6050 (I2C)
```
ESP32 GPIO21 (SDA) ──── SDA
ESP32 GPIO22 (SCL) ──── SCL
ESP32 3.3V         ──── VCC
ESP32 GND          ──── GND
AD0                ──── GND (dirección 0x68) o VCC (0x69)
```

## Gas y calidad de aire

| Módulo | Interface | Voltaje | Detecta | Librería |
|--------|-----------|---------|---------|----------|
| MQ-2 | Analógico | 5V | GLP, metano, humo | ADC + calibración |
| MQ-135 | Analógico | 5V | CO2, NH3, benceno | ADC + calibración |
| CCS811 | I2C | 3.3V | eCO2, TVOC | `ccs811` |
| SGP30 | I2C | 3.3V | eCO2, TVOC | `sgp30` |

## Corriente y voltaje

| Módulo | Interface | Voltaje | Rango | Librería |
|--------|-----------|---------|-------|----------|
| INA219 | I2C | 3.3-5V | ±3.2A, 0-26V | `ina219` |
| ACS712 | Analógico | 5V | ±5/20/30A | ADC + calibración |
| ZMPT101B | Analógico | 5V | AC 0-250V | ADC + calibración |

## Peso y fuerza

| Módulo | Interface | Voltaje | Rango | Librería |
|--------|-----------|---------|-------|----------|
| HX711 + celda de carga | Digital (CLK+DATA) | 5V | Según celda | `hx711` |
| FSR402 | Analógico | 3.3V | 0-10kg | ADC + divisor |

## Agua y suelo

| Módulo | Interface | Voltaje | Detecta | Librería |
|--------|-----------|---------|---------|----------|
| Sensor humedad suelo | Analógico | 3.3-5V | Humedad suelo | ADC directo |
| Sensor nivel de agua | Analógico | 3.3-5V | Nivel líquido | ADC directo |
| Sensor flujo YF-S201 | Digital (pulsos) | 5V | Caudal 1-30L/min | Interrupción |
