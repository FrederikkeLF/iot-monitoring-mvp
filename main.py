
import logging
from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel

from database_mysql import connect_db as connect_mysql

# Opret API
app = FastAPI(title="Intelligent IoT - Monitoring MVP")

# Grænseværdi for temperatur
THRESHOLD = 80

# Logger til overvågning og fejlfinding
logger = logging.getLogger("uvicorn.error")

# Beskriv en sensormåling
class Measurement(BaseModel):
    device_id: str
    temperature: float


# API-forside
@app.get("/")
def home():
    return {"message": "API'et virker!"}


# Modtag og gem sensormålinger i MySQL
@app.post("/measurements")
def receive_measurement(measurement: Measurement):
    return save_mysql_measurement(measurement)


# Hent alle målinger fra MySQL
@app.get("/measurements")
def get_measurements():

    connection = connect_mysql()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM measurements ORDER BY id DESC"
            )

            rows = cursor.fetchall()

        return rows

    finally:
        connection.close()




# Hent alle events fra MySQL
@app.get("/events")
def get_events():

    connection = connect_mysql()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM domain_events ORDER BY id DESC"
            )

            rows = cursor.fetchall()

        return rows

    finally:
        connection.close()




# Hent alle alarmer fra MySQL
@app.get("/alerts")
def get_alerts():

    connection = connect_mysql()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM alerts ORDER BY id DESC"
            )

            rows = cursor.fetchall()

        return rows

    finally:
        connection.close()

# Gem en sensormåling i MySQL
def save_mysql_measurement(measurement: Measurement):

    events = ["SensorValueReceived"]
    status = "normal"

    # Kontrollér temperaturen
    if measurement.temperature > THRESHOLD:
        events.append("AnomalyDetected")
        status = "alarm"

    recorded_at = datetime.now(timezone.utc).isoformat()

    # Forbind til MySQL
    connection = connect_mysql()

    try:
        with connection.cursor() as cursor:

            # Gem målingen
            cursor.execute(
                """
                INSERT INTO measurements
                (device_id, temperature, recorded_at)
                VALUES (%s, %s, %s)
                """,
                (
                    measurement.device_id,
                    measurement.temperature,
                    recorded_at
                )
            )

            measurement_id = cursor.lastrowid

            # Gem events
            for event_type in events:
                cursor.execute(
                    """
                    INSERT INTO domain_events
                    (measurement_id, event_type, recorded_at)
                    VALUES (%s, %s, %s)
                    """,
                    (measurement_id, event_type, recorded_at)
                )

            # Gem alarm ved høj temperatur
            if status == "alarm":
                cursor.execute(
                    """
                    INSERT INTO alerts
                    (measurement_id, message, recorded_at)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        measurement_id,
                        "Temperature exceeds threshold",
                        recorded_at
                    )
                )

        # Gem ændringerne permanent
        connection.commit()

        # Registrer resultatet i systemloggen
        logger.info(
            "Measurement %s saved successfully",
            measurement_id
        )

        if status == "alarm":
            logger.warning(
                "AnomalyDetected for measurement %s",
                measurement_id
            )
    
    except Exception:
        logger.exception(
            "Database error while saving measurement"
        )
        connection.rollback()
        raise

    finally:
        connection.close()

    return {
        "measurement_id": measurement_id,
        "device_id": measurement.device_id,
        "temperature": measurement.temperature,
        "events": events,
        "status": status
    }
