# Agrar GPT API

## Endpunkt
`GET /climate?lat=XX&lon=YY`

## Antwortformat
```json
{
  "temperature_avg": 9.3,
  "precipitation_mm": 735,
  "vegetation_period_days": 212,
  "trend": {
    "10y_temp_rise": 1.4,
    "10y_precip_change": -3.2
  }
}
```

## Deployment bei Render
1. Repository auf GitHub hochladen
2. Bei [https://render.com](https://render.com) registrieren
3. Neues Web Service starten (Python, Free Plan)
4. GitHub-Repo verbinden
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`
