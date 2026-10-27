import json
import requests
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

token = cfg["bot_token"]
base_url = f"https://api.telegram.org/bot{token}"

me = requests.get(f"{base_url}/getMe").json()
print("Bot Username:", me.get("result", {}).get("username"))
print("Bot Name:", me.get("result", {}).get("first_name"))

# Check updates with long polling (timeout 5s)
res = requests.get(f"{base_url}/getUpdates?timeout=5", timeout=10).json()
print("Pending updates count:", len(res.get("result", [])))
for u in res.get("result", []):
    print("Update:", u)
