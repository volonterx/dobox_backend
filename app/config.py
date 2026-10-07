import os
from dotenv import load_dotenv

load_dotenv()

SECRET = os.environ["SECRET"]
GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "true").lower() == "true"
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
