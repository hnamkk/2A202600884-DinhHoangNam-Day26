# 🎓 Dự án: Hệ thống kết nối AI với Cơ Sở Dữ Liệu (SQLite MCP Server)

Chào mừng bạn đến với dự án! Đây là một hệ thống giúp các Trợ lý Trí tuệ Nhân tạo (như AI Gemini, Claude) có thể tự động truy cập, tìm kiếm và phân tích dữ liệu học sinh/khóa học trong trường học của chúng ta, mà bạn không cần phải tự tay lục lọi báo cáo.

AI sẽ tự động đóng vai trò như một người thư viện cần mẫn, nhận lệnh từ bạn (bằng tiếng Việt thông thường) và lấy ra chính xác số liệu bạn cần.

---

## 🚀 Hướng dẫn Cài đặt & Sử dụng (Dành cho người mới)

Dự án đã được cấu hình tự động hóa tối đa. Bạn chỉ cần làm theo các bước click chuột đơn giản sau:

### Bước 1: Chuẩn bị hệ thống
Mở cửa sổ dòng lệnh (Terminal / PowerShell) và di chuyển vào thư mục của dự án:
```powershell
cd d:\2A202600884-DinhHoangNam-Day26
```

### Bước 2: Chạy thử Trợ lý AI mô phỏng (Dễ nhất)
Chúng tôi đã chuẩn bị sẵn một giao diện mô phỏng để bạn đóng vai AI và kiểm tra xem hệ thống lấy dữ liệu có chính xác không.

1. Vào thư mục làm việc chính:
   ```powershell
   cd implementation
   ```
2. Nhấn đúp vào file `start_inspector.bat` (hoặc gõ `.\start_inspector.bat` vào Terminal).
3. Trình duyệt của bạn sẽ hiện ra một giao diện bảng điều khiển.

**Cách dùng trên bảng điều khiển:**
- Bấm nút **Connect** (Kết nối).
- Chọn thẻ **Tools** (Công cụ) ở trên cùng. Bạn sẽ thấy 3 công cụ (giống như 3 kỹ năng của AI):
  - 🔍 `search`: Dùng để tra cứu danh sách học sinh hoặc khóa học.
  - ➕ `insert`: Dùng để thêm một dữ liệu mới vào sổ sách.
  - 📊 `aggregate`: Dùng để tính toán thống kê (như tính điểm trung bình, đếm số học sinh).
- Bạn có thể điền thử thông tin vào ô trống và bấm **Run Tool** để xem dữ liệu trả về!

---

## 🛠 Nếu bạn là Kỹ thuật viên (Chạy bằng lệnh)

Nếu bạn không thích dùng giao diện mô phỏng, bạn có thể chạy kịch bản kiểm thử tự động nội bộ:
```powershell
cd implementation
$env:PYTHONPATH='.' ; ..\.venv\Scripts\python.exe verify_server.py
```
*(Hệ thống sẽ tự động in ra màn hình các kết quả test mẫu)*

---

## 💡 Cơ chế hoạt động (Dành cho sự tò mò)
- **UI/UX cho người dùng thực sự nằm ở đâu?** Bạn sẽ không trực tiếp dùng hệ thống này. Hệ thống này chạy ngầm phía sau. Giao diện (UI) thực sự của bạn chính là ô chat của **Gemini** hoặc **ChatGPT**. Bạn chỉ cần chat với AI: *"Hãy tính điểm trung bình của lớp A1 cho tôi"*, và AI sẽ tự dùng hệ thống này để tính toán rồi trả lời lại cho bạn bằng câu văn tự nhiên nhất!
- Dự án có cơ chế bảo vệ nghiêm ngặt: Tuyệt đối không cho phép tìm kiếm các dữ liệu sai lệch hoặc thực hiện các hành động nguy hiểm phá hoại dữ liệu. Lỗi sẽ được báo lại cho AI bằng ngôn ngữ thân thiện để AI tự sửa.
