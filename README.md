
# Intelligent IoT – Monitoring MVP

## Projektbeskrivelse

Dette projekt er en teknisk MVP udviklet til
Intelligent IoT Solutions A/S.

Løsningen demonstrerer, hvordan sensordata kan
modtages, behandles og gemmes, samt hvordan
systemet automatisk kan registrere afvigelser
og oprette alarmer.

## Teknologier

- Python 3.12
- FastAPI (REST API)
- MySQL 8.4
- Docker og Docker Compose
- GitHub Actions (CI/CD)
- Pytest (automatiserede tests)
- Postman (API-test)

## Funktionalitet

Systemet kan:

1. Modtage temperaturmålinger via REST API.
2. Registrere domæne-eventet SensorValueReceived.
3. Kontrollere temperaturen mod en grænseværdi.
4. Registrere AnomalyDetected ved temperaturer over 80 °C.
5. Oprette og gemme alarmer.
6. Gemme og hente målinger, events og alarmer fra MySQL.

## API-endpoints

| Metode | Endpoint | Funktion |
|---|---|---|
| GET | / | Kontrollerer API'et |
| POST | /measurements | Modtager sensordata |
| GET | /measurements | Henter målinger |
| GET | /events | Henter events |
| GET | /alerts | Henter alarmer |

## Arkitektur

Løsningen består af to Docker-containere:

- FastAPI: Modtager og behandler sensordata.
- MySQL: Gemmer målinger, events og alarmer.

Data opbevares i et Docker-volume.

## Test og CI/CD

Projektet anvender Pytest til automatiserede tests.

GitHub Actions udfører automatisk:
- Installation af afhængigheder
- Oprettelse af MySQL-testdatabase
- Automatiserede tests
- Docker-build
- Publicering til GitHub Container Registry

## Teststatus

- Lokale API-tests: Gennemført
- Automatiserede tests: Bestået
- Docker Compose: Testet
- Postman: Testet
- Lokal deployment fra GitHub-image: Testet
- Test fra anden computer: Ikke gennemført


## Installation og lokal opstart

### Forudsætninger

For at køre systemet skal følgende være installeret:

- Git
- Docker Desktop

Brugeren skal desuden have adgang til projektets
private GitHub-repository.

### 1. Hent projektet

Åbn en terminal, og kør:

    git clone https://github.com/FrederikkeLF/iot-monitoring-mvp.git
    cd iot-monitoring-mvp

### 2. Konfigurer databasen

Opret en lokal .env-fil ud fra eksempelfilen:

    cp .env.example .env

Åbn .env, og erstat eksempelværdierne med
dine egne adgangskoder.

Filen må ikke uploades til GitHub.

### 3. Start Docker

Sørg for, at Docker Desktop kører.

Start derefter systemet:

    docker compose up -d --build

Docker Compose starter to containere:
- api: FastAPI REST API
- db: MySQL-database

### 4. Opret databasetabeller

Ved første installation skal tabellerne oprettes:

    docker compose exec api python database_mysql.py

Dette opretter følgende tabeller:

- measurements
- domain_events
- alerts

### 5. Kontrollér containerne

Kør:

    docker compose ps

Begge containere skal være startet.
MySQL skal vise status healthy.

### 6. Åbn API'et

Åbn følgende adresse i browseren:

http://127.0.0.1:8002/docs

Her vises Swagger med API'ets fem endpoints.

### 7. Test systemet

Send følgende JSON gennem POST /measurements:

    {
      "device_id": "WT-001",
      "temperature": 95
    }

Forventet resultat:
- status: alarm
- Event: SensorValueReceived
- Event: AnomalyDetected
- Alarm oprettes i MySQL

Kontrollér resultatet gennem:
- GET /measurements
- GET /events
- GET /alerts

### 8. Stop systemet

Stop containerne med:

    docker compose down

MySQL-data bevares i Docker-volumet.

Bemærk: Brug ikke docker compose down -v,
medmindre du bevidst vil slette databasevolumet.
