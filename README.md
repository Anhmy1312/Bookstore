# Quản lý nhà sách – Bài tập lớn Công nghệ phần mềm (Đề tài 3)

Website Python Flask + MySQL, viết theo slide Python Flask của thầy (Flask-SQLAlchemy, Flask-Login). Đây là **khung dự án tuần 1**: CSDL + dữ liệu mẫu + trang đọc dữ liệu từ MySQL.
Các chức năng (đăng nhập, nhập sách, bán sách, đặt sách, báo cáo, quy định) sẽ làm từ tuần 2.

## Cần cài trước
- Python 3.10 trở lên
- MySQL 8.0.16+ (hoặc XAMPP/MariaDB 10.2+). Bản cũ hơn vẫn chạy nhưng sẽ **bỏ qua** các ràng buộc CHECK.

## Chạy trên máy mới (làm đúng thứ tự)

**1. Tạo môi trường ảo và cài thư viện** (chạy trong thư mục `bookstore/`)

| Hệ điều hành | Lệnh |
| --- | --- |
| Windows (PowerShell/CMD) | `python -m venv venv` → `venv\Scripts\activate` |
| macOS / Linux | `python3 -m venv venv` → `source venv/bin/activate` |

Rồi: `pip install -r requirements.txt`

**2. Khai báo mật khẩu MySQL của máy bạn**
Copy `.env.example` thành `.env`, mở ra sửa `DB_PASSWORD` (XAMPP mặc định không có mật khẩu thì để trống sau dấu `=`).
File `.env` mỗi máy một khác, **không đưa lên GitHub** (đã có trong `.gitignore`).

**3. Tạo CSDL + dữ liệu mẫu**
- Dòng lệnh: `mysql -u root -p < schema.sql`
- Hoặc MySQL Workbench: *File → Open SQL Script → chọn `schema.sql` → bấm biểu tượng tia sét*.
- Hoặc phpMyAdmin (XAMPP): tab *Import* → chọn `schema.sql`.

**4. Chạy website**
`python app.py` rồi mở http://127.0.0.1:5000

**5. Tự kiểm tra** – mở http://127.0.0.1:5000/kiem-tra-db. Kết quả đúng:
`nguoi_dung 5 · quy_dinh 3 · the_loai 5 · sach 20 · các bảng còn lại 0`. Trang chủ hiện bảng 20 đầu sách.

## Tài khoản mẫu (mật khẩu chung: `123456`)

| Tên đăng nhập | Vai trò | Dùng cho |
| --- | --- | --- |
| `quantri` | Người quản trị | Thống kê, báo cáo, thay đổi quy định |
| `quanly` | Người quản lý (kho) | Lập phiếu nhập, quản lý sách |
| `nhanvien` | Nhân viên bán hàng | Bán tại quầy, thu tiền đơn trả tại nhà sách |
| `khachhang`, `khachhang2` | Khách hàng | Đặt sách online |

## Cấu trúc thư mục và người phụ trách

| Thư mục / file | Việc | Ai |
| --- | --- | --- |
| `app.py`, `config.py`, `extensions.py` | Khởi động app, cấu hình + chuỗi kết nối MySQL, khai báo `db` và `login` | Cả hai (sửa phải báo nhau) |
| `models.py` | 8 lớp model (`db.Model`) khớp 8 bảng trong `schema.sql` | Cả hai (sửa phải báo nhau) |
| `schema.sql` | Bảng + dữ liệu mẫu + tài khoản mẫu (nguồn sự thật của CSDL, code **không** gọi `db.create_all()`) | Cả hai (sửa phải báo nhau) |
| `blueprints/auth.py`, `dat_sach.py`, `ban_hang.py` | Đăng nhập, đặt sách, bán tại quầy | B |
| `blueprints/kho.py`, `admin.py` | Nhập sách + quản lý sách, báo cáo + quy định | A |
| `templates/` | `base.html` dùng chung; mỗi module một thư mục con | Theo module |

## Quy tắc làm việc chung
- Ai sửa cấu trúc bảng thì sửa trong `schema.sql` **và** lớp tương ứng trong `models.py`, nhắn người kia, và **cả hai chạy lại `schema.sql`** (dữ liệu thử sẽ mất).
- Dùng GitHub private; ít nhất cũng gửi file zip cho nhau mỗi tối.
- Tên bảng/cột phải trùng với báo cáo (sơ đồ lớp, lược đồ CSDL). Đổi tên ở đâu thì đổi ở cả ba nơi: báo cáo, `schema.sql`, code.

## Lỗi thường gặp

| Thông báo | Cách xử lý |
| --- | --- |
| `Access denied for user 'root'` | Sai `DB_PASSWORD` trong `.env` |
| `Unknown database 'nha_sach'` | Chưa chạy `schema.sql` (bước 3) |
| `Can't connect to MySQL server` | MySQL chưa bật, hoặc sai `DB_PORT` |
| `'cryptography' package is required` | Chạy lại `pip install -r requirements.txt` |
| `No module named 'flask_sqlalchemy'` hoặc `'flask_login'` | Chưa bật môi trường ảo, hoặc chưa `pip install -r requirements.txt` |
| Chữ tiếng Việt bị lỗi font trong MySQL Workbench | Chạy lại `schema.sql` (file đã đặt `utf8mb4`) |
