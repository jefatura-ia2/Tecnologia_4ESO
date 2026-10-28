// Material complementario: se puede consultar en cualquier momento, sin depender de las misiones.
// Para añadir otro recurso, copia el archivo HTML a frontend/public/recursos/ y añade una entrada aquí.
export const RECURSOS = [
  {
    id: 'picolab-pcb',
    icono: '🧩',
    titulo: 'PicoLab·IA: diseña tu primera PCB con inteligencia artificial',
    autor: 'Prof. NachoTEC · IES Valle del Jerte',
    archivo: '/recursos/picolab-pcb.html',
    sesiones: '8 sesiones de 55 min',
    resumen:
      'Taller para diseñar, encargar y soldar una placa base (shield) para la Raspberry Pi Pico usando herramientas de IA gratuitas: qué es una PCB, ley de Ohm y esquemas, la IA como copiloto, ficha técnica, esquemático auditado, diseño del PCB con DRC, Gerbers y fabricación, y soldadura y prueba.',
    relacion: 'Complementa las misiones 1 y 3 (Pico W, LEDs, pulsadores, electrónica y medida).',
    etiquetas: ['Electrónica', 'PCB', 'IA', 'Soldadura'],
  },
  {
    id: 'sim-pn532',
    icono: '🧊',
    titulo: 'Simulador 3D: PN532 por I2C con la Raspberry Pi Pico W',
    autor: 'José I. Sánchez Castaño · IES Valle del Jerte',
    archivo: '/simuladores/pn532_i2c_pico_w_3d.html',
    sesiones: 'Montaje interactivo',
    resumen: 'Montaje en 3D del lector NFC PN532 sobre protoboard con la Pico W: SDA → GP6, SCL → GP7, 3V3 (pin 36) y GND (pin 8), con los interruptores en modo I2C. Gira, acerca y desplaza la vista.',
    relacion: 'Misión 3, sección «NFC: leer tarjetas con el PN532 por I2C».',
    etiquetas: ['NFC', 'I2C', 'Pico W', '3D'],
  },
  {
    id: 'sim-ws2812',
    icono: '🌈',
    titulo: 'Simulador 3D: tira WS2812 de 8 LED con ESP32-C3 SuperMini',
    autor: 'José I. Sánchez Castaño · IES Valle del Jerte',
    archivo: '/simuladores/ws2812_esp32c3_3d.html',
    sesiones: 'Montaje interactivo',
    resumen: 'Montaje en 3D de la tira NeoPixel con la ESP32-C3 SuperMini: DIN → IO3, 5V → 5V y GND → GND, con los LED animados.',
    relacion: 'Misión 3, sección «Actuadores: cerradura de 12 V y tira de LED WS2812».',
    etiquetas: ['WS2812', 'NeoPixel', 'ESP32-C3', '3D'],
  },
]
