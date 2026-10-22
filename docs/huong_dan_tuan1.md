# Hướng dẫn tuần 1 từ số 0 – nền tảng để làm tuần 2

Tài liệu này dạy lại **cách tạo nên phần tuần 1** (CSDL + khung Flask) theo đúng thứ tự, giải thích
*vì sao* mỗi quyết định, và cuối cùng chỉ rõ **mỗi thứ ở tuần 1 được dùng thế nào ở tuần 2**.
Đọc xong bài này bạn hiểu toàn bộ mã nguồn hiện có và tự viết được phần tuần 2.

---

## Bước 0 – Chuẩn bị môi trường (mỗi máy một lần)

```powershell
cd D:\Công Nghệ Phần Mềm\nha_sach_tuan1\bookstore
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env      # TẠO RIÊNG cho máy này, không push lên GitHub
notepad .env                 # sửa DB_PASSWORD cho đúng máy
```

`requirements.txt` (6 dòng, đủ dùng):
```
Flask>=3.0
Flask-SQLAlchemy>=3.1
Flask-Login>=0.6.3
PyMySQL>=1.1
cryptography>=42.0      # PyMySQL cần gói này để đăng nhập MySQL 8 (caching_sha2_password)
python-dotenv>=1.0
```
> `cryptography` là gói hay bị quên → lỗi `'cryptography' package is required`.

**Vì sao dùng PyMySQL + SQLAlchemy thay vì SQL thuần?** Slide của thầy dùng Flask-SQLAlchemy; SQLAlchemy
cho ta `Model.query` gọn và quản lý transaction/quan hệ. Vẫn là SQL thật, chỉ khác cách viết.

---

## Bước 1 – Thiết kế CSDL: `schema.sql` (NGUỒN SỰ THẬT)

Đề yêu cầu 5 nghiệp vụ (YC1–YC5) → 4 vai trò → **8 bảng**. Bảng nào sinh ra từ nghiệp vụ nào:

| Bảng | Sinh ra từ nghiệp vụ | Cột chính |
| --- | --- | --- |
| `nguoi_dung` | đăng nhập, phân quyền 4 vai trò | `ten_dang_nhap`, `mat_khau_hash`, `ho_ten`, `vai_tro` (ENUM) |
| `quy_dinh` | YC5 – 3 ngưỡng sửa được | `ten` (PK), `gia_tri`, `mo_ta` |
| `the_loai` | YC1/YC3 | `ten` |
| `sach` | YC1/YC3/YC5 | `ma_vach` (UNIQUE), `ten`, `the_loai_id` (FK), `tac_gia`, `don_gia`, `so_luong_ton` |
| `phieu_nhap` | YC1 – phiếu nhập | `ngay_nhap`, `nguoi_quan_ly_id` (FK) |
| `chi_tiet_phieu_nhap` | YC1 – nhiều–nhiều (phiếu ↔ sách) | PK kép `(phieu_nhap_id, sach_id)`, `so_luong` |
| `don_hang` | YC2 (đơn online) + YC3 (hoá đơn quầy) – **dùng chung** | `kenh` (ENUM), `hinh_thuc_tt` (ENUM), `trang_thai` (ENUM), `ngay_tao`, `han_lay_sach` |
| `chi_tiet_don_hang` | YC2/YC3 – nhiều–nhiều (đơn ↔ sách) | PK kép `(don_hang_id, sach_id)`, `so_luong`, `don_gia` |

### 1.1 Ba kiểu ràng buộc được dùng trong schema.sql
```sql
CONSTRAINT ck_sach_ton  CHECK (so_luong_ton >= 0)          -- không cho tồn âm
CONSTRAINT ck_ctpn_so_luong CHECK (so_luong > 0)            -- số lượng phải > 0
CONSTRAINT ck_dh_han_lay CHECK (hinh_thuc_tt = 'TRUC_TIEP' OR han_lay_sach IS NULL)
ENUM('KHACH','NHANVIEN','QUANLY','QUANTRI')                 -- chỉ 4 vai trò hợp lệ
```
- **CHECK**: MySQL 8.0.16+ / MariaDB 10.2+ mới có tác dụng. Bản cũ bỏ qua → **code vẫn phải tự kiểm tra**
  (đây là lý do tuần 2 kiểm tra luật 150/300 trong Python chứ không dựa vào CHECK).
- **ENUM**: ràng buộc giá trị ở mức CSDL, không chỉ ở code.

### 1.2 Dữ liệu mẫu cố ý chọn khó để thử luật
```
5 tài khoản mẫu (quantri, quanly, nhanvien, khachhang, khachhang2), mật khẩu chung 123456
5 thể loại · 20 đầu sách
  - tồn >= 300 (Mắt biếc 320, Dế Mèn 450, Cha giàu cha nghèo 500, Đắc nhân tâm 380, Nghĩ giàu 340) → KHÔNG được nhập
  - tồn = 300 (Truyện Kiều) → biên, KHÔNG được nhập (đề nói "tồn dưới 300")
  - tồn = 299 (Tôi thấy hoa vàng...) → biên, ĐƯỢC nhập
  - tồn = 0 (Vũ trụ (Cosmos)) → hết hàng, thử báo lỗi khi bán/đặt
```

### 1.3 Mật khẩu mẫu được băm sẵn, không lưu mật khẩu thô
```sql
INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau_hash, ho_ten, vai_tro) VALUES
  ('quantri', 'pbkdf2:sha256:1000000$ZZ4wPO10qIa9Gd3E$7164e9d4...', 'Nguyễn Văn Quản Trị', 'QUANTRI'),
```
`mat_khau_hash` = chuỗi băm. Khi đăng nhập, code so băm (`check_password_hash`), không so mật khẩu thô.
Tài khoản tạo mới cũng phải băm bằng **đúng phương pháp** `pbkdf2:sha256` để khớp.

### 1.4 Chạy schema.sql (1 lần cho mỗi máy)
```powershell
mysql -u root -p < schema.sql
```
Hoặc Workbench: *File → Open SQL Script → schema.sql → bấm ⚡*. Hoặc phpMyAdmin: tab Import.
File này **chạy lại được nhiều lần** (xoá & tạo lại bảng của dự án) → dữ liệu thử sẽ mất, cSDL khác không bị ảnh hưởng.

---

## Bước 2 – Khung Flask (4 file, thứ tự rất quan trọng)

### 2.1 `extensions.py` (9 dòng) – tạo `db` và `login` TRƯỚC, gắn app SAU
```python
db = SQLAlchemy()
login = LoginManager()
```
**Vì sao tách riêng?** Nếu khai báo `db = SQLAlchemy(app)` trong `models.py` thì `models.py` phải import `app`
mà `app.py` lại phải import `models` → **import vòng** (`ImportError: cannot import name ... from partially initialized module`).
Cách đúng: `extensions.py` tạo object rỗng → `app.py` gọi `db.init_app(app)`.

### 2.2 `config.py` – cấu hình & bí mật
```python
load_dotenv()                                    # đọc .env cạnh app.py
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "doi-khoa-nay-truoc-khi-nop-bai")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{_user}:{quote(_password, safe='')}@{_host}:{_port}/{_name}?charset=utf8mb4")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
```
- `SECRET_KEY`: ký cookie session. Không có → lỗi khi dùng session.
- `quote(password, safe='')`: mật khẩu có `@`, `/`, `#` sẽ phá URL → mã hoá.
- `charset=utf8mb4`: tiếng Việt có dấu.
- `pool_pre_ping=True`: tránh *"MySQL server has gone away"*.
- `.env` khác nhau mỗi máy → không push (đã có trong `.gitignore`).

### 2.3 `models.py` – 8 lớp khớp 8 bảng
```python
class TheLoai(db.Model):
    __tablename__ = "the_loai"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(100), nullable=False, unique=True)
    sach = relationship("Sach", backref="the_loai", lazy=True)

class Sach(db.Model):
    __tablename__ = "sach"
    the_loai_id = Column(Integer, ForeignKey(TheLoai.id), nullable=False)
```
Quy tắc:
1. `__tablename__` = tên bảng thật (snake_case, khác tên class).
2. **Thứ tự khai báo class quan trọng**: class được `ForeignKey` tham chiếu phải khai báo trước
   (`TheLoai` trước `Sach`, `NguoiDung` trước `PhieuNhap`/`DonHang`...).
3. `relationship(..., backref="the_loai")` tạo thuộc tính đi ngược: `sach.the_loai.ten` trong template.
4. `DonHang` có 2 khoá ngoại cùng trỏ `nguoi_dung` → phải chỉ rõ:
   ```python
   khach = relationship("NguoiDung", foreign_keys=[khach_id], backref="don_hang_da_dat")
   nhan_vien = relationship("NguoiDung", foreign_keys=[nhan_vien_id], backref="don_hang_da_thanh_toan")
   ```
5. **KHÔNG gọi `db.create_all()`** – bảng đã do `schema.sql` tạo. Gọi thêm sẽ thành 2 nguồn sự thật.
6. Thêm hàm tiện ích vào model cho gọn:
   ```python
   class NguoiDung(db.Model, UserMixin):
       def kiem_tra_mat_khau(self, mat_khau):
           return check_password_hash(self.mat_khau_hash, mat_khau)
   class QuyDinh(db.Model):
       @staticmethod
       def lay_gia_tri(ten):
           quy_dinh = db.session.get(QuyDinh, ten)
           return quy_dinh.gia_tri if quy_dinh else None
   class DonHang(db.Model):
       def tinh_tong_tien(self):
           return sum(ct.so_luong * ct.don_gia for ct in self.chi_tiet)
   ```

### 2.4 `app.py` – Application Factory + 4 món đồ dùng suốt đời
```python
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login.init_app(app)
    for module in (auth, kho, admin, dat_sach, ban_hang):
        app.register_blueprint(module.bp)

    @login.user_loader
    def load_user(user_id):
        return db.session.get(NguoiDung, int(user_id))

    @app.template_filter("vnd")
    def dinh_dang_vnd(so):
        return "{:,.0f}".format(so).replace(",", ".") + " đ"

    @app.route("/")
    def trang_chu():
        sach = Sach.query.order_by(Sach.id).all()
        return render_template("index.html", sach=sach)

    @app.errorhandler(SQLAlchemyError)
    def loi_csdl(loi):
        return render_template("loi_db.html", loi=getattr(loi, "orig", loi)), 500

    @app.errorhandler(404)
    def khong_tim_thay(loi):
        return render_template("page_not_found.html"), 404
    return app

app = create_app()
if __name__ == "__main__":
    app.run(debug=True)
```
4 món đồ dùng suốt đời:
| Món | Tác dụng | Dùng ở tuần 2 ở đâu |
|---|---|---|
| `create_app()` | Tạo app theo mẫu Factory | Giữ nguyên, chỉ thêm route vào blueprint |
| `register_blueprint` | Gắn 5 nhóm route | Mỗi người thêm route vào file của mình |
| `login.user_loader` | Nạp lại user từ session | Bắt buộc cho `current_user` trong decorator |
| `template_filter("vnd")` | Định dạng tiền | Giỏ hàng, hoá đơn, báo cáo |
| `errorhandler` | Trang lỗi thân thiện | Lỗi CSDL khi chạy nghiệp vụ |

---

## Bước 3 – Giao diện nền (Jinja2)

### 3.1 `base.html` – khung chung cho MỌI trang
```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<nav class="navbar navbar-expand navbar-dark bg-dark mb-4">
  <div class="navbar-nav">{% include "_menu.html" %}</div>
</nav>
<main class="container">
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% for loai, noi_dung in messages %}
      <div class="alert alert-{{ loai }}">{{ noi_dung }}</div>
    {% endfor %}
  {% endwith %}
  {% block content %}{% endblock %}
</main>
```
- Bootstrap 5 từ CDN → không phải viết CSS.
- `{% include "_menu.html" %}`: menu tách riêng → 2 người cùng sửa không conflict git.
- `{% block content %}`: chỗ các trang con đổ nội dung vào.

### 3.2 `index.html` – trang đọc dữ liệu đầu tiên
```html
{% extends "base.html" %}
{% block title %}Danh sách sách{% endblock %}
{% block content %}
  {% for s in sach %}
    <td>{{ s.the_loai.ten }}</td>          <!-- dùng quan hệ backref -->
    <td>{{ s.don_gia|vnd }}</td>            <!-- dùng bộ lọc vnd -->
  {% endfor %}
{% endblock %}
```
- `{% extends %}` + `{% block %}` = kế thừa template (giống extends/block của slide).
- `loop.index` = số thứ tự trong vòng lặp.
- `{{ s.the_loai.ten }}` – nhờ `backref` mới không phải viết JOIN.

### 3.3 `kiem_tra_db.html` + route `/kiem-tra-db` – TRANG KIỂM TRA quan trọng nhất khi làm nhóm
```python
CAC_BANG = [("nguoi_dung", NguoiDung), ("quy_dinh", QuyDinh), ...]
thong_ke = [(ten_bang, model.query.count()) for ten_bang, model in CAC_BANG]
```
**Hai bạn mở trang này trên máy mình: cùng số dòng = cùng CSDL mẫu.**
Sau khi chạy `schema.sql`, kết quả đúng là:
`nguoi_dung 5 · quy_dinh 3 · the_loai 5 · sach 20 · các bảng còn lại 0`.

### 3.4 `loi_db.html` + `page_not_found.html` – trang lỗi
`loi_db.html` liệt kê 5 nguyên nhân hay gặp để người khác tự sửa được:
MySQL chưa bật / sai `.env` / chưa chạy `schema.sql` / thiếu `cryptography` / thiếu `flask_sqlalchemy`.

---

## Bước 4 – Chạy & tự kiểm tra

```powershell
python app.py            # hoặc: venv\Scripts\python.exe app.py
```
Mở `http://127.0.0.1:5000` → bảng 20 đầu sách; `http://127.0.0.1:5000/kiem-tra-db` → đúng số liệu.
Phải `cd` vào thư mục `bookstore` trước khi chạy (vì `.env` nằm cạnh `app.py` và import là kiểu tuyệt đối).

---

## Bước 5 – Git
```powershell
git init; git add -A; git commit -m "Tuan 1: khung Flask + CSDL + du lieu mau"
git remote add origin https://github.com/<tai-khoan>/<ten-repo>.git
git push -u origin main
```
`.gitignore`: `.env`, `venv/`, `__pycache__/`, `*.pyc`, `.idea/`, `.vscode/`.

---

## Bước 6 – BẢNG LIÊN KẾT: tuần 1 → tuần 2 (đọc để hiểu "code tuần 2 đứng trên nền gì")

| Thứ ở tuần 1 | Tuần 2 dùng nó thế nào |
| --- | --- |
| `schema.sql` (8 bảng) | Mọi truy vấn tuần 2 đều dựa trên đúng 8 bảng này. Đổi bảng = sửa `schema.sql` + `models.py` + báo bạn kia + **cả hai chạy lại `schema.sql`** |
| `models.py` (8 lớp) | `Sach.query...` trong `kho.py`, `dat_sach.py`, `ban_hang.py`; `QuyDinh.lay_gia_tri()` đọc luật 150/300/48 |
| `QuyDinh` + `lay_gia_tri()` | **Nguồn của YC5**: đổi 150 → 100 ở trang quy định thì lần nhập sách sau áp dụng ngay |
| `DonHang.tinh_tong_tien()` | Tổng tiền **không lưu** trong CSDL, luôn tính từ `chi_tiet_don_hang` |
| `NguoiDung.kiem_tra_mat_khau()` | `auth.py` dùng khi đăng nhập; `generate_password_hash` khi đăng ký |
| `app.py` + `register_blueprint` | Tuần 2 chỉ **thêm route vào blueprint**, không sửa `app.py` |
| `login.user_loader` | Điều kiện tiên quyết để có `current_user` → decorator `vai_tro_required` |
| `base.html` (extends/block) | Mọi template tuần 2 kế thừa từ đây; thêm `{% include "_menu.html" %}` |
| `_menu.html` | Thêm mục theo vai trò KHACH / NHANVIEN |
| bộ lọc `vnd` | Giỏ hàng, hoá đơn, báo cáo hiển thị tiền |
| `loi_db.html` + `errorhandler(SQLAlchemyError)` | Lỗi CSDL khi chạy nghiệp vụ tuần 2 |
| route `/kiem-tra-db` | Kiểm tra CSDL sau **mỗi lần thay đổi** trong tuần 2 |
| `db.session` | Thêm/sửa/xoá dữ liệu tuần 2 (luôn kèm `commit()` / `rollback()`) |
| `/` hiện bảng sách | Tuần 2 chuyển trang này sang `dat_sach.py` cho khách xem |

**Nguyên tắc vàng của cả đề tài:** *CSDL là nguồn sự thật duy nhất.* Code chỉ đọc/ghi; không tự ý đổi tên bảng/cột
vì tên đó còn xuất hiện trong sơ đồ lớp, lược đồ CSDL và báo cáo.
