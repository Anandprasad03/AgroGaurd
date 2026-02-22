from fastapi import APIRouter
from pydantic import BaseModel, Field
import requests
from datetime import datetime

router = APIRouter(prefix="/weather", tags=["Weather API"])

class WeatherInput(BaseModel):
    location: str = Field("", description="Manual city name")
    lat: float = Field(None, description="Live Latitude")
    lon: float = Field(None, description="Live Longitude")

@router.post("")
def get_weather(data: WeatherInput):
    lat, lon = data.lat, data.lon
    city_name = "Your Live Location"

    # Step 1: If user typed a city, we convert it to coordinates (Geocoding API - Also Free!)
    if data.location:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={data.location}&count=1"
        try:
            geo_res = requests.get(geo_url).json()
            if "results" not in geo_res or not geo_res["results"]:
                return {"error": f"Could not find the city: {data.location}"}
            
            lat = geo_res["results"][0]["latitude"]
            lon = geo_res["results"][0]["longitude"]
            city_name = geo_res["results"][0]["name"]
        except Exception:
            return {"error": "Failed to find location coordinates."}

    if lat is None or lon is None:
        return {"error": "Please provide a location or enable GPS."}

    # Step 2: Fetch Weather Data from Open-Meteo (NO API KEY NEEDED!)
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
        "hourly": "temperature_2m",
        "daily": "temperature_2m_max",
        "timezone": "auto"
    }

    try:
        res = requests.get(weather_url, params=params).json()

        # Parse Current Data
        current = res["current"]
        bullet_points = [
            f"**Location:** {city_name}",
            f"**Current Temperature:** {current['temperature_2m']} °C",
            f"**Humidity:** {current['relative_humidity_2m']}%",
            f"**Precipitation:** {current['precipitation']} mm",
            f"**Wind Speed:** {current['wind_speed_10m']} km/h"
        ]

        # Parse Hourly Data (Next 24 Hours)
        hourly_times = res["hourly"]["time"][:24]
        hourly_temps = res["hourly"]["temperature_2m"][:24]
        # Format times neatly (e.g., "14:00")
        formatted_hourly_times = [t.split("T")[1] for t in hourly_times]

        # Parse Daily Data (Next 7 Days)
        daily_dates = res["daily"]["time"]
        daily_temps = res["daily"]["temperature_2m_max"]
        # Format dates to Day Names (e.g., "Monday")
        formatted_daily_dates = [datetime.strptime(d, "%Y-%m-%d").strftime("%A") for d in daily_dates]

        return {
            "bullet_points": bullet_points,
            "hourly": {"labels": formatted_hourly_times, "data": hourly_temps},
            "daily": {"labels": formatted_daily_dates, "data": daily_temps}
        }

    except Exception as e:
        print(f"⚠️ Weather API Error: {e}")
        return {"error": "Failed to fetch weather data from Open-Meteo."}