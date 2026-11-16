
import json
import os
import random
import time

from urllib.request import Request, urlopen
from urllib.error import URLError

# Adressen til vores IoT REST API
API_URL = os.getenv(
    "IOT_API_URL",
    "http://127.0.0.1:8002/measurements"
)

DEVICE_ID = "RPI-SIM-001"


# Simuler en temperatursensor
def read_temperature():
    return round(random.uniform(60, 100), 1)


# Send en måling til vores API
def send_measurement():
    temperature = read_temperature()

    data = {
        "device_id": DEVICE_ID,
        "temperature": temperature
    }

    request = Request(
        API_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urlopen(request, timeout=10) as response:
        result = json.load(response)

    print(
        f"Temperatur: {temperature} °C "
        f"| Status: {result['status']} "
        f"| Måling ID: {result['measurement_id']}"
    )


# Kør automatisk hvert 10. sekund
if __name__ == "__main__":
    print("Virtuel Raspberry Pi startet!")

    try:
        while True:
            try:
                send_measurement()
            except (URLError, TimeoutError) as error:
                print(f"Kunne ikke kontakte API: {error}")

            time.sleep(10)

    except KeyboardInterrupt:
        print("\nSimulator stoppet.")
