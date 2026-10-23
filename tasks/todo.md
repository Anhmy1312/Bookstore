# Task list – Tuần 3 phần A (3/11 – 9/11/2026) – Báo cáo + Chart.js

Nguồn kế hoạch: `tasks/plan.md`. Chi tiết: `PROJECT_CONTEXT.md` (mục 3, 4, 13, 14, 15).

## Quy tắc vàng báo cáo (YC4)
- Chỉ tính đơn `trang_thai = 'HOAN_TAT'`
- Theo tháng của `ngay_tao`
- Dùng `don_gia` đã chốt trong `chi_tiet_don_hang` (không lấy từ bảng `sach`)

## Phase 1 – Route báo cáo & truy vấn SQLAlchemy
- [ ] T1. Route `/admin/bao-cao`: trang chủ báo cáo, chọn tháng, hiển thị tổng quan (tổng doanh thu, tổng đơn, tổng sách bán).
- [ ] T2. Route `/admin/bao-cao/doanh-thu-the-loai`: truy vấn doanh thu theo thể loại trong tháng (chỉ đơn `HOAN_TAT`).
- [ ] T3. Route `/admin/bao-cao/tan-suat-sach`: truy vấn tần suất bán sách theo tháng (chỉ đơn `HOAN_TAT`).
- [ ] ✅ Checkpoint 1: 3 route trả về 200, dữ liệu hiển thị đúng trong template.

## Phase 2 – Template báo cáo + Chart.js
- [ ] T4. Template `admin/bao_cao.html`: form chọn tháng, nút vào 2 báo cáo chi tiết.
- [ ] T5. Template `admin/bao_cao_doanh_thu_the_loai.html`: bảng doanh thu theo thể loại + biểu đồ cột Chart.js.
- [ ] T6. Template `admin/bao_cao_tan_suat_sach.html`: bảng tần suất bán sách + biểu đồ cột Chart.js.
- [ ] ✅ Checkpoint 2: 3 trang báo cáo hiển thị đúng dữ liệu, biểu đồ Chart.js vẽ được.

## Phase 3 – Kiểm thử tự động
- [ ] T7. Script `kiem_thu_bao_cao.py`: tạo dữ liệu đơn `HOAN_TAT` trong nhiều tháng, kiểm tra các route báo cáo, tự phục hồi dữ liệu mẫu.
- [ ] T8. Chạy lại `kiem_thu_tuan2.py` và `kiem_thu_khach_ban_hang.py` để đảm bảo không làm hỏng phần cũ.
- [ ] ✅ Checkpoint 3: Tất cả test pass, CSDL về đúng 5/3/5/20/0/0/0/0 sau khi kiểm thử.

## Phase 4 – Hồ sơ báo cáo của A (tuần 3)
- [ ] T9. Cập nhật `docs/thiet_ke_xu_ly_A.md`: bổ sung bảng 3 cột cho 3 màn hình báo cáo.
- [ ] T10. Cập nhật `PROJECT_CONTEXT.md`: ghi lại trạng thái tuần 3.
- [ ] ✅ Checkpoint 4: báo cáo và code khớp nhau, tên bảng/cột trùng `schema.sql`.

## Sau mỗi phase
- [ ] Dọn dữ liệu thử trong `nha_sach` (giữ nguyên 5/3/5/20/0/0/0/0)
- [ ] Cập nhật `PROJECT_CONTEXT.md` + commit git
