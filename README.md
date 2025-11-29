# Escáner de Puertos Multihilo (Red Team Tool)

Herramienta de línea de comandos (CLI) desarrollada en Python para el escaneo rápido y eficiente de puertos TCP/UDP. Implementa concurrencia mediante hilos (threading), detección inteligente de servicios y técnicas de evasión básicas.

Subo también un documento de texto hecho por mi donde están los 1000 puertos más comunmente usados. El scanner usa este archivo para el escaneo por defecto, guardalo todo junto.

## 📋 Características
* **Multihilo:** Escaneo concurrente de cientos de puertos en segundos.
* **Híbrido:** Soporte para protocolos TCP (Connect Scan) y UDP.
* **Banner Grabbing Inteligente:** Limpieza automática de respuestas y detección de servicios.
* **Modo Sigilo:** Aleatorización de puertos, User-Agent falso y control de delay (Jitter).
* **Reportes:** Exportación de resultados a formato JSON.

## 🛠️ Instalación
No requiere librerías externas. Funciona con Python 3.x nativo.

## 💻 Uso
usage: scanner.py [-h] -t TARGET [-o OUTPUT] [--threads THREADS] [-all] [-u] [--delay DELAY]

Escáner Multihilo TCP/UDP Mejorado

Options:

    -h, --help           show this help message and exit
    
    -t, --target TARGET  IP Objetivo
    
    -o, --output OUTPUT  Salida JSON
    
    --threads THREADS    Hilos
    
    -all, --all-ports    Escanear 1-65535

    -u, --udp            Activar escaneo UDP (Por defecto es TCP)

    --delay DELAY        Segundos de espera entre peticiones (Evasión)


Por defecto:

    OUTPUT: reporte_scan.json
    
    THREADS: 250
    
    (Sin -u): Solo escanea puertos TCP
    
    (Sin -all): 1000 puertos más comunmente usados
    
    DELAY: 0.0

## ⚠️ Nota Legal
No me hago responsable de nada para lo que se use esta herramienta. Se ha diseñado únicamente con fines educativos. Es ilegal escanear IPs públicas. Puedes usar "scanme.nmap.org" u otra IP exclusivamente dentro de un entorno de prácticas privado.
