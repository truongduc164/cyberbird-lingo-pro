# 🦅 CyberBird Lingo PRO v3.3.1 — AI Pedagogical Curator & Cloud OTA Edition

Game bay phản xạ học Tiếng Trung – Tiếng Anh – Tiếng Việt thực chiến dành cho kỹ sư, quản lý sản xuất nhà xưởng & tự động hóa, phát triển bởi **DEAN OPTIMIZE**.

🔗 **Link Cố Định Vĩnh Viễn 24/7 (Mọi Client Web / iOS PWA / Android):** https://truongduc164.github.io/cyberbird-lingo/

---

## 🏗️ Kiến Trúc Tách Lớp (Sẵn Sàng Cho Cá Nhân & Thương Mại Hóa)

Dự án được thiết kế tách biệt hoàn toàn giữa **Core Engine (Sở hữu trí tuệ riêng)** và **Client PWA Phân Phối**:

1. **🔒 Core Engine Repo (Private IP — Repo hiện tại):**
   - Chứa toàn bộ mã nguồn lõi: Bộ thu thập & lọc dữ liệu Read-Only [`central_daily_watchdog.py`](./central_daily_watchdog.py), AI Biên tập viên sư phạm [`ai_diary_curator.py`](./ai_diary_curator.py), Bộ xuất bản Cloud OTA [`cloud_pages_publisher.py`](./cloud_pages_publisher.py), và Bộ đóng gói Android APK [`vibe_packager.py`](./vibe_packager.py).
   - Không chứa khóa bí mật hay token cá nhân trong Git (đã tách mẫu cấu hình tại [`telegram_video_hub/config.example.json`](./telegram_video_hub/config.example.json)).
2. **🌐 Public Client CDN (`truongduc164/cyberbird-lingo` — GitHub Pages):**
   - Chỉ chứa tài nguyên tĩnh đã biên dịch (`index.html`, `sw.js`, `manifest.json`, dữ liệu bài học đã khử thông tin nhạy cảm & âm thanh MP3).
   - Hoạt động 24/7 miễn phí băng thông, không lộ mã nguồn Python backend.

---

## 🌟 Điểm Nổi Bật Ở Bản Chuẩn Ổn Định `v3.3.1-stable`

1. **🤖 AI Biên Tập Viên Sư Phạm $0 Chi Phí API ([`ai_diary_curator.py`](./ai_diary_curator.py)):**
   - Kết nối trực tiếp cầu nối nội bộ `discover_antigravity_ls()` (`language_server.exe --model=flash`) dùng hạn mức có sẵn của Antigravity (**$0 chi phí API trả phí bên ngoài**), kèm bộ biên tập sư phạm dự phòng thông minh.
   - Đọc dữ liệu nhật ký từ Ổ `Z:\` (`\\100.77.193.96\DeanHub` — **100% Chỉ Đọc, tốn 0 KB trên VPS**) và `ReaKey` (`reavault.db`).
   - Tự động sửa lỗi OCR chữ Hán, lọc bỏ tên riêng/mã nội bộ/nhắc việc cá nhân và tổng kết thành **Chủ đề bài học (`topic_title`) + Bản tóm tắt (`summary`) + Mẹo thực chiến (`learning_tip`) + Từ vựng có từ nhiễu cùng trường nghĩa + Hội thoại cân xứng**.

2. **⏰ Chốt Sổ Định Kỳ Cuối Giờ Làm Việc (`17:30` Hằng Ngày — 0 MB RAM Chạy Ngầm):**
   - Không nuôi vòng lặp chạy ngầm 24/7 gây tốn tài nguyên.
   - Đúng **17:30 chiều hằng ngày** (Windows Task Scheduler `DeanOptimize_CyberBird_DailyDigest_1730`), hệ thống chạy tàng hình ~15–20 giây gom toàn bộ nhật ký trong ngày, gọi AI đúc kết 1 lần chuẩn chỉnh, tạo MP3 `zh-CN-XiaoxiaoNeural`, đẩy OTA lên GitHub Pages rồi **tự thoát hoàn toàn**.
   - Nếu `17:30` máy đang tắt/ngủ, cờ `StartWhenAvailable` sẽ tự chạy bù ngay khi mở máy lại.

3. **📱 Tương Thích Toàn Diện iPhone Safari PWA & Android Offline Vault:**
   - Giao diện tối ưu `100dvh` mượt mà trên mọi màn hình di động, nút vào chơi ngay trong tầm tay.
   - Tự động lưu 100% file âm thanh MP3 vào bộ nhớ Offline trên iPhone Safari (hỗ trợ `HTTP 206 Partial Content` trong [`sw.js`](./cyberbird_lingo/sw.js)) và Android PWA.

---

## 🚀 Lộ Trình Mở Rộng Thương Mại Hóa (Commercial Roadmap)

Trên nền tảng `v3.3.1-stable` hiện tại, khi chuyển sang thương mại hóa có thể mở rộng ngay mà không cần viết lại lõi:
- **Gói Chuyên Ngành (Vertical Packs):** Đóng gói các bộ chuyên đề riêng (Cơ khí CNC, SMT/PCB, Khuôn mẫu ép nhựa, Logistics xuất nhập khẩu, Tiếng Trung công xưởng cho doanh nghiệp FDI).
- **Multi-Tenant SaaS / License Key:** Thêm cổng đăng nhập nhẹ (Supabase / Firebase Auth) trên PWA và phân phối gói bài học theo tài khoản học viên hoặc theo phòng ban doanh nghiệp.
- **App Store / Google Play Release:** Xuất bản trực tiếp từ dự án [`CyberBirdLingo_Android`](./CyberBirdLingo_Android) (TWA / WebView Native) lên Google Play hoặc đóng gói Capacitor lên Apple App Store.

---

## 🛠️ Các Tệp Điều Khiển Nhanh

- **Chốt bài học AI thủ công ngay lập tức & mở Game:** Nhấp đúp [`CHAY_CYBERBIRD_FULL.bat`](./CHAY_CYBERBIRD_FULL.bat).
- **Cài đặt / Bật lại lịch tự động 17:30 hằng ngày:** Chạy [`CAIDAT_LICH_17H30_CUOI_GIO.ps1`](./CAIDAT_LICH_17H30_CUOI_GIO.ps1).
- **Tắt lịch tự động 17:30 hằng ngày:** Nhấp đúp [`TAT_LICH_TU_DONG.bat`](./TAT_LICH_TU_DONG.bat).

---
*Phát triển & Tối ưu bởi **DEAN OPTIMIZE**.*
