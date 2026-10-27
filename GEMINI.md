# 🎮 Dự Án 23: CyberBird Lingo PRO v3.0 — Living Daily Diary & Timeline Edition

> **Phạm vi dự án (Isolated Workspace):** Phát triển độc lập Game học ngoại ngữ phản xạ bay **CyberBird Lingo PRO** (`cyberbird_lingo/`), hệ thống tổng hợp nhật ký ngầm **Silent Daily Watchdog** (`central_daily_watchdog.py`), và bộ đóng gói ứng dụng Android Native/PWA 1-Click **VibeToApk** (`vibe_packager.py`, `CyberBirdLingo_Android/`).

## 📌 Trạng Thái Hiện Tại (`v3.0.0-pro`)
- **3 Chế Độ Bay Phản Xạ Chuyên Sâu:**
  1. `📅 Nhật Ký Ngày (Timeline)`: Tự động nạp từ vựng & hội thoại thực tế mỗi ngày từ nhật ký dịch thuật ReaKey (`reavault.db`), thư mục chia sẻ Tailscale (`WinShare`) và `inbox_diary/` — hỗ trợ lọc `[🔥 Trộn Từ & Câu | 🎯 Chỉ Từ Nhật Ký | 💬 Chỉ Câu Thực Chiến]` và chọn từng ngày trên Timeline.
  2. `🎯 Từ Vựng (165+ từ)`: Đã tích hợp thêm 45 thuật ngữ tủ điện & tự động hóa công nghiệp (`变频器`, `微型断路器`, `交流接触器`, `伺服电机`, `触摸屏`...) cùng 7 chủ đề (`🏭 Xưởng Mũ`, `⚡ Điện Tử & TĐH`, `💼 Văn Phòng`, `💻 Công Nghệ`, `🗣️ Giao Tiếp`, `☕ Ẩm Thực`, `🐱 Động Vật`).
  3. `💬 Hội Thoại Thực Chiến (31+ tình huống)`: Có thanh lọc chủ đề riêng (`🌟 Tất Cả`, `🏭 Nhà Xưởng`, `💻 IT & Kỹ Thuật`, `💼 Văn Phòng`, `🤝 Đời Sống`).
- **Silent Daily Watchdog (`central_daily_watchdog.py` + `START_SILENT_WATCHDOG.vbs`):**
  - Chạy hoàn toàn im lặng dưới nền (`pythonw.exe`, zero popup), quét tự động mỗi 5 phút.
  - Tự lọc nhiễu, gắn Pinyin thanh điệu (`pypinyin`), sinh giọng đọc Neural `zh-CN-XiaoxiaoNeural` (`cyberbird_lingo/audio/daily/`), và xuất đồng thời `daily_timeline.json` (Live HTTP) + `daily_timeline_data.js` (Offline APK / `file://` không dính lỗi CORS).
- **Tính năng UX & Offline PWA / APK:**
  - Tự động đồng bộ tốc độ đọc theo cấp độ (`0.85x / 1.0x / 1.2x`), tùy chỉnh cỡ chữ ô cổng bay (`14px / 16.5px / 19px`) kèm cơ chế tự co chữ `maxWidth` chống tràn cổng.
  - Service Worker `cyberbird-lingo-v3.0-timeline` cơ chế **Network-First** cho HTML & dữ liệu nhật ký, **Cache-First** cho âm thanh MP3.

## ⚡ Lệnh Chạy Nhanh
```powershell
# 1. Đồng bộ Nhật Ký Ngày tức thì (1 lần):
python central_daily_watchdog.py --once

# 2. Kích hoạt Watchdog chạy ngầm hoàn toàn im lặng (Zero Window):
wscript.exe START_SILENT_WATCHDOG.vbs

# 3. Khởi động trọn bộ (Watchdog + Web Server 8099 + Cloudflare Tunnel):
.\CHAY_CYBERBIRD_FULL.bat

# 4. Đóng gói Android Native Project (v3.0.0) + ZIP:
python vibe_packager.py -i cyberbird_lingo -o CyberBirdLingo_Android -n "CyberBirdLingo" -p "com.dean.cyberbirdlingo"
```

## 📱 Quy Tắc Tương Tác Từ Xa (Telegravity / Telegram)
- Khi Sếp DEAN điều khiển từ xa qua Telegram: **TUYỆT ĐỐI KHÔNG gọi công cụ `ask_question`** (vì hộp thoại GUI trên máy tính làm treo phiên từ xa). Nếu cần xin ý kiến chọn phương án, hãy viết trực tiếp câu hỏi đánh số `1, 2, 3` bằng văn bản trong câu trả lời.
- Thương hiệu phát triển: **DEAN OPTIMIZE**.
