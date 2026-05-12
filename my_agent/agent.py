from google.adk.agents import Agent, ParallelAgent

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

parallel_specialists = ParallelAgent(
    name="parallel_specialists",
    sub_agents=[weather_agent, time_agent],
)

root_agent = Agent(
    name="my_agent",
    model="gemini-2.5-flash-lite",
    description="A coordinator.",
    instruction="Delegate to parallel_specialists for any weather or time question. Then summarize their results for the user.",
    sub_agents=[parallel_specialists],
)