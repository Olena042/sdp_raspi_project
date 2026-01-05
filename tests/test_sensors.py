"""Tests for sensor API endpoints."""


def test_get_temperature(client):
    """Test temperature endpoint returns valid data."""
    response = client.get("/api/sensors/temperature")
    assert response.status_code == 200

    data = response.get_json()
    assert "value" in data
    assert "unit" in data
    assert data["unit"] == "celsius"
    assert data["mock"] is True
    assert isinstance(data["value"], (int, float))


def test_get_humidity(client):
    """Test humidity endpoint returns valid data."""
    response = client.get("/api/sensors/humidity")
    assert response.status_code == 200

    data = response.get_json()
    assert "value" in data
    assert "unit" in data
    assert data["unit"] == "percent"
    assert data["mock"] is True
    assert isinstance(data["value"], (int, float))


def test_get_all_sensors(client):
    """Test combined sensor endpoint returns all data."""
    response = client.get("/api/sensors/all")
    assert response.status_code == 200

    data = response.get_json()
    assert "temperature" in data
    assert "humidity" in data
    assert "timestamp" in data

    assert data["temperature"]["unit"] == "celsius"
    assert data["humidity"]["unit"] == "percent"


def test_sensor_values_in_range(client):
    """Test mock sensor values are within expected ranges."""
    response = client.get("/api/sensors/all")
    data = response.get_json()

    temp = data["temperature"]["value"]
    humidity = data["humidity"]["value"]

    # Mock values should be within defined bounds
    assert 18.0 <= temp <= 28.0
    assert 30.0 <= humidity <= 70.0
