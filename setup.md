# setup.md
# local development and deployment with optional NVIDIA NIM AI boost

## local run (rule‑based fallback without AI key)
pip install -r requirements.txt
python main.py
# visit http://localhost:8000

## upgrade to AI‑powered roasts (free)
1. sign up at https://build.nvidia.com/explore/discover (no credit card needed)
2. generate an API key from the NVIDIA AI Foundation catalog
3. create a file named `.env` in the project root and add:
   NVIDIA_API_KEY=nvapi-your-key-here
4. restart the app – it will auto‑switch to using Llama 3.1 8B for brutal AI roasts

## deployment (Render)
- push the whole project to a GitHub repository
- go to render.com, create a new Web Service, connect the repo
- build command: `pip install -r requirements.txt`
- start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- in the Render dashboard, add an environment variable:
  NVIDIA_API_KEY = your-key
- deploy (the app ignores .env on Render and uses the env variable)