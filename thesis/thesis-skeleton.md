# Lopputyö runko

## 1. Johdanto

--
## 2. Lähtökohdat

### 2.1 Uhkatiedot
#### 2.1.1 Uhkatietotyypit
- IPv4
- IPv6
- File hashes
- Domain
- URL
#### 2.1.2 Uhkatietojen kerääminen
- SIEM
- Verkkoliikenne
- Forensiikka
- Honeypots
#### 2.1.3 Uhkatietojen käyttö

### 2.2 Julkisiin lähteisiin perustuva tiedustelu-tieto
#### 2.2.1 Joukkoistettu uhkatieto
- AbuseIPDB
- VirusTotal
#### 2.2.2 Kaupalliset toimittajat
- GreyNoise
- Mandiant
#### 2.2.1 Uhkatietojen analysointi
- Luokittelu (benign, suspicious, malicious)

### 2.3 Työkalut
- SOAR integraatiot
- ThreatOwl

--
## 3. Teknologiat

### 3.1 Python
#### 3.1.1 Flask
- Blueprints
#### 3.1.2 Gunicorn
#### 3.1.3 Celery
- Worker
- Tasks
#### 3.1.4 asyncio
- async/await
- aiohttp

### 3.2 Redis
- Cache
- Message queue

### 3.3 Docker
- Container

--
## 4. Työn toteutus

### 4.1 Flask API
#### 4.1.1 API toiminnallisuus
- Task ID
#### 4.1.2 API endpointit
- Search
- Search task
- Sources
- Add API key
- Debug endpoints
#### 4.1.3 Palautus datan muoto
- `"summary": "summary", "verdict": "VERDICT", "url": "url", "data": {}`

### 4.2 Celery workers
#### 4.2.1 Celery tasks

### 4.3 Julkisiin lähteisiin perustuvat lähteet
#### 4.3.1 BaseSource
#### 4.3.2 HTTP kyselyt

### 4.3 Tiedon varastoiminen
- SQLite
- ORM
#### 4.3.1 Välimuisti
- Redis
#### 4.3.2 Salaus
- Fernet

### 4.5 Docker compose
#### 4.5.1 Containers
#### 4.5.2 Networking
#### 4.5.3 Healthchecks
#### 4.5.4 Logging

### 4.6 Testaus
#### 4.6.1 API endpoint testaus
- Postman
- Load testing
#### 4.6.2 Tietokanta testaus
#### 4.6.3 Yksikkötestaus

--
## 5. Tulokset

### 5.1 Toiminnallisuus

### 5.2 Käyttöönotto
#### 5.2.1 Tuotantoympäristössä
- Reverse proxy
#### 5.2.2 Yksittäinen tietoturva-asiantuntija

### 5.3 Käyttö
#### 5.3.1 Tuotantoympäristössä
#### 5.3.2 Yksittäinen tietoturva-asiantuntija

### 5.3 Jatkokehitys
- Autentikointi

--
## 6. Yhteenveto