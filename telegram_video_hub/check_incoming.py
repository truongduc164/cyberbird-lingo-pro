import json
import requests
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

token = cfg["bot_token"]
base_url = f"https://api.telegram.org/bot{token}"

resp = requests.get(f"{base_url}/getUpdates", timeout=10)
data = resp.json()
results = data.get("result", [])
print(f"Total updates: {len(results)}")

downloaded_file = None

for u in results:
    msg = u.get("message") or u.get("channel_post") or {}
    if "photo" in msg:
        photos = msg["photo"]
        best_photo = photos[-1]
        fid = best_photo["file_id"]
        print(f"Found photo: file_id={fid}, dimensions={best_photo.get('width')}x{best_photo.get('height')}")
        
        # Get file path
        f_resp = requests.get(f"{base_url}/getFile?file_id={fid}", timeout=10).json()
        if f_resp.get("ok"):
            fpath = f_resp["result"]["file_path"]
            dl_url = f"https://api.telegram.org/file/bot{token}/{fpath}"
            img_data = requests.get(dl_url, timeout=20).content
            
            target_path = Path("user_uploaded_image.jpg")
            target_path.write_bytes(img_data)
            print(f"✅ Downloaded user image to: {target_path.resolve()} ({len(img_data)} bytes)")
            downloaded_file = target_path
    elif "document" in msg:
        doc = msg["document"]
        if doc.get("mime_type", "").startswith("image/"):
            fid = doc["file_id"]
            print(f"Found document image: {doc.get('file_name')}")
            f_resp = requests.get(f"{base_url}/getFile?file_id={fid}", timeout=10).json()
            if f_resp.get("ok"):
                fpath = f_resp["result"]["file_path"]
                dl_url = f"https://api.telegram.org/file/bot{token}/{fpath}"
                img_data = requests.get(dl_url, timeout=20).content
                target_path = Path("user_uploaded_image.jpg")
                target_path.write_bytes(img_data)
                print(f"✅ Downloaded user document image to: {target_path.resolve()} ({len(img_data)} bytes)")
                downloaded_file = target_path

if not downloaded_file:
    print("No image found in getUpdates.")
