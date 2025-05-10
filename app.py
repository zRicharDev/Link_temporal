from flask import Flask, send_file, abort
import os
import uuid
import time
import threading
from PIL import ImageGrab

app = Flask(__name__)

# Diccionario para almacenar tokens y su fecha de expiración
capturas = {}

# Carpeta temporal
CAPTURA_DIR = "capturas_temporal"
os.makedirs(CAPTURA_DIR, exist_ok=True)

# Guardar la captura y generar el token
def crear_captura():
    token = str(uuid.uuid4())
    archivo = os.path.join(CAPTURA_DIR, f"{token}.png")
    imagen = ImageGrab.grab()
    imagen.save(archivo)

    capturas[token] = time.time() + 20  # expira en 10 minutos

    # Programar limpieza
    threading.Timer(600, lambda: eliminar_captura(token)).start()

    return f"http://localhost:5000/captura/{token}"

# Eliminar archivo e invalidar token
def eliminar_captura(token):
    archivo = os.path.join(CAPTURA_DIR, f"{token}.png")
    if os.path.exists(archivo):
        os.remove(archivo)
    capturas.pop(token, None)

@app.route("/captura/<token>")
def servir_captura(token):
    if token in capturas and time.time() < capturas[token]:
        archivo = os.path.join(CAPTURA_DIR, f"{token}.png")
        if os.path.exists(archivo):
            return send_file(archivo, mimetype="image/png")
    return abort(404)

if __name__ == "__main__":
    print("Enlace generado:", crear_captura())
    app.run(debug=True)