
from unittest.mock import MagicMock
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


# Test 5: Simuler en databasefejl
def test_database_error_logging(monkeypatch, caplog):

    # Opret en falsk databaseforbindelse
    fake_connection = MagicMock()

    fake_cursor = (
        fake_connection.cursor.return_value
        .__enter__.return_value
    )

    # Simuler en fejl, når systemet forsøger at gemme data
    fake_cursor.execute.side_effect = RuntimeError(
        "Simulated database failure"
    )

    # Brug den falske forbindelse i denne test
    monkeypatch.setattr(
        "main.connect_mysql",
        lambda: fake_connection
    )

    # Kontroller at fejlen registreres
    with caplog.at_level("ERROR", logger="uvicorn.error"):

        with pytest.raises(
            RuntimeError,
            match="Simulated database failure"
        ):

            client.post(
                "/measurements",
                json={
                    "device_id": "TEST-ERROR-001",
                    "temperature": 95
                }
            )

    # Kontroller at ændringerne annulleres
    fake_connection.rollback.assert_called_once()

    # Kontroller at forbindelsen lukkes
    fake_connection.close.assert_called_once()

    # Kontroller ERROR-loggen
    assert "Database error while saving measurement" in caplog.text
