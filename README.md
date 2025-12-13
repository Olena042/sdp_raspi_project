# Raspberry Pi Sensor API

A REST API for Raspberry Pi that exposes sensor data and system information.

## Team Members
- Olena Pashchenko
- Christian Occampo Torres

## Project Description

This project is for the Software Development Processes (SDP) subject. It provides a Flask-based REST API that:
- Reads temperature and humidity from a DHT11 sensor
- Provides system information (CPU, memory)
- Supports mock mode for development without hardware

## Project Structure

```
sdp_raspi_project/
├── app.py              # The entire application
├── requirements.txt    # Dependencies
└── README.md
```

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python3 app.py
```

The API will be available at `http://localhost:5000`

## Configuration

Set environment variables to customize:

```bash
export MOCK_SENSORS=True   # Use fake sensor data (default)
export MOCK_SENSORS=False  # Use real DHT11 sensor
export DHT_PIN=4           # GPIO pin for sensor
export PORT=5000           # Server port
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info and list of endpoints |
| GET | `/api/sensors/temperature` | Get temperature reading |
| GET | `/api/sensors/humidity` | Get humidity reading |
| GET | `/api/sensors/all` | Get all sensor data |
| GET | `/api/system/info` | Get system information |
| GET | `/api/system/cpu` | Get CPU usage and temperature |
| GET | `/api/system/memory` | Get memory usage |
| GET | `/api/system/health` | Health check endpoint |

## Example Response

```bash
curl http://localhost:5000/api/sensors/temperature
```

```json
{
  "value": 23.5,
  "unit": "celsius",
  "mock": true
}
```

## Hardware Setup (DHT11)

When deploying to Raspberry Pi:

1. Connect DHT11 sensor:
   - VCC -> 3.3V (Pin 1)
   - GND -> Ground (Pin 6)
   - DATA -> GPIO 4 (Pin 7)

2. Install Pi-specific dependencies:
   ```bash
   pip install adafruit-circuitpython-dht RPi.GPIO
   ```

3. Set `MOCK_SENSORS=False`

## Docker
