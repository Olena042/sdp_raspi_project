import os
import random
import platform
import socket
import threading
import time
from datetime import datetime, timezone

from flask import Flask, jsonify
import psutil
import requests

# Configuration
MOCK_SENSORS = os.getenv("MOCK_SENSORS", "True").lower() == "true"
DHT_PIN = int(os.getenv("DHT_PIN", 4))
PORT = int(os.getenv("PORT", 5000))

# ThingSpeak Configuration
THINGSPEAK_API_KEY = os.getenv("THINGSPEAK_API_KEY", "3U5DFFDLYTB512Y0")
THINGSPEAK_URL = "https://api.thingspeak.com/update"
PUBLISH_INTERVAL = int(os.getenv("PUBLISH_INTERVAL", 20))  # seconds

# Track last publish status
last_publish = {"status": None, "timestamp": None, "temperature": None, "humidity": None}

# Mock sensor state (for realistic gradual changes)
mock_state = {"temperature": 22.0, "humidity": 50.0}

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


# --- ThingSpeak Publishing ---

def get_sensor_readings():
    """Get current temperature and humidity readings."""
    if MOCK_SENSORS or dht_device is None:
        # Gradual random walk for realistic mock data
        mock_state["temperature"] += random.uniform(-0.5, 0.5)
        mock_state["temperature"] = max(18.0, min(28.0, mock_state["temperature"]))
        mock_state["humidity"] += random.uniform(-2.0, 2.0)
        mock_state["humidity"] = max(30.0, min(70.0, mock_state["humidity"]))
        temp = round(mock_state["temperature"], 1)
        humidity = round(mock_state["humidity"], 1)
    else:
        try:
            temp = dht_device.temperature
            humidity = dht_device.humidity
        except Exception:
            temp = None
            humidity = None
    return temp, humidity


def publish_to_thingspeak():
    """Publish sensor data to ThingSpeak."""
    global last_publish
    temp, humidity = get_sensor_readings()

    if temp is None or humidity is None:
        last_publish["status"] = "error"
        last_publish["timestamp"] = datetime.now(timezone.utc).isoformat()
        return False

    try:
        params = {
            "api_key": THINGSPEAK_API_KEY,
            "field1": temp,
            "field2": humidity
        }
        response = requests.get(THINGSPEAK_URL, params=params, timeout=10)

        if response.status_code == 200 and response.text != "0":
            last_publish["status"] = "success"
            last_publish["entry_id"] = response.text
        else:
            last_publish["status"] = "failed"

        last_publish["timestamp"] = datetime.now(timezone.utc).isoformat()
        last_publish["temperature"] = temp
        last_publish["humidity"] = humidity
        return last_publish["status"] == "success"
    except Exception as e:
        last_publish["status"] = f"error: {str(e)}"
        last_publish["timestamp"] = datetime.now(timezone.utc).isoformat()
        return False


def thingspeak_publisher():
    """Background thread that publishes to ThingSpeak periodically."""
    while True:
        publish_to_thingspeak()
        print(f"Published to ThingSpeak: {last_publish}")
        time.sleep(PUBLISH_INTERVAL)


# Start background publisher thread
publisher_thread = threading.Thread(target=thingspeak_publisher, daemon=True)
publisher_thread.start()


# --- Sensor Endpoints ---

@app.route("/api/sensors/temperature")
def get_temperature():
    temp, _ = get_sensor_readings()
    if temp is None:
        return jsonify({"error": "Failed to read sensor"}), 500
    mock = MOCK_SENSORS or dht_device is None
    return jsonify({"value": temp, "unit": "celsius", "mock": mock})


@app.route("/api/sensors/humidity")
def get_humidity():
    _, humidity = get_sensor_readings()
    if humidity is None:
        return jsonify({"error": "Failed to read sensor"}), 500
    mock = MOCK_SENSORS or dht_device is None
    return jsonify({"value": humidity, "unit": "percent", "mock": mock})


@app.route("/api/sensors/all")
def get_all_sensors():
    temp, humidity = get_sensor_readings()
    mock = MOCK_SENSORS or dht_device is None
    return jsonify({
        "temperature": {"value": temp, "unit": "celsius", "mock": mock},
        "humidity": {"value": humidity, "unit": "percent", "mock": mock},
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


# --- ThingSpeak Endpoints ---

@app.route("/api/thingspeak/status")
def get_thingspeak_status():
    return jsonify({
        "last_publish": last_publish,
        "publish_interval_seconds": PUBLISH_INTERVAL,
        "channel_url": "https://thingspeak.com/channels/YOUR_CHANNEL_ID"
    })


# --- Root Endpoint ---

@app.route("/")
def index():
    return jsonify({
        "name": "Raspberry Pi Sensor API",
        "version": "1.0.0",
        "mock_mode": MOCK_SENSORS,
        "thingspeak_enabled": True,
        "endpoints": [
            "/api/sensors/temperature",
            "/api/sensors/humidity",
            "/api/sensors/all",
            "/api/system/info",
            "/api/system/cpu",
            "/api/system/memory",
            "/api/system/health",
            "/api/thingspeak/status"
        ]
    })


if __name__ == "__main__":
    print(f"Starting Raspberry Pi Sensor API on port {PORT}")
    print(f"Mock mode: {MOCK_SENSORS}")
    # Disable reloader in hardware mode to prevent GPIO conflicts
    use_reloader = MOCK_SENSORS
    app.run(host="0.0.0.0", port=PORT, debug=True, use_reloader=use_reloader)
