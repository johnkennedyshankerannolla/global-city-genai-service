import azure.functions as func
import logging
import requests
import os
from dotenv import load_dotenv
import openai

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_DEPLOYMENT_NAME = os.getenv("OPENAI_DEPLOYMENT_NAME")

openai.api_key = OPENAI_API_KEY


def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        simple_weather = {
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "city": data["name"]
        }
        return simple_weather
    else:
        logging.error(f"Weather API error: {response.status_code} - {response.text}")
        return None


def get_places(city_name):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=tourist+attractions+in+{city_name}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("results", [])[:5]  # top 5 only
        simple_places = []
        for place in results:
            simple_places.append({
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "rating": place.get("rating")
            })
        return simple_places
    else:
        logging.error(f"Google Places API error: {response.status_code} - {response.text}")
        return []


def get_ai_insight(city_name, weather_desc):
    prompt = (
        f"Write a short, engaging paragraph about the city of {city_name}. "
        f"Include some interesting facts and mention the current weather as '{weather_desc}'."
    )

    try:
        response = openai.Completion.create(
            engine=OPENAI_DEPLOYMENT_NAME,
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
            n=1,
            stop=None,
        )
        insight_text = response.choices[0].text.strip()
        return insight_text
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return "No AI insight available at the moment."


app = func.FunctionApp()


@app.route(route="get_city_info", auth_level=func.AuthLevel.ANONYMOUS)
def get_city_info(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    city = req.params.get('name')
    if not city:
        try:
            req_body = req.get_json()
            city = req_body.get('name')
        except Exception:
            pass

    if not city:
        return func.HttpResponse(
            "Please provide a city name in the query string or in the request body.",
            status_code=400
        )

    weather = get_weather(city)
    if not weather:
        return func.HttpResponse(
            f"Could not retrieve weather data for city: {city}",
            status_code=500
        )

    places = get_places(city)

    ai_insight = get_ai_insight(city, weather.get("description", "unknown"))

    result = {
        "city": city,
        "weather": weather,
        "attractions": places,
        "insight": ai_insight
    }

    return func.HttpResponse(
        body=json.dumps(result, indent=2),
        status_code=200,
        mimetype="application/json"
    )
