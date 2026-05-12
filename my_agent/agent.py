from google.adk.agents import Agent

# Mock tools (same as before — fine for learning)
def get_weather(city: str) -> dict:
    return {"status": "success", "city": city, "weather": "sunny, 22°C"}

def get_current_time(city: str) -> dict:
    return {"status": "success", "city": city, "time": "10:30 AM"}

# Specialist 1: weather only
weather_agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    description="Answers questions about weather in a city.",
    instruction="You are a weather specialist. Use get_weather to answer.",
    tools=[get_weather],
)

# Specialist 2: time only
time_agent = Agent(
    name="time_agent",
    model="gemini-2.5-flash",
    description="Answers questions about the current time in a city.",
    instruction="You are a time specialist. Use get_current_time to answer.",
    tools=[get_current_time],
)

# Coordinator: delegates to specialists
root_agent = Agent(
    name="my_agent",
    model="gemini-2.5-flash",
    description="A coordinator that routes questions to specialists.",
    instruction=(
        "You are a coordinator. "
        "Delegate weather questions to weather_agent. "
        "Delegate time questions to time_agent. "
        "If a question needs both, delegate to both."
    ),
    sub_agents=[weather_agent, time_agent],
)