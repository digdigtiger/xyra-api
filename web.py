from flask import Flask, request
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

DB_FILE = "data.json"

# Crear DB si no existe
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump([], f)

def save_data(entry):
    with open(DB_FILE, "r") as f:
        data = json.load(f)

    data.append(entry)

    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# 🌐 VERIFICACIÓN
@app.route("/")
def verify():
    user_id = request.args.get("id")
    username = request.args.get("user")

    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    # INFO IP
    try:
        res = requests.get(f"https://ipapi.co/{ip}/json/").json()
        country = res.get("country_name")
        city = res.get("city")
        vpn = res.get("proxy")
    except:
        country = "Unknown"
        city = "Unknown"
        vpn = False

    # FOTO TELEGRAM (si luego conectas bot)
    photo = f"https://api.telegram.org/file/botTOKEN/photos/{user_id}.jpg"

    entry = {
        "user_id": user_id,
        "username": username,
        "ip": ip,
        "country": country,
        "city": city,
        "device": user_agent,
        "vpn": vpn,
        "photo": photo,
        "time": str(datetime.now())
    }

    save_data(entry)

    return f"""
    <h2>✅ Verificación completada</h2>
    <p>Ya puedes usar Xyra @{username}</p>
    <a href="https://t.me/TU_GRUPO">🚀 Unirse a la comunidad</a>

    <p style='margin-top:20px;font-size:12px;color:gray;'>
    Al continuar aceptas el uso de datos técnicos básicos para verificación.
    </p>
    """

# 🔒 PANEL PRIVADO
@app.route("/admin")
def admin():
    password = request.args.get("pass")

    if password != "1234":
        return "❌ Acceso denegado"

    with open(DB_FILE, "r") as f:
        data = json.load(f)

    html = "<h2>📊 PANEL XYRA</h2>"

    for user in data[::-1]:
        html += f"""
        <hr>
        <b>ID:</b> {user['user_id']} <br>
        <b>User:</b> @{user['username']} <br>
        <b>IP:</b> {user['ip']} <br>
        <b>País:</b> {user['country']} <br>
        <b>Ciudad:</b> {user['city']} <br>
        <b>Dispositivo:</b> {user['device']} <br>
        <b>VPN:</b> {user['vpn']} <br>
        <b>Fecha:</b> {user['time']} <br>
        """

    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)