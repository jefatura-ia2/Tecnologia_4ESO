#!/usr/bin/env python3
"""Genera la estructura de carpetas para un nuevo proyecto ESP32."""

import os
import sys

def scaffold(project_name, output_dir="."):
    base = os.path.join(output_dir, project_name)
    dirs = [
        "firmware/lib",
        "firmware/web",
        "firmware/utils",
        "3d-design/stl",
        "3d-design/fusion360",
        "docs/images",
        "pcb",
    ]
    files = {
        "firmware/boot.py": '# boot.py — WiFi configuration\nimport network\n',
        "firmware/main.py": '# main.py — Entry point\nimport uasyncio as asyncio\n',
        "firmware/config.py": '# config.py — Project configuration\nfrom micropython import const\n',
        "firmware/lib/__init__.py": "",
        "firmware/lib/sensors.py": "# Sensor classes\n",
        "firmware/lib/actuators.py": "# Actuator classes\n",
        "firmware/web/server.py": "# HTTP + WebSocket server\n",
        "firmware/web/index.html": "<!DOCTYPE html>\n<html><head><title>ESP32</title></head><body></body></html>\n",
        "firmware/utils/logger.py": "# Logging utility\n",
        "firmware/utils/watchdog.py": "# Watchdog manager\n",
        "docs/README.md": f"# {project_name}\n\nProyecto generado con esp32-automation skill.\n",
        "docs/BOM.md": "# Bill of Materials\n\n| # | Componente | Cantidad | Precio |\n|---|-----------|----------|--------|\n",
        "docs/WIRING.md": "# Diagrama de Cableado\n\n## Conexiones\n",
    }

    for d in dirs:
        os.makedirs(os.path.join(base, d), exist_ok=True)

    for filepath, content in files.items():
        full_path = os.path.join(base, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    print(f"Proyecto '{project_name}' creado en {os.path.abspath(base)}")
    print(f"  {len(dirs)} directorios, {len(files)} archivos")

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "mi-proyecto-esp32"
    out = sys.argv[2] if len(sys.argv) > 2 else "."
    scaffold(name, out)
