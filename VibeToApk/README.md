# 📱 VibeToApk Studio
> **1-Click Packaging for Vibe Coding to Android APK**  
> Biến ý tưởng Web App từ Vibe Coding thành ứng dụng di động Android (.APK) hoàn chỉnh.

---

## 💡 1. APK là gì? Tại sao dân "Vibe Coding" trên TikTok lại phát sốt vì nó?

- **APK (Android Package Kit)** là định dạng file cài đặt ứng dụng cho hệ điều hành Android (tương tự như file `.exe` trên Windows hay `.dmg` trên macOS).
- **Cơn sốt trên TikTok:**  
  Trào lưu **"Vibe Coding"** (dùng AI như Claude, ChatGPT, Gemini, DeepSeek gõ vài câu prompt tạo ra ứng dụng web/game chỉ trong vài chục giây) đang bùng nổ mạnh mẽ.  
  Tuy nhiên, code sinh ra thường chỉ là file web (`index.html`) chạy trên máy tính. Dân vibe coding luôn muốn:  
  👉 **"Làm sao đóng gói con web app vừa code xong thành 1 file .APK để cài thẳng vào điện thoại Android dùng như app thật hoặc share cho bạn bè tải về?"**
- Dự án nổi bật trên GitHub: `DeadWaveWave/demo2apk` (đã được clone vào thư mục này để tham khảo).

---

## 🍏 2. Còn iPhone (iOS) thì sao? Có làm giống Android được không?

Đây là câu hỏi rất hay mà mọi người đều thắc mắc:
- Trên iPhone, định dạng file cài đặt tên là **`.IPA`** (chứ không phải `.APK`).
- Tuy nhiên, **Apple là một "khu vườn đóng kín" (Walled Garden)** với bảo mật cực kỳ khắt khe:
  - Bạn **KHÔNG THỂ** gửi file `.ipa` qua Zalo/Telegram rồi bảo người dùng iPhone bấm cài đặt tự do như Android được.
  - Apple bắt buộc file `.ipa` phải có **Chứng chỉ số (Code Signing Certificate)** từ tài khoản Apple Developer ($99/năm) hoặc phải cài qua máy Mac.

### 🌟 "Vũ khí bí mật" của dân Vibe Coding trên iPhone: **PWA (Progressive Web App)**
Để giải quyết bài toán trên iPhone mà không tốn $99/năm hay cần máy Mac:
1. Bạn đưa Web App lên mạng (qua Vercel, Netlify, Cloudflare hoặc GitHub Pages hoàn toàn miễn phí).
2. Người dùng mở link bằng trình duyệt **Safari trên iPhone**.
3. Bấm nút **Chia sẻ (Share)** ở đáy màn hình ➔ Chọn **"Thêm vào Màn hình chính" (Add to Home Screen)**.
4. Ngay lập tức:
   - Một **Icon ứng dụng độc lập** xuất hiện trên màn hình iPhone (giống hệt app tải từ App Store).
   - Khi mở lên: **Full màn hình 100%**, ẩn hoàn toàn thanh URL của Safari, có biểu tượng riêng, lưu dữ liệu offline, mượt mà như app gốc!
   - Đã được nhúng sẵn cấu hình trong dự án `VibeToApk` này!

---

## 🛠️ 2. Cấu trúc thư mục VibeToApk (Gọn gàng & Khoa học)

```text
VibeToApk/
├── sample_vibe_app/          # Ứng dụng mẫu Vibe Coding (VibeFocus Pomodoro UI cực đẹp)
│   └── index.html
├── web_studio/               # Giao diện Web Studio giả lập màn hình iPhone/Android
│   └── index.html
├── generated_android_project/# Mã nguồn Android Project native (Java, Gradle, Manifest)
│   ├── app/src/main/
│   │   ├── AndroidManifest.xml
│   │   ├── java/.../MainActivity.java
│   │   └── assets/www/       # Toàn bộ mã web được nhúng vào đây
│   └── .github/workflows/
│       └── build-apk.yml     # Kịch bản GitHub Action tự động build file .apk trên Cloud
├── VibeFocus_Android_Project.zip # File ZIP đóng gói sẵn sàng chia sẻ/deploy
├── vibe_packager.py          # Script Python tự động đóng gói 1-Click
├── run_studio.bat            # Click đúp chuột để mở Web Studio giả lập
└── demo2apk_repo/            # Mã nguồn nghiên cứu từ dự án hot GitHub
```

---

## 🚀 3. Cách sử dụng (3 bước đơn giản):

1. **Xem thử giao diện ứng dụng trên màn hình điện thoại:**
   - Nhấp đúp chuột vào file `run_studio.bat`.
   - Trình duyệt sẽ mở giả lập điện thoại cho phép bạn bấm thử app Pomodoro trực tiếp.

2. **Đóng gói app của riêng bạn:**
   - Đặt file HTML của bạn vào thư mục (hoặc chỉ định đường dẫn).
   - Chạy lệnh:
     ```bash
     python vibe_packager.py -i <duong_dan_file_html> -n "TenAppCuaBan"
     ```
   - Hệ thống sẽ tự động tạo project Android và file ZIP hoàn chỉnh.

3. **Lấy file APK cài vào điện thoại:**
   - **Cách 1 (Miễn phí & Không cần cài Android Studio):** Tải file ZIP lên GitHub cá nhân, tab **Actions** của GitHub sẽ tự động biên dịch và tạo link tải file `.apk` về điện thoại trong 2 phút!
   - **Cách 2 (Cài nhanh qua PWA):** Mở app trên Chrome điện thoại và chọn menu **"Thêm vào màn hình chính" (Install App)**.
