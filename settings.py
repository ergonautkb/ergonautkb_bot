import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_TOKEN = os.environ.get("API_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID", -1001684962025)
RULES_URL = "https://t.me/ergonautkb_chat/6042/6043"
