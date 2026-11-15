
import os
import pymysql
from dotenv import load_dotenv

# Indlæs adgangskoder fra .env
load_dotenv()


# Opret forbindelse til MySQL
def connect_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3307")),
        user="iot_user",
        password=os.environ["MYSQL_PASSWORD"],
        database=os.getenv("DB_NAME", "iot_monitoring"),
        cursorclass=pymysql.cursors.DictCursor
    )


# Opret vores tre tabeller
def create_tables():
    connection = connect_db()

    try:
        with connection.cursor() as cursor:

            # Tabel 1: Sensormålinger
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS measurements (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id VARCHAR(100) NOT NULL,
                    temperature DOUBLE NOT NULL,
                    recorded_at VARCHAR(40) NOT NULL
                )
            """)

            # Tabel 2: Events
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS domain_events (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    measurement_id INT NOT NULL,
                    event_type VARCHAR(100) NOT NULL,
                    recorded_at VARCHAR(40) NOT NULL
                )
            """)

            # Tabel 3: Alarmer
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    measurement_id INT NOT NULL,
                    message TEXT NOT NULL,
                    recorded_at VARCHAR(40) NOT NULL
                )
            """)

        connection.commit()
        print("Alle tre MySQL-tabeller er oprettet!")

    finally:
        connection.close()


# Kør kun dette, når filen startes direkte
if __name__ == "__main__":
    create_tables()
