from dotenv import load_dotenv
import os

load_dotenv()

OWM_api_key = os.getenv('OWM_api_key')
GCuseragent = os.getenv('user_agent')


print(f"openweathermap API Key: {OWM_api_key}")
print(f"geocoder user agent: {GCuseragent}")
