
import pytest

from fastapi.testclient import TestClient
from main import app

from database_mysql import connect_db

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


# Test 4: Kontroller at data gemmes i MySQL
def test_alarm_persisted_in_mysql():

    response = client.post(
        "/measurements",
        json={
            "device_id": "TEST-DB-001",
            "temperature": 100
        }
    )

    assert response.status_code == 200

    measurement_id = response.json()["measurement_id"]

    connection = connect_db()

    try:
        with connection.cursor() as cursor:

            # Kontroller målingen
            cursor.execute(
                "SELECT * FROM measurements WHERE id = %s",
                (measurement_id,)
            )
            measurement = cursor.fetchone()

            # Kontroller events
            cursor.execute(
                "SELECT event_type FROM domain_events "
                "WHERE measurement_id = %s",
                (measurement_id,)
            )
            events = cursor.fetchall()

            # Kontroller alarm
            cursor.execute(
                "SELECT * FROM alerts WHERE measurement_id = %s",
                (measurement_id,)
            )
            alarm = cursor.fetchone()

    finally:
        connection.close()

    assert measurement is not None
    assert measurement["device_id"] == "TEST-DB-001"
    assert measurement["temperature"] == 100

    event_types = {event["event_type"] for event in events}

    assert event_types == {
        "SensorValueReceived",
        "AnomalyDetected"
    }

    assert alarm is not None
    assert alarm["message"] == "Temperature exceeds threshold"
