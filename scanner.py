import socket
import threading
from queue import Queue
import sys
import json
import argparse
import os
import string
import random
import time


print_lock = threading.Lock()
resultados = []
progreso_contador = [0]

def limpiar_banner_texto(banner):
    if not banner:
        return "Sin banner"
    
    caracteres_seguros = set(string.ascii_letters + string.digits + string.punctuation + " ")
    

    raros = sum(1 for c in banner if c not in caracteres_seguros)
    

    if raros > len(banner) * 0.2:
        return "[Datos Binarios o Cifrados - No legible]"
    
    return banner

def obtener_nombre_servicio(puerto, protocolo='tcp'):
    try:
        return socket.getservbyport(puerto, protocolo)
    except:
        return "desconocido"


def escanear_tcp(ip, puerto):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    banner = None
    
    try:
        resultado = s.connect_ex((ip, puerto))
        if resultado == 0:

            try:
                mensaje = (
                    b"HEAD / HTTP/1.1\r\n"
                    b"Host: " + str(ip).encode() + b"\r\n"
                    b"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0\r\n"
                    b"Connection: close\r\n\r\n"
                )
                s.send(mensaje)
                datos = s.recv(1024)
                if datos:
                    banner = datos.decode(errors='ignore').split('\n')[0].strip()
            except:
                pass
            
            s.close()
            return {"puerto": puerto, "protocolo": "TCP", "estado": "abierto", "banner": banner or "Sin banner"}
        s.close()
    except:
        pass
    return None


def escanear_udp(ip, puerto):
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2.0) 
    banner = None
    
    try:

        s.sendto(b'Hello', (ip, puerto))
        

        datos, _ = s.recvfrom(1024)
        banner = datos.decode(errors='ignore').split('\n')[0].strip()
        
        return {"puerto": puerto, "protocolo": "UDP", "estado": "abierto", "banner": banner or "Respuesta recibida"}
    except socket.timeout:

        return None
    except:
        return None
    finally:
        s.close()

def worker(ip, cola, total_puertos, usar_udp, delay):
    while not cola.empty():
        puerto = cola.get()

        if delay > 0:
            tiempo_real = delay * random.uniform(0.8, 1.2)
            time.sleep(tiempo_real)
        
        if usar_udp:
            info = escanear_udp(ip, puerto)
        else:
            info = escanear_tcp(ip, puerto)
        
        if info:
            nombre_servicio = obtener_nombre_servicio(puerto, "udp" if usar_udp else "tcp")
            

            banner_seguro = limpiar_banner_texto(info['banner'])
            
            info['servicio'] = nombre_servicio
            info['banner'] = banner_seguro 
            resultados.append(info)
            
            with print_lock:

                sys.stdout.write('\r' + ' ' * 90 + '\r')
                

                print(f"[+] {info['protocolo']} {info['puerto']} ({nombre_servicio}): {banner_seguro}")
                

                sys.stdout.flush()
        
        progreso_contador[0] += 1
        imprimir_progreso(progreso_contador[0], total_puertos)
        cola.task_done()        

def imprimir_progreso(actual, total):
    if total == 0: return
    porcentaje = (actual / total) * 100
    barra_len = 30
    lleno = int(barra_len * actual // total)
    barra = "█" * lleno + "-" * (barra_len - lleno)

    sys.stdout.write(f"\rEscaneando: |{barra}| {porcentaje:.1f}% Completado")
    sys.stdout.flush()

def guardar_reporte(datos, archivo):
    with open(archivo, "w") as f:
        json.dump(datos, f, indent=4)
    print(f"\n[i] Reporte guardado en {archivo}")

def obtener_puertos_archivo(ruta):
    if not os.path.exists(ruta): return []
    res = []
    with open(ruta, 'r') as f:
        for l in f:
            if l.strip().isdigit(): res.append(int(l.strip()))
    return res


def main():
    parser = argparse.ArgumentParser(description="Escáner Multihilo TCP/UDP Mejorado")
    
    parser.add_argument("-t", "--target", required=True, help="IP Objetivo")
    parser.add_argument("-o", "--output", default="reporte_scan.json", help="Salida JSON")
    parser.add_argument("--threads", type=int, default=250, help="Hilos")
    parser.add_argument("-all", "--all-ports", action="store_true", help="Escanear 1-65535")
    parser.add_argument("-u", "--udp", action="store_true", help="Activar escaneo UDP (Por defecto es TCP)")
    parser.add_argument("--delay", type=float, default=0.0, help="Segundos de espera entre peticiones (Evasión)")

    args = parser.parse_args()


    try:
        target_ip = socket.gethostbyname(args.target)
    except:
        print("Error resolviendo IP")
        sys.exit()


    lista_puertos = []
    if args.all_ports:
        lista_puertos = list(range(1, 65536))
    else:
        lista_puertos = obtener_puertos_archivo("top-1000-puertos.txt")
        if not lista_puertos:
            print("[i] No se encontró archivo de puertos, usando 1-1024 por defecto.")
            lista_puertos = list(range(1, 1025))

    random.shuffle(lista_puertos)        

    modo = "UDP" if args.udp else "TCP"
    print(f"\n--- Objetivo: {args.target} ({target_ip}) ---")
    print(f"--- Modo: {modo} | Puertos: {len(lista_puertos)} | Hilos: {args.threads} ---\n")

    cola = Queue()
    for p in lista_puertos: cola.put(p)

    hilos = []
    num_hilos = min(args.threads, len(lista_puertos))
    
    for _ in range(num_hilos):
        t = threading.Thread(target=worker, args=(target_ip, cola, len(lista_puertos), args.udp, args.delay))
        t.daemon = True
        t.start()
        hilos.append(t)

    cola.join()
    imprimir_progreso(len(lista_puertos), len(lista_puertos))
    
    if resultados:
        guardar_reporte(resultados, args.output)
    else:
        print("\nNo se encontraron puertos abiertos que respondieran.")

if __name__ == "__main__":
    main()