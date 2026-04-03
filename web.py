from flask import Flask, request
import requests
import os
from datetime import datetime
from pymongo import MongoClient, errors

app = Flask(__name__)

# 🔥 CONEXIÓN A MONGODB CON TLS Y TIMEOUT
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    print("⚠️ MONGO_URI no está definido en variables de entorno")
client = MongoClient(MONGO_URI, tls=True, serverSelectionTimeoutMS=10000)

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
        res = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5).json()
        country = res.get("country_name", "Unknown")
        city = res.get("city", "Unknown")
        vpn = res.get("proxy", False)
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

    # 🔥 GUARDAR EN MONGO CON MANEJO DE ERRORES
    try:
        collection.insert_one(entry)
        message = f"✅ XYRA_USER @{username} verificado correctamente."
    except errors.ServerSelectionTimeoutError:
        message = "⚠️ XYRA_USER no disponible (MongoDB inaccesible)"
    except Exception as e:
        message = f"⚠️ Error al guardar datos: {str(e)}"

    return f"""
    <h2>{message}</h2>
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

    try:
        users = list(collection.find().sort("_id", -1))
    except errors.ServerSelectionTimeoutError:
        return "⚠️ No se puede conectar a la base de datos"

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
