import os
import requests
from dotenv import load_dotenv
import openai

load_dotenv()  # Load from .env

# ENV Vars expected:
# OPENWEATHER_API_KEY, GOOGLE_API_KEY, OPENAI_API_KEY, OPENAI_DEPLOYMENT_NAME

def fetch_city_data(city_name):
    weather = get_weather(city_name)
    attractions = get_tourist_attractions(city_name)
    insight = get_ai_insight(city_name)

    return {
        "city": city_name,
        "weather": weather,
        "attractions": attractions,
        "insight": insight
    }

def get_weather(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    return {
        "description": data["weather"][0]["description"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"]
    }

def get_tourist_attractions(city):
    api_key = os.getenv("GOOGLE_API_KEY")
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=tourist+attractions+in+{city}&key={api_key}"
    response = requests.get(url)
    data = response.json()

    results = []
    for place in data.get("results", [])[:5]:  # Limit to 5
        results.append({
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "rating": place.get("rating")
        })
    return results

def get_ai_insight(city):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    deployment = os.getenv("OPENAI_DEPLOYMENT_NAME")  # Your model deployment name in Azure

    prompt = f"""
You are a travel guide. Give a compelling 4-line story about why someone should visit {city}. Include a cultural reference and one attraction.
"""

    response = openai.ChatCompletion.create(
        engine=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )

    return response['choices'][0]['message']['content'].strip()
