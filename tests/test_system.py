"""Tests for system API endpoints."""


def test_get_system_info(client):
    """Test system info endpoint returns expected fields."""
    response = client.get("/api/system/info")
    assert response.status_code == 200

    data = response.get_json()
    assert "hostname" in data
    assert "platform" in data
    assert "platform_release" in data
    assert "architecture" in data
    assert "python_version" in data


def test_get_cpu(client):
    """Test CPU endpoint returns expected fields."""
    response = client.get("/api/system/cpu")
    assert response.status_code == 200

    data = response.get_json()
    assert "usage_percent" in data
    assert "count" in data
    assert "temperature_celsius" in data
    assert isinstance(data["usage_percent"], (int, float))
    assert isinstance(data["count"], int)


def test_get_memory(client):
    """Test memory endpoint returns expected fields."""
    response = client.get("/api/system/memory")
    assert response.status_code == 200

    data = response.get_json()
    assert "total_mb" in data
    assert "used_mb" in data
    assert "usage_percent" in data
    assert data["total_mb"] > 0
    assert data["used_mb"] > 0


def test_health_check(client):
    """Test health endpoint returns healthy status."""
    response = client.get("/api/system/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_root_endpoint(client):
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.get_json()
    assert data["name"] == "Raspberry Pi Sensor API"
    assert "version" in data
    assert "endpoints" in data
    assert isinstance(data["endpoints"], list)
    assert len(data["endpoints"]) > 0


def test_thingspeak_status(client):
    """Test ThingSpeak status endpoint."""
    response = client.get("/api/thingspeak/status")
    assert response.status_code == 200

    data = response.get_json()
    assert "last_publish" in data
    assert "publish_interval_seconds" in data
