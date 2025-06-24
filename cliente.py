# Guarda como client.py en la computadora 2

import requests
import os
import random
import time
import sys
import socketserver

def main():
    # URL del servidor (ajustar según la IP de la computadora 1)
    server_url = "http://127.0.0.1:8080"  # Reemplazar X con la IP correcta
    
    print(f"Cliente de prueba para MitM - Conectando a {server_url}")
    print("=" * 50)
    
    while True:
        print("\nSeleccione una acción:")
        print("1. Hacer login")
        print("2. Descargar archivo")
        print("3. Subir archivo")
        print("4. Simulación automática (todas las acciones)")
        print("0. Salir")
        
        choice = input("> ")
        
        if choice == "1":
            do_login(server_url)
        elif choice == "2":
            download_file(server_url)
        elif choice == "3":
            upload_file(server_url)
        elif choice == "4":
            automatic_simulation(server_url)
        elif choice == "0":
            break
        else:
            print("Opción no válida")

def do_login(server_url):
    """Simula un inicio de sesión"""
    username = input("Usuario: ")
    password = input("Contraseña: ")
    
    try:
        response = requests.post(f"{server_url}/login", data={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            print(f"Login exitoso como {username}")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error de conexión: {e}")

def download_file(server_url):
    """Descarga un archivo del servidor"""
    files = ["test1.jpg", "test2.png", "documento.pdf"]
    
    print("Archivos disponibles:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    
    choice = input("Seleccione archivo (número): ")
    try:
        index = int(choice) - 1
        if 0 <= index < len(files):
            filename = files[index]
            print(f"Descargando {filename}...")
            
            response = requests.get(f"{server_url}/images/{filename}", stream=True)
            
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Archivo guardado: {filename} ({os.path.getsize(filename)} bytes)")
            else:
                print(f"Error: {response.status_code}")
        else:
            print("Selección inválida")
    except Exception as e:
        print(f"Error: {e}")

def generate_random_file(filename, size_kb):
    """Genera un archivo con contenido aleatorio"""
    size_bytes = size_kb * 1024
    with open(filename, 'wb') as f:
        f.write(os.urandom(size_bytes))
    return filename

def upload_file(server_url):
    """Sube un archivo al servidor"""
    print("1. Usar archivo existente")
    print("2. Generar archivo aleatorio")
    choice = input("> ")
    
    filename = None
    if choice == "1":
        filename = input("Nombre del archivo: ")
        if not os.path.exists(filename):
            print(f"Error: El archivo {filename} no existe")
            return
    else:
        size = input("Tamaño en KB (p.ej. 100): ")
        try:
            size_kb = int(size)
            file_type = random.choice([".txt", ".jpg", ".pdf", ".doc"])
            filename = f"random_file_{int(time.time())}{file_type}"
            generate_random_file(filename, size_kb)
            print(f"Archivo generado: {filename}")
        except:
            print("Tamaño inválido")
            return
    
    try:
        with open(filename, 'rb') as f:
            files = {'file': (os.path.basename(filename), f)}
            response = requests.post(f"{server_url}/upload", files=files)
            
        if response.status_code == 200:
            print(f"Archivo subido exitosamente: {filename}")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error de conexión: {e}")

def automatic_simulation(server_url):
    """Ejecuta una simulación automática de acciones"""
    try:
        print("Iniciando simulación automática...")
        print("-" * 50)
        
        # Simular login
        print("1. Haciendo login...")
        username = f"usuario_{int(time.time())}"
        password = f"pass_{random.randint(1000, 9999)}"
        
        response = requests.post(f"{server_url}/login", data={
            "username": username,
            "password": password
        })
        print(f"   Login como {username}:{password} - Status: {response.status_code}")
        time.sleep(2)
        
        # Descargar archivos
        print("2. Descargando archivos...")
        files = ["test1.jpg", "test2.png", "documento.pdf"]
        for filename in files:
            print(f"   Descargando {filename}...")
            response = requests.get(f"{server_url}/images/{filename}", stream=True)
            
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"   Guardado: {filename} ({os.path.getsize(filename)} bytes)")
            time.sleep(1)
        
        # Subir archivos
        print("3. Subiendo archivos...")
        for i in range(3):
            size_kb = random.randint(50, 200)
            file_types = [".txt", ".jpg", ".pdf", ".doc"]
            file_type = random.choice(file_types)
            filename = f"upload_file_{i}{file_type}"
            
            generate_random_file(filename, size_kb)
            print(f"   Subiendo {filename} ({size_kb} KB)...")
            
            with open(filename, 'rb') as f:
                files = {'file': (filename, f)}
                response = requests.post(f"{server_url}/upload", files=files)
                
            print(f"   Status: {response.status_code}")
            time.sleep(1)
            
        print("-" * 50)
        print("Simulación completada.")
        
    except Exception as e:
        print(f"Error en simulación: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
            # Ejecutar como servidor
            from http.server import SimpleHTTPRequestHandler
            handler = SimpleHTTPRequestHandler
            PORT = 8080  # Define el puerto del servidor
            with socketserver.TCPServer(("", PORT), handler) as httpd:
                print(f"Servidor ejecutándose en puerto {PORT}")
                httpd.serve_forever()
    else:
        # Ejecutar como cliente
        main()