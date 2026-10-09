# Ilustraciones de las lecciones

Las imágenes de `frontend/public/img/*.svg` (osciloscopio, montajes y circuitos neumáticos) se generan con estos scripts:

```bash
cd scripts/ilustraciones
python3 fig_osc.py        # panel, lectura de PWM, compensación de sonda, cerradura en dos canales
python3 fig_montajes.py   # PWM + sonda, PN532, cerradura con MOSFET, LEDs y pulsador
python3 fig_neuma.py      # simple efecto, doble efecto con dos 3/2, finales de carrera
```

En las lecciones (YAML) se insertan con Markdown: `![texto alternativo](/img/nombre.svg)` y debajo una línea `*pie de figura*`.

Misiones 9-12 (espacio-fase, estampadora, seta NC, bimanual, panel WiFi y GRAFCET):

```bash
python3 fig_avanzado.py
```

`lib.py` y `neuma_simbolos.py` contienen las piezas reutilizables (pantalla de osciloscopio, Pico W, módulo MOSFET, válvulas 3/2, cilindros…).
