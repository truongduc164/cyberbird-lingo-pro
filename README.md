# 🦅 CyberBird Lingo PRO v3.0 — Living Daily Diary & Timeline Edition

Game bay phản xạ học Tiếng Trung – Tiếng Anh – Tiếng Việt thực chiến dành riêng cho kỹ sư, quản lý sản xuất nhà xưởng & tự động hóa, phát triển bởi **DEAN OPTIMIZE**.

---

## 🌟 Điểm Mới Nổi Bật Ở Bản `v3.0.0 PRO`

1. **📅 Chế Độ Nhật Ký Ngày (`Daily Timeline`) — Học Đúng Thứ Vừa Đụng Thực Tế:**
   - Tích hợp **Silent Daily Watchdog** ([`central_daily_watchdog.py`](./central_daily_watchdog.py)) chạy ngầm cực êm, tự động tổng hợp dữ liệu giao tiếp thực tế trong ngày từ:
     - Cơ sở dữ liệu dịch thuật **ReaKey** (`reavault.db` — nhật ký WeChat, Zalo, SOP xưởng mũ `BTN-8-11`, đơn hàng Nhật `7071`, lô thử `SMI-16`, thuật ngữ tủ điện...).
     - Thư mục chia sẻ mạng Tailscale (`WinShare`) và hộp thư ghi chú nhanh (`inbox_diary/*.txt`, `*.md`).
   - Tự động lọc câu nhiễu, tách từ vựng cốt lõi (`2–7` ký tự Hán) & dựng tình huống hội thoại hỏi-đáp thực chiến, gắn Pinyin chuẩn dấu và kết xuất giọng đọc Neural `zh-CN-XiaoxiaoNeural` vào `cyberbird_lingo/audio/daily/`.
   - Cho phép chọn ngày trên thanh Timeline và chọn chế độ bay: **🔥 Trộn Từ & Câu**, **🎯 Chỉ Từ Nhật Ký**, hoặc **💬 Chỉ Câu Thực Chiến**.

2. **⚡ Kho Nội Dung Mở Rộng Lên `250+` Đơn Vị Học Thực Chiến:**
   - **Từ vựng cơ sở + Tủ điện Tự động hóa (`165+` từ):** Gồm 7 chuyên ngành (`🏭 Xưởng Mũ`, `⚡ Điện Tử & TĐH`, `💼 Văn Phòng`, `💻 Công Nghệ`, `🗣️ Giao Tiếp`, `☕ Ẩm Thực`, `🐱 Động Vật`), tích hợp trọn bộ 45 thuật ngữ thiết bị điện công nghiệp (`变频器`, `微型断路器`, `交流接触器`, `伺服电机`, `触摸屏`, `可编程控制器`...).
   - **Nhật ký thực tế trong ngày (`89+` từ & `6+` câu thực chiến mới mỗi ngày)**.
   - **Hội thoại phản xạ (`31+` tình huống):** Có bộ lọc chủ đề riêng biệt.

3. **🎛️ Trải Nghiệm Điều Khiển & Âm Thanh Chuẩn AAA:**
   - Tự động đồng bộ tốc độ đọc giọng bản xứ theo cấp độ bay (`🟢 Dễ 0.85x` • `🟡 Vừa 1.0x` • `🔴 Pro 1.2x`) hoặc chỉnh tay độc lập.
   - Tùy chỉnh cỡ chữ ô cổng bay (`14px` • `16.5px` • `19px`) kết hợp thuật toán `maxWidth` tự co giãn thông minh, đảm bảo câu dài không bao giờ tràn khỏi khung cổng.
   - Tương thích **100% Offline** trên cả Web PWA (iOS/Android) lẫn gói cài đặt **Android Native APK** nhờ cơ chế kép `daily_timeline.json` + `daily_timeline_data.js`.

---

## 🚀 Hướng Dẫn Khởi Chạy Nhanh

- **Khởi chạy trọn gói 1-Click (Watchdog + Server + Cloudflare Tunnel):**
  Nhấp đúp vào [`CHAY_CYBERBIRD_FULL.bat`](./CHAY_CYBERBIRD_FULL.bat).
- **Chỉ bật Silent Watchdog chạy ngầm hoàn toàn ẩn cửa sổ:**
  Nhấp đúp vào [`START_SILENT_WATCHDOG.vbs`](./START_SILENT_WATCHDOG.vbs).
- **Đóng gói ra dự án Android Studio & GitHub Actions APK:**
  ```powershell
  python vibe_packager.py -i cyberbird_lingo -o CyberBirdLingo_Android -n "CyberBirdLingo" -p "com.dean.cyberbirdlingo"
  ```

---
*Phát triển & Tối ưu bởi **DEAN OPTIMIZE**.*
