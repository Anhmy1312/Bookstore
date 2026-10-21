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
- [ ] Vẽ ảnh mockup bằng Mockflow cho 4 màn hình của A (đề yêu cầu, không chụp màn hình web)
- [ ] Chờ B xong `auth.py`/`dat_sach.py`/`ban_hang.py` rồi ghép: menu cần thêm mục "Đặt sách", "Bán tại quầy", "Đơn của tôi" theo vai trò KHACH/NHANVIEN
- [ ] Tuần 3: 2 báo cáo + Chart.js (`/admin/bao-cao`), theo sơ đồ UC07 đã vẽ
