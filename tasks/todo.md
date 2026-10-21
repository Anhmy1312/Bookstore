# Task list – Tuần 2 phần A (27/10 – 2/11/2026)

Nguồn kế hoạch: `tasks/plan.md`. Chi tiết: `PROJECT_CONTEXT.md` (mục 3, 4, 13, 14, 15).

## Phase 0 – Nền dùng chung
- [x] T0. Commit tuần 1 lên git – repo thật là `bookstore/` (remote `Anhmy1312/Bookstore`); `docs/` + `tasks/` đã chuyển vào repo để backup chung
- [x] T1. `bookstore/quyen.py` – decorator `vai_tro_required` (file MỚI, không đụng file của B)
- [x] T2. `bookstore/blueprints/auth.py` – `/dang-nhap`, `/dang-xuat` (nền tối giản, B mở rộng được) + `templates/dang_nhap.html`
- [x] T3. `bookstore/templates/base.html` – menu theo vai trò, tên người dùng, nút đăng xuất, hiện flash
- [x] ✅ Checkpoint 0: 5 vai trò đăng nhập được, chặn đúng vai trò, `/kiem-tra-db` đúng

## Phase 1 – `kho.py` quản lý sách (YC5)
- [x] T4. `/kho/sach` – danh sách, tìm kiếm, thêm, sửa, xoá (bắt lỗi 1451/1062) + 2 template
- [x] ✅ Checkpoint 1: CRUD chạy đúng trên MySQL thật; xoá sách đã có giao dịch bị chặn đúng thông báo

## Phase 2 – `kho.py` lập phiếu nhập (YC1)
- [x] T5. `/kho/phieu-nhap` – form nhiều dòng, luật 150/300 đọc từ `quy_dinh`, transaction + cộng tồn + template
- [x] ✅ Checkpoint 2: nhập 100 bị từ chối; tồn ≥ 300 bị từ chối; nhập hợp lệ thì tồn tăng đúng (150 → 300)

## Phase 3 – `admin.py` quy định (YC5)
- [x] T6. `/admin/quy-dinh` – sửa `nhap_toi_thieu`, `nguong_ton_de_nhap`, `gio_huy_don` + template
- [x] ✅ Checkpoint 3: 120 cuốn bị từ chối khi quy định = 150, được nhận khi đổi quy định = 100 (tồn 280 → 400) → luật đọc động

## Phase 4 – Hồ sơ báo cáo của A
- [x] T7. Sequence + activity diagram UC05, UC07 → `docs/nguon_ve/*.md` (Mermaid, dán vào mermaid.live để xuất ảnh)
- [x] T8. Bảng thiết kế xử lý (sự kiện | xử lý | dữ liệu đọc/ghi) cho 4 màn hình của A + gợi ý mockup → `docs/thiet_ke_xu_ly_A.md`
- [x] ✅ Checkpoint 4: khớp với code đã chạy, tên bảng/cột trùng `schema.sql`

## Sau mỗi phase
- [x] Dọn dữ liệu thử trong `nha_sach` (đã về đúng 5/3/5/20/0/0/0/0)
- [x] Cập nhật `PROJECT_CONTEXT.md` + commit git

## Lỗi đã gặp và cách sửa (đừng làm lại)
- Decorator trả nhầm biến (`return boc_trong` thay vì `return kiem_tra`) → Flask báo trùng endpoint.
- Dùng `if loi is None` trong khi hàm kiểm tra trả `""` → nhánh lưu bị bỏ qua, phiếu nhập không được ghi. Dùng `if not loi`.
- `db.session.delete(sach)` với sách đã có giao dịch → SQLAlchemy cố xoá trắng khoá ngoại (AssertionError). Dùng kiểm tra trước + `db.session.execute(db.delete(Sach).where(...))`.
- Xoá sách trong script kiểm thử làm mất dữ liệu mẫu → chụp lại bảng `sach` trước khi thử và phục hồi sau (xem `kiem_thu_tuan2.py`).

## Việc còn lại của tuần 2 (nếu còn thời gian)
- [ ] Vẽ ảnh mockup bằng Mockflow cho 4 màn hình của A và 9 màn hình của B (đề yêu cầu, không chụp màn hình web)
- [ ] Tuần 3: 2 báo cáo + Chart.js (`/admin/bao-cao`), theo sơ đồ UC07 đã vẽ
- [ ] B rà lại `auth.py` (hiện là bản nền tối giản) nếu B muốn thêm chức năng đăng ký của nhân viên/quản lý

---

# PHẦN B – khách hàng + nhân viên bán hàng (đã code xong 21/10/2026)

## Phase B0 – Nền dùng chung
- [x] B0. `bookstore/nghiem_vu.py` (MỚI): `tao_don_hang()` (tạo đơn + chi tiết + trừ tồn), `huy_don_qua_han()` (tự huỷ đơn `CHO_LAY` quá hạn + trả lại tồn), các hàm giỏ hàng session (`KHOA_GIO_HANG`, `KHOA_GIO_QUAY`)
- [x] B1. `blueprints/auth.py` mở rộng: `/dang-ky` (khách tự đăng ký, vai trò KHACH, băm `pbkdf2:sha256`), `/tai-khoan` (xem thông tin + đổi mật khẩu)
- [x] B2. `templates/_menu.html` (MỚI) – tách menu khỏi `base.html` để hai bạn cùng sửa không conflict; thêm mục cho KHACH và NHANVIEN
- [x] ✅ Checkpoint B0: 20/20 trang theo 5 vai trò trả về 200, không có trang lỗi 500

## Phase B1 – `dat_sach.py` (khách đặt sách, YC2)
- [x] B3. `/dat-sach/` danh sách sách (tìm/lọc, chỉ sách còn hàng), `/dat-sach/gio-hang/them`
- [x] B4. `/dat-sach/gio-hang` (xem, `/cap-nhat`, `/xoa`), `/dat-sach/dat-hang` (2 hình thức thanh toán)
- [x] B5. `/dat-sach/don-hang` (đơn của tôi, tự huỷ quá hạn), `/dat-sach/don-hang/<id>`, `/dat-sach/don-hang/<id>/huy`
- [x] ✅ Checkpoint B1: đặt `TRUC_TIEP` → `CHO_LAY` + hạn 48h, tồn bị trừ; đặt `ONLINE` → `HOAN_TAT`, `han_lay_sach=NULL`; thêm vượt tồn bị từ chối; khách khác không xem đơn người khác

## Phase B2 – `ban_hang.py` (bán tại quầy, YC3 + UC04)
- [x] B6. `/ban-hang/` – quét mã vạch / chọn sách, giỏ quầy (session riêng), thanh toán lập hoá đơn `kenh=QUAY`, `khach_id=NULL`, `nhan_vien_id` có, `don_gia` chốt lúc bán
- [x] B7. `/ban-hang/hoa-don/<id>` (in hoá đơn), `/ban-hang/don-cho-lay` + `/don-cho-lay/<id>/xac-nhan` (UC04: CHO_LAY → HOAN_TAT)
- [x] ✅ Checkpoint B2: quét mã vạch tạo đúng hoá đơn; xác nhận lấy sách chuyển `HOAN_TAT`; đơn quá hạn tự huỷ và **tồn kho được cộng lại**

## Phase B3 – Hồ sơ báo cáo của B
- [x] B8. Sequence + activity UC02 (đặt sách), UC03 (bán tại quầy), UC04 (xác nhận lấy sách) → `docs/nguon_ve/`
- [x] B9. `docs/thiet_ke_xu_ly_B.md` – bảng 3 cột cho 9 màn hình của B + gợi ý mockup
- [x] ✅ Checkpoint B3: khớp code đã chạy, tên bảng/cột trùng `schema.sql`

## Kiểm thử
- [x] `kiem_thu_khach_ban_hang.py` – 11 nhóm kiểm thử, tự phục hồi dữ liệu mẫu
- [x] Chạy lại `kiem_thu_tuan2.py` (phần A) → vẫn PASS sau khi tách menu và đổi `auth.py`
- [x] Dữ liệu mẫu sau kiểm thử: 5/3/5/20/0/0/0/0, tồn kho đúng như ban đầu

## Lỗi đã gặp ở phần B (đừng làm lại)
1. Bảng `nguoi_dung` **không có cột `email`** (chỉ có `id, ten_dang_nhap, mat_khau_hash, ho_ten, vai_tro`) → không thêm trường email vào form đăng ký, và đừng sửa `schema.sql`/`models.py` một cách tùy tiện.
2. Gõ nhầm `hanh_lay_sach` thay vì `han_lay_sach` → `AttributeError`.
3. Route bán tại quầy phải khai báo `methods=["GET", "POST"]` nếu form gửi POST.
4. Script kiểm thử phải **chụp ảnh dữ liệu trước** và **bỏ qua phục hồi nếu ảnh chụp rỗng** — nếu không sẽ xoá nhầm dữ liệu mẫu (đã xảy ra 1 lần, khôi phục bằng cách chạy lại `schema.sql`).
