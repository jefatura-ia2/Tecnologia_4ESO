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
]
