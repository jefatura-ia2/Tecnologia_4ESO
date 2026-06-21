# Ejemplo: Estación Meteorológica IoT

Ejemplo de proyecto completo generado con esta skill.

## Requisitos
- Medir: temperatura, humedad, presión, luz ambiental
- Display OLED local + dashboard web
- Enviar datos por MQTT cada 5 minutos
- Deep sleep entre lecturas (alimentado por batería)
- Carcasa impresa en PETG para exterior (bajo tejado)

## BOM resumido
- ESP32 DevKit v1
- BME280 (temp/hum/presión)
- BH1750 (luz)
- SSD1306 OLED 0.96"
- Batería 18650 + módulo TP4056
- Carcasa PETG con ranuras de ventilación

## Invocación de la skill
```
/esp32-automation Estación meteorológica IoT con sensores de temperatura,
humedad, presión y luz. Display OLED. Datos por MQTT. Alimentación por
batería 18650 con deep sleep. Carcasa para exterior.
```
