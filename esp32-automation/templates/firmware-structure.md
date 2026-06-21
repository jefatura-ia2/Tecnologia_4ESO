# Estructura de Firmware — [Nombre del Proyecto]

## Árbol de archivos

```
firmware/
├── boot.py              # WiFi + configuración de red
├── main.py              # Loop principal con uasyncio
├── config.py            # Pines, credenciales, intervalos
├── lib/
│   ├── __init__.py
│   ├── sensors.py       # Clases de sensores
│   ├── actuators.py     # Clases de actuadores
│   ├── display.py       # Driver display (si aplica)
│   └── comms.py         # MQTT/BLE (si aplica)
├── web/
│   ├── server.py        # Servidor HTTP + WebSocket
│   ├── index.html       # Dashboard (comprimido gzip)
│   ├── style.css        # Tailwind CDN
│   └── app.js           # Lógica frontend
└── utils/
    ├── logger.py        # Logging a archivo/consola
    ├── watchdog.py      # WDT + recuperación
    └── ota.py           # Actualización OTA (opcional)
```

## Dependencias MicroPython

| Librería | Fuente | Instalación |
|----------|--------|-------------|
| `uasyncio` | Built-in | — |
| `dht` | Built-in | — |
| `ssd1306` | Built-in | — |
| `neopixel` | Built-in | — |
| — | micropython-lib | `mpremote mip install [nombre]` |

## Flujo de ejecución

```
POWER ON
  │
  ├── boot.py: conectar WiFi / crear AP
  │
  └── main.py:
        ├── Inicializar sensores
        ├── Inicializar actuadores
        ├── Inicializar servidor web
        │
        └── asyncio.gather(
              sensor_loop(),      # Lee sensores cada Xms
              server.start(),     # Escucha HTTP/WS en :80
              watchdog_loop(),    # Feed WDT cada 5s
              display_loop(),     # Actualiza display cada 500ms
            )
```

## Modo test

Ejecutar en REPL para verificar componentes individualmente:

```python
# Test sensor
from lib.sensors import [SensorClass]
s = [SensorClass](pin=XX)
print(s.read())

# Test actuador
from lib.actuators import [ActuatorClass]
a = [ActuatorClass](pin=XX)
a.on()  # verificar
a.off()

# Test I2C scan
from machine import Pin, I2C
i2c = I2C(0, sda=Pin(21), scl=Pin(22))
print([hex(d) for d in i2c.scan()])
```
