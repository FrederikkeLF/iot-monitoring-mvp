
import pytest

from fastapi.testclient import TestClient
from main import app

# Opret en testklient til vores API
client = TestClient(app)


# Sørg for, at alle tests bruger testdatabasen
@pytest.fixture(autouse=True)
def use_test_database(monkeypatch):
    monkeypatch.setenv("DB_NAME", "iot_monitoring_test")


# Test 1: Normal temperatur
def test_normal_temperature():

    response = client.post(
        "/measurements",
        json={
            "device_id": "TEST-001",
            "temperature": 65
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "normal"


# Test 2: For høj temperatur
def test_high_temperature():

    response = client.post(
        "/measurements",
        json={
            "device_id": "TEST-002",
            "temperature": 85
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "alarm"
    assert "AnomalyDetected" in response.json()["events"]


# Test 3: Præcis på grænseværdien
def test_threshold():

    response = client.post(
        "/measurements",
        json={
            "device_id": "TEST-003",
            "temperature": 80
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "normal"

