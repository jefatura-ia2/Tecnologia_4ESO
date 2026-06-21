# Fusion 360 — Guía de Diseño para Carcasas Electrónicas

## Flujo de trabajo paramétrico

### 1. Crear parámetros de usuario

Antes de modelar, definir todos los parámetros en Modify > Change Parameters > User Parameters:

| Parámetro | Ejemplo | Descripción |
|-----------|---------|-------------|
| `wall_thickness` | 2.0 mm | Espesor de pared |
| `board_width` | 25.4 mm | Ancho PCB/placa |
| `board_length` | 48.26 mm | Largo PCB/placa |
| `board_height` | 1.6 mm | Espesor PCB |
| `clearance` | 0.3 mm | Holgura ensamblaje |
| `screw_diameter` | 3.0 mm | Diámetro tornillo |
| `screw_pillar_od` | 6.0 mm | Diámetro ext pilar |
| `component_height` | 15.0 mm | Altura máx componentes |
| `lid_overlap` | 3.0 mm | Solape tapa-base |
| `fillet_radius` | 2.0 mm | Radio de redondeo ext |
| `vent_width` | 1.5 mm | Ancho ranura ventilación |
| `vent_spacing` | 3.0 mm | Espaciado entre ranuras |
| `cable_diameter` | 5.0 mm | Diámetro pasacables |

### 2. Secuencia de modelado recomendada

1. **Sketch base** → rectángulo `board_width + 2*wall_thickness + 2*clearance` x `board_length + ...`
2. **Extruir caja** → altura = `wall_thickness + component_height + clearance`
3. **Shell** → vaciar con espesor `wall_thickness`, cara superior abierta
4. **Pilares tornillos** → cilindros en esquinas, `screw_pillar_od`, agujero `screw_diameter - 0.5`
5. **Rieles PCB** → extrusión de 1mm para apoyo de placa a altura `wall_thickness`
6. **Aberturas** → sketch en caras laterales para USB, conectores, LEDs
7. **Ventilación** → patrón rectangular de ranuras en cara superior/lateral
8. **Guías de cables** → canales de 2mm para enrutamiento interno
9. **Tapa** → nuevo cuerpo, con labio de encaje `lid_overlap`
10. **Snap-fits o tornillos** → mecanismo de cierre
11. **Fillets** → redondeos exteriores `fillet_radius`
12. **Chaflanes** → 0.4mm en aristas de contacto con cama

### 3. Reglas de diseño para impresión FDM

| Característica | Mínimo | Recomendado | Notas |
|----------------|--------|-------------|-------|
| Espesor pared | 1.2mm | 1.6-2.0mm | Múltiplo del ancho de nozzle |
| Agujeros tornillos | Ø nominal - 0.5mm | — | El plástico se contrae |
| Tolerancia ajuste presión | 0.15mm | 0.2-0.3mm | Por lado |
| Tolerancia ajuste holgado | 0.3mm | 0.4-0.5mm | Por lado |
| Puentes sin soporte | — | ≤40mm | Con enfriamiento adecuado |
| Voladizo sin soporte | ≤45° | ≤40° | Desde vertical |
| Texto grabado | Profundidad 0.6mm | 0.8mm | Ancho mín letra 1mm |
| Texto en relieve | Altura 0.6mm | 0.8mm | Ancho mín letra 1.5mm |
| Snap-fit espesor | 1.5mm | 2.0mm | PLA: cuidado con fragilidad |
| Pin alineamiento | Ø3mm holgura 0.2mm | — | Para alinear tapa/base |

### 4. Diseño del labio de encaje (tapa)

```
SECCIÓN TRANSVERSAL:

  Base:                    Tapa:
  ┌─────────────┐          ┌─────────────┐
  │             │          │             │
  │  ┌───────┐  │          │  ┌───────┐  │
  │  │ labio │  │    →←    │  │ranura │  │
  │  │ 1.5mm │  │  0.3mm   │  │1.8mm  │  │
  │  └───────┘  │          │  └───────┘  │
  │             │          └─────────────┘
  └─────────────┘

  Labio base: wall_thickness * 0.6
  Ranura tapa: labio + clearance (0.3mm)
  Profundidad: lid_overlap (3mm)
```

### 5. Aberturas para conectores ESP32

| Conector | Ancho | Alto | Offset desde PCB |
|----------|-------|------|-------------------|
| Micro USB | 8mm | 3.5mm | 0mm (ras de placa) |
| USB-C | 9.5mm | 3.5mm | 0mm |
| Jack barrel 5.5mm | Ø 8mm | — | Centro a 5mm de PCB |
| Pin headers (fila) | n×2.54mm + 1mm | 8.5mm | 0mm |
| Botón táctil | Ø 4mm | — | Enrasado con carcasa |
| LED 3mm | Ø 3.2mm | — | — |
| LED 5mm | Ø 5.2mm | — | — |
| Display OLED 0.96" | 26×14mm | — | Ventana en tapa |
| Cables (pasacables) | Ø cable + 1mm | — | Con strain relief |

### 6. Exportación para impresión

1. **Seleccionar cuerpo** → clic derecho → "Save as STL"
2. **Refinamiento**: High (recomendado para piezas pequeñas)
3. **Exportar base y tapa por separado** como STL independientes
4. **Nombrar**: `proyecto_base_v1.stl`, `proyecto_tapa_v1.stl`
5. **Verificar**: en Bambu Studio importar y comprobar orientación

### 7. Consideraciones de ensamblaje

- **Insertos roscados M3**: agujero Ø4.2mm, instalar con soldador a 220°C
- **Tornillos autorroscantes M2.5**: agujero Ø2.0mm, profundidad 8mm
- **Pies de goma**: recesos Ø10mm × 1mm en base inferior
- **Alivio de tensión de cables**: clip o ranura en punto de entrada
- **Etiqueta**: receso rectangular 0.5mm profundidad para pegatina
