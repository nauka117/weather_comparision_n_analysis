import requests
from datetime import datetime
import json

def get_city_coordinates(city_name:str) -> tuple[str]:
    """Get city coordinates with Nominatim API"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name,
        "format": "json",
        "addressdetails": 0,
        "limit": 1  # limit number of results. We need only 1
    }
    
    headers = {
        "User-Agent": AGENT_DATA  # Remember, here is my data from .gitignore
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        results = response.json()
        if results:
            return results[0]["lat"], results[0]["lon"]  # Return the first result
        else:
            return None  # No results found
    else:
        print(f"Error: {response.status_code}")
        return None

def get_daily_weather(city_name:str, date_request:str):

    coordinates = get_city_coordinates(city_name)
    date_start = int(datetime.strptime(f"{date_request} 00:00", "%d.%m.%Y %H:%M").timestamp())
    date_end = int(datetime.strptime(f"{date_request} 23:00", "%d.%m.%Y %H:%M").timestamp())
    url = "https://history.openweathermap.org/data/2.5/history/city"
    params = {
        "lat":      float(coordinates[0]),
        "lon":      float(coordinates[1]),
        "type":     "hour",
        "appid":    API_KEY,
        "start":    date_start,
        "end":      date_end
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"ERROR: {response.status_code}, {response.text}")
        return None

def add_dw_to_raw(daily_weather:dict, date_filename:str):
    with open(f'data/raw/{date_filename}.json', 'w', encoding='utf-8') as json_file:
        json.dump(daily_weather, json_file, ensure_ascii=False, indent=4)
    print(f"Data for {date_filename} succesfully written to json file")

#------ I HAVE keys/ DIRECTORY IN .gitignore
#------ WHERE I STORE MY OWN API KEYS AND AGENT DATA

with open("keys/openweathermap.txt") as key_file:
    API_KEY = key_file.read()

with open("keys/user-agent-osm.txt") as agent_file:
    # format: YourAppName/1.0 (your.email@example.com)
    AGENT_DATA = agent_file.read()


city_name = "Rostov-on-Don"
result = get_daily_weather(city_name, "10.01.2024")

add_dw_to_raw(result, "10.01.2024")