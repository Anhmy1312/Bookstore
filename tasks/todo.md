# Task list – Tuần 2 phần A (27/10 – 2/11/2026)

Nguồn kế hoạch: `tasks/plan.md`. Chi tiết: `PROJECT_CONTEXT.md` (mục 3, 4, 13, 14, 15).

## Phase 0 – Nền dùng chung
- [ ] T0. Commit tuần 1 lên git (repo `main` chưa có commit nào)
- [ ] T1. `bookstore/quyen.py` – decorator `vai_tro_required`
- [ ] T2. `bookstore/blueprints/auth.py` – `/dang-nhap`, `/dang-xuat` (nền tối giản) + `templates/dang_nhap.html`
- [ ] T3. `bookstore/templates/base.html` – menu theo vai trò, tên người dùng, nút đăng xuất
- [ ] ✅ Checkpoint 0: 5 vai trò đăng nhập được, chặn đúng vai trò, `/kiem-tra-db` đúng

## Phase 1 – `kho.py` quản lý sách (YC5)
- [ ] T4. `/kho/sach` – danh sách, tìm kiếm, thêm, sửa, xoá (bắt lỗi 1451/1062) + 2 template
- [ ] ✅ Checkpoint 1: CRUD chạy đúng trên MySQL thật; xoá sách đã có giao dịch bị chặn

## Phase 2 – `kho.py` lập phiếu nhập (YC1)
- [ ] T5. `/kho/phieu-nhap` – form nhiều dòng, luật 150/300 đọc từ `quy_dinh`, transaction + cộng tồn + template
- [ ] ✅ Checkpoint 2: nhập 100 bị từ chối; tồn ≥ 300 bị từ chối; nhập hợp lệ thì tồn tăng đúng

## Phase 3 – `admin.py` quy định (YC5)
- [ ] T6. `/admin/quy-dinh` – sửa `nhap_toi_thieu`, `nguong_ton_de_nhap`, `gio_huy_don` + template
- [ ] ✅ Checkpoint 3: đổi 150 → 100 thì áp dụng ngay cho lần nhập sau

## Phase 4 – Hồ sơ báo cáo của A
- [ ] T7. Sequence + activity diagram UC05, UC07 → `docs/nguon_ve/` (Mermaid)
- [ ] T8. Mockup + bảng thiết kế xử lý (sự kiện | xử lý | dữ liệu đọc/ghi) → `docs/thiet_ke_xu_ly_A.md`
- [ ] ✅ Checkpoint 4: khớp với code đã chạy, tên bảng/cột trùng `schema.sql`

## Sau mỗi phase
- [ ] Dọn dữ liệu thử trong `nha_sach` (giữ nguyên 5/3/5/20)
- [ ] Cập nhật `PROJECT_CONTEXT.md` (mục trạng thái) + commit git
