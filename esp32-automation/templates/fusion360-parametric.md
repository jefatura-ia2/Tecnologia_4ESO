# Parámetros Fusion 360 — [Nombre del Proyecto]

## Parámetros de usuario (Modify > Change Parameters)

Crear estos parámetros antes de comenzar el modelado:

### Dimensiones principales
| Nombre | Expresión | Valor | Comentario |
|--------|-----------|-------|------------|
| `board_width` | — mm | — | Ancho del PCB/placa |
| `board_length` | — mm | — | Largo del PCB/placa |
| `board_height` | 1.6 mm | 1.6 | Espesor del PCB |
| `component_height` | — mm | — | Altura máx componentes sobre PCB |

### Carcasa
| Nombre | Expresión | Valor | Comentario |
|--------|-----------|-------|------------|
| `wall` | 2.0 mm | 2.0 | Espesor de pared |
| `clearance` | 0.3 mm | 0.3 | Holgura PCB↔carcasa |
| `lid_overlap` | 3.0 mm | 3.0 | Profundidad encaje tapa |
| `fillet_ext` | 2.0 mm | 2.0 | Radio redondeo exterior |
| `chamfer_base` | 0.4 mm | 0.4 | Chaflán base (elephant foot) |

### Montaje
| Nombre | Expresión | Valor | Comentario |
|--------|-----------|-------|------------|
| `screw_d` | 3.0 mm | 3.0 | Diámetro tornillo |
| `screw_hole` | `screw_d - 0.5 mm` | 2.5 | Agujero para autorroscante |
| `insert_hole` | `screw_d + 1.2 mm` | 4.2 | Agujero para inserto roscado |
| `pillar_od` | `screw_d * 2` | 6.0 | Diámetro ext pilar |
| `pillar_height` | `component_height + board_height` | — | Altura del pilar |

### Calculados (no editar)
| Nombre | Expresión | Comentario |
|--------|-----------|------------|
| `inner_w` | `board_width + 2 * clearance` | Ancho interior |
| `inner_l` | `board_length + 2 * clearance` | Largo interior |
| `outer_w` | `inner_w + 2 * wall` | Ancho exterior |
| `outer_l` | `inner_l + 2 * wall` | Largo exterior |
| `box_h` | `wall + component_height + clearance + board_height` | Altura caja |

## Secuencia de modelado

1. Sketch en plano XY → Rectángulo centrado `outer_w × outer_l`
2. Extrude → `box_h`
3. Shell → espesor `wall`, cara superior abierta
4. [Continuar según proyecto específico...]
