import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
AMAP_JS_KEY = os.getenv("AMAP_JS_KEY", "")

DEFAULT_CITY_CENTER = (39.9042, 116.4074)  # 北京天安门

if not DEEPSEEK_API_KEY:
    raise RuntimeError("DEEPSEEK_API_KEY is not set. Please copy .env.example to .env and fill it.")
