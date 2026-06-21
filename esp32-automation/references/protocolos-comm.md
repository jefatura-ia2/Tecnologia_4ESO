# Protocolos de Comunicación

## WiFi — Servidor web y WebSocket

### Patrón: servidor HTTP + WebSocket async
```python
import uasyncio as asyncio
import network
import json

class WebServer:
    def __init__(self, port=80):
        self.port = port
        self.routes = {}
        self.ws_clients = set()

    def route(self, path):
        def decorator(handler):
            self.routes[path] = handler
            return handler
        return decorator

    async def handle_client(self, reader, writer):
        request_line = await reader.readline()
        method, path, _ = request_line.decode().split()
        headers = {}
        while True:
            line = await reader.readline()
            if line == b'\r\n':
                break
            key, val = line.decode().strip().split(': ', 1)
            headers[key] = val

        if 'Upgrade' in headers and headers['Upgrade'] == 'websocket':
            await self._handle_websocket(reader, writer, headers)
        elif path in self.routes:
            response = await self.routes[path](method, headers)
            writer.write(response.encode())
            await writer.drain()
        else:
            writer.write(b'HTTP/1.1 404\r\n\r\nNot Found')
            await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def broadcast_ws(self, data):
        msg = json.dumps(data)
        dead = set()
        for ws in self.ws_clients:
            try:
                await ws.send(msg)
            except:
                dead.add(ws)
        self.ws_clients -= dead

    async def start(self):
        server = await asyncio.start_server(self.handle_client, '0.0.0.0', self.port)
        print(f'Server on port {self.port}')
```

## MQTT

### Patrón: cliente MQTT con reconexión
```python
from umqtt.simple import MQTTClient
import uasyncio as asyncio

class MQTTManager:
    def __init__(self, client_id, broker, port=1883, user=None, pwd=None):
        self.client = MQTTClient(client_id, broker, port, user, pwd)
        self.subscriptions = {}
        self.connected = False

    def on_message(self, topic, msg):
        topic = topic.decode()
        if topic in self.subscriptions:
            self.subscriptions[topic](msg.decode())

    async def connect(self):
        try:
            self.client.set_callback(self.on_message)
            self.client.connect()
            for topic in self.subscriptions:
                self.client.subscribe(topic)
            self.connected = True
        except Exception as e:
            self.connected = False
            await asyncio.sleep(5)
            await self.connect()

    def subscribe(self, topic, callback):
        self.subscriptions[topic] = callback

    async def publish(self, topic, msg):
        if self.connected:
            try:
                self.client.publish(topic, msg)
            except:
                self.connected = False

    async def loop(self):
        while True:
            if self.connected:
                try:
                    self.client.check_msg()
                except:
                    self.connected = False
                    await self.connect()
            await asyncio.sleep_ms(100)
```

## I2C — Escaneo y comunicación

```python
from machine import Pin, I2C

i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
devices = i2c.scan()
print(f'Dispositivos I2C: {[hex(d) for d in devices]}')
```

## SPI — Configuración

```python
from machine import Pin, SPI

spi = SPI(2, baudrate=1000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(23), miso=Pin(19))
cs = Pin(5, Pin.OUT, value=1)
```

## Bluetooth Low Energy (BLE)

```python
import bluetooth
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

class BLEPeripheral:
    def __init__(self, name="ESP32"):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self._irq)
        self.name = name
        self.connections = set()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self.connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self.connections.discard(conn_handle)
            self._advertise()

    def _advertise(self):
        payload = bytes([0x02, 0x01, 0x06]) + \
                  bytes([len(self.name) + 1, 0x09]) + \
                  self.name.encode()
        self.ble.gap_advertise(100_000, payload)
```
