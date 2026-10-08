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
