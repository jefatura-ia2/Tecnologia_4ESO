# [Nombre del Proyecto]

> Breve descripción del proyecto en una frase.

## Índice

1. Descripción general
2. Requisitos
3. Bill of Materials (BOM)
4. Esquema de conexiones
5. Firmware
6. Interfaz web
7. Diseño 3D
8. Fabricación e impresión
9. Guía de ensamblaje
10. Troubleshooting

---

## 1. Descripción general

**Objetivo**: [Qué hace el sistema]
**Entorno**: [Dónde se instala]
**Alimentación**: [Fuente de energía]
**Comunicación**: [WiFi/BLE/MQTT/etc.]

### Diagrama de bloques

```
[Sensor 1] ──┐
[Sensor 2] ──┤
             ├── [ESP32] ──┬── [Actuador 1]
[Botón]    ──┤             ├── [Actuador 2]
[Config]   ──┘             ├── [Display]
                           └── [Web UI / MQTT]
```

---

## 2. Requisitos

### Funcionales
- [ ] RF1: [Descripción]
- [ ] RF2: [Descripción]

### No funcionales
- [ ] RNF1: Tiempo de respuesta < [X]ms
- [ ] RNF2: Consumo máximo [X]mA
- [ ] RNF3: Resistencia a [condiciones]

---

## 3. Bill of Materials (BOM)

| # | Componente | Cantidad | Especificación | Enlace | Precio aprox |
|---|-----------|----------|----------------|--------|-------------|
| 1 | ESP32 DevKit | 1 | WROOM-32 | — | €5 |
| 2 | — | — | — | — | — |

**Coste total estimado**: €XX

---

## 4. Esquema de conexiones

### Tabla de pines

| ESP32 GPIO | Componente | Pin del módulo | Función | Notas |
|-----------|-----------|---------------|---------|-------|
| — | — | — | — | — |

### Diagrama de cableado

[Descripción textual detallada del circuito]

### Notas de alimentación

- Consumo total estimado: [X]mA
- Fuente recomendada: [especificación]
- Protecciones: [fusible, diodo, etc.]

---

## 5. Firmware

### Estructura de archivos
```
firmware/
├── boot.py
├── main.py
├── config.py
├── lib/
├── web/
└── utils/
```

### Instalación
1. Instalar MicroPython en ESP32: `esptool.py --port COMX erase_flash`
2. Flashear firmware: `esptool.py --port COMX write_flash -z 0x1000 esp32-xxx.bin`
3. Copiar archivos: `mpremote connect COMX cp -r firmware/ :`
4. Reiniciar ESP32

### Configuración
Editar `config.py` con los parámetros de red y proyecto.

---

## 6. Interfaz web

### Funcionalidades
- Dashboard: [descripción]
- Controles: [descripción]
- Configuración: [descripción]

### Acceso
- URL: `http://[IP_ESP32]/`
- AP mode: `http://192.168.4.1/` (SSID: ESP32-Config)

---

## 7. Diseño 3D

### Archivos
- `proyecto_base_v1.stl` — Base de la carcasa
- `proyecto_tapa_v1.stl` — Tapa de la carcasa
- `proyecto_v1.f3d` — Archivo fuente Fusion 360

### Parámetros principales
| Parámetro | Valor | Ajustable |
|-----------|-------|-----------|
| — | — | — |

### Instrucciones Fusion 360
[Paso a paso para modelar desde cero]

---

## 8. Fabricación e impresión

### Perfil de impresión
- **Material**: [PLA/PETG/ABS]
- **Nozzle**: 0.4mm
- **Altura de capa**: 0.20mm
- **Relleno**: [X]% [patrón]
- **Perímetros**: [N]
- **Soportes**: [Sí/No, tipo]
- **Tiempo estimado**: [X]h [X]min

### Post-procesado
1. [Pasos de acabado]

---

## 9. Guía de ensamblaje

### Orden de montaje
1. [ ] [Paso 1]
2. [ ] [Paso 2]

### Checklist de verificación (antes de energizar)
- [ ] Verificar polaridad de alimentación
- [ ] Comprobar continuidad de GND
- [ ] Verificar que no hay cortocircuitos
- [ ] Conectar USB y verificar consola serial
- [ ] Probar modo test: [comando]

---

## 10. Troubleshooting

| Problema | Posible causa | Solución |
|----------|--------------|----------|
| No enciende | Alimentación incorrecta | Verificar voltaje y polaridad |
| No conecta WiFi | Credenciales incorrectas | Verificar config.py, usar AP mode |
| Sensor lee 0 | Cable suelto | Revisar conexiones I2C/SPI |
| — | — | — |
