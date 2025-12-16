import os
import random
import platform
import socket
from datetime import datetime, timezone

from flask import Flask, jsonify
import psutil

# Configuration
MOCK_SENSORS = os.getenv("MOCK_SENSORS", "True").lower() == "true"
DHT_PIN = int(os.getenv("DHT_PIN", 4))
PORT = int(os.getenv("PORT", 5000))

# Initialize sensor (only on Raspberry Pi)
dht_device = None
if not MOCK_SENSORS:
    try:
        import board
        import adafruit_dht
        pin = getattr(board, f"D{DHT_PIN}")
        dht_device = adafruit_dht.DHT11(pin)
    except Exception as e:
        print(f"Could not initialize sensor: {e}")
        print("Using mock mode instead")

app = Flask(__name__)


# --- Sensor Endpoints ---

@app.route("/api/sensors/temperature")
def get_temperature():
    if MOCK_SENSORS or dht_device is None:
        temp = round(random.uniform(18.0, 28.0), 1)
        return jsonify({"value": temp, "unit": "celsius", "mock": True})
    try:
        temp = dht_device.temperature
        return jsonify({"value": temp, "unit": "celsius", "mock": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sensors/humidity")
def get_humidity():
    if MOCK_SENSORS or dht_device is None:
        humidity = round(random.uniform(30.0, 70.0), 1)
        return jsonify({"value": humidity, "unit": "percent", "mock": True})
    try:
        humidity = dht_device.humidity
        return jsonify({"value": humidity, "unit": "percent", "mock": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sensors/all")
def get_all_sensors():
    temp_response = get_temperature().get_json()
    humidity_response = get_humidity().get_json()
    return jsonify({
        "temperature": temp_response,
        "humidity": humidity_response,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


# --- System Endpoints ---

@app.route("/api/system/info")
def get_system_info():
    return jsonify({
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version()
    })


@app.route("/api/system/cpu")
def get_cpu():
    cpu_temp = None
    thermal_file = "/sys/class/thermal/thermal_zone0/temp"
    if os.path.exists(thermal_file):
        try:
            with open(thermal_file) as f:
                cpu_temp = round(int(f.read().strip()) / 1000, 1)
        except Exception:
            pass

    return jsonify({
        "usage_percent": psutil.cpu_percent(interval=0.1),
        "count": psutil.cpu_count(),
        "temperature_celsius": cpu_temp
    })


@app.route("/api/system/memory")
def get_memory():
    mem = psutil.virtual_memory()
    return jsonify({
        "total_mb": round(mem.total / (1024 * 1024), 1),
        "used_mb": round(mem.used / (1024 * 1024), 1),
        "usage_percent": mem.percent
    })


@app.route("/api/system/health")
def get_health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


# --- Root Endpoint ---

@app.route("/")
def index():
    return jsonify({
        "name": "Raspberry Pi Sensor API",
        "version": "1.0.0",
        "mock_mode": MOCK_SENSORS,
        "endpoints": [
            "/api/sensors/temperature",
            "/api/sensors/humidity",
            "/api/sensors/all",
            "/api/system/info",
            "/api/system/cpu",
            "/api/system/memory",
            "/api/system/health"
        ]
    })


if __name__ == "__main__":
    print(f"Starting Raspberry Pi Sensor API on port {PORT}")
    print(f"Mock mode: {MOCK_SENSORS}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
