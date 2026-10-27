# 🎮 Dự Án 23: CyberBird Lingo PRO v3.1 — Living Daily Diary (`Z:\` DeanHub Edition)

> **Phạm vi dự án (Isolated Workspace):** Phát triển độc lập Game học ngoại ngữ phản xạ bay **CyberBird Lingo PRO** (`cyberbird_lingo/`), hệ thống tổng hợp nhật ký ngầm từ **Ổ Share VPS 24/7 `Z:\` (`\\100.77.193.96\DeanHub`)** qua **Silent Daily Watchdog** (`central_daily_watchdog.py`), và bộ đóng gói ứng dụng Android Native/PWA 1-Click **VibeToApk** (`vibe_packager.py`, `CyberBirdLingo_Android/`).

## 📌 Kiến Trúc Đồng Bộ Hằng Ngày Qua Ổ Share `Z:\` (`v3.1.0-pro`)
- **Nguồn trung tâm 24/7 (`Z:\` -> `\\100.77.193.96\DeanHub` — CHỈ ĐỌC 100%, KHÔNG GHI LÊN Ổ Z:):**
  1. `Z:\_system\nhat_ky.db`: Tự động chụp bản sao ra thư mục tạm (`Zero-Lock`, không bao giờ khóa DB của VPS) để đọc toàn bộ `clipboard_text`, `note`, `starred` (⭐ `#ghim`), `rescue_file` và `reminders` từ cả **máy Dell công xưởng**, **laptop T14**, lẫn **Bot Telegram `@Dean_keyboard_bot`**.
  2. `Z:\03_Nhat_Ky_Hang_Ngay\YYYY-MM-DD.md`: Sổ nhật ký Markdown hằng ngày.
  3. `Z:\01_Files_Cuu_Ho\`: Chỉ đọc file văn bản cứu hộ (`.txt`, `.md`). Tuyệt đối **KHÔNG lưu/sao chép ngược** bộ game hay file âm thanh lên `Z:\04_Kho_Chung_Dung_Chung` để bảo vệ dung lượng VPS!
  4. `15. REA\ReaKey\server\data\reavault.db` & `inbox_diary/`: Kết hợp kho 45 thuật ngữ Tủ điện & Tự động hóa (`glossary`) + lịch sử dịch nhanh ReaKey.
- **Tự Động Hóa Đầu-Cuối (`central_daily_watchdog.py`):**
  - Tự động kết nối lại ổ `Z:\` nếu máy vừa thức dậy từ chế độ Sleep.
  - Tự lọc rác, tự dịch Tiếng Trung -> Tiếng Việt & Tiếng Anh (lưu đệm vĩnh viễn tại `.translation_cache.json`), tự dựng câu trả lời logic thực chiến nhà xưởng, gắn Pinyin thanh điệu và sinh giọng đọc `zh-CN-XiaoxiaoNeural`.
  - **100% file cập nhật (`daily_timeline.json`, `daily_timeline_data.js`, `audio/daily/*.mp3`) chỉ lưu gọn trong thư mục dự án `D:\0.PROGRAMME\4. DEAN OPTIMIZE\23. CyberBird-Lingo-Game\cyberbird_lingo\`**!

## ⚡ Lệnh Chạy Nhanh
```powershell
# 1. Đồng bộ ngay lập tức từ Ổ Z:\ (1 lần):
python central_daily_watchdog.py --once

# 2. Khởi động trọn bộ (Watchdog Z:\ + Web Server 8099 + Cloudflare Tunnel):
.\CHAY_CYBERBIRD_FULL.bat

# 3. Đóng gói Android Native Project + ZIP:
python vibe_packager.py -i cyberbird_lingo -o CyberBirdLingo_Android -n "CyberBirdLingo" -p "com.dean.cyberbirdlingo"
```

## 📱 Quy Tắc Tương Tác Từ Xa (Telegravity / Telegram)
- Khi Sếp DEAN điều khiển từ xa qua Telegram: **TUYỆT ĐỐI KHÔNG gọi công cụ `ask_question`** (vì hộp thoại GUI trên máy tính làm treo phiên từ xa). Nếu cần xin ý kiến chọn phương án, hãy viết trực tiếp câu hỏi đánh số `1, 2, 3` bằng văn bản trong câu trả lời.
- Thương hiệu phát triển: **DEAN OPTIMIZE**.
