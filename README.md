# TEC_IVJP_lab27 · 4º ESO

Plataforma web para un **curso completo de Tecnología de 4º ESO** (36 semanas × 3 h = **108 h**) del IES Valle del Jerte (Plasencia). Combina **programación en MicroPython** (Raspberry Pi Pico W y ESP32-S3-DevKit), un **laboratorio de electrónica** (osciloscopio PROMAX serie 600, lector NFC PN532 y cerradura de solenoide de 12 V) y **neumática y electroneumática**: compresor, unidad de acondicionamiento, válvulas selectoras y antirretorno, **electroválvulas de 12 V 2/2 y 3/2** gobernadas con un **módulo MOSFET**, **cilindros de simple y doble efecto** y **finales de carrera**.

| Trim. | | Misión | Semanas |
|---|---|---|---|
| 1.º | 🐍 | 1. MicroPython I: fundamentos y entradas/salidas | 1-3 |
| 1.º | ⏱️ | 2. MicroPython II: tiempo, estados y clases | 4-6 |
| 1.º | 🔐 | 3. Laboratorio: osciloscopio y control de acceso NFC | 7-9 |
| 1.º | 💨 | 4. Neumática I: aire comprimido y cilindros | 10-12 |
| 2.º | 🔀 | 5. Neumática II: válvulas y circuitos básicos | 13-15 |
| 2.º | ⚡ | 6. Electroválvulas con MicroPython | 16-18 |
| 2.º | ↔️ | 7. Cilindros de doble efecto y enclavamientos | 19-21 |
| 2.º | 🎯 | 8. Finales de carrera: ciclos por posición | 22-24 |
| 3.º | 🔁 | 9. Secuencias de varios cilindros | 25-27 |
| 3.º | 🛑 | 10. Seguridad y modos de marcha | 28-30 |
| 3.º | 📡 | 11. Control WiFi, registro y mantenimiento | 31-33 |
| 3.º | 🏭 | 12. Proyecto final: automatiza una máquina | 34-36 |

- **48 secciones** (4 por misión) con teoría, ejemplos para las dos placas, práctica de aula/taller y evaluación obligatoria (test, completar huecos y **72 ejercicios de código** corregidos automáticamente en un simulador de MicroPython).
- Cada misión acaba con un **proyecto corto** (3 h): contador de piezas, semáforo, **control de acceso NFC**, elevador, puerta desde dos puntos, expulsor, barrera, prensa, estampadora A+ B+ B− A−, prensa segura con bimanual, panel web… y un **proyecto final** con GRAFCET.
- **Fotos obligatorias de los montajes**: en 35 secciones (los 12 proyectos cortos y las prácticas de taller o laboratorio) el alumno debe subir una foto de su montaje (desde el móvil, se reduce sola a ~1600 px). La sección no cuenta como superada hasta que hay foto; el profesor las revisa en **Panel → 📷 Fotos** (aceptar / rechazar con comentario). Una foto rechazada vuelve a pedirse, pero no bloquea lo que el alumno ya tenía desbloqueado. Qué secciones piden foto se indica en el YAML con `foto: { indicaciones: "…" }`.
- **Desbloqueo progresivo**, **pistas** que no revelan la respuesta, **anti-trampa** (tiempo mínimo, espera tras fallos seguidos, alertas de código copiado).
- **Panel del profesorado**: progreso, alertas, dificultad por pregunta, soluciones, desbloqueo para toda la clase, notas manuales y exportación CSV.
- **Ilustraciones** de los montajes de prácticas, del osciloscopio y de los circuitos neumáticos dentro de las lecciones.
- **Recursos** (material complementario de acceso libre, en paralelo a las sesiones): taller **PicoLab·IA** para diseñar, fabricar y soldar una PCB para la Pico con ayuda de IA. Para añadir otro recurso: copia su HTML a `frontend/public/recursos/` y añádelo en `frontend/src/lib/recursos.js`.
- **Calendario** del curso que salta las semanas de vacaciones. Programación sesión a sesión en [`docs/temporalizacion.md`](docs/temporalizacion.md).

---

## 🚀 Publicar en Netlify (recomendado)

Todo funciona en Netlify, sin servidor propio:

- **Web** (Vue) → archivos estáticos.
- **API** (`/api/*`) → una Netlify Function (`netlify/functions/api.mjs`).
- **Datos** (cuentas, progreso, entregas) → **Netlify Blobs** (se activa solo, sin configurar nada).
- **Corrección del código Python** → en el navegador del alumno con **Pyodide** (Python compilado a WebAssembly, incluido en la web, no depende de CDNs externos).

### Opción A · Desde GitHub (despliegue automático)

1. Sube esta carpeta a un repositorio de GitHub (ya incluye un commit inicial):
   ```bash
   git remote add origin https://github.com/TU_USUARIO/Tecnologia_4ESO.git
   git push -u origin main
   ```
2. En Netlify: **Add new site → Import an existing project → GitHub** y elige el repositorio.
   La configuración de compilación se lee de `netlify.toml` (no hay que tocar nada).
3. Antes del primer despliegue, en **Site configuration → Environment variables**, añade las variables de la tabla de abajo (como mínimo `SECRET_KEY` y `TEACHER_PASSWORD`).
4. **Deploy**. Abre la web, entra con usuario `profesor` y tu `TEACHER_PASSWORD`, y comparte con la clase el **código de clase** que aparece en el panel.

### Opción B · Desde tu ordenador con Netlify CLI

```bash
npm install
npx netlify-cli login
npx netlify-cli init              # crea o enlaza el sitio
npx netlify-cli env:set SECRET_KEY "una-cadena-larga-y-aleatoria-de-32-o-mas-caracteres"
npx netlify-cli env:set TEACHER_PASSWORD "tu-contraseña"
npx netlify-cli deploy --build --prod
```

> ⚠️ No uses el despliegue «arrastrar y soltar» de Netlify: no ejecuta la compilación ni publica la función de la API.

### Variables de entorno

| Variable | Obligatoria | Ejemplo | Para qué |
|---|---|---|---|
| `SECRET_KEY` | **Sí** | 40 caracteres aleatorios | Firma las sesiones. Genera una con `openssl rand -hex 32`. |
| `TEACHER_PASSWORD` | **Sí** | `MiClaveSegura` | Contraseña del usuario `profesor`. Si la cambias, la cuenta se actualiza al entrar con la nueva. |
| `TEACHER_USERNAME` | No | `profesor` | Usuario del profesorado. |
| `TEACHER_FULLNAME` | No | `José (Tecnología)` | Nombre que se muestra. |
| `CLASS_CODE` | No | `4ESO-NEUMA` (por defecto) | Código para que el alumnado se registre. |
| `COURSE_START_DATE` | No | `2026-09-14` | Primer día del curso (se usa su lunes). |
| `SKIP_WEEKS` | No | `2026-12-21,2026-12-28,2027-03-22` | Fechas de semanas sin clase (Navidad, Semana Santa…); el calendario las salta. |
| `MIN_SECONDS_BEFORE_SUBMIT` | No | `120` | Tiempo mínimo en una sección antes del primer envío. |
| `FREE_ATTEMPTS` | No | `3` | Fallos seguidos permitidos antes de imponer espera. |
| `COOLDOWN_BASE_SECONDS` | No | `60` | Espera (crece con cada fallo extra). |
| `PLAGIARISM_THRESHOLD` | No | `0.92` | Similitud de código a partir de la cual se crea una alerta. |

### Cómo se corrige y qué hay que saber

- **Test y huecos** se corrigen en la función de Netlify: las respuestas **nunca** llegan al navegador.
- **Código**: el navegador ejecuta las pruebas con Pyodide (la primera vez descarga ~13 MB, luego queda en caché) y la función calcula la nota y el feedback. La solución de referencia nunca sale del servidor, pero **un alumno con conocimientos avanzados podría manipular los resultados de las pruebas** desde las herramientas del navegador. Para una corrección 100 % en servidor usa la opción con Docker (abajo). El historial de entregas del panel muestra siempre el código enviado.
- Plan gratuito de Netlify: suele bastar para varias clases; consulta los límites actuales de funciones y Blobs de tu plan.

### Probar en local sin Netlify

```bash
npm install
npm run build
npm run dev          # http://localhost:8888 · usuario profesor / profe123 · datos en .datos-locales/
npm test             # 153 pruebas: API + todas las soluciones ejecutadas en Pyodide
```

---

## 🏫 Alternativa: servidor del centro con Docker

El mismo frontend funciona con un servidor Python (FastAPI + SQLite) que corrige el código **en el servidor** dentro de un sandbox.

```bash
cp .env.example .env          # edita contraseña, código de clase y fecha
docker compose up -d --build  # http://IP-del-servidor:8080
```

Pruebas del servidor Python: `cd backend && pip install -r requirements.txt pytest httpx && python -m pytest`.

---

## Estructura

```
netlify.toml                    configuración de Netlify
netlify/functions/api.mjs       API (Netlify Function) · lib/: auth, corrección, anti-trampa, almacenamiento
frontend/                       Vue 3 + Vite · public/recursos/: material complementario (HTML autocontenidos) · public/sandbox/worker.mjs (Pyodide en un Web Worker)
backend/app/content/missions/   ← EL TEMARIO (YAML, editable sin programar). Lo usan Netlify y Docker.
backend/app/sandbox/harness.py  simulador de MicroPython (machine, time, neopixel, network, bluetooth…)
backend/                        servidor alternativo FastAPI (Docker)
scripts/build.mjs               genera el temario para la función y copia Pyodide y el simulador
scripts/dev-server.mjs          servidor local que imita Netlify
scripts/ilustraciones/          generadores de las imágenes SVG de las lecciones (frontend/public/img)
tests/                          pruebas Node (API y soluciones en Pyodide)
firmware/                       taller.py (Electrovalvula, CilindroDE, Seta), pn532_uart.py (lector NFC), secretos.py
docs/temporalizacion.md         programación sesión a sesión y calificación sugerida
```

## Editar el temario

Cada misión es un archivo YAML en `backend/app/content/missions/`. Tipos de pregunta:

```yaml
- id: q1
  type: quiz
  question: "..."
  options:
    - {id: a, text: "...", feedback: "pista si eligen esta"}
    - {id: b, text: "..."}
  answer: b
- id: f1
  type: fill_blank
  text: "led = Pin(___, Pin.OUT)"
  blanks: [{accept: ["15"], hint: "..."}]
- id: c1
  type: code
  prompt: "..."
  starter: "def f(x):\n    pass"
  solution: "def f(x):\n    return x * 2"
  tests:
    - {desc: "f(2) = 4", call: "f(2)", expected: 4}
    - {desc: "Enciende el LED", check: "any(e[2] == 'value' for e in _log)"}
```

Tras editar, ejecuta `npm test` (comprueba que todas las soluciones pasan) y haz `git push`: Netlify vuelve a publicar solo.

## Banco neumático: material y conexiones

**Neumática:** compresor con depósito, unidad de acondicionamiento (filtro-regulador-lubricador con manómetro), válvulas selectoras (función O) y antirretorno, electroválvulas **2/2 NC** y **3/2 NC** de **12 V DC**, cilindros de simple y doble efecto, reguladores de caudal, tubo de 4/6 mm y racores rápidos. Un cilindro de doble efecto se gobierna con **dos 3/2 NC** (una por cámara) y un **enclavamiento por software** que nunca activa las dos a la vez.

**Electrónica:** módulo MOSFET de **nivel lógico** de 4 canales (AOD4184/IRLZ44N; los de IRF520 no conducen bien a 3,3 V) con **diodo de libre circulación** (1N4007) en cada bobina, fuente de 12 V (≥ 2 A), pulsadores MARCHA/PARO, **seta de emergencia NC** y finales de carrera (microrruptores con rodillo o reed). GND común entre placa, módulo y fuente.

| Señal | Pico W | ESP32-S3 |
|---|---|---|
| EV1-EV4 → módulo MOSFET | GP10-GP13 | GPIO 4-7 |
| MARCHA · PARO/2.º bimanual · SETA (NC) | GP14 · GP15 · GP16 | GPIO 14 · 15 · 16 |
| Finales de carrera a0 · a1 · b0 · b1 | GP18 · GP19 · GP20 · GP21 | GPIO 17 · 18 · 8 · 9 |
| LED de estado | `Pin("LED")` | NeoPixel en GPIO 48 |

Todas las entradas usan `Pin.PULL_UP` y van a GND (pulsado/pisado = 0). La seta NC da 0 en reposo y 1 si se pulsa **o si se corta el cable**.

## Laboratorio de electrónica (misión 3): material y conexiones

- **Osciloscopio PROMAX serie OD-600** con sonda x1/x10. Práctica con la PWM de la placa (GP22 en la Pico W, GPIO 21 en la ESP32-S3).
- **PN532 NFC RFID Module V3** por **I2C** (interruptores 1 = ON, 2 = OFF, dirección 0x24) con la librería `firmware/pn532_i2c.py` y el programa de prueba `firmware/pn532_i2c_main.py`: SDA → GP6 y SCL → GP7 en la Pico W (GPIO 10 y 11 en la ESP32-S3). Simulador 3D del montaje en `frontend/public/simuladores/`.
- **Tira WS2812 de 8 LED** como semáforo del control de acceso (DIN en GP22 · GPIO 21 · IO3 en la ESP32-C3 SuperMini), con `firmware/tira_colores.py` y su simulador 3D.
- **Cerradura de solenoide de 12 V** (fail-secure) en el canal 1 del módulo MOSFET (GP10 · GPIO 4), con diodo 1N4007 y como máximo 3 s activada.

**Seguridad en el taller:** gafas siempre que haya aire; 3-4 bar en el aula (2 bar en las primeras pruebas); nunca conectar/desconectar tubos con presión; los 12 V nunca llegan a la placa.

## Notas sobre el hardware

- **ESP32-S3**: el LED de la placa es un RGB direccionable (NeoPixel) en GPIO 48 (GPIO 38 en algunas revisiones). Evita GPIO 0, 3, 45, 46 (arranque) y 19-20 (USB).
- **Pico W**: el LED es `Pin("LED")`. GP23-25 y GP29 los usa el chip WiFi.
