# server.py

import http.server
import socketserver
import os
from email.parser import BytesParser
from email.policy import default
import random

PORT = 8080
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class TestHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Servidor de Prueba</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 600px; margin: 0 auto; }
                    .form-group { margin-bottom: 15px; }
                    input[type=text], input[type=password], input[type=file] { width: 100%; padding: 8px; }
                    input[type=submit] { padding: 10px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
                    h2 { margin-top: 30px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Servidor de Prueba para MitM</h1>
                    
                    <h2>Login</h2>
                    <form action="/login" method="post">
                        <div class="form-group">
                            <label>Usuario:</label>
                            <input type="text" name="username" required>
                        </div>
                        <div class="form-group">
                            <label>Password:</label>
                            <input type="password" name="password" required>
                        </div>
                        <input type="submit" value="Iniciar sesión">
                    </form>
                    
                    <h2>Subir Archivo</h2>
                    <form action="/upload" method="post" enctype="multipart/form-data">
                        <div class="form-group">
                            <label>Archivo:</label>
                            <input type="file" name="file" required>
                        </div>
                        <input type="submit" value="Subir archivo">
                    </form>
                    
                    <h2>Descargar Imagenes </h2>
                    <ul>
                        <li><a href="/images/test1.jpg">test1.jpg</a></li>
                        <li><a href="/images/test2.png">test2.png</a></li>
                        <li><a href="/images/documento.pdf">documento.pdf</a></li>
                    </ul>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path.startswith('/images/'):
            filename = self.path.split('/')[-1]
            content_type = 'application/octet-stream'
            file_content = None
            
            if filename == 'test1.jpg':
                content_type = 'image/jpeg'
                file_content = self.generate_random_bytes(15000)
            elif filename == 'test2.png':
                content_type = 'image/png'
                file_content = self.generate_random_bytes(20000)
            elif filename == 'documento.pdf':
                content_type = 'application/pdf'
                file_content = self.generate_random_bytes(30000)
            
            if file_content:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Content-Length', str(len(file_content)))
                self.end_headers()
                self.wfile.write(file_content)
            else:
                self.send_error(404, "Archivo no encontrado")
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            fields = dict(x.split('=') for x in post_data.split('&'))
            
            username = fields.get('username', '')
            password = fields.get('password', '')
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            response = f"""
            <!DOCTYPE html>
            <html>
            <head><title>Login Exitoso</title></head>
            <body>
                <h1>Login Exitoso</h1>
                <p>Bienvenido, {username}!</p>
                <p><a href="/">Volver al inicio</a></p>
            </body>
            </html>
            """
            self.wfile.write(response.encode())
            print(f"Login recibido: Usuario={username}, Contraseña={password}")
        
        elif self.path == '/upload':
            content_type = self.headers['Content-Type']
            if not content_type or not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Se requiere multipart/form-data")
                return
                
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            headers = BytesParser(policy=default).parsebytes(self.headers.as_bytes())
            
            boundary = headers.get_boundary()
            if boundary is None:
                self.send_error(400, "No se encontró el boundary en los headers")
                return
                
            parts = body.split(b'--' + boundary.encode())
            filename = None
            
            for part in parts:
                if b'Content-Disposition' in part:
                    disposition = part.split(b'\r\n')[1]
                    if b'filename=' in disposition:
                        filename = disposition.split(b'filename="')[1].split(b'"')[0].decode()
                        filepath = os.path.join(UPLOAD_DIR, filename)
                        file_data = part.split(b'\r\n\r\n', 1)[1].rsplit(b'\r\n', 1)[0]
                        
                        with open(filepath, 'wb') as f:
                            f.write(file_data)
                        break
            
            if filename:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                response = f"""
                <!DOCTYPE html>
                <html>
                <head><title>Subida Exitosa</title></head>
                <body>
                    <h1>Archivo Subido Correctamente</h1>
                    <p>Archivo guardado: {filename}</p>
                    <p><a href="/">Volver al inicio</a></p>
                </body>
                </html>
                """
                self.wfile.write(response.encode())
                print(f"Archivo subido: {filename}")
            else:
                self.send_error(400, "No se encontró archivo")
        else:
            self.send_error(404, "Ruta no encontrada")

    def generate_random_bytes(self, size):
        return bytes([random.randint(0, 255) for _ in range(size)])

# --- Configurar y arrancar el servidor ---
with socketserver.TCPServer(("", PORT), TestHTTPRequestHandler) as httpd:
    print(f"Servidor escuchando en el puerto {PORT}")
    httpd.serve_forever()