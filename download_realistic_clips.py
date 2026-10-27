import sys
import requests
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CLIPS = [
    ("girl_phone.mp4", "https://assets.mixkit.co/videos/41484/41484-720.mp4"),
    ("relaxing_coffee.mp4", "https://assets.mixkit.co/videos/42436/42436-720.mp4"),
    ("stretching.mp4", "https://assets.mixkit.co/videos/43120/43120-720.mp4")
]

assets_dir = Path("realistic_assets")
assets_dir.mkdir(parents=True, exist_ok=True)

headers = {"User-Agent": "Mozilla/5.0"}

for name, url in CLIPS:
    dest = assets_dir / name
    if dest.exists() and dest.stat().st_size > 100000:
        print(f"Already exists: {name} ({dest.stat().st_size / (1024*1024):.1f} MB)")
        continue

    print(f"Downloading {name} from {url}...")
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            dest.write_bytes(r.content)
            print(f"✅ Saved {name} ({len(r.content) / (1024*1024):.1f} MB)")
        else:
            print(f"❌ Failed: HTTP {r.status_code}")
    except Exception as e:
        print(f"❌ Error downloading {name}: {e}")
