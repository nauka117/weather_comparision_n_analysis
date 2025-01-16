from pydantic_settings import BaseSettings
from pydantic import field_validator, ValidationError
import re


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