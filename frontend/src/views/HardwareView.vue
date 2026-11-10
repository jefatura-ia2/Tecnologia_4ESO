<template>
  <div>
    <h1>Material del taller</h1>
    <p class="muted">Placas programadas en MicroPython con Thonny y un banco neumático: compresor, unidad de
      acondicionamiento, válvulas, electroválvulas de 12 V y cilindros. Casi todo el código funciona igual en las dos placas;
      cuando cambia algo, los ejemplos muestran las dos versiones.</p>

    <div class="card warn-card">
      <h3 style="margin-top:0">⚠️ Normas de seguridad del banco neumático</h3>
      <ul>
        <li><strong>Gafas de seguridad</strong> siempre que haya aire en el circuito.</li>
        <li>Presión de trabajo en el aula: <strong>3-4 bar</strong> (ajustada en el regulador de la unidad de acondicionamiento).</li>
        <li><strong>Nunca</strong> conectes ni desconectes tubos con presión: cierra la llave y purga antes.</li>
        <li>No dirijas el aire hacia nadie ni acerques las manos a un cilindro en movimiento.</li>
        <li>La placa trabaja a 3,3 V; las electroválvulas a 12 V. <strong>Nunca</strong> conectes los 12 V a la placa: solo a través del módulo MOSFET.</li>
      </ul>
    </div>

    <div class="boards mt">
      <article v-for="b in boards" :key="b.id" class="card board" :class="b.id">
        <h2>{{ b.id === 'pico_w' ? '🟩' : '⬛' }} {{ b.name }}</h2>
        <table>
          <tbody>
            <tr><th>Procesador</th><td>{{ b.chip }}</td></tr>
            <tr><th>RAM / Flash</th><td>{{ b.ram }} / {{ b.flash }}</td></tr>
            <tr><th>WiFi</th><td>{{ b.wifi }}</td></tr>
            <tr><th>USB</th><td>{{ b.usb }}</td></tr>
            <tr><th>LED</th><td>{{ b.led }}</td></tr>
            <tr><th>Salidas</th><td>{{ b.ml }}</td></tr>
            <tr><th>En el curso</th><td>{{ b.spi }}</td></tr>
          </tbody>
        </table>
        <a :href="b.firmware" target="_blank" rel="noopener">Descargar firmware MicroPython ↗</a>
      </article>
    </div>

    <div class="card mt prose">
      <h3>Conexiones usadas en el curso</h3>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Elemento</th><th>Pico W</th><th>ESP32-S3</th><th>Notas</th></tr></thead>
          <tbody>
            <tr><td>EV1 · EV2 · EV3 · EV4 (señal del módulo MOSFET)</td><td>GP10 · GP11 · GP12 · GP13</td><td>GPIO 4 · 5 · 6 · 7</td><td>1 = electroválvula activada</td></tr>
            <tr><td>Pulsador MARCHA (a GND)</td><td>GP14</td><td>GPIO 14</td><td><code>Pin.PULL_UP</code> · pulsado = 0</td></tr>
            <tr><td>Pulsador PARO / 2.º pulsador bimanual</td><td>GP15</td><td>GPIO 15</td><td><code>Pin.PULL_UP</code> · pulsado = 0</td></tr>
            <tr><td>Seta de EMERGENCIA (contacto NC)</td><td>GP16</td><td>GPIO 16</td><td>Reposo = 0 · pulsada o cable roto = 1</td></tr>
            <tr><td>Finales de carrera A0 · A1</td><td>GP18 · GP19</td><td>GPIO 17 · 18</td><td>A0 = cilindro A dentro · A1 = fuera</td></tr>
            <tr><td>Finales de carrera B0 · B1</td><td>GP20 · GP21</td><td>GPIO 8 · 9</td><td>Contacto NA a GND · pisado = 0</td></tr>
            <tr><td>PN532 NFC V3 por I2C (SDA · SCL)</td><td>GP6 · GP7 (I2C1, pines 9 y 10)</td><td>GPIO 10 · GPIO 11</td><td>Interruptores 1 = ON, 2 = OFF · VCC a 3V3 · dirección 0x24</td></tr>
            <tr><td>Tira WS2812 de 8 LED (DIN)</td><td>GP22 · 5V a VBUS</td><td>GPIO 21 · 5V</td><td>ESP32-C3 SuperMini: IO3 · brillo ≤ 0,25 con USB</td></tr>
            <tr><td>Cerradura de solenoide 12 V</td><td>GP10 (canal 1 del MOSFET)</td><td>GPIO 4 (canal 1 del MOSFET)</td><td>Con diodo 1N4007 · máx. 3 s abierta</td></tr>
            <tr><td>Salida PWM para el osciloscopio</td><td>GP22</td><td>GPIO 21</td><td>Punta de la sonda al pin, pinza a GND</td></tr>
            <tr><td>LED de la placa</td><td><code>Pin("LED")</code></td><td>NeoPixel en <code>Pin(48)</code></td><td>Indicador de estado</td></tr>
          </tbody>
        </table>
      </div>
      <p class="small muted">En la ESP32-S3 se evitan los GPIO 0, 3, 45 y 46 (arranque) y 19-20 (USB).</p>
    </div>

    <div class="card mt prose">
      <h3>Etapa de potencia: módulo MOSFET</h3>
      <ul>
        <li>Usa módulos con <strong>MOSFET de nivel lógico</strong> (AOD4184/D4184, IRLZ44N…), que conducen bien con 3,3 V.
          Los módulos con <strong>IRF520 no funcionan bien a 3,3 V</strong>.</li>
        <li>Cada electroválvula lleva un <strong>diodo de libre circulación</strong> (1N4007 o 1N5819) en paralelo con la bobina, con la banda hacia +12 V
          (muchos módulos ya lo incorporan).</li>
        <li>La fuente de 12 V (≥ 2 A para 4 válvulas) y la placa deben compartir <strong>GND</strong>.</li>
      </ul>
      <h3>Componentes neumáticos</h3>
      <table>
        <tbody>
          <tr><th>Compresor</th><td>Produce el aire comprimido y lo guarda en el depósito; el presostato lo para al llegar a la presión máxima.</td></tr>
          <tr><th>Unidad de acondicionamiento</th><td>Filtro (agua y partículas) + regulador con manómetro (fija la presión de trabajo) + lubricador.</td></tr>
          <tr><th>Electroválvula 2/2 NC 12 V</th><td>Abre o cierra el paso (soplado, llenado, corte).</td></tr>
          <tr><th>Electroválvula 3/2 NC 12 V</th><td>Presión o escape: cilindro de simple efecto o una cámara de un doble efecto.</td></tr>
          <tr><th>Válvula antirretorno</th><td>Deja pasar el aire en un solo sentido.</td></tr>
          <tr><th>Válvula selectora</th><td>Función O: deja pasar la señal que llega por cualquiera de sus dos entradas.</td></tr>
          <tr><th>Cilindro de simple efecto</th><td>Avanza con aire y vuelve por muelle.</td></tr>
          <tr><th>Cilindro de doble efecto</th><td>Avanza y retrocede con aire (dos tomas).</td></tr>
        </tbody>
      </table>

      <h3>Laboratorio de electrónica (misión 3)</h3>
      <table class="table">
        <tbody>
          <tr><th>Osciloscopio PROMAX serie OD-600</th><td>Osciloscopio digital (OD-603, OD-606, OD-610…). Sonda en x10 y el mismo ajuste en el menú del canal; compensa la sonda con su salida de calibración; la pinza de masa solo a GND. Nunca se mide la red de 230 V.</td></tr>
          <tr><th>PN532 NFC RFID Module V3</th><td>Lector NFC de 13,56 MHz. En el curso se usa por I2C con la librería <a href="/descargas/pn532_i2c.py">pn532_i2c.py</a> y el programa de prueba <a href="/descargas/pn532_i2c_main.py">pn532_i2c_main.py</a> (guárdalo como main.py). <a href="/simuladores/pn532_i2c_pico_w_3d.html" target="_blank" rel="noopener">Montaje en 3D ↗</a></td></tr>
          <tr><th>Tira WS2812 (NeoPixel) de 8 LED</th><td>LED RGB direccionables con un solo cable de datos (DIN). Hasta 60 mA por LED en blanco: con alimentación USB usa brillo ≤ 0,25. Programa de prueba: <a href="/descargas/tira_colores.py">tira_colores.py</a>. <a href="/simuladores/ws2812_esp32c3_3d.html" target="_blank" rel="noopener">Montaje en 3D con ESP32-C3 ↗</a></td></tr>
          <tr><th>ESP32-C3 SuperMini</th><td>Placa pequeña (22,5 × 18 mm) con WiFi/BLE y USB-C, programable con MicroPython. En la misión 3 se usa para la tira WS2812 (DIN en IO3) y es el cerebro del Smart Sign (misiones 4-6).</td></tr>
          <tr><th>Cerradura de solenoide 12 V</th><td>Fail-secure: cerrada sin corriente, se abre con 12 V (≈ 0,5-1 A). Siempre con módulo MOSFET y diodo de libre circulación; no dejarla activada más de unos segundos.</td></tr>
        </tbody>
      </table>

      <h3>Pomo motorizado (misión 3, sección 5)</h3>
      <table class="table">
        <tbody>
          <tr><th>Servo MG996R</th><td>Servo de engranajes metálicos: 9,4 kg·cm a 4,8 V (11 kg·cm a 6 V), 0,17 s/60°, hasta ≈ 2,5 A con el eje bloqueado. PWM de 50 Hz: 0,5 ms = 0°, 1,5 ms = 90°. Señal en GP15 (Pico W) o GPIO 5 (ESP32-S3); <strong>alimentación externa de 5-6 V con GND común</strong> y condensador de 470-1000 µF.</td></tr>
          <tr><th>Prototipos impresos</th><td>
            <a href="/descargas/pomo_mg996r/01_puente_MG996R.stl">01_puente_MG996R.stl</a> (se atornilla a los tubos del pomo y sostiene el servo) ·
            <a href="/descargas/pomo_mg996r/02_acoplamiento_MG996R.stl">02_acoplamiento_MG996R.stl</a> (une el servo con la pletina; prisionero M3) ·
            <a href="/descargas/pomo_mg996r/03_bloque_medida_par.stl">03_bloque_medida_par.stl</a> (mide el par con el dinamómetro de muelle: anclaje a 15 mm del eje) ·
            <a href="/simuladores/pomo_mg996r_anatomia.html">despiece interactivo</a></td></tr>
        </tbody>
      </table>

      <h3>Proyecto Smart Sign IoT (misiones 4-6)</h3>
      <table class="table">
        <tbody>
          <tr><th>Batería 18650 + portapilas</th><td>Li-ion de 3,7 V nominal (4,2 V cargada), ≈ 2500 mAh. Portapilas con cable y conector JST. Nunca se cortocircuita ni se descarga por debajo de 3 V.</td></tr>
          <tr><th>TP4056 con protección (USB-C)</th><td>Cargador de una celda Li-ion con protección DW01: entrada USB-C, pines B+/B− a la batería y OUT+/OUT− a la carga. LED rojo cargando, azul/verde cargada.</td></tr>
          <tr><th>MT3608 (elevador)</th><td>Convertidor <em>boost</em> de 2-24 V a 5-28 V. <strong>Ajusta la salida a 5,0 V con el potenciómetro y el polímetro antes de conectar la placa.</strong> Rendimiento ≈ 85 %.</td></tr>
          <tr><th>Metacrilato de 5 mm</th><td>Plancha de 160 × 120 mm iluminada por el canto. Mide su espesor real con el calibre: suele variar ±0,2 mm. Corte solo con la láser y el profesor.</td></tr>
          <tr><th>Sensor PIR HC-SR501 / AM312</th><td>Movimiento por infrarrojos: salida digital (1 = movimiento). En la ESP32-C3, IO4.</td></tr>
          <tr><th>Sensor de luz BH1750</th><td>Luz en lux por I2C (dirección 0x23). ESP32-C3: SDA → IO5, SCL → IO6, VCC → 3V3.</td></tr>
          <tr><th>Impresoras 3D</th><td><strong>Bambu Lab A1</strong> (256 × 256 × 256 mm): piezas de precisión y la probeta de tolerancias. <strong>Artillery Sidewinder X1</strong> (300 × 300 × 400 mm): piezas grandes y PETG.</td></tr>
          <tr><th>Descargas</th><td>
            <a href="/descargas/smart_sign/marco_cartel.scad">marco_cartel.scad</a> (OpenSCAD paramétrico) ·
            <a href="/descargas/smart_sign/stl/soporte.stl">soporte.stl</a> ·
            <a href="/descargas/smart_sign/stl/tapa.stl">tapa.stl</a> ·
            <a href="/descargas/smart_sign/stl/capuchon.stl">capuchon.stl</a> ·
            <a href="/descargas/smart_sign/stl/probeta.stl">probeta.stl</a> ·
            <a href="/descargas/cartel_mqtt.py">cartel_mqtt.py</a> ·
            <a href="/descargas/smart_sign/mosquitto.conf">mosquitto.conf</a> ·
            <a href="/descargas/smart_sign/panel_profesor.html">panel_profesor.html</a> (se aloja en el servidor del instituto)</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../lib/api.js'

const boards = ref([])
onMounted(async () => { boards.value = await api('/hardware') })
</script>

<style scoped>
.boards { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }
.board.pico_w { border-top: 5px solid var(--pico); }
.board.esp32_s3 { border-top: 5px solid var(--esp); }
.board h2 { margin-top: 0; }
th { width: 30%; }
.warn-card { border-left: 5px solid var(--warn); background: var(--warn-soft); }
</style>
