from flask import Flask, request
import requests
import os
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)

# 🔥 CONEXIÓN A MONGODB
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client["xyra_db"]
collection = db["users"]

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

    entry = {
        "user_id": user_id,
        "username": username,
        "ip": ip,
        "country": country,
        "city": city,
        "device": user_agent,
        "vpn": vpn,
        "time": str(datetime.now())
    }

    # 🔥 GUARDAR EN MONGO
    collection.insert_one(entry)

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

    users = list(collection.find().sort("_id", -1))

    html = "<h2>📊 PANEL XYRA</h2>"

    for user in users:
        html += f"""
        <hr>
        <b>ID:</b> {user.get('user_id')} <br>
        <b>User:</b> @{user.get('username')} <br>
        <b>IP:</b> {user.get('ip')} <br>
        <b>País:</b> {user.get('country')} <br>
        <b>Ciudad:</b> {user.get('city')} <br>
        <b>Dispositivo:</b> {user.get('device')} <br>
        <b>VPN:</b> {user.get('vpn')} <br>
        <b>Fecha:</b> {user.get('time')} <br>
        """

    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
