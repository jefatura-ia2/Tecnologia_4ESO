# Bambu Lab — Perfiles de Impresión para Carcasas Electrónicas

## Impresoras soportadas

| Modelo | Volumen | Multi-color | Cámara cerrada | Notas |
|--------|---------|-------------|-----------------|-------|
| A1 mini | 180×180×180mm | Con AMS lite | No | Entrada, ideal para prototipado |
| A1 | 256×256×256mm | Con AMS lite | No | Versatil, buena relación calidad/precio |
| P1S | 256×256×256mm | Con AMS | Sí | Ideal para ABS/ASA/PA |
| X1C | 256×256×256mm | Con AMS | Sí | Tope de gama, LIDAR |

## Materiales recomendados por aplicación

### PLA — Prototipado y carcasas interiores
```
Temperatura nozzle:  210-220°C
Temperatura cama:    55-60°C
Velocidad:           150-200 mm/s (Bambu Lab optimizado)
Ventilador:          100%
Relleno:             15-20% gyroid
Perímetros:          3 (1.2mm con nozzle 0.4)
Capas sólidas:       4 superior, 3 inferior
Altura capa:         0.20mm (estándar) / 0.12mm (detalle)
```
Pros: fácil, sin warping, buen acabado. Contras: frágil, baja resistencia térmica (60°C).

### PETG — Carcasas funcionales
```
Temperatura nozzle:  235-245°C
Temperatura cama:    70-80°C
Velocidad:           120-150 mm/s
Ventilador:          30-50%
Relleno:             20% gyroid
Perímetros:          3
Altura capa:         0.20mm
Retracción:          Aumentar 10% vs PLA
```
Pros: resistente, flexible, resistencia térmica 80°C. Contras: stringing, peor bridging.

### ABS/ASA — Exterior y alta temperatura (requiere cámara cerrada: P1S/X1C)
```
Temperatura nozzle:  250-260°C
Temperatura cama:    100-110°C
Velocidad:           120-150 mm/s
Ventilador:          0-30%
Relleno:             20% gyroid
Perímetros:          3-4
Cámara:              Cerrada obligatorio
Primera capa:        Velocidad 50%, flow 105%
```
Pros: resistencia térmica 100°C, resistente UV (ASA). Contras: warping, necesita cámara.

### TPU — Juntas, antivibraciones, protectores
```
Temperatura nozzle:  220-230°C
Temperatura cama:    50°C
Velocidad:           50-80 mm/s (reducir significativamente)
Ventilador:          50-80%
Relleno:             15% gyroid
Retracción:          Mínima o desactivada
Direct drive:        Requerido (Bambu Lab lo tiene)
```

## Perfiles optimizados por tipo de pieza

### Carcasa (base + tapa)
```yaml
material: PETG (funcional) o PLA (prototipo)
altura_capa: 0.20mm
perímetros: 3
relleno: 15% gyroid
soportes: solo donde necesario (tree supports)
orientación: abertura hacia arriba
brim: 5mm si base > 100mm
seam: esquina trasera (aligned)
primera_capa_velocidad: 50%
```

### Piezas mecánicas (engranajes, soportes de motor)
```yaml
material: PETG o ABS
altura_capa: 0.16mm
perímetros: 4-5
relleno: 40-60% gyroid
capas_solidas_top: 6
capas_solidas_bottom: 5
orientación: eje de rotación vertical
soportes: tree supports, distancia Z 0.2mm
```

### Soportes de montaje y brackets
```yaml
material: PETG
altura_capa: 0.20mm
perímetros: 4
relleno: 30% cubic
orientación: cara de montaje en cama
soportes: mínimos
```

### Guías de cables y separadores
```yaml
material: PLA
altura_capa: 0.28mm (rápido)
perímetros: 2
relleno: 10% grid
orientación: plano en cama
```

## Configuración de soportes en Bambu Studio

### Tree supports (recomendado para carcasas)
```
Tipo: Tree (orgánico)
Ángulo umbral: 40°
Distancia Z: 0.2mm (1 capa)
Distancia XY: 0.4mm
Interfaz: 3 capas
Solo en cama: No (para aberturas laterales)
```

### Soportes pintados (control manual)
Usar "Support painting" en Bambu Studio para:
- Forzar soporte en puentes cortos que el slicer ignora
- Eliminar soporte en zonas accesibles para post-procesado
- Controlar exactamente dónde se genera soporte

## Post-procesado

### Insertos roscados (heat-set inserts)
1. Agujero en diseño: Ø4.2mm para inserto M3
2. Calentar soldador a 220°C (PLA) o 260°C (PETG)
3. Colocar inserto en punta del soldador
4. Presionar verticalmente, lento y constante
5. Dejar enfriar antes de atornillar

### Lijado y acabado
1. Lija 200 → 400 → 800 para superficie lisa
2. Imprimación spray para pintar
3. Acetone vapor smoothing solo para ABS (en ventilación)

### Unión de piezas
- **Cianoacrilato (CA)**: unión rápida PLA/PETG, frágil
- **Epoxi 5min**: unión fuerte, tiempo de trabajo
- **Soldadura por fricción**: rotary tool con filamento como "varilla de soldadura"
- **Tornillos M3**: usar insertos roscados o agujeros autorroscantes

## Checklist pre-impresión

- [ ] STL sin errores (verificar en Bambu Studio: reparar si hay avisos)
- [ ] Orientación óptima (mínimos soportes, cara estética arriba)
- [ ] Primera capa bien adherida (calibrar con Bambu Auto-Calibration)
- [ ] Material correcto seleccionado en AMS
- [ ] Cama limpia (IPA para PLA/PETG, pegamento para ABS)
- [ ] Soportes configurados donde necesario
- [ ] Verificar tiempo estimado y material necesario
- [ ] Timelapse activado si se quiere documentar
