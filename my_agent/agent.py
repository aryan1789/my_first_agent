import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent, ParallelAgent, SequentialAgent


def get_weather(city: str) -> dict:
    """Returns the current weather for a city using Open-Meteo (no API key needed)."""
    try:
        # 1. Geocode the city to lat/lon
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=10,
        ).json()
        if not geo.get("results"):
            return {"status": "error", "error_message": f"City '{city}' not found"}

        result = geo["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]
        timezone = result.get("timezone", "UTC")

        # 2. Fetch current weather
        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weather_code,wind_speed_10m",
            },
            timeout=10,
        ).json()
        current = weather["current"]

        # 3. Translate the WMO weather code into something readable
        code_map = {
            0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
            45: "foggy", 48: "depositing rime fog",
            51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
            61: "slight rain", 63: "moderate rain", 65: "heavy rain",
            71: "slight snow", 73: "moderate snow", 75: "heavy snow",
            80: "rain showers", 81: "moderate rain showers", 82: "violent rain showers",
            95: "thunderstorm", 96: "thunderstorm with hail", 99: "severe thunderstorm",
        }
        condition = code_map.get(current["weather_code"], "unknown conditions")

        return {
            "status": "success",
            "city": city,
            "temperature_c": current["temperature_2m"],
            "condition": condition,
            "wind_kmh": current["wind_speed_10m"],
            "timezone": timezone,
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_current_time(city: str) -> dict:
    """Returns the current time in a city by looking up its timezone via Open-Meteo."""
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=10,
        ).json()
        if not geo.get("results"):
            return {"status": "error", "error_message": f"City '{city}' not found"}

        tz_name = geo["results"][0].get("timezone", "UTC")
        now = datetime.now(ZoneInfo(tz_name))
        return {
            "status": "success",
            "city": city,
            "time": now.strftime("%I:%M %p"),
            "date": now.strftime("%A, %B %d, %Y"),
            "timezone": tz_name,
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


# Specialists
weather_agent = Agent(
    name="weather_agent",
    model="gemini-3-flash-preview",
    description="Answers weather questions for any city.",
    instruction=(
        "Your ONLY job is to report weather. "
        "Call get_weather for the city mentioned in the user's question. "
        "Respond with weather information only: conditions, temperature, and wind. "
        "Do NOT mention time, date, or anything else. "
        "If the question asks about non-weather topics, ignore those parts entirely. "
        "Example output: 'Tokyo: partly cloudy, 18°C, wind 12 km/h.'"
    ),
    tools=[get_weather],
    output_key="weather_result",
)

time_agent = Agent(
    name="time_agent",
    model="gemini-3-flash-preview",
    description="Answers time questions for any city.",
    instruction=(
        "Your ONLY job is to report the current time. "
        "Call get_current_time for the city mentioned in the user's question. "
        "Respond with time information only: time and date. "
        "Do NOT mention weather, temperature, or anything else. "
        "If the question asks about non-time topics, ignore those parts entirely. "
        "Example output: 'London: 10:30 AM, Tuesday, May 13.'"
    ),
    tools=[get_current_time],
    output_key="time_result",
)

# Parallel block
parallel_specialists = ParallelAgent(
    name="parallel_specialists",
    sub_agents=[weather_agent, time_agent],
)

# Merger
merger_agent = Agent(
    name="merger_agent",
    model="gemini-3-flash-preview",
    description="Combines weather and time results into one reply.",
    instruction=(
        "Combine these into one friendly response:\n\n"
        "Weather: {weather_result}\n"
        "Time: {time_result}\n\n"
        "Be concise. Present both clearly."
    ),
)

# Root pipeline
root_agent = SequentialAgent(
    name="my_agent",
    sub_agents=[parallel_specialists, merger_agent],
)