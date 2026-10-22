# Hướng dẫn đọc toàn bộ mã nguồn – Đề tài 3 Quản lý nhà sách

Tài liệu này giảng giải **từng dòng code** của phần đã code (tuần 2: phần A kho + quản trị,
phần B khách + bán hàng). Đọc theo thứ tự bài 0 → bài 10 sẽ hiểu hệ thống chạy thế nào.

---

## Bài 0 – Bản đồ toàn bộ mã nguồn

```
bookstore/
├── app.py                  Khởi động app, đăng ký blueprint, user_loader, bộ lọc vnd, xử lý lỗi
├── config.py               Đọc .env, dựng chuỗi kết nối MySQL
├── extensions.py           Tạo db = SQLAlchemy(), login = LoginManager() (tách riêng chống import vòng)
├── models.py               8 lớp model khớp 8 bảng trong schema.sql
├── schema.sql              NGUỒN SỰ THẬT của CSDL: tạo bảng + dữ liệu mẫu
├── quyen.py                Decorator phân quyền theo 4 vai trò (FILE DÙNG CHUNG)
├── nghiem_vu.py            Hàm nghiệp vụ dùng chung: tạo đơn, tự huỷ đơn quá hạn, giỏ hàng (FILE DÙNG CHUNG)
├── blueprints/
│   ├── auth.py             Đăng nhập / đăng ký / đăng xuất / tài khoản
│   ├── kho.py              Quản lý sách + lập phiếu nhập (QUANLY)
│   ├── admin.py            Sửa quy định (QUANTRI) — tuần 3 thêm báo cáo
│   ├── dat_sach.py         Khách xem sách, giỏ hàng, đặt sách, đơn của tôi (KHACH)
│   └── ban_hang.py         Bán tại quầy, hoá đơn, xác nhận lấy sách (NHANVIEN)
├── templates/
│   ├── base.html           Khung HTML chung (nav, hiện flash) — mọi trang extends
│   ├── _menu.html          Menu theo vai trò (file riêng để 2 người sửa khỏi conflict)
│   ├── dang_nhap.html, dang_ky.html, tai_khoan.html
│   ├── kho/                sach_danh_sach.html, sach_form.html, phieu_nhap.html
│   ├── dat_sach/           danh_sach.html, gio_hang.html, dat_hang.html, don_hang.html, chi_tiet_don_hang.html
│   └── ban_hang/           ban_hang.html, hoa_don.html, don_cho_lay.html
├── kiem_thu_tuan2.py            Bộ kiểm thử tự động cho phần A
├── kiem_thu_khach_ban_hang.py   Bộ kiểm thử tự động cho phần B
└── docs/
    ├── hinh/               use_case_tong.png, so_do_lop.png, luoc_do_csdl.png
    ├── nguon_ve/           File .dot (Graphviz) + các file .md Mermaid cho UC02/03/04/05/07
    ├── thiet_ke_xu_ly_A.md, thiet_ke_xu_ly_B.md   Bảng 3 cột cho mục 2.5 báo cáo
    └── huong_dan_code.md   File này
```

**Quy ước quan trọng:** `schema.sql` là nguồn sự thật của CSDL. `models.py` phải khớp từng cột.
Không bao giờ gọi `db.create_all()` (sẽ tạo 2 nguồn sự thật).

---

## Bài 1 – Một request đi qua hệ thống như thế nào

Hãy hình dung 1 lần bấm nút "Thêm sách vào giỏ hàng" của khách:

```
Trình duyệt  --POST /dat-sach/gio-hang/them-->  Flask
                                                ├─ tìm đúng route trong url_map
                                                ├─ chạy decorator vai_tro_required("KHACH")
                                                ├─ vào view function dat_sach.them_vao_gio()
                                                ├─ đọc/ghi MySQL qua SQLAlchemy (models.py)
                                                └─ render_template(...) -> HTML -> trả về trình duyệt
```

### 1.1 `app.py` – nơi khởi động mọi thứ

```python
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)   # nạp cấu hình từ config.py
    db.init_app(app)                  # gắn SQLAlchemy vào app
    login.init_app(app)               # gắn Flask-Login vào app

    for module in (auth, kho, admin, dat_sach, ban_hang):
        app.register_blueprint(module.bp)   # đăng ký 5 nhóm route

    @login.user_loader
    def load_user(user_id):
        return db.session.get(NguoiDung, int(user_id))

    @app.template_filter("vnd")
    def dinh_dang_vnd(so):
        return "{:,.0f}".format(so).replace(",", ".") + " đ"

    @app.errorhandler(SQLAlchemyError)
    def loi_csdl(loi): ...          # lỗi CSDL -> trang loi_db.html
    @app.errorhandler(404)
    def khong_tim_thay(loi): ...    # trang không tồn tại
    return app
```

**Điểm cần hiểu:**
- `create_app()` dùng mẫu **Application Factory**: tạo app trong hàm, trả về. Sau này muốn tạo app
  khác (test, script) chỉ cần gọi `create_app()`.
- `db.init_app(app)` + `login.init_app(app)`: vì dự án chia nhiều file, nếu khai báo `db = SQLAlchemy(app)`
  ngay trong `models.py` sẽ gây **import vòng** (models ↔ app). Nên `extensions.py` tạo `db` trống trước,
  rồi `app.py` gắn app vào sau.
- `@login.user_loader`: Flask-Login chỉ lưu **id** người dùng trong cookie. Mỗi request, Flask-Login gọi hàm này
  để lấy lại đối tượng `NguoiDung` đầy đủ → biến `current_user` trong template/code.
- `@app.template_filter("vnd")`: đăng ký bộ lọc Jinja. Trong template gọi `{{ sach.don_gia | vnd }}` → "95.000 đ".

### 1.2 `config.py` – nối tới MySQL mà không lộ mật khẩu

```python
load_dotenv()          # đọc file .env cạnh app.py
_host = os.environ.get("DB_HOST", "127.0.0.1")
_password = os.environ.get("DB_PASSWORD", "")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "doi-khoa-nay-truoc-khi-nop-bai")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{_user}:{quote(_password, safe='')}"
        f"@{_host}:{_port}/{_name}?charset=utf8mb4")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
```

- `SECRET_KEY`: dùng để **ký** cookie session. Không có nó thì Flask báo lỗi khi dùng session.
- `quote(_password, safe='')`: mật khẩu có ký tự đặc biệt (`@`, `/`, `#`) sẽ phá URL kết nối
  → `quote` mã hoá cho an toàn.
- `pool_pre_ping=True`: trước khi lấy kết nối từ pool, kiểm tra còn sống không → tránh lỗi
  "MySQL server has gone away" khi MySQL ngủ lâu rồi tắt.
- Mỗi máy một file `.env` riêng, `.env` đã nằm trong `.gitignore` (không push lên GitHub).

### 1.3 `models.py` – ánh xạ bảng MySQL thành lớp Python

```python
class TheLoai(db.Model):
    __tablename__ = "the_loai"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(100), nullable=False, unique=True)
    sach = relationship("Sach", backref="the_loai", lazy=True)

class Sach(db.Model):
    __tablename__ = "sach"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_vach = Column(String(13), nullable=False, unique=True)
    the_loai_id = Column(Integer, ForeignKey(TheLoai.id), nullable=False)
    so_luong_ton = Column(Integer, nullable=False, default=0)
```

**Điểm cần hiểu:**
- `__tablename__`: tên bảng thật trong MySQL (viết snake_case, khác tên class).
- `Column(...)` ↔ cột trong bảng: kiểu dữ liệu, `nullable`, `unique`, `default`.
- `ForeignKey(TheLoai.id)`: cột khoá ngoại → MySQL lo chặn dữ liệu sai (thêm sách mà `the_loai_id`
  không tồn tại sẽ bị MySQL từ chối).
- `relationship(..., backref="the_loai", lazy=True)`: tạo thuộc tính `sach.the_loai` để lấy danh mục
  của 1 cuốn sách mà không phải viết SQL JOIN. `lazy=True` = chỉ lấy khi thật sự cần.
- **Thứ tự khai báo class quan trọng**: class được `ForeignKey` tham chiếu phải khai báo trước.
- `DonHang` có 2 khoá ngoại cùng trỏ tới `nguoi_dung` → phải chỉ rõ `foreign_keys=[...]` trong `relationship`.

---

## Bài 2 – Đăng nhập và phân quyền (nền của cả hệ thống)

### 2.1 `auth.py` – đăng nhập

```python
@bp.route("/dang-nhap", methods=["GET", "POST"])
def dang_nhap():
    ...
    nguoi_dung = db.session.query(NguoiDung).filter(
        NguoiDung.ten_dang_nhap == ten_dang_nhap     # so với TÊN CỘT, không so biến với chính nó
    ).first()
    if nguoi_dung is None or not nguoi_dung.kiem_tra_mat_khau(mat_khau):
        loi = "Tên đăng nhập hoặc mật khẩu không đúng."
    else:
        login_user(nguoi_dung)        # lưu id vào session (cookie đã ký)
        dich = request.args.get("next", "")
        if dich.startswith("/") and not dich.startswith("//"):
            return redirect(dich)     # quay lại đúng trang khách định vào trước đó
        return redirect(url_for("trang_chu"))
```

- `login_user()`: Flask-Login ghi `user_id` vào session. Từ đó mọi request đều biết "ai đang đăng nhập"
  qua `current_user`.
- `kiem_tra_mat_khau()` (trong `models.py`): `check_password_hash(self.mat_khau_hash, mat_khau)` –
  so băm, không so mật khẩu thô. CSDL chỉ lưu `mat_khau_hash`.
- `next`: khi bị decorator chặn, ta gửi kèm `?next=/duong-dan-cu`. Sau khi đăng nhập thì quay lại
  đúng trang đó. Kiểm tra `startswith("/")` để chặn **open redirect** (không cho chuyển tới site ngoài).
- Băm mật khẩu khi đăng ký: `generate_password_hash(mk, method="pbkdf2:sha256")` – dùng **đúng** phương pháp
  băm của tài khoản mẫu trong `schema.sql` (không dùng `scrypt` mặc định vì một số máy macOS không hỗ trợ).

### 2.2 `quyen.py` – decorator phân quyền (FILE DÙNG CHUNG, không sửa chung)

```python
def vai_tro_required(*vai_tro_duoc_phep):
    def boc_trong(f):
        @wraps(f)
        def kiem_tra(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.dang_nhap", next=request_full_path()))
            if vai_tro_hien_tai() not in vai_tro_duoc_phep:
                flash("Bạn không có quyền truy cập chức năng này.", "danger")
                return redirect(url_for("trang_chu"))
            return f(*args, **kwargs)
        return kiem_tra          # ← PHẢI trả về kiem_tra, không phải boc_trong
    return boc_trong
```

**Bài học:**
- **Decorator** = hàm bọc hàm khác để thêm hành vi trước khi hàm gốc chạy. Giống "anh bảo vệ đứng ở cửa".
- `@wraps(f)`: giữ lại tên/docstring của hàm gốc. Quan trọng với Flask: **tên hàm quyết định tên endpoint**;
  trả nhầm biến sẽ gây lỗi *"View function mapping is overwriting an existing endpoint"*.
- `*vai_tro_duoc_phep`: nhận nhiều vai trò. Dùng: `@vai_tro_required("QUANLY")` hoặc
  `@vai_tro_required("NHANVIEN", "QUANTRI", "QUANLY")`.
- Sử dụng:
  ```python
  @bp.route("/kho/sach")
  @vai_tro_required("QUANLY")     # decorator PHẢI nằm dưới @bp.route
  def danh_sach_sach(): ...
  ```
  (Trang đăng nhập nằm trên, nên khi request tới: `route` → `vai_tro_required` → view function.)

---

## Bài 3 – Phần A: quản lý sách và lập phiếu nhập (`kho.py`)

### 3.1 Danh sách + tìm kiếm

```python
truy_van = Sach.query
if tu_khoa:
    truy_van = truy_van.filter(
        db.or_(Sach.ten.ilike(f"%{tu_khoa}%"),
               Sach.ma_vach.ilike(f"%{tu_khoa}%"),
               Sach.tac_gia.ilike(f"%{tu_khoa}%")))
if the_loai_id.isdigit():
    truy_van = truy_van.filter(Sach.the_loai_id == int(the_loai_id))
sach_list = truy_van.order_by(Sach.id).all()
```
`Sach.query` là `select` của SQLAlchemy; `.filter()` thêm điều kiện, `.all()` lấy hết kết quả.
`ilike` = không phân biệt hoa/thường, `%` = "ký tự bất kỳ".

### 3.2 Thêm / sửa / xoá – bắt lỗi ràng buộc

```python
try:
    db.session.add(sach)
    db.session.commit()
except IntegrityError:
    db.session.rollback()          # ← BẮT BUỘC rollback sau khi lỗi
    flash("Mã vạch đã tồn tại, vui lòng dùng mã khác.", "danger")
```

- `db.session.add(x)`: đưa đối tượng vào "hàng đợi" của session.
- `db.session.commit()`: ghi xuống MySQL (thực thi trong 1 transaction).
- `IntegrityError`: MySQL từ chối (mã vạch trùng, khoá ngoại sai...). Bắt lỗi để hiện thông báo thân thiện
  thay vì trang lỗi 500.
- **`db.session.rollback()` là bắt buộc**: session đang ở trạng thái lỗi, mọi query sau sẽ hỏng
  (`PendingRollbackError`) nếu không rollback.

**Xoá sách đã có giao dịch** (bài học quan trọng):
```python
da_nhap = db.session.query(ChiTietPhieuNhap).filter_by(sach_id=sach_id).first()
da_ban = db.session.query(ChiTietDonHang).filter_by(sach_id=sach_id).first()
if da_nhap is not None or da_ban is not None:
    flash("Sách đã có giao dịch, không thể xoá.", "danger")
    return redirect(...)
db.session.execute(db.delete(Sach).where(Sach.id == sach_id))   # bulk delete
```
- Ta **kiểm tra trước** để báo đúng lý do cho người dùng.
- Dùng **bulk delete** (`db.session.execute(db.delete(...))`) thay vì `db.session.delete(sach)`:
  khi xoá bằng ORM, SQLAlchemy cố tự "xoá trắng" khoá ngoại ở bảng con (`chi_tiet_phieu_nhap.sach_id` là
  **khoá chính**, không cho NULL) → lỗi `AssertionError` chứ không phải `IntegrityError` → 500 thay vì
  thông báo thân thiện.

### 3.3 Lập phiếu nhập – luật 150/300 đọc động từ bảng `quy_dinh`

```python
so_luong_toi_thieu = QuyDinh.lay_gia_tri("nhap_toi_thieu") or 0
nguong_ton = QuyDinh.lay_gia_tri("nguong_ton_de_nhap")
```
```python
def kiem_tra_cac_dong_nhap(danh_sach_id, danh_sach_sl, so_luong_toi_thieu, nguong_ton):
    for stt, (sach_id, so_luong) in enumerate(zip(danh_sach_id, danh_sach_sl), start=1):
        ...
        if so_luong < so_luong_toi_thieu:
            return f"Dòng {stt} ({sach.ten}): số lượng nhập phải từ {so_luong_toi_thieu} cuốn trở lên.", []
        if nguong_ton is not None and sach.so_luong_ton >= nguong_ton:
            return f"Dòng {stt} ({sach.ten}): tồn kho hiện tại là {sach.so_luong_ton} cuốn, chỉ được nhập khi tồn nhỏ hơn {nguong_ton}.", []
    return None, dong_hop_le      # ← trả None (không lỗi), không phải "" (chuỗi rỗng)
```

**Bài học rất quan trọng (bug đã gặp):** hàm kiểm tra trả `""` khi thành công, nhưng code lại kiểm tra
`if loi is None:`. `"" is None` là **False** → cả khối lưu bị bỏ qua, phiếu nhập không được ghi mà
không có báo lỗi nào. Sửa: **dùng `if not loi:`** (kiểm tra "rỗng" theo nghĩa đúng) và trả `None`
khi không có lỗi.

**Transaction khi lưu phiếu nhập:**
```python
phieu = PhieuNhap(ngay_nhap=ngay_nhap, nguoi_quan_ly_id=current_user.id)
db.session.add(phieu)
try:
    db.session.flush()                      # ghi thẳng vào DB để lấy phieu.id, chưa commit
    for sach, so_luong in dong_hop_le:
        db.session.add(ChiTietPhieuNhap(phieu_nhap_id=phieu.id, sach_id=sach.id, so_luong=so_luong))
        sach.so_luong_ton += so_luong        # cộng tồn kho
    db.session.commit()                      # ghi tất cả cùng lúc (hoặc không gì cả)
except IntegrityError:
    db.session.rollback()
```
- `flush()`: đẩy thay đổi xuống DB **để lấy khoá chính tự sinh** (`phieu.id`) mà chưa commit.
- Nếu một dòng sai → `rollback()` → **không** để lại phiếu nửa vời. Đây là tính chất ACID của transaction.

---

## Bài 4 – Phần A: trang quy định (`admin.py`)

```python
@bp.route("/quy-dinh", methods=["GET", "POST"])
@vai_tro_required("QUANTRI")
def quy_dinh():
    quy_dinh_list = QuyDinh.query.order_by(QuyDinh.ten).all()
    if request.method == "POST":
        for quy_dinh in quy_dinh_list:
            gia_tri = request.form.get(quy_dinh.ten, "").strip()
            if not gia_tri.isdigit():
                loi.append(f"Giá trị của «{quy_dinh.ten}» phải là số nguyên không âm.")
            else:
                gia_tri_moi[quy_dinh.ten] = int(gia_tri)
        if loi: ...
        else:
            for quy_dinh in quy_dinh_list:
                quy_dinh.gia_tri = gia_tri_moi[quy_dinh.ten]
            db.session.commit()
```
**Ý nghĩa cốt lõi của YC5:** số 150/300/48 **không viết cứng trong code** mà đọc từ bảng `quy_dinh`.
Người quản trị sửa ở đây → lần nhập sách sau tự động áp dụng giá trị mới (đã kiểm chứng: đổi 150 → 100
thì nhập 120 cuốn được chấp nhận ngay).

---

## Bài 5 – Phần B: khách đặt sách (`dat_sach.py` + `nghiem_vu.py`)

### 5.1 Giỏ hàng nằm trong session

```python
KHOA_GIO_HANG = "gio_hang"        # khách đặt online
KHOA_GIO_QUAY = "gio_hang_quay"   # nhân viên tại quầy
```
Giỏ hàng lưu trong **session** (cookie đã ký ở server): `{"<id_sách>": <số lượng>}`.
Hai khoá khác nhau vì khách và nhân viên dùng chung 1 máy (quầy) mà không lẫn giỏ của nhau.

### 5.2 Đặt sách – 2 hình thức thanh toán

```python
don, loi = tao_don_hang(kenh="ONLINE", khach_id=current_user.id,
                        ten_khach=current_user.ho_ten, nhan_vien_id=None,
                        hinh_thuc_tt=hinh_thuc, chi_tiet=chi_tiet)
```
Trong `nghiem_vu.py`:
```python
if kenh == "ONLINE":
    trang_thai = "CHO_LAY" if hinh_thuc_tt == "TRUC_TIEP" else "HOAN_TAT"
else:
    trang_thai = "HOAN_TAT"          # bán tại quầy: đã thanh toán ngay

gio_huy = QuyDinh.lay_gia_tri("gio_huy_don") or 0
han_lay_sach = None
if trang_thai == "CHO_LAY":
    han_lay_sach = datetime.now() + timedelta(hours=gio_huy)
...
for sach, so_luong in chi_tiet:
    db.session.add(ChiTietDonHang(don_hang_id=don.id, sach_id=sach.id,
                                   so_luong=so_luong, don_gia=sach.don_gia))  # CHỐT giá
    sach.so_luong_ton -= so_luong      # TRỪ tồn ngay khi đặt
db.session.commit()
```

| | Trực tiếp tại nhà sách (`TRUC_TIEP`) | Thanh toán online (`ONLINE`) |
|---|---|---|
| `trang_thai` | `CHO_LAY` | `HOAN_TAT` |
| `han_lay_sach` | `ngay_tao + gio_huy_don` giờ | `NULL` |
| Tự huỷ quá hạn | ✅ có | ❌ không bao giờ |
| Giao hàng | Khách đến lấy | Miễn phí |

Ràng buộc CHECK trong CSDL cũng bảo vệ: `CHECK (hinh_thuc_tt = 'TRUC_TIEP' OR han_lay_sach IS NULL)`.

### 5.3 Tự huỷ đơn quá hạn – không cần bộ lập lịch

```python
def huy_don_qua_han():
    gio_huy = QuyDinh.lay_gia_tri("gio_huy_don")
    han = datetime.now() - timedelta(hours=gio_huy)
    don_hangs = DonHang.query.filter(
        DonHang.trang_thai == "CHO_LAY",
        DonHang.han_lay_sach.isnot(None),
        DonHang.han_lay_sach < han).all()
    for don in don_hangs:
        for ct in don.chi_tiet:
            sach = db.session.get(Sach, ct.sach_id)
            if sach: sach.so_luong_ton += ct.so_luong      # TRẢ LẠI tồn kho
        don.trang_thai = "DA_HUY"
    db.session.commit()
```
Được gọi **mỗi khi** mở trang "Đơn của tôi" hoặc "Đơn chờ lấy sách". Cách này đơn giản, không cần
task scheduler/cron, và vẫn đúng về mặt nghiệp vụ (đơn quá hạn bị huỷ ngay khi ai đó mở trang liên quan).

### 5.4 Bảo mật dữ liệu của khách
```python
don = db.session.get(DonHang, don_hang_id)
if don is None or don.khach_id != current_user.id:
    return redirect(url_for("dat_sach.don_hang_cua_toi"))
```
Khách này không được xem/huỷ đơn của khách khác (đã kiểm thử: trả về 302).

---

## Bài 6 – Phần B: bán tại quầy (`ban_hang.py`)

### 6.1 Quét mã vạch
```python
if ma_vach:
    sach = Sach.query.filter(Sach.ma_vach == ma_vach).first()
    if sach is None:
        return f"Không tìm thấy sách có mã vạch {ma_vach}."
```
Máy quét mã vạch hoạt động như bàn phím: quét là gõ chuỗi mã + Enter → nằm trong ô `ma_vach` →
form POST. Nên ô nhập mã vạch phải có `autofocus` để không phải click chuột.

### 6.2 Lập hoá đơn tại quầy
```python
don, loi = tao_don_hang(kenh="QUAY", khach_id=None,          # khách vãng lai
                        ten_khach=ten_khach,
                        nhan_vien_id=current_user.id,         # nhân viên thanh toán
                        hinh_thuc_tt="TRUC_TIEP", chi_tiet=chi_tiet)
```
- `khach_id=None` vì khách mua tại quầy có thể không có tài khoản → CSDL cho phép NULL.
- `nhan_vien_id` = người đang bán (đề yêu cầu "nhân viên thanh toán" trên hoá đơn).
- `trang_thai='HOAN_TAT'` ngay vì đã thu tiền tại quầy.

### 6.3 UC04 – xác nhận khách lấy sách và thu tiền
```python
@bp.route("/don-cho-lay/<int:don_hang_id>/xac-nhan", methods=["POST"])
@vai_tro_required("NHANVIEN")
def xac_nhan_lay_sach(don_hang_id):
    huy_don_qua_han()                       # kiểm tra lần cuối còn trong hạn không
    don = db.session.get(DonHang, don_hang_id)
    if don is None or don.trang_thai != "CHO_LAY":
        flash("Đơn hàng không còn ở trạng thái chờ lấy sách.", "danger")
        return redirect(url_for("ban_hang.don_cho_lay"))
    don.nhan_vien_id = current_user.id
    don.trang_thai = "HOAN_TAT"
    db.session.commit()
```
Tồn kho **không** thay đổi ở bước này (đã trừ lúc đặt hàng) – chỉ đổi trạng thái đơn.

---

## Bài 7 – Giao diện (Jinja2 templates)

### 7.1 Kế thừa template
```html
<!-- templates/kho/sach_danh_sach.html -->
{% extends "base.html" %}
{% block title %}Quản lý sách{% endblock %}
{% block content %}
  ... nội dung trang ...
{% endblock %}
```
`base.html` giữ khung chung (nav, hiện flash). Mỗi trang chỉ viết phần `content`.

### 7.2 Menu theo vai trò – tách file riêng
```html
<!-- templates/_menu.html -->
{% if current_user.is_authenticated %}
  {% if current_user.vai_tro == 'KHACH' %}
    <a class="nav-link" href="{{ url_for('dat_sach.gio_hang') }}">Giỏ hàng</a>
  {% elif current_user.vai_tro == 'NHANVIEN' %}
    <a class="nav-link" href="{{ url_for('ban_hang.ban_tai_quay') }}">Bán tại quầy</a>
  ...
{% endif %}
```
`base.html` chỉ có 1 dòng `{% include "_menu.html" %}` → hai bạn cùng sửa menu mà **không xung đột git**
(bạn sửa `_menu.html`, tôi sửa file khác).

### 7.3 Thông báo flash
```html
{% with messages = get_flashed_messages(with_categories=true) %}
  {% for loai, noi_dung in messages %}
    <div class="alert alert-{{ loai }}">{{ noi_dung }}</div>
  {% endfor %}
{% endwith %}
```
Trong code: `flash("Đã lập phiếu nhập #12.", "success")` → hiện alert xanh; `"danger"` → alert đỏ.

### 7.4 Bảng 3 cột cho báo cáo (mục 2.5)
Mỗi màn hình trong `docs/thiet_ke_xu_ly_A.md` / `thiet_ke_xu_ly_B.md` có bảng:
**Sự kiện | Xử lý | Dữ liệu đọc/ghi** – đó chính là cách giải thích code của bạn cho thầy đọc.

---

## Bài 8 – Kiểm thử tự động (2 script)

- `kiem_thu_tuan2.py` – phần A: đăng nhập 4 vai trò, chặn sai vai trò, CRUD sách, luật 150/300,
  đổi quy định 150 → 100 xem luật áp dụng ngay.
- `kiem_thu_khach_ban_hang.py` – phần B: đăng ký khách, giỏ hàng, đặt sách 2 hình thức, hạn 48 giờ,
  tự huỷ quá hạn (tồn được trả lại), bán tại quầy bằng mã vạch, xác nhận lấy sách, khách khác không
  xem được đơn người khác.

**Nguyên tắc quan trọng của script kiểm thử:**
1. **Chụp ảnh dữ liệu trước** khi thử (`chup_cSDL()`).
2. **Phục hồi sau** khi thử (`phuc_hoi_cSDL()`) → CSDL về đúng trạng thái `5/3/5/20/0/0/0/0`.
3. **Bỏ qua phục hồi nếu ảnh chụp rỗng** – nếu không sẽ xoá nhầm dữ liệu mẫu (đã xảy ra 1 lần,
   khôi phục bằng cách chạy lại `schema.sql`).

---

## Bài 9 – Những lỗi đã gặp (bài học để không làm lại)

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| `View function mapping is overwriting an existing endpoint` | Decorator trả nhầm biến (`return boc_trong` thay vì `return kiem_tra`) | Trả đúng hàm bọc |
| Phiếu nhập không được lưu, không báo lỗi | `if loi is None` nhưng hàm kiểm tra trả `""` | Dùng `if not loi`, trả `None` khi không lỗi |
| Xoá sách có giao dịch → lỗi 500 | ORM cố xoá trắng khoá ngoại (`AssertionError`) | Kiểm tra giao dịch trước + bulk delete |
| `AttributeError: ... has no attribute 'hanh_lay_sach'` | Gõ sai tên cột | Đúng là `han_lay_sach` |
| 405 Method Not Allowed khi bấm nút | Route thiếu `methods=["POST"]` | Thêm vào `@bp.route` |
| Đăng ký lỗi `no attribute 'email'` | Bảng `nguoi_dung` **không có cột email** | Không hỏi email; muốn thêm phải sửa cả `schema.sql` + `models.py` |
| Lỗi `PendingRollbackError` | Bắt `IntegrityError` mà không `rollback()` | Luôn `db.session.rollback()` trong except |
| Mất dữ liệu mẫu khi chạy script test | Phục hồi chạy cả khi ảnh chụp rỗng | Chụp trước, bỏ qua phục hồi khi rỗng |
| Console PowerShell lỗi tiếng Việt | Console dùng cp1252 | Ghi file UTF-8 rồi đọc, hoặc `PYTHONIOENCODING=utf-8` |

---

## Bài 10 – Câu hỏi tự kiểm tra (để ôn thi)

1. Vì sao `extensions.py` tạo `db` riêng thay vì `db = SQLAlchemy(app)` trong `models.py`?
2. `@login.user_loader` dùng để làm gì? Nếu xoá hàm đó thì chuyện gì xảy ra?
3. `login_user()` lưu gì vào session? Vì sao không lưu cả đối tượng `NguoiDung`?
4. Vì sao phải gọi `db.session.rollback()` trong khối `except IntegrityError`?
5. `flush()` khác `commit()` thế nào? Vì sao phiếu nhập dùng `flush()`?
6. Vì sao luật 150/300/48 phải đọc từ bảng `quy_dinh` chứ không viết cứng?
7. Vì sao xoá sách dùng `db.session.execute(db.delete(...))`?
8. Vì sao đơn thanh toán online không bao giờ bị tự huỷ?
9. `don_gia` lưu trong `chi_tiet_don_hang` (không lấy lại từ `sach`) giúp ích gì?
10. Vì sao `huy_don_qua_han()` không cần chạy bằng cron mà vẫn đúng?
11. `next` trong URL đăng nhập dùng để làm gì? Cần kiểm tra gì để tránh open redirect?
12. Vì sao tách `_menu.html` riêng?
