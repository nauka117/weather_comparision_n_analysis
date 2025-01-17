from pydantic_settings import BaseSettings
from pydantic import field_validator, ValidationError
import re

import datetime as dt

import requests

class Settings(BaseSettings):
    OWM_api_key: str
    GC_user_agent: str

    class Config:
        env_file = ".env"
    
    @field_validator("OWM_api_key")
    def validate_OWM_api_key(cls, value):
        if len(value) != 32:
            raise ValueError("OWM_api_key must be 32 characters long.")
        if not re.fullmatch(r"[a-f0-9]{32}", value):
            raise ValueError("OWM_api_key must be a 32-character hexadecimal string.")
        return value

try:
    settings = Settings()
    print(f"openweathermap API Key: {settings.OWM_api_key}")
    print(f"geocoder user agent: {settings.GC_user_agent}")
except ValidationError as e:
    print(".env file configuration error:", e)


class HistoricalWeatherRequest:
    base_url: str
    api_key: str

    location: list[float]
    start_date: dt.datetime
    end_date: dt.datetime

    def setLocationCoordinates(self, longitude: float, latitude: float):
        self.location = [longitude, latitude]
    
    def setLocationCity(self, city_name):
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": city_name,
            "format": "json",
            "addressdetails": 0,
            "limit": 1  # limit for results. We need only 1st (most relevant) result
        }
        headers = {
            "User-Agent": settings.GC_user_agent  # required by Nominatim API to identify the request source
        }
        response = requests.get(base_url, params=params, headers=headers)
        if response.status_code == 200:
            results = response.json()
            if results:
                self.location = [results[0]["lat"], results[0]["lon"]]
            else:
                print(f"No results found for city: {city_name}")
                return None
        else:
            print(f"Error: {response.status_code}")
            return None
    
    def setDate(self, date: str):
        
        formats = [
            "%Y-%m-%d",  # ISO 8601 format  -   YYYY-MM-DD
            "%d.%m.%Y",  # Russian format   -   DD.MM.YYYY
            "%m.%d.%Y",  # US format        -   MM/DD/YYYY
            "%d/%m/%Y",  # European format  -   DD/MM/YYYY
        ]

        for fmt in formats:
            try:
                date_obj = dt.datetime.strptime(date, fmt)
                unix_timestamp = int(date_obj.timestamp())
                self.start_date = unix_timestamp
            except ValueError:
                continue

        raise ValueError(f"Date '{date}' is not in a recognized format. \nAllowed formats: YYYY-MM-DD, DD.MM.YYYY, MM/DD/YYYY, DD/MM/YYYY")

    

class HistoricalWeatherRequest_OWM(HistoricalWeatherRequest):
    """Subclass of HistoricalWeatherRequest for OpenWeatherMap API"""
    def __init__(self):
        self.base_url = "https://history.openweathermap.org/data/2.5/history/city"
        self.api_key = settings.OWM_api_key


summa = lambda a, b: a + b