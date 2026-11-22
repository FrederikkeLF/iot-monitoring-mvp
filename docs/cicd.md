
# CI/CD og Deployment
## Intelligent IoT – Monitoring MVP

### 1. Formål

Projektet anvender GitHub Actions til at automatisere
test, build og publicering af Docker-images.

Formålet er at sikre, at ændringer i kildekoden
bliver kontrolleret, før en ny version publiceres.

### 2. Continuous Integration (CI)

CI-processen er defineret i:

.github/workflows/ci.yml

Workflowet aktiveres ved push til main og ved
pull requests rettet mod main.

Jobbet test-and-build udfører følgende:

1. Henter kildekoden fra GitHub.
2. Installerer Python 3.12 og projektets afhængigheder.
3. Starter en midlertidig MySQL-testdatabase.
4. Opretter de nødvendige databasetabeller.
5. Udfører automatiserede tests med Pytest.
6. Kontrollerer, at Docker-imaget kan bygges.

De automatiserede tests kontrollerer blandt andet
temperaturgrænsen på 80 grader.

### 3. Continuous Delivery (CD)

Hvis test-and-build gennemføres korrekt,
kan jobbet publish-image starte.

Jobbet bygger og publicerer Docker-imaget til
GitHub Container Registry (GHCR).

Imaget bygges til to processorarkitekturer:

- linux/amd64
- linux/arm64

Det gør løsningen anvendelig på både
Intel/AMD-computere og Apple Silicon.

Imaget publiceres med både latest-tag og et
versionsspecifikt commit-ID.

### 4. Deployment

Deployment er demonstreret lokalt ved hjælp af
Docker Compose og filen compose.deploy.yaml.

I modsætning til compose.yaml anvender
deployment-filen et færdigbygget Docker-image
fra GitHub Container Registry.

API-containeren kommunikerer med en separat
MySQL-container via Docker-netværket.

MySQL anvender et Docker-volume til persistent
datalagring.

Deployment sker foreløbig manuelt og ikke
automatisk til en ekstern server.

### 5. Verifikation

Følgende er gennemført:

- Automatiserede tests via GitHub Actions
- Docker-build og publicering til GHCR
- Multi-platform build til AMD64 og ARM64
- Download af publiceret Docker-image
- Lokal deployment med Docker Compose
- Verifikation af eksisterende data efter deployment
- API-test med Swagger og Postman

REST API'et er testet fra en anden computer
med succes. Testen bekræfter, at API'et kan
tilgås over netværket fra en anden enhed.

### 6. Sikkerhed og begrænsninger

Databaseadgangskoder gemmes lokalt i .env,
som er udeladt fra Git.

GitHub Actions anvender en midlertidig
testdatabase med særskilte testoplysninger.

Det publicerede Docker-image er privat.

API'et har endnu ikke implementeret
brugerautentifikation, TLS-terminering eller
egentlig produktionsovervågning.

Løsningen skal derfor betragtes som en teknisk
MVP og ikke et produktionsklart IoT-system.
