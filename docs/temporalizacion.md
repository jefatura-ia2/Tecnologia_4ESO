# Temporalización — TEC_IVJP_lab27 (4º ESO)

Curso completo: **36 semanas × 3 sesiones de 1 h = 108 h** en doce misiones de tres semanas (9 h cada una), repartidas en tres trimestres. Cada misión termina con un **proyecto corto** (3 h).

| Trimestre | Misión | Semanas | Horas | Nota mínima por sección |
|---|---|---|---|---|
| 1.º | 🐍 M1. MicroPython I: fundamentos y entradas/salidas | 1-3 | 9 | 70 % |
| 1.º | ⏱️ M2. MicroPython II: tiempo, estados y clases | 4-6 | 9 | 70 % |
| 1.º | 🔐 M3. Laboratorio: osciloscopio y control de acceso NFC | 7-9 | 9 | 75 % |
| 1.º | 💨 M4. Neumática I: aire comprimido y cilindros | 10-12 | 9 | 75 % |
| 2.º | 🔀 M5. Neumática II: válvulas y circuitos básicos | 13-15 | 9 | 75 % |
| 2.º | ⚡ M6. Electroválvulas con MicroPython | 16-18 | 9 | 80 % |
| 2.º | ↔️ M7. Cilindros de doble efecto y enclavamientos | 19-21 | 9 | 80 % |
| 2.º | 🎯 M8. Finales de carrera: ciclos por posición | 22-24 | 9 | 80 % |
| 3.º | 🔁 M9. Secuencias de varios cilindros | 25-27 | 9 | 80 % |
| 3.º | 🛑 M10. Seguridad y modos de marcha | 28-30 | 9 | 80 % |
| 3.º | 📡 M11. Control WiFi, registro y mantenimiento | 31-33 | 9 | 80 % |
| 3.º | 🏭 M12. Proyecto final: automatiza una máquina | 34-36 | 9 | 80 % |

> En la plataforma, el calendario empieza en `COURSE_START_DATE` y salta las semanas de vacaciones indicadas en `SKIP_WEEKS` (Navidad, Semana Santa…).

## Bloques de contenido

- **Programación en MicroPython** (M1-M2 y transversal en todo el curso): tipos de datos, listas y diccionarios, funciones, entradas/salidas digitales, antirrebote y flancos, temporización sin bloquear, máquinas de estados, clases y objetos, excepciones (`try/finally`), interrupciones, archivos, WiFi y HTTP.
- **Laboratorio de electrónica** (M3): osciloscopio PROMAX serie 600 (V/div, s/div, disparo, sonda x10, medidas de frecuencia y ciclo de trabajo), lector NFC PN532 por puerto serie y cerradura de solenoide de 12 V con MOSFET: proyecto de control de acceso.
- **Neumática básica** (M4-M5): producción y acondicionamiento del aire, presión y fuerza, consumo, válvulas distribuidoras y simbología, antirretorno y selectora, circuitos de mando directo e indirecto.
- **Electroneumática programada** (M6-M12): etapa de potencia con MOSFET, electroválvulas 2/2 y 3/2 de 12 V, cilindros de simple y doble efecto, finales de carrera, secuencias, seguridad (seta, bimanual), mantenimiento y GRAFCET.

## Sesión a sesión

## 1.º trimestre

### 🐍 Misión 1: MicroPython I: fundamentos y entradas/salidas

*Python esencial, salidas digitales, pulsadores, flancos y antirrebote*

**Objetivos**

- Instalar MicroPython y trabajar con Thonny (REPL y main.py) en la Pico W o la ESP32-S3.
- Usar variables, condicionales, bucles, funciones, listas y diccionarios.
- Controlar salidas digitales (LEDs que más adelante serán electroválvulas) y leer pulsadores con pull-up.
- Detectar flancos y filtrar rebotes de contactos mecánicos.

**Criterios de evaluación relacionados**

- Programa sistemas de control que leen entradas y gobiernan salidas utilizando estructuras de control y funciones.
- Descompone problemas en partes y depura programas de forma sistemática.

**Material:** Raspberry Pi Pico W o ESP32-S3-DevKit + cable USB de datos · Protoboard, 4 LEDs + 4 resistencias de 220 Ω, 2 pulsadores, cables · Ordenador con Thonny

| Semana | Sesión | Contenido | Sección |
|---|---|---|---|
| 1 | 1 | Presentación del curso. Normas del taller. Instalar MicroPython | `m1s1` |
| 1 | 2 | Python esencial: variables, condiciones y bucles | `m1s1` |
| 1 | 3 | Funciones, listas y diccionarios | `m1s1` |
| 2 | 1 | Salidas digitales: los LEDs que serán electroválvulas | `m1s2` |
| 2 | 2 | Listas de salidas y funciones con parámetros | `m1s2` |
| 2 | 3 | Entradas: pulsadores y resistencia pull-up | `m1s3` |
| 3 | 1 | Flancos y antirrebote | `m1s3` |
| 3 | 2 | Proyecto corto: contador de piezas (montaje y programa) | `m1s4` |
| 3 | 3 | Proyecto corto: pruebas, mejora y presentación | `m1s4` |

| Sección | Tipo | Horas | Ítems evaluados |
|---|---|---|---|
| m1s1 · Thonny, REPL y Python esencial | Lección | 2 | 3 test · 1 completar · 2 código |
| m1s2 · Salidas digitales: los LEDs que serán electroválvulas | Lección | 2 | 2 test · 1 completar · 2 código |
| m1s3 · Entradas: pulsadores, flancos y antirrebote | Lección | 2 | 2 test · 0 completar · 2 código |
| m1s4 · Proyecto corto: contador de piezas | Proyecto corto | 3 | 1 test · 0 completar · 2 código |

### ⏱️ Misión 2: MicroPython II: tiempo, estados y clases

*Temporización sin bloquear, máquinas de estados y programación orientada a objetos*

**Objetivos**

- Medir tiempos con ticks_ms y ticks_diff y temporizar sin bloquear el programa.
- Modelar el comportamiento de una máquina con una máquina de estados.
- Crear clases con atributos y métodos para representar componentes (pulsadores, temporizadores…).

**Criterios de evaluación relacionados**

- Diseña algoritmos que responden a eventos y al paso del tiempo sin bloquear el sistema.
- Utiliza estructuras de datos y programación orientada a objetos para organizar el código.

**Material:** Placa + protoboard, 3 LEDs (rojo, ámbar, verde) + resistencias, 2 pulsadores

| Semana | Sesión | Contenido | Sección |
|---|---|---|---|
| 4 | 1 | Por qué sleep() bloquea la máquina | `m2s1` |
| 4 | 2 | ticks_ms y ticks_diff: temporizar sin bloquear | `m2s1` |
| 4 | 3 | Máquinas de estados: estados, eventos y transiciones | `m2s2` |
| 5 | 1 | Tablas de transiciones con diccionarios | `m2s2` |
| 5 | 2 | Clases y objetos: atributos y métodos | `m2s3` |
| 5 | 3 | Clases para el taller: Pulsador y Temporizador | `m2s3` |
| 6 | 1 | Proyecto corto: semáforo con pulsador peatonal (diseño) | `m2s4` |
| 6 | 2 | Proyecto corto: programación y pruebas | `m2s4` |
| 6 | 3 | Proyecto corto: mejoras y presentación | `m2s4` |

| Sección | Tipo | Horas | Ítems evaluados |
|---|---|---|---|
| m2s1 · El tiempo sin bloquear | Lección | 2 | 1 test · 1 completar · 2 código |
| m2s2 · Máquinas de estados | Lección | 2 | 1 test · 0 completar · 2 código |
| m2s3 · Clases y objetos | Lección | 2 | 2 test · 0 completar · 2 código |
| m2s4 · Proyecto corto: semáforo con pulsador peatonal | Proyecto corto | 3 | 1 test · 0 completar · 1 código |

### 🔐 Misión 3: Laboratorio: osciloscopio y control de acceso NFC

*Medir señales con el osciloscopio PROMAX serie 600 y abrir una cerradura de solenoide de 12 V con tarjetas NFC (PN532)*

**Objetivos**

- Manejar un osciloscopio digital (PROMAX serie 600) para medir tensión, periodo, frecuencia y ciclo de trabajo.
- Generar señales PWM con la placa y comprobarlas en el osciloscopio.
- Leer el identificador (UID) de tarjetas NFC con el módulo PN532 NFC RFID V3 por puerto serie.
- Gobernar una cerradura de solenoide de 12 V con un módulo MOSFET de forma segura.
- Programar un control de acceso con lista de tarjetas autorizadas y bloqueo tras varios intentos fallidos.

**Criterios de evaluación relacionados**

- Utiliza instrumentos de medida (osciloscopio) para analizar el funcionamiento de circuitos electrónicos.
- Diseña y programa sistemas de control con sensores de identificación y actuadores electromecánicos.
- Valora la seguridad y la privacidad en los sistemas de identificación.

**Material:** Osciloscopio PROMAX serie 600 (OD-603, OD-606, OD-610…) con su sonda x1/x10 · Raspberry Pi Pico W o ESP32-S3-DevKit, protoboard y cables · Módulo PN532 NFC RFID Module V3 y tarjetas o llaveros NFC (MIFARE Classic / NTAG) · Cerradura de solenoide de 12 V, módulo MOSFET de nivel lógico, diodo 1N4007 y fuente de 12 V · Archivo pn532_uart.py (carpeta firmware del proyecto)

| Semana | Sesión | Contenido | Sección |
|---|---|---|---|
| 7 | 1 | El osciloscopio: pantalla, divisiones, V/div y s/div | `m3s1` |
| 7 | 2 | Sonda x1/x10, disparo y medidas automáticas: la PWM de la placa | `m3s1` |
| 7 | 3 | NFC y RFID: tarjetas, UID y el módulo PN532 | `m3s2` |
| 8 | 1 | Conectar el PN532 por puerto serie y leer tarjetas | `m3s2` |
| 8 | 2 | La cerradura de solenoide: MOSFET, diodo y fuente de 12 V | `m3s3` |
| 8 | 3 | Ver la conmutación de la cerradura con el osciloscopio | `m3s3` |
| 9 | 1 | Proyecto corto: control de acceso NFC (montaje) | `m3s4` |
| 9 | 2 | Proyecto corto: programación y bloqueo por intentos | `m3s4` |
| 9 | 3 | Proyecto corto: pruebas y presentación | `m3s4` |

| Sección | Tipo | Horas | Ítems evaluados |
|---|---|---|---|
| m3s1 · Introducción al osciloscopio PROMAX serie 600 | Lección | 2 | 3 test · 1 completar · 2 código |
| m3s2 · NFC: leer tarjetas con el PN532 | Lección | 2 | 2 test · 0 completar · 2 código |
| m3s3 · La cerradura de solenoide de 12 V | Lección | 2 | 2 test · 0 completar · 2 código |
| m3s4 · Proyecto corto: control de acceso NFC | Proyecto corto | 3 | 2 test · 0 completar · 1 código |

### 💨 Misión 4: Neumática I: aire comprimido y cilindros

*Compresor, unidad de acondicionamiento, presión, fuerza y consumo de aire*

**Objetivos**

- Explicar cómo se produce, almacena y acondiciona el aire comprimido.
- Manejar las unidades de presión y distinguir presión manométrica y absoluta.
- Calcular la fuerza de cilindros de simple y doble efecto y el consumo de aire.
- Trabajar en el banco neumático cumpliendo las normas de seguridad.

**Criterios de evaluación relacionados**

- Analiza el funcionamiento de sistemas neumáticos, describiendo sus componentes y calculando magnitudes básicas.
- Trabaja en el taller de forma segura respetando las normas de uso de los equipos.

**Material:** Compresor con depósito, unidad de acondicionamiento (filtro-regulador-lubricador) y tubo · Cilindros de simple y doble efecto · Gafas de seguridad · Placa con Thonny (para los programas de cálculo)

| Semana | Sesión | Contenido | Sección |
|---|---|---|---|
| 10 | 1 | ¿Por qué neumática? Normas de seguridad del banco | `m4s1` |
| 10 | 2 | Compresor, depósito, presostato y purga | `m4s1` |
| 10 | 3 | Unidad de acondicionamiento y unidades de presión | `m4s1` |
| 11 | 1 | Presión y fuerza: F = p · A | `m4s2` |
| 11 | 2 | Cilindros de simple y doble efecto en el banco | `m4s2` |
| 11 | 3 | Consumo de aire y elección del cilindro | `m4s3` |
| 12 | 1 | Proyecto corto: elevador neumático (cálculo) | `m4s4` |
| 12 | 2 | Proyecto corto: montaje con mando eléctrico directo | `m4s4` |
| 12 | 3 | Proyecto corto: pruebas y ficha técnica | `m4s4` |

| Sección | Tipo | Horas | Ítems evaluados |
|---|---|---|---|
| m4s1 · El aire comprimido: producción y acondicionamiento | Lección | 3 | 3 test · 1 completar · 2 código |
| m4s2 · Presión, fuerza y cilindros | Lección | 2 | 2 test · 1 completar · 2 código |
| m4s3 · Consumo de aire y elección del cilindro | Lección | 1 | 1 test · 0 completar · 2 código |
| m4s4 · Proyecto corto: elevador neumático con mando directo | Proyecto corto | 3 | 2 test · 0 completar · 1 código |

## 2.º trimestre

### 🔀 Misión 5: Neumática II: válvulas y circuitos básicos

*Vías y posiciones, simbología, antirretorno, selectora y primeros circuitos*

**Objetivos**

- Interpretar la designación (vías/posiciones) y la simbología normalizada de las válvulas.
- Conocer la numeración de las vías y el estado de reposo (NC/NA) de una válvula.
- Utilizar válvulas antirretorno y selectoras (función O) en circuitos.
- Montar circuitos básicos de mando de cilindros de simple y doble efecto.

**Criterios de evaluación relacionados**

- Interpreta y realiza esquemas neumáticos sencillos utilizando simbología normalizada.
- Monta y comprueba circuitos neumáticos de mando de cilindros.

**Material:** Banco neumático (compresor, unidad de acondicionamiento, tubo de 4/6 mm) · Electroválvulas 2/2 y 3/2 NC de 12 V, válvula selectora, válvula antirretorno · Cilindros de simple y doble efecto, pulsadores, fuente de 12 V, diodos 1N4007

| Semana | Sesión | Contenido | Sección |
|---|---|---|---|
| 13 | 1 | Válvulas distribuidoras: vías, posiciones y reposo | `m5s1` |
| 13 | 2 | Simbología y numeración de vías | `m5s1` |
| 13 | 3 | Antirretorno y selectora (función O) | `m5s2` |
| 14 | 1 | Circuito 1: simple efecto con 3/2 (mando directo) | `m5s3` |
| 14 | 2 | Circuito 2: doble efecto con dos 3/2 | `m5s3` |
| 14 | 3 | Circuito 3: ¿por qué no sirve una 2/2? Errores típicos | `m5s3` |
| 15 | 1 | Proyecto corto: puerta neumática desde dos puntos (diseño) | `m5s4` |
| 15 | 2 | Proyecto corto: montaje y pruebas | `m5s4` |
| 15 | 3 | Proyecto corto: presentación. Repaso del trimestre | `m5s4` |

| Sección | Tipo | Horas | Ítems evaluados |
|---|---|---|---|
| m5s1 · Válvulas distribuidoras y simbología | Lección | 2 | 2 test · 1 completar · 2 código |
| m5s2 · Antirretorno y selectora (función O) | Lección | 1 | 2 test · 0 completar · 2 código |
| m5s3 · Circuitos básicos de mando de cilindros | Lección | 3 | 2 test · 0 completar · 2 código |
| m5s4 · Proyecto corto: puerta neumática desde dos puntos | Proyecto corto | 3 | 1 test · 0 completar · 1 código |

### ⚡ Misión 6: Electroválvulas con MicroPython

*Etapa de potencia con MOSFET, la clase Electrovalvula y el cilindro de simple efecto automático*

**Objetivos**

- Explicar por qué un pin no puede mover una electroválvula de 12 V y montar la etapa de potencia con MOSFET.
- Proteger el circuito con diodo de libre circulación y masa común.
- Programar la clase Electrovalvula y usarla para automatizar un cilindro de simple efecto.
- Garantizar el estado seguro de las salidas incluso si el programa falla (try/finally).

**Criterios de evaluación relacionados**

- Diseña y monta la interfaz de potencia entre un microcontrolador y actuadores de mayor tensión.
- Programa el control automático de actuadores neumáticos aplicando criterios de seguridad.

**Material:** Placa, módulos MOSFET de nivel lógico (AOD4184/D4184 o IRLZ44N), diodos 1N4007 o 1N5819 · Fuente de 12 V (≥ 2 A), electroválvulas 3/2 NC y 2/2 NC de 12 V · Cilindro de simple efecto, banco neumático, polímetro

| Semana | Sesión | Contenido | Sección |
|---|---|---|---|
| 16 | 1 | ¿Por qué no basta un pin? Corriente de la bobina | `m6s1` |
| 16 | 2 | El MOSFET como interruptor. Diodo y masa común | `m6s1` |
| 16 | 3 | Montaje y comprobación con polímetro | `m6s1` |
| 17 | 1 | La clase Electrovalvula | `m6s2` |
| 17 | 2 | Cilindro de simple efecto automático | `m6s3` |
| 17 | 3 | Estado seguro con try/finally | `m6s3` |
| 18 | 1 | Proyecto corto: expulsor de piezas (montaje) | `m6s4` |
| 18 | 2 | Proyecto corto: programa y soplado con 2/2 | `m6s4` |
| 18 | 3 | Proyecto corto: pruebas y presentación | `m6s4` |

| Sección | Tipo | Horas | Ítems evaluados |
|---|---|---|---|
| m6s1 · La etapa de potencia: MOSFET, diodo y 12 V | Lección | 3 | 3 test · 0 completar · 2 código |
| m6s2 · La clase Electrovalvula | Lección | 1 | 1 test · 0 completar · 1 código |
| m6s3 · Cilindro de simple efecto automático | Lección | 2 | 1 test · 0 completar · 2 código |
| m6s4 · Proyecto corto: expulsor de piezas | Proyecto corto | 3 | 1 test · 0 completar · 1 código |

### ↔️ Misión 7: Cilindros de doble efecto y enclavamientos

*Dos electroválvulas 3/2 por cilindro, enclavamiento por software, temporización y velocidad*

**Objetivos**

- Gobernar un cilindro de doble efecto con dos electroválvulas 3/2 NC.
- Programar un enclavamiento que impida activar a la vez las dos cámaras.
- Automatizar ciclos temporizados de avance, espera y retroceso.
- Medir y ajustar la velocidad de un cilindro.

**Criterios de evaluación relacionados**

- Programa sistemas automáticos con actuadores neumáticos aplicando condiciones de seguridad.
- Comprueba y ajusta el funcionamiento de un automatismo midiendo sus magnitudes.

**Material:** Placa + 2 módulos MOSFET, 2 electroválvulas 3/2 NC de 12 V, cilindro de doble efecto · Válvula antirretorno, banco neumático, cronómetro (o la propia placa)

| Semana | Sesión | Contenido | Sección |
|---|---|---|---|
| 19 | 1 | Doble efecto con dos 3/2: montaje | `m7s1` |
| 19 | 2 | Enclavamiento: nunca las dos a la vez | `m7s1` |
| 19 | 3 | La clase CilindroDE | `m7s1` |
| 20 | 1 | Ciclo temporizado avance-espera-retroceso | `m7s2` |
| 20 | 2 | Ciclos repetidos y contador | `m7s2` |
| 20 | 3 | Velocidad del cilindro y regulación | `m7s3` |
| 21 | 1 | Proyecto corto: barrera neumática (diseño) | `m7s4` |
| 21 | 2 | Proyecto corto: programación y montaje | `m7s4` |
| 21 | 3 | Proyecto corto: pruebas y presentación | `m7s4` |

| Sección | Tipo | Horas | Ítems evaluados |
|---|---|---|---|
| m7s1 · Doble efecto con dos 3/2: el enclavamiento | Lección | 3 | 2 test · 0 completar · 1 código |
| m7s2 · Ciclos temporizados | Lección | 2 | 1 test · 0 completar · 1 código |
| m7s3 · Velocidad del cilindro y regulación | Lección | 1 | 2 test · 0 completar · 1 código |
| m7s4 · Proyecto corto: barrera neumática | Proyecto corto | 3 | 1 test · 0 completar · 1 código |

### 🎯 Misión 8: Finales de carrera: ciclos por posición

*Sensores de posición, espera con tiempo límite y diagnóstico de atascos y fugas*

**Objetivos**

- Conectar y leer finales de carrera para conocer la posición real de los cilindros.
- Programar ciclos que avanzan cuando el sensor confirma la posición, no cuando pasa un tiempo.
- Vigilar los tiempos de cada movimiento para detectar atascos, fugas o falta de presión.

**Criterios de evaluación relacionados**

- Integra sensores en sistemas automáticos para controlar su funcionamiento en lazo cerrado.
- Diagnostica fallos de funcionamiento a partir de la información de los sensores.

**Material:** Finales de carrera (microinterruptores con rodillo), soportes y bridas · Placa, módulos MOSFET, 2 electroválvulas 3/2 NC, cilindro de doble efecto

| Semana | Sesión | Contenido | Sección |
|---|---|---|---|
| 22 | 1 | Finales de carrera: tipos, contactos y montaje | `m8s1` |
| 22 | 2 | Conexión a la placa y lectura de la posición | `m8s1` |
| 22 | 3 | Esperar a un sensor con tiempo límite | `m8s2` |
| 23 | 1 | Ciclo A+ A- por sensores | `m8s2` |
| 23 | 2 | Vigilancia de tiempos: atascos y fugas | `m8s3` |
| 23 | 3 | Estado seguro ante una alarma | `m8s3` |
| 24 | 1 | Proyecto corto: prensa con retorno automático (montaje) | `m8s4` |
| 24 | 2 | Proyecto corto: programa con alarmas | `m8s4` |
| 24 | 3 | Proyecto corto: pruebas de fallo y presentación | `m8s4` |

| Sección | Tipo | Horas | Ítems evaluados |
|---|---|---|---|
| m8s1 · Finales de carrera | Lección | 2 | 2 test · 1 completar · 1 código |
| m8s2 · Esperar a un sensor con tiempo límite | Lección | 2 | 1 test · 0 completar · 1 código |
| m8s3 · Vigilancia de tiempos: atascos y fugas | Lección | 2 | 1 test · 0 completar · 1 código |
| m8s4 · Proyecto corto: prensa con retorno automático | Proyecto corto | 3 | 1 test · 0 completar · 1 código |

## 3.º trimestre

### 🔁 Misión 9: Secuencias de varios cilindros

*Notación de movimientos, diagrama espacio-fase y secuencias por sensores*

**Objetivos**

- Describir el funcionamiento de una máquina con la notación de movimientos (A+ B+ B- A-) y el diagrama espacio-fase.
- Comprobar que una secuencia es válida antes de ejecutarla.
- Programar secuencias de dos cilindros, primero por tiempo y después por finales de carrera.
- Calcular el tiempo de ciclo y la producción de una máquina.

**Criterios de evaluación relacionados**

- Representa y programa secuencias de funcionamiento de sistemas automáticos con varios actuadores.
- Evalúa el rendimiento de un sistema automático calculando su tiempo de ciclo y su producción.

**Material:** Placa, 4 módulos MOSFET, 4 electroválvulas 3/2 NC (o 3 si un cilindro es de simple efecto) · Dos cilindros (A y B) con sus finales de carrera a0, a1, b0, b1

| Semana | Sesión | Contenido | Sección |
|---|---|---|---|
| 25 | 1 | Notación A+ B+ … y diagrama espacio-fase | `m9s1` |
| 25 | 2 | Secuencias válidas e imposibles | `m9s1` |
| 25 | 3 | Ejecutar secuencias por tiempo | `m9s2` |
| 26 | 1 | Dos cilindros con el diccionario de cilindros | `m9s2` |
| 26 | 2 | Secuencias por sensores: la máquina de pasos | `m9s3` |
| 26 | 3 | Secuencia por sensores en el banco | `m9s3` |
| 27 | 1 | Proyecto corto: estampadora A+ B+ B- A- (montaje) | `m9s4` |
| 27 | 2 | Proyecto corto: programa por sensores | `m9s4` |
| 27 | 3 | Proyecto corto: tiempo de ciclo, producción y presentación | `m9s4` |

| Sección | Tipo | Horas | Ítems evaluados |
|---|---|---|---|
| m9s1 · Notación de movimientos y diagrama espacio-fase | Lección | 2 | 2 test · 0 completar · 2 código |
| m9s2 · Ejecutar secuencias por tiempo | Lección | 2 | 1 test · 0 completar · 1 código |
| m9s3 · Secuencias por sensores: la máquina de pasos | Lección | 2 | 1 test · 0 completar · 2 código |
| m9s4 · Proyecto corto: estampadora A+ B+ B- A- | Proyecto corto | 3 | 1 test · 0 completar · 1 código |

### 🛑 Misión 10: Seguridad y modos de marcha

*Paro de emergencia, interrupciones, mando bimanual y ciclo único/continuo*

**Objetivos**

- Diseñar el paro de emergencia de una máquina con contacto NC (seguridad positiva) y rearme manual.
- Usar interrupciones (Pin.irq) para reaccionar al instante.
- Programar un mando bimanual y los modos de marcha ciclo único y ciclo continuo.
- Integrar todo en una máquina de estados segura.

**Criterios de evaluación relacionados**

- Aplica criterios de seguridad en el diseño y la programación de máquinas automáticas.
- Analiza los riesgos de un sistema automático y propone medidas de protección.

**Material:** Seta de emergencia con contacto NC (o pulsador NC), 2 pulsadores para el bimanual · Placa, módulos MOSFET, electroválvulas y cilindro de doble efecto con finales de carrera

| Semana | Sesión | Contenido | Sección |
|---|---|---|---|
| 28 | 1 | Riesgos de una máquina. La seta de emergencia | `m10s1` |
| 28 | 2 | Contacto NC y seguridad positiva. Estado seguro | `m10s1` |
| 28 | 3 | Interrupciones con Pin.irq | `m10s2` |
| 29 | 1 | Mando bimanual | `m10s3` |
| 29 | 2 | Modos de marcha: ciclo único y continuo | `m10s3` |
| 29 | 3 | Rearme y señalización | `m10s3` |
| 30 | 1 | Proyecto corto: prensa segura (diseño de estados) | `m10s4` |
| 30 | 2 | Proyecto corto: programación y montaje | `m10s4` |
| 30 | 3 | Proyecto corto: pruebas de seguridad y presentación | `m10s4` |

| Sección | Tipo | Horas | Ítems evaluados |
|---|---|---|---|
| m10s1 · Paro de emergencia y estado seguro | Lección | 2 | 2 test · 0 completar · 2 código |
| m10s2 · Interrupciones | Lección | 1 | 1 test · 0 completar · 1 código |
| m10s3 · Mando bimanual y modos de marcha | Lección | 3 | 2 test · 0 completar · 2 código |
| m10s4 · Proyecto corto: prensa segura | Proyecto corto | 3 | 1 test · 0 completar · 1 código |

### 📡 Misión 11: Control WiFi, registro y mantenimiento

*Servidor web en la placa, panel de control seguro, registro de ciclos y diagnóstico*

**Objetivos**

- Conectar la placa a la WiFi y servir una página web y datos JSON.
- Diseñar un panel de control remoto que respete siempre la seguridad local.
- Registrar los ciclos de la máquina en un archivo y planificar el mantenimiento.
- Detectar ciclos anómalos (lentos) como indicio de fugas o falta de presión.

**Criterios de evaluación relacionados**

- Integra comunicaciones en sistemas automáticos para su supervisión y control remoto de forma segura.
- Analiza datos de funcionamiento para el mantenimiento de máquinas.

**Material:** Placa con WiFi, red de 2,4 GHz del aula (o punto de acceso) · Máquina de los proyectos anteriores (estampadora o prensa) · Móvil u ordenador para el panel

| Semana | Sesión | Contenido | Sección |
|---|---|---|---|
| 31 | 1 | La placa en la red: WiFi e IP | `m11s1` |
| 31 | 2 | HTTP: peticiones, rutas y respuestas | `m11s1` |
| 31 | 3 | Panel de control: rutas /estado, /ciclo y /paro | `m11s2` |
| 32 | 1 | La seguridad manda: lo remoto nunca anula lo local | `m11s2` |
| 32 | 2 | Registro de ciclos en un archivo CSV | `m11s3` |
| 32 | 3 | Mantenimiento: contadores y ciclos lentos | `m11s3` |
| 33 | 1 | Proyecto corto: panel de la estampadora (servidor) | `m11s4` |
| 33 | 2 | Proyecto corto: página de estadísticas | `m11s4` |
| 33 | 3 | Proyecto corto: pruebas y presentación | `m11s4` |

| Sección | Tipo | Horas | Ítems evaluados |
|---|---|---|---|
| m11s1 · WiFi y servidor web en la placa | Lección | 2 | 1 test · 0 completar · 2 código |
| m11s2 · Panel de control seguro | Lección | 2 | 1 test · 0 completar · 1 código |
| m11s3 · Registro de ciclos y mantenimiento | Lección | 2 | 1 test · 0 completar · 3 código |
| m11s4 · Proyecto corto: panel de la estampadora | Proyecto corto | 3 | 1 test · 0 completar · 1 código |

### 🏭 Misión 12: Proyecto final: automatiza una máquina

*GRAFCET, asignación de pines, pruebas, documentación y construcción por equipos*

**Objetivos**

- Describir el funcionamiento de una máquina con un GRAFCET y programarlo como máquina de estados.
- Planificar el cableado comprobando que la asignación de pines es correcta.
- Probar el automatismo de forma sistemática y documentarlo.
- Diseñar, montar, programar y presentar un automatismo electroneumático completo.

**Criterios de evaluación relacionados**

- Diseña y construye sistemas automáticos electroneumáticos programados que resuelven un problema real.
- Documenta y comunica el proceso de diseño, las pruebas y los resultados.
- Trabaja en equipo aplicando las normas de seguridad del taller.

**Material:** Kit completo del taller (compresor, unidad de mantenimiento, electrovalvulas 2/2 y 3/2, cilindros, finales de carrera) · Placa, módulo MOSFET, fuente de 12 V, pulsadores y seta · Cuaderno de proyecto (plantilla del docente)

| Semana | Sesión | Contenido | Sección |
|---|---|---|---|
| 34 | 1 | GRAFCET: etapas, transiciones y acciones | `m12s1` |
| 34 | 2 | Del GRAFCET al código | `m12s1` |
| 34 | 3 | Elegir proyecto y dibujar su GRAFCET | `m12s1` |
| 35 | 1 | Tabla de conexiones y asignación de pines | `m12s2` |
| 35 | 2 | Montaje neumático y eléctrico | `m12s2` |
| 35 | 3 | Plan de pruebas y documentación | `m12s3` |
| 36 | 1 | Proyecto final: programación y ajuste | `m12s4` |
| 36 | 2 | Proyecto final: pruebas y mejoras | `m12s4` |
| 36 | 3 | Proyecto final: presentación y evaluación | `m12s4` |

| Sección | Tipo | Horas | Ítems evaluados |
|---|---|---|---|
| m12s1 · GRAFCET y máquinas de estados | Lección | 3 | 2 test · 0 completar · 1 código |
| m12s2 · Asignación de pines y montaje | Lección | 2 | 1 test · 0 completar · 1 código |
| m12s3 · Plan de pruebas y documentación | Lección | 1 | 3 test · 0 completar · 0 código |
| m12s4 · Proyecto final por equipos | Proyecto corto | 3 | 1 test · 0 completar · 1 código |

## Calificación sugerida

Por trimestre:

- **50 %** evaluación automática de la plataforma (media de las misiones del trimestre en el CSV).
- **35 %** proyectos cortos en el banco neumático (nota del profesor en cada misión: funcionamiento, montaje, seguridad).
- **15 %** prácticas de aula, cuaderno y actitud en el taller (normas de seguridad).

En el 3.er trimestre, el **proyecto final** (M12) puede pesar el 50 % con la rúbrica de la sección m12s4.

Adapta los porcentajes a la programación didáctica del departamento.
