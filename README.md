# my_first_agent

A multi-agent system built with Google's [Agent Development Kit (ADK)](https://google.github.io/adk-docs/). The agent answers questions about the current weather and time in any city, using real data from the [Open-Meteo](https://open-meteo.com/) API.

Built as a hands-on intro to ADK — covers tools, multi-agent delegation, workflow agents, session state, and Cloud Run deployment.

## Live deployment

**Service URL:** https://adk-default-service-name-876216527948.us-central1.run.app

Running on Google Cloud Run with the ADK web UI enabled. Open the URL, pick `my_agent` from the dropdown, and ask something like *"What's the weather in Auckland and what time is it there?" Or Simply put in a location and it will output the time and location*.

## Architecture

The root agent is a `SequentialAgent` that runs two stages:

1. **`ParallelAgent`** — fans out to two specialists that run simultaneously:
   - `weather_agent` calls `get_weather` (Open-Meteo current conditions)
   - `time_agent` calls `get_current_time` (Open-Meteo geocoding → timezone lookup)
2. **`merger_agent`** — reads both results from session state via `{weather_result}` and `{time_result}` placeholders and produces a single combined reply.

Each specialist writes its output to session state with `output_key`, which is how the merger picks them up.

```
SequentialAgent (root)
├── ParallelAgent
│   ├── weather_agent → output_key="weather_result"
│   └── time_agent    → output_key="time_result"
└── merger_agent (reads both from state)
```

## Tech stack

- **Framework:** google-adk (Python)
- **Model:** Gemini (currently `gemini-3.1-flash-lite-preview`)
- **Tools:** custom Python functions calling Open-Meteo
- **Deployment:** Cloud Run (built with `adk deploy cloud_run`)

## Running locally

```bash
# Clone and enter the project
cd my_first_agent

# Set up a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1     # Windows
# source .venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Add your Gemini API key
# Create my_agent/.env with:
#   GOOGLE_GENAI_USE_VERTEXAI=FALSE
#   GOOGLE_API_KEY=your_key_here
# Get a key from https://aistudio.google.com/apikey

# Run the web dev UI
adk web
```

Then open http://127.0.0.1:8000 and select `my_agent`.

For terminal-only interaction:

```bash
adk run my_agent
```

## Project structure

```
my_first_agent/
├── my_agent/
│   ├── agent.py        # Agent definitions and tools
│   ├── __init__.py
│   └── .env            # API keys (gitignored)
├── requirements.txt
├── .gitignore
└── README.md
```

## Redeploying

To push changes to Cloud Run:

```bash
adk deploy cloud_run --project=first-agent-dev --region=us-central1 --with_ui my_agent
```

The API key is set as a Cloud Run environment variable (not baked into the image). To update it:

```bash
gcloud run services update adk-default-service-name \
  --region=us-central1 \
  --update-env-vars="GOOGLE_API_KEY=your_key_here,GOOGLE_GENAI_USE_VERTEXAI=FALSE"
```

## Notes

- The `--with_ui` flag exposes the ADK dev UI publicly. Fine for a demo, but remove it for any real production use — it exposes session data and agent internals.
- Cloud Run only bills for actual request handling, so an idle service costs essentially nothing.
- Free-tier Gemini quotas reset at midnight Pacific Time. Multi-agent setups burn through requests quickly (3+ LLM calls per turn).