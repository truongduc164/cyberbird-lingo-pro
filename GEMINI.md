# 🎮 Dự Án 23: CyberBird Lingo PRO & VibeToApk Studio

> **Phạm vi dự án (Isolated Workspace):** Chỉ tập trung phát triển Game học ngoại ngữ phản xạ bay **CyberBird Lingo PRO** (`cyberbird_lingo/`) và bộ đóng gói ứng dụng Android Native/PWA 1-Click **VibeToApk** (`vibe_packager.py`, `CyberBirdLingo_Android/`).

## 📌 Trạng Thái Hiện Tại (`v2.6.0-pro`)
- **Kho nội dung:** 120+ từ vựng & 25 tình huống hội thoại thực chiến có giọng đọc Neural `zh-CN-XiaoxiaoNeural` (`cyberbird_lingo/audio/`):
  - `🏭 Xưởng Mũ (27)` • `⚡ Điện Tử & TĐH (15)` • `💼 Văn Phòng (15)` • `💻 Công Nghệ (15)` • `🗣️ Giao Tiếp (16)` • `☕ Ẩm Thực (12)` • `🐱 Động Vật (6)`.
- **Tính năng UX:** Tự động đồng bộ tốc độ đọc theo cấp độ (`0.85x / 1.0x / 1.2x`), tùy chỉnh cỡ chữ ô cổng bay (`14px / 16.5px / 19px`), nút `🏠 Menu` tức thì, hỗ trợ PWA iOS/Android & gói APK Offline 100%.
- **Định hướng tiếp theo (Central Daily Watchdog):** Tích hợp `central_daily_sync.py` đọc log thực tế hằng ngày từ `D:\0.PROGRAMME\4. DEAN OPTIMIZE\15. REA\ReaKey\server\data\reavault.db` (cột `ts`) để nạp vào chế độ Daily Timeline.
- **Lịch sử phiên trước (khi còn ở thư mục tạm 12):** `conversation://e82280ae-fffc-487b-b2f4-243487438045`

## ⚡ Lệnh Chạy Nhanh
```powershell
# Chạy web server cục bộ cổng 8099:
python -m http.server 8099 --directory cyberbird_lingo

# Đóng gói Android Native Project + ZIP:
python vibe_packager.py -i cyberbird_lingo -o CyberBirdLingo_Android -n "CyberBirdLingo" -p "com.dean.cyberbirdlingo"
```

## 📱 Quy Tắc Tương Tác Từ Xa (Telegravity / Telegram)
- Khi Sếp DEAN điều khiển từ xa qua Telegram: **TUYỆT ĐỐI KHÔNG gọi công cụ `ask_question`** (vì hộp thoại GUI trên máy tính làm treo phiên từ xa). Nếu cần xin ý kiến chọn phương án, hãy viết trực tiếp câu hỏi đánh số `1, 2, 3` bằng văn bản trong câu trả lời.
- Thương hiệu phát triển: **DEAN OPTIMIZE**.
