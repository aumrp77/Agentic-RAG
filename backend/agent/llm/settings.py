from pydantic import BaseModel
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables first
# From backend/agent/llm/settings.py -> go up 4 levels to project root
env_path = Path(__file__).parent.parent.parent.parent / ".env"

# Try to load with python-dotenv first
load_dotenv(dotenv_path=env_path, override=True)

# If load_dotenv didn't work, manually parse the .env file
if not os.getenv('OPENAI_API_KEY') and env_path.exists():
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('OPENAI_API_KEY='):
                    api_key_value = line.split('=', 1)[1].strip()
                    os.environ['OPENAI_API_KEY'] = api_key_value
                    break
    except Exception:
        pass  # Fail silently if we can't read the file

class LLMSettings(BaseModel):
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 4000
    api_key: str = os.getenv("OPENAI_API_KEY", "").strip()

settings = LLMSettings()