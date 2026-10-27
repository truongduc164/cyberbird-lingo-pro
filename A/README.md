# ⚡ VIBERADAR (Dự án Thư mục A)
> **Trạm radar bắt sóng xu hướng công nghệ toàn cầu & kích hoạt tia sáng ý tưởng bất chợt (Spontaneous Vibe Sparks)**

Dự án này được thiết kế riêng cho thư mục `A` trong không gian làm việc `12.Vibe idea (tạm)`, giải quyết bài toán: **"Khi chưa biết làm dự án gì, hãy để xu hướng thế giới khơi dậy ý tưởng cho bạn!"**

---

## 🌟 Tính Năng Nổi Bật

1. **Quét xu hướng đa nguồn thời gian thực (Không cần API key)**:
   - 🐱 **GitHub Trending & Rising**: Quét các repository open-source mới nổi, tăng vọt stars trong ngày/tuần.
   - 📰 **Hacker News (Top Stories & Show HN)**: Lấy trực tiếp từ Firebase API các dự án indie maker và bài thảo luận công nghệ hot nhất.
   - 🤗 **Hugging Face AI**: Cập nhật các model AI và Web Spaces demo đang bùng nổ lượt tải và tương tác.
   - ✍️ **Dev.to**: Lấy các bài chia sẻ kinh nghiệm, tutorial và công cụ thịnh hành từ các developer toàn cầu.

2. **💡 Bộ Kích Hoạt Ý Tưởng (Vibe Spark Engine)**:
   - Tự động trích xuất các từ khóa nóng nhất hôm nay (`#agent`, `#llm`, `#automation`, `#cli`,...).
   - **Biến đổi xu hướng thành ý tưởng thực tế**: Đề xuất tên dự án, bài toán giải quyết, độ khó (ví dụ: *1 buổi tối* hoặc *1 cuối tuần*), tech stack đề xuất và điểm Vibe Score (`/100`).
   - Có nút **"🎲 Nảy Ý Tưởng Mới"** để gieo quẻ / xáo trộn và sinh ra các góc nhìn dự án khác nhau.
   - **1-Click Chuyển sang Video**: Bấm nút `🎬 Tạo Video` trên bất kỳ ý tưởng nào để tự động chuyển sang Video Studio sản xuất video ngay lập tức!

3. **🎬 Xưởng Sản Xuất Video Tự Động (Video Automation Studio - Lõi REA)**:
   - **Kế thừa kiến trúc tinh hoa từ `MoneyPrinterTurbo` & `Frame Engine`** nhưng đã được bóc tách tinh gọn (Zero Bloat, không cần GPU khủng, không cần PyTorch nặng nề).
   - Tự động phân cảnh (Storyboard Scenes), sinh giọng đọc tiếng Việt/Anh chuẩn (Google TTS), hiệu ứng chuyển động Ken Burns và Typography nổi bật.
   - Ghép nối và xuất video Full HD `1080x1920` (Shorts/TikTok/Reels) hoặc `1920x1080` (YouTube) chỉ trong ~20 giây!

4. **📝 Két Lưu Trữ Ý Tưởng Bất Chợt (Idea Vault)**:
   - Bất cứ khi nào bạn nảy ra một ý tưởng hay ho trong đầu, hãy gõ ngay vào ô ghi chú.
   - Hỗ trợ đổi trạng thái trực quan: `💡 Ý Tưởng` ➔ `🔨 Đang Build` ➔ `✅ Hoàn Thành`.
   - Lưu trữ bền vững tại file `data/my_vibe_ideas.json`.

4. **Trải nghiệm 2 chế độ**:
   - 🖥️ **Terminal CLI (Bảng màu Rich)**: Chạy nhanh chỉ trong vài giây, xem bảng tóm tắt ngay trên console.
   - 🌐 **Web Dashboard Siêu Đẹp**: Giao diện Dark mode Cyberpunk / Glassmorphism, xem card trực quan, lọc theo nguồn, xem báo cáo Markdown.

---

## 🚀 Cách Sử Dụng Nhanh

### Cách 1: Click Đúp Chuột (Khuyên Dùng Trên Windows)
- Click đúp vào `start_web.bat` ➔ Khởi động Web Dashboard (gồm cả Radar xu hướng và Video Studio) tại `http://127.0.0.1:8765`.
- Click đúp vào `start_video_maker.bat` ➔ Chạy công cụ tạo video tự động trên Terminal với menu chọn lựa.
- Click đúp vào `start_radar.bat` ➔ Chạy quét nhanh hiển thị bảng màu ngay trên màn hình đen (Terminal).

### Cách 2: Chạy Qua Lệnh Terminal
Từ thư mục `A/`:

```powershell
# 1. Tạo video tự động từ chủ đề:
python make_video.py --topic "3 Bí Mật Về Trí Tuệ Nhân Tạo Năm 2026"

# 2. Tạo video từ file truyện ngắn (.txt):
python make_video.py --file "C:/duong_dan/truyen.txt"

# 3. Mở Web Dashboard tương tác toàn diện:
python run_web.py

# 4. Quét nhanh xu hướng dòng lệnh & xuất báo cáo Markdown:
python run_radar.py
```

---

## 📂 Cấu Trúc Thư Mục

```
A/
├── config.py                 # Cấu hình nguồn quét, từ khóa, port web
├── requirements.txt          # Danh sách thư viện (requests, bs4, fastapi, uvicorn, rich)
├── run_radar.py              # Script quét dòng lệnh với bảng màu Rich
├── run_web.py                # Script khởi động Web Dashboard
├── start_radar.bat           # File click đúp chạy terminal trên Windows
├── start_web.bat             # File click đúp chạy Web Dashboard trên Windows
│
├── core/                     # Nhân xử lý logic
│   ├── github_scanner.py     # Quét GitHub Trending & Rising
│   ├── hn_scanner.py         # Quét Hacker News Top & Show HN
│   ├── hf_scanner.py         # Quét Hugging Face Models & Spaces
│   ├── devto_scanner.py      # Quét Dev.to Trending
│   ├── vibe_engine.py        # Phân tích xu hướng & tổng hợp ý tưởng
│   ├── storage.py            # Quản lý lưu trữ cache & két ý tưởng
│   └── report_generator.py   # Xuất báo cáo Markdown
│
├── web/                      # Giao diện Web Dashboard
│   ├── app.py                # Backend FastAPI REST API
│   └── static/
│       ├── index.html        # Giao diện Dashboard hiện đại
│       ├── style.css         # Dark theme, Glassmorphism, Glowing badges
│       └── app.js            # Xử lý tương tác, fetch dữ liệu, lưu ý tưởng
│
├── data/                     # Dữ liệu cục bộ
│   ├── trends_cache.json     # Dữ liệu xu hướng đã quét
│   └── my_vibe_ideas.json    # Két lưu trữ các ý tưởng của bạn
│
└── reports/                  # Báo cáo xuất ra
    ├── vibe_digest_latest.md # Báo cáo xu hướng mới nhất
    └── vibe_digest_YYYY-MM-DD.md
```

---

## 💡 Triết Lý Vibe Coding
Khi một ý tưởng bất chợt nảy sinh:
1. Đừng vội tính toán kiến trúc phức tạp hay setup hạ tầng lớn.
2. Hãy tạo một prototype nhỏ (script đơn lẻ, CLI tool, hoặc micro web UI).
3. Sử dụng các framework nhẹ (`FastAPI`, `Click`, `Rich`, `Streamlit`, `SQLite`) để hoàn thành trong 1 buổi tối.
4. Ghi chép hành trình vào `Két Ý Tưởng` để theo dõi tiến độ từ `💡 Ý Tưởng` ➔ `🔨 Đang Build` ➔ `✅ Hoàn Thành`!
