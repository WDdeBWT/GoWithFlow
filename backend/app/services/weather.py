import httpx
from datetime import datetime


async def get_weather(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,precipitation_probability",
        "timezone": "Asia/Shanghai",
        "forecast_days": 1,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    now = datetime.now().strftime("%Y-%m-%dT%H:00")
    times = data["hourly"]["time"]
    idx = 0
    for i, t in enumerate(times):
        if t >= now:
            idx = i
            break

    return {
        "temperature": data["hourly"]["temperature_2m"][idx],
        "precipitation_probability": data["hourly"]["precipitation_probability"][idx],
    }
