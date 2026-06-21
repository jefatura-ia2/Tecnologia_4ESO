# Diagrama de Cableado — [Nombre del Proyecto]

## Alimentación

```
[Fuente 5V] ──── VIN (ESP32)
                 GND (ESP32) ──── GND común
                 3.3V (ESP32) ──── VCC módulos 3.3V
```

⚠️ **Regla**: todos los GND deben estar conectados (GND común).

## Bus I2C

```
ESP32 GPIO21 (SDA) ──┬── [Módulo 1] SDA
                     ├── [Módulo 2] SDA
                     └── Pull-up 4.7kΩ ── 3.3V

ESP32 GPIO22 (SCL) ──┬── [Módulo 1] SCL
                     ├── [Módulo 2] SCL
                     └── Pull-up 4.7kΩ ── 3.3V

Direcciones I2C:
- Módulo 1: 0x__
- Módulo 2: 0x__
```

## Sensores

```
ESP32 GPIO__ ──── [Sensor] DATA/OUT
3.3V/5V     ──── [Sensor] VCC
GND         ──── [Sensor] GND
Notas: [pull-up, divisor resistivo, etc.]
```

## Actuadores

```
ESP32 GPIO__ ──── [Driver/Relé] IN
[Fuente]     ──── [Driver/Relé] VCC
GND común    ──── [Driver/Relé] GND
[Driver OUT] ──── [Actuador]
```

## Display

```
ESP32 GPIO21 (SDA) ──── SDA
ESP32 GPIO22 (SCL) ──── SCL
3.3V              ──── VCC
GND               ──── GND
```

## Tabla resumen de conexiones

| ESP32 GPIO | Dirección | Componente | Pin | Cable color |
|-----------|-----------|-----------|-----|-------------|
| — | — | — | — | — |

## Notas importantes

1. **Level shifting**: [componentes que necesitan 5V → 3.3V]
2. **Capacitores de desacople**: 100nF cerámico en VCC de cada módulo
3. **Protección**: [fusible, diodo, TVS según aplique]
4. **Consumo total**: [cálculo de corriente]
