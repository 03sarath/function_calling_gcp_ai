import requests
import os
from dotenv import load_dotenv

load_dotenv()

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city):
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant weather information
            temperature = data['main']['temp']
            weather_condition = data['weather'][0]['main'].lower()
            
            # Map weather conditions to our food recommendation categories
            if temperature < 15:
                weather_category = 'cold'
            elif temperature > 25:
                weather_category = 'hot'
            elif 'rain' in weather_condition:
                weather_category = 'rainy'
            else:
                weather_category = 'mild'
                
            return {
                'temperature': temperature,
                'weather_condition': weather_condition,
                'weather_category': weather_category
            }
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None 