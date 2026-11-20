# 🪧 Smart Sign IoT · Guía del profesor

Proyecto de las **misiones 4, 5 y 6** de TEC_IVJP_lab27 (semanas 10-18, primer trimestre, después del
control de acceso NFC). El alumnado trabaja como un equipo de producto ágil: un cartel de aula de metacrilato
iluminado por el canto, con batería, que el profesor controla desde un panel web del servidor del instituto.

| Fase | Misión · semanas | Contenido |
|---|---|---|
| Sprint 1 · dos equipos en paralelo | M4 · 10-12 | **Equipo A** (mecánica): CAD, tolerancias, impresión 3D · **Equipo B** (electrónica): energía, PCB, LED y deepsleep · Sprint Review |
| Hito de integración + Sprint 2 | M5 · 13-15 | Cartel autónomo (uniformidad ≥ 0,7, ≥ 8 h de batería) · Mosquitto 1883/9001 · MQTT en la ESP32-C3 · panel del profesor |
| Sprint 3 + Sprint 4 | M6 · 16-18 | Investigación de campo · PIR y BH1750 · PCB v2 · topics `aula/{id}/status` · panel del pasillo · demo final |

> El backlog original del proyecto tiene 10 semanas; aquí ocupa **9** (Sprint 3 y Sprint 4 comparten la misión 6).

## Archivos de esta carpeta

| Archivo | Qué es |
|---|---|
| `marco_cartel.scad` | Modelo **paramétrico** de OpenSCAD: soporte de pared, tapa, capuchón y probeta de tolerancias (variable `pieza`) |
| `stl/*.stl` | Las cuatro piezas ya exportadas con metacrilato de 5 mm y holgura de 0,2 mm |
| `mosquitto.conf` | Configuración del broker: 1883 (TCP, carteles) y 9001 (WebSockets, panel) con contraseña |
| `panel_profesor.html` | Panel del profesor (React + mqtt.js en un solo archivo). Modo pasillo: varias aulas separadas por comas |
| `../firmware/cartel_mqtt.py` | Programa del cartel para la ESP32-C3 SuperMini (se guarda como `main.py`) |

Todo se descarga también desde la app: `/descargas/smart_sign/…` y `/descargas/cartel_mqtt.py`.

## A. Organización de los equipos (Sprint 1)

- Grupos de 4-6: la mitad en el **Equipo A** (mecánica) y la otra mitad en el **Equipo B** (electrónica).
- **Rotación de roles** semanal: uno o dos miembros cambian de equipo cada semana para que todos aprendan las dos
  disciplinas. Se anota en el Kanban.
- **Daily Scrum** de 5 minutos al empezar cada sesión. Pregunta clave del Equipo A al B: *«¿Las medidas de la caja
  son las correctas para que quepa la batería?»*. Las respuestas actualizan el **contrato de medidas** del README.
- Repositorio en GitHub por grupo con README, tablero (GitHub Projects o papel fotografiado) y fotos de cada demo.

## B. Impresoras 3D

| Impresora | Volumen | Uso en el proyecto |
|---|---|---|
| **Bambu Lab A1** | 256 × 256 × 256 mm | Probeta de tolerancias (≈ 10 min), soporte con la ranura, tapa y capuchón. Caben 2-3 iteraciones por sesión |
| **Artillery Sidewinder X1** | 300 × 300 × 400 mm | Piezas grandes, versiones en **PETG** (resiste ≈ 80 °C frente a ≈ 60 °C del PLA) o lotes mientras la A1 está ocupada |

Parámetros: capa 0,2 mm (0,12 en la probeta), 4 perímetros, relleno 15-20 % giroide, soporte con la ranura hacia
arriba y sin soportes (el hueco del USB-C tiene techo en punta). Soporte ≈ 40 cm³ ≈ 50 g de PLA.

**Tolerancias**: el metacrilato «de 5 mm» suele medir entre 4,8 y 5,3 mm. Que cada grupo mida el suyo e imprima la
probeta (ranuras 5,0 · 5,1 · 5,2 · 5,3 · 5,4 mm) antes de imprimir el soporte. Juego correcto: 0,1-0,4 mm.

## C. Electrónica y energía

- ESP32-C3 SuperMini: tira WS2812 en **IO3** (IO8 es pin de arranque y lleva el LED de la placa; el código base del
  proyecto usaba `Pin(8)`). PIR en IO4; BH1750 por I2C en IO5 (SDA) / IO6 (SCL), dirección 0x23.
- **Ajustar el MT3608 a 5,0 V antes de conectar la placa** (suele venir a otra tensión).
- TP4056 **con protección** (DW01, salidas OUT+/OUT−). Polímetro siempre en serie para medir corriente.
- MicroPython no tiene `np.brightness`: el brillo se aplica escalando el color.
- Cada WS2812 consume ≈ 1 mA aunque esté apagado: en la PCB v2, MOSFET de canal P para cortar la tira.

## D. Servidor (Sprint 2)

```bash
sudo apt install mosquitto mosquitto-clients nginx
sudo cp mosquitto.conf /etc/mosquitto/conf.d/smart_sign.conf
sudo mosquitto_passwd -c /etc/mosquitto/passwd cartel
sudo mosquitto_passwd /etc/mosquitto/passwd panel
sudo systemctl restart mosquitto
sudo ufw allow from 192.168.0.0/16 to any port 1883 proto tcp
sudo ufw allow from 192.168.0.0/16 to any port 9001 proto tcp
sudo cp panel_profesor.html /var/www/html/index.html     # el profesor abre http://IP-del-servidor/
```

- Los carteles se conectan al **1883** (TCP) y el panel al **9001** (WebSockets). Si el router o el cortafuegos del
  centro bloquean esos puertos, pide al administrador de red que los abra **solo para la LAN**.
- El panel **no** se publica en Netlify: una página `https://` no puede abrir `ws://` (contenido mixto) y el broker
  no es accesible desde Internet. Para notificaciones push reales hay que servir el panel por HTTPS y usar `wss://`.
- Prueba rápida: `mosquitto_sub -h IP -u cartel -P *** -t 'aula/#' -v` y
  `mosquitto_pub -h IP -u panel -P *** -t aula/203/status -m rojo -r`.

## E. Evaluación (rúbrica ágil del proyecto)

| Criterio | Peso | Descripción |
|---|---|---|
| Trabajo en paralelo (Sprint 1) | 20 % | Coordinación entre equipos, cumplimiento del Sprint Goal, calidad de la mecánica o la electrónica |
| Hito de integración | 15 % | El cartel ensamblado funciona con batería y los LED iluminan correctamente |
| Conexión y software (Sprint 2) | 25 % | Mosquitto 1883/9001, despliegue del panel y comunicación con la ESP32 por MQTT |
| Investigación y sensores | 15 % | Calidad de los datos de campo y justificación del rediseño (PCB v2 y lógica de sensores) |
| Metodología ágil y documentación | 25 % | Kanban, Dailys, Sprint Reviews y README en GitHub |

La app evalúa además cada sección (ejercicios autocorregidos + foto obligatoria del montaje en las secciones de taller).

## F. Variante: letrero tipo bandera (carril + pieza de pared)

Diseño alternativo para el pasillo: carril de 200 mm con letras, dos placas WS2812 de 8 LED tras PLA translúcido,
ESP32-C3 SuperMini y reductor 12 → 5 V dentro del carril; pieza de pared con alimentación de 12 V. Unión por espiga
pentagonal (0,15 mm por cara) + 2 Molex que conectan al empujar + 2 tornillos M3×16 desde abajo.

| Archivo | Qué es |
|---|---|
| `letrero_bandera/letrero_aulas.py` | Modelo paramétrico (Python + trimesh). Medidas de Molex, placa LED, ESP32 y reductor al principio |
| `letrero_bandera/letrero_bandera_stl.zip` | Carril, pieza de pared, tapas, letras y **galgas `00a`/`00b`** (imprimir primero) |
| `/simuladores/letrero_bandera_3d.html` | Visor 3D interactivo del montaje (también en *Recursos* de la app) |

Pinout propuesto del Molex: amarillo +12 V · negros GND · rojo libre (bus de datos futuro). Las medidas de los Molex
son estimadas: que cada grupo las mida con el calibre e imprima la galga `00a` antes de las piezas grandes.
