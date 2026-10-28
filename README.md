# 🦅 CyberBird Lingo PRO v3.2.1 — AI Pedagogical Curator & Cloud OTA Edition

Game bay phản xạ học Tiếng Trung – Tiếng Anh – Tiếng Việt thực chiến dành riêng cho kỹ sư, quản lý sản xuất nhà xưởng & tự động hóa, phát triển bởi **DEAN OPTIMIZE**.

🔗 **Link Cố Định Vĩnh Viễn 24/7 (Mọi Client):** https://truongduc164.github.io/cyberbird-lingo/

---

## 🌟 Điểm Mới Nổi Bật Ở Bản `v3.2.1 PRO`

1. **🤖 AI Biên Tập Viên Sư Phạm ([`ai_diary_curator.py`](./ai_diary_curator.py)):**
   - Đọc dữ liệu nhật ký từ Ổ `Z:\` (`\\100.77.193.96\DeanHub` — **100% Chỉ Đọc, tốn 0 KB trên VPS**) và `ReaKey` (`reavault.db`).
   - Tự động sửa lỗi OCR chữ Hán, lọc bỏ tên riêng/mã nội bộ/nhắc việc cá nhân và tổng kết thành **Chủ đề bài học (`topic_title`) + Bản tóm tắt (`summary`) + Mẹo thực chiến (`learning_tip`) + Từ vựng có từ nhiễu cùng trường nghĩa + Hội thoại cân xứng**.

2. **⏰ Chốt Sổ Định Kỳ Cuối Giờ Làm Việc (`17:30` Hằng Ngày — Zero Background RAM):**
   - Không nuôi vòng lặp chạy ngầm 24/7 gây tốn tài nguyên.
   - Đúng **17:30 chiều hằng ngày** (Windows Task Scheduler `DeanOptimize_CyberBird_DailyDigest_1730`), hệ thống chạy tàng hình ~15 giây gom toàn bộ nhật ký trong ngày (và cả phần tăng ca tối hôm trước nếu có), gọi AI đúc kết 1 lần chuẩn chỉnh, tạo MP3 `zh-CN-XiaoxiaoNeural`, đẩy OTA lên GitHub Pages rồi **tự thoát hoàn toàn**.
   - Nếu `17:30` máy đang tắt/ngủ, cờ `StartWhenAvailable` sẽ tự chạy bù 1 lần ngay khi mở máy lại.

3. **☁️ Link Cố Định Vĩnh Viễn & Kho Offline iPhone/Android ([`cloud_pages_publisher.py`](./cloud_pages_publisher.py)):**
   - Phục vụ 24/7 trên **GitHub Pages CDN** kể cả khi tắt máy tính.
   - Tự động lưu 100% file âm thanh MP3 vào bộ nhớ Offline trên iPhone Safari (hỗ trợ `HTTP 206 Partial Content` trong [`sw.js`](./cyberbird_lingo/sw.js)) và Android PWA.

---

## 🚀 Các Tệp Điều Khiển Nhanh

- **Chốt bài học AI thủ công ngay lập tức & mở Game:** Nhấp đúp [`CHAY_CYBERBIRD_FULL.bat`](./CHAY_CYBERBIRD_FULL.bat).
- **Cài đặt / Bật lại lịch tự động 17:30 hằng ngày:** Chạy [`CAIDAT_LICH_17H30_CUOI_GIO.ps1`](./CAIDAT_LICH_17H30_CUOI_GIO.ps1).
- **Tắt lịch tự động 17:30 hằng ngày:** Nhấp đúp [`TAT_LICH_TU_DONG.bat`](./TAT_LICH_TU_DONG.bat).

---
*Phát triển & Tối ưu bởi **DEAN OPTIMIZE**.*
