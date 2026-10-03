import os
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("MODEL", "qwen2.5-coder:7b")