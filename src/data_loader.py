import asyncio
import aiohttp

import os
from pydantic import Field
from pydantic_settings import BaseSettings

from datetime import datetime, timedelta

import json


class Settings(BaseSettings):
    """
    Class for reading protected data from .env (like api keys, agent info, etc.)
    """

    OWM_API_KEY: str = Field(alias="OWM_api_key")
    AGENT_DATA: str = Field(alias="user_agent")

    class Config:
        env_file = os.path.expanduser(".env")
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()


async def get_city_coordinates(session:aiohttp.ClientSession, city_name:str) -> tuple[str]:
    """Get city coordinates with Nominatim API"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name,
        "format": "json",
        "addressdetails": 0,
        "limit": 1  # limit number of results. We need only 1
    }
    headers = {
        "User-Agent": settings.AGENT_DATA
    }
    
    async with session.get(url=url, params=params, headers=headers) as response:

        if response.status == 200:
            results = await response.json()
            if results:
                return results[0]["lat"], results[0]["lon"]  # Return the first result
            else:
                return None  # No results found
        else:
            print(f"Error: {response.status_code}")
            return None

async def get_daily_weather(session:aiohttp.ClientSession, city_name:str, date_request:str):

    coordinates = await get_city_coordinates(session, city_name)
    
    date_start = int(datetime.strptime(f"{date_request} 00:00", "%d.%m.%Y %H:%M").timestamp())
    date_end = int(datetime.strptime(f"{date_request} 23:00", "%d.%m.%Y %H:%M").timestamp())
    
    url = "https://history.openweathermap.org/data/2.5/history/city"
    params = {
        "lat":      float(coordinates[0]),
        "lon":      float(coordinates[1]),
        "type":     "hour",
        "appid":    settings.OWM_API_KEY,
        "start":    date_start,
        "end":      date_end
    }

    async with session.get(url=url, params=params) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"ERROR: {response.status_code}, {response.text}")
            return None

def add_dw_to_raw(daily_weather:dict, date_filename:str):
    with open(f'data/raw/{date_filename}.json', 'w', encoding='utf-8') as json_file:
        json.dump(daily_weather, json_file, ensure_ascii=False, indent=4)
    print(f"Data for {date_filename} succesfully written to json file")


async def main():
    
    city_name = "Rostov-on-Don"

    # send querries for dates from 11.01.24 to 14.01.2024
    start_date = datetime(2024, 1, 11)
    end_date = datetime(2024, 1, 14)

    async with aiohttp.ClientSession() as session:

        current_date = start_date

        while current_date <= end_date:
            date_format = current_date.strftime("%d.%m.%Y")  #  format date
            current_date += timedelta(days=1)
            
            result = await get_daily_weather(session, city_name, date_format)
            add_dw_to_raw(result, date_format)
            
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
