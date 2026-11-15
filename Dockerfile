
# Brug Python som fundament
FROM python:3.12-slim

# Opret arbejdsmappe inde i containeren
WORKDIR /app

# Kopier listen over Python-pakker
COPY requirements.txt .

# Installer de nødvendige pakker
RUN pip install --no-cache-dir -r requirements.txt

# Kopier vores API-kode
COPY main.py .
COPY database_mysql.py .

# Angiv API'ets port
EXPOSE 8000

# Start API-serveren
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
