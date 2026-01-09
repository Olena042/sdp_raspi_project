# Raspberry Pi Sensor API 

A REST API for Raspberry Pi that exposes sensor data and system information.

## Team Members
- Olena Pashchenko
- Christian Ocampo Torres

## Project Description

This project is for the Software Development Processes (SDP) subject. It provides a Flask-based REST API that:
- Reads temperature and humidity from a DHT11 sensor
- Publishes sensor data to ThingSpeak for visualization
- Provides system information (CPU, memory)
- Supports mock mode for development without hardware

## Project Structure

```
sdp_raspi_project/
├── .github/
│   └── workflows/
│       └── ci.yml       # CI/CD pipeline
├── app.py               # Flask API application
├── requirements.txt     # Python dependencies
├── requirements-dev.txt # Development dependencies (linting)
├── .flake8              # Flake8 configuration
├── tests/               # pytest test suite
├── Dockerfile           # Multi-stage container build
├── docker-compose.yml   # Container orchestration
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
# Sensor settings
export MOCK_SENSORS=True   # Use fake sensor data (default)
export MOCK_SENSORS=False  # Use real DHT11 sensor
export DHT_PIN=4           # GPIO pin for sensor
export PORT=5000           # Server port

# ThingSpeak integration
export THINGSPEAK_API_KEY=your_api_key  # ThingSpeak write API key
export PUBLISH_INTERVAL=20              # Publish interval in seconds
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
| GET | `/api/thingspeak/status` | Get ThingSpeak publish status |

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

3. Run with sudo (required for GPIO access):
   ```bash
   sudo MOCK_SENSORS=False venv/bin/python3 app.py
   ```

## ThingSpeak Integration

The API automatically publishes sensor data to ThingSpeak every 20 seconds.

1. Create a ThingSpeak channel at https://thingspeak.com
2. Get your Write API Key from the channel settings
3. Set the environment variable:
   ```bash
   export THINGSPEAK_API_KEY=your_write_api_key
   ```

Data fields:
- **Field 1**: Temperature (°C)
- **Field 2**: Humidity (%)

Check publish status:
```bash
curl http://localhost:5000/api/thingspeak/status
```

## Docker

### Building the Image

```bash
# Build for local architecture
docker build -t raspi-sensor-api .

# Build for Raspberry Pi (ARM64) from another machine
docker buildx build --platform linux/arm64 -t raspi-sensor-api .
```

### Running the Container

```bash
# Run in mock mode (development)
docker run -p 5000:5000 raspi-sensor-api

# Run with real sensor (Raspberry Pi)
docker run -p 5000:5000 --privileged \
  -e MOCK_SENSORS=False \
  raspi-sensor-api
```

### Docker Compose

```bash
# Mock mode (development)
docker-compose up -d

# Hardware mode (Raspberry Pi with sensor)
docker-compose --profile hardware up -d sensor-api-hardware
```

## Troubleshooting

## Stop and remove containers

```bash
#To stop running containers and remove them
docker-compose down

#Verify which containers are running
docker-compose ps

#Restart all services
docker-compose restart
```

## Linting

```bash
pip install flake8
flake8 app.py
```

## Testing

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v
```

Tests run in mock mode automatically, so no hardware is required.

## CI/CD

This project uses GitHub Actions for continuous integration and deployment.

### Pipeline Stages

1. **Lint**: Runs flake8 to check code quality
2. **Test**: Runs pytest test suite
3. **Build & Push**: Builds Docker image and pushes to registries (requires lint and test to pass)

### Triggers

- **Push to main**: Runs full pipeline (lint + test + build + push)
- **Pull requests**: Runs lint + test + build (no push)

### Workflow File

See `.github/workflows/ci.yml` for the pipeline configuration.

## Git Branch Strategy

This project uses a simplified GitHub Flow branching strategy:

```
main (production)
  │
  ├── feature/add-temperature-endpoint
  ├── feature/thingspeak-integration
  ├── fix/sensor-reading-bug
  └── test-set-up-and-ci-improvement
```

### Branches

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code. Protected branch. |
| `feature/*` | New features and enhancements |
| `fix/*` | Bug fixes |
| `test-*` | Testing and CI/CD improvements |

### Workflow

1. Create a feature branch from `main`
2. Make changes and commit
3. Push branch and open a Pull Request
4. CI pipeline runs (lint + test + build)
5. Review and merge to `main`
6. CI builds and pushes Docker image to registries

### Branch Protection

The `main` branch is protected:
- Requires pull request before merging
- CI checks must pass before merge

## Repository Links

- **GitHub**: https://github.com/Olena042/sdp_raspi_project
- **Container Registry**: ghcr.io/olena042/sdp_raspi_project
