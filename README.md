# 🖼️ Photo Collage App

Ứng dụng ghép nhiều ảnh thành một ảnh duy nhất, viết bằng **Python + Streamlit + Pillow**.  
Bạn có thể tải nhiều ảnh, chọn bố cục, chỉnh màu nền, viền ảnh và tải ảnh ghép về dễ dàng.

## 🚀 Tính năng

- Upload nhiều ảnh (PNG/JPG/WebP).
- 3 kiểu bố cục: **Grid**, **Horizontal strip**, **Vertical strip**.
- Tùy chỉnh:
  - Màu nền.
  - Khoảng cách giữa ảnh.
  - Padding (lề ngoài).
  - Viền ảnh.
  - Giữ tỉ lệ ảnh (letterbox) hoặc ép vừa ô.
  - Giới hạn kích thước ảnh đầu ra.
- Xem trước kết quả và tải về dưới dạng `.jpg`.

## 📦 Cài đặt

1. Clone repo:

   ```bash
   git clone https://github.com/ducduy2424/MosaicArt.git
   cd photo-collage-app
   pip install -r requirements.txt
   streamlit run photo_collage_app.py

   ```
