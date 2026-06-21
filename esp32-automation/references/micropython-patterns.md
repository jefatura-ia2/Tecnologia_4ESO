# MicroPython — Patrones y Buenas Prácticas

## Estructura base de proyecto

```python
# config.py — Configuración centralizada
from micropython import const

# === Pines ===
PIN_LED = const(2)
PIN_RELAY = const(26)
PIN_DHT = const(4)
PIN_SDA = const(21)
PIN_SCL = const(22)

# === WiFi ===
WIFI_SSID = "MiRed"
WIFI_PASS = "MiClave"
WIFI_AP_SSID = "ESP32-Config"
WIFI_AP_PASS = "12345678"

# === MQTT ===
MQTT_BROKER = "192.168.1.100"
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = "casa/salon"

# === Intervalos (ms) ===
SENSOR_INTERVAL = const(2000)
DISPLAY_INTERVAL = const(500)
WS_BROADCAST_INTERVAL = const(1000)
WATCHDOG_TIMEOUT = const(30000)
```

## Patrón: boot.py con WiFi + fallback AP

```python
# boot.py
import network
import time
from config import WIFI_SSID, WIFI_PASS, WIFI_AP_SSID, WIFI_AP_PASS

def connect_wifi():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if sta.isconnected():
        return sta.ifconfig()[0]
    sta.connect(WIFI_SSID, WIFI_PASS)
    for _ in range(20):  # 10 segundos timeout
        if sta.isconnected():
            print(f'WiFi conectado: {sta.ifconfig()[0]}')
            return sta.ifconfig()[0]
        time.sleep(0.5)
    # Fallback: modo AP
    sta.active(False)
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=WIFI_AP_SSID, password=WIFI_AP_PASS,
              authmode=network.AUTH_WPA2_PSK)
    print(f'AP mode: {ap.ifconfig()[0]}')
    return ap.ifconfig()[0]

ip = connect_wifi()
```

## Patrón: main.py con uasyncio

```python
# main.py
import uasyncio as asyncio
from machine import Pin, WDT
from config import *

# Importar módulos del proyecto
from lib.sensors import SensorManager
from lib.actuators import ActuatorManager
from web.server import WebServer

async def sensor_loop(sensors, server):
    """Lee sensores y broadcast por WebSocket."""
    while True:
        data = sensors.read_all()
        await server.broadcast_ws(data)
        await asyncio.sleep_ms(SENSOR_INTERVAL)

async def watchdog_loop(wdt):
    """Alimenta el watchdog periódicamente."""
    while True:
        wdt.feed()
        await asyncio.sleep_ms(5000)

async def main():
    # Watchdog: reinicia si se cuelga > 30s
    wdt = WDT(timeout=WATCHDOG_TIMEOUT)

    sensors = SensorManager()
    actuators = ActuatorManager()
    server = WebServer(port=80)

    # Registrar rutas
    server.register_routes(sensors, actuators)

    # Lanzar tareas concurrentes
    await asyncio.gather(
        server.start(),
        sensor_loop(sensors, server),
        watchdog_loop(wdt),
    )

try:
    asyncio.run(main())
except Exception as e:
    print(f'Error fatal: {e}')
    import machine
    machine.reset()
```

## Patrón: clase sensor reutilizable

```python
# lib/sensors.py
from machine import Pin, ADC, I2C
import dht
import time

class SensorBase:
    """Clase base para todos los sensores."""
    def __init__(self, name, unit):
        self.name = name
        self.unit = unit
        self.last_value = None
        self.last_read = 0
        self.error_count = 0

    def read(self):
        raise NotImplementedError

    def safe_read(self):
        try:
            self.last_value = self.read()
            self.error_count = 0
            self.last_read = time.ticks_ms()
            return self.last_value
        except Exception as e:
            self.error_count += 1
            print(f'Error {self.name}: {e} (x{self.error_count})')
            return self.last_value  # Devuelve último valor válido

    def to_dict(self):
        return {
            'name': self.name,
            'value': self.last_value,
            'unit': self.unit,
            'age_ms': time.ticks_diff(time.ticks_ms(), self.last_read)
        }


class DHTSensor(SensorBase):
    def __init__(self, pin, model=22):
        super().__init__('DHT' + str(model), '°C/%RH')
        Sensor = dht.DHT22 if model == 22 else dht.DHT11
        self.sensor = Sensor(Pin(pin))

    def read(self):
        self.sensor.measure()
        return {
            'temperature': self.sensor.temperature(),
            'humidity': self.sensor.humidity()
        }


class AnalogSensor(SensorBase):
    def __init__(self, pin, name, unit, min_val=0, max_val=100):
        super().__init__(name, unit)
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)  # 0-3.3V
        self.min_val = min_val
        self.max_val = max_val

    def read(self):
        raw = self.adc.read()  # 0-4095
        return self.min_val + (raw / 4095) * (self.max_val - self.min_val)


class SensorManager:
    def __init__(self):
        self.sensors = {}

    def add(self, sensor_id, sensor):
        self.sensors[sensor_id] = sensor

    def read_all(self):
        return {sid: s.safe_read() for sid, s in self.sensors.items()}

    def to_dict(self):
        return {sid: s.to_dict() for sid, s in self.sensors.items()}
```

## Patrón: clase actuador

```python
# lib/actuators.py
from machine import Pin, PWM

class Relay:
    def __init__(self, pin, active_low=True):
        self.pin = Pin(pin, Pin.OUT)
        self.active_low = active_low
        self.state = False
        self.off()

    def on(self):
        self.pin.value(0 if self.active_low else 1)
        self.state = True

    def off(self):
        self.pin.value(1 if self.active_low else 0)
        self.state = False

    def toggle(self):
        self.on() if not self.state else self.off()


class ServoMotor:
    def __init__(self, pin, min_us=500, max_us=2500):
        self.pwm = PWM(Pin(pin), freq=50)
        self.min_us = min_us
        self.max_us = max_us
        self.angle = 90
        self.set_angle(90)

    def set_angle(self, angle):
        angle = max(0, min(180, angle))
        self.angle = angle
        us = self.min_us + (angle / 180) * (self.max_us - self.min_us)
        self.pwm.duty_ns(int(us * 1000))

    def detach(self):
        self.pwm.deinit()


class MotorDC:
    def __init__(self, pin_in1, pin_in2, pin_pwm, freq=1000):
        self.in1 = Pin(pin_in1, Pin.OUT)
        self.in2 = Pin(pin_in2, Pin.OUT)
        self.pwm = PWM(Pin(pin_pwm), freq=freq)
        self.speed = 0
        self.stop()

    def forward(self, speed=100):
        self.in1.value(1)
        self.in2.value(0)
        self.speed = max(0, min(100, speed))
        self.pwm.duty(int(self.speed * 1023 / 100))

    def reverse(self, speed=100):
        self.in1.value(0)
        self.in2.value(1)
        self.speed = max(0, min(100, speed))
        self.pwm.duty(int(self.speed * 1023 / 100))

    def stop(self):
        self.in1.value(0)
        self.in2.value(0)
        self.pwm.duty(0)
        self.speed = 0


class ActuatorManager:
    def __init__(self):
        self.actuators = {}

    def add(self, act_id, actuator):
        self.actuators[act_id] = actuator

    def execute(self, act_id, action, **kwargs):
        if act_id in self.actuators:
            method = getattr(self.actuators[act_id], action, None)
            if method:
                return method(**kwargs)
        return None
```

## Patrón: OTA (actualización over-the-air)

```python
import urequests
import os

OTA_URL = "http://mi-servidor.local/firmware/"

def check_update(current_version):
    try:
        r = urequests.get(OTA_URL + "version.json")
        info = r.json()
        r.close()
        if info['version'] > current_version:
            return info
    except:
        pass
    return None

def download_file(filename):
    r = urequests.get(OTA_URL + filename)
    with open(filename, 'w') as f:
        f.write(r.text)
    r.close()

def apply_update(file_list):
    for f in file_list:
        download_file(f)
    import machine
    machine.reset()
```

## Patrón: deep sleep con wake-up

```python
import machine
import esp32

# Wake-up por timer (30 minutos)
machine.deepsleep(30 * 60 * 1000)

# Wake-up por GPIO (ej: PIR sensor en GPIO33)
esp32.wake_on_ext0(pin=machine.Pin(33), level=esp32.WAKEUP_ANY_HIGH)
machine.deepsleep()

# Detectar causa del despertar
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('Desperté de deep sleep')
```
