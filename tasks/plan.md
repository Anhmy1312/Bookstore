# Kế hoạch tuần 3 – Phần A (kho + quản trị) — Đề tài 3 Quản lý nhà sách

Thời gian: 3/11 – 9/11/2026. Nhóm: **A = kho + quản trị** (`kho.py`, `admin.py`; UC05, UC07).
Người thực hiện phiên này: **A**. B lo `auth.py`, `dat_sach.py`, `ban_hang.py` (UC02, UC03) — **đã hoàn thành tuần 2**.

## 1. Mục tiêu tuần 3 (giữ nguyên theo kế hoạch trong `AnhMy.docx`)
- **YC4 Thống kê báo cáo**: A làm 2 báo cáo theo tháng (bảng + Chart.js).
- **Quy tắc vàng**: Chỉ tính đơn `trang_thai = 'HOAN_TAT'`, theo tháng của `ngay_tao`, dùng `don_gia` đã chốt trong `chi_tiet_don_hang` (không lấy từ bảng `sach`).
- Báo cáo 1: Doanh thu theo tháng cho từng thể loại (thể loại, doanh thu, số lượt bán, tỷ lệ, tổng doanh thu).
- Báo cáo 2: Tần suất bán sách theo tháng (tên sách, thể loại, số lượng, tỷ lệ).
- **Không thêm tính năng mới ngoài báo cáo** (quy tắc tuần 4: không thêm tính năng mới).

## 2. Quyết định kiến trúc
| Vấn đề | Quyết định | Lý do |
|---|---|---|
| Trang báo cáo | 3 route trong `admin.py`: `/admin/bao-cao` (trang chủ chọn tháng), `/admin/bao-cao/doanh-thu-the-loai`, `/admin/bao-cao/tan-suat-sach` | Gọn gọn, dễ điều hướng |
| Thư viện biểu đồ | **Chart.js** qua CDN (`https://cdn.jsdelivr.net/npm/chart.js`) | Không cần pip install, nhẹ, phổ biến |
| Menu | Thêm mục "Báo cáo" vào `templates/_menu.html` cho `QUANTRI` | `_menu.html` đã tách riêng, không đụng file của B |
| Truy vấn báo cáo | Dùng SQLAlchemy ORM (`join`, `func.sum`, `func.count`, `extract`) | Khớp với stack hiện tại, không viết SQL thuần |
| Dữ liệu thử | Script kiểm thử tự tạo dữ liệu đơn `HOAN_TAT` trong nhiều tháng khác nhau, sau đó restore | Đảm bảo báo cáo có dữ liệu để xem biểu đồ |

## 3. Danh sách việc (mỗi việc là 1 lát nhỏ, kiểm chứng được)

### Phase 1 — Route báo cáo & truy vấn SQLAlchemy
- [ ] **T1. Route `/admin/bao-cao`**: trang chủ báo cáo, chọn tháng, hiển thị tổng quan (tổng doanh thu, tổng đơn, tổng sách bán).
- [ ] **T2. Route `/admin/bao-cao/doanh-thu-the-loai`**: truy vấn doanh thu theo thể loại trong tháng (chỉ đơn `HOAN_TAT`), trả về danh sách cho template.
- [ ] **T3. Route `/admin/bao-cao/tan-suat-sach`**: truy vấn tần suất bán sách theo tháng (chỉ đơn `HOAN_TAT`), trả về danh sách cho template.
- [ ] ✅ **Checkpoint 1**: 3 route trả về 200, dữ liệu hiển thị đúng trong template (chưa cần biểu đồ).

### Phase 2 — Template báo cáo + Chart.js
- [ ] **T4. Template `admin/bao_cao.html`**: form chọn tháng, nút vào 2 báo cáo chi tiết.
- [ ] **T5. Template `admin/bao_cao_doanh_thu_the_loai.html`**: bảng doanh thu theo thể loại + biểu đồ cột Chart.js.
- [ ] **T6. Template `admin/bao_cao_tan_suat_sach.html`**: bảng tần suất bán sách + biểu đồ cột Chart.js.
- [ ] ✅ **Checkpoint 2**: 3 trang báo cáo hiển thị đúng dữ liệu, biểu đồ Chart.js vẽ được.

### Phase 3 — Kiểm thử tự động
- [ ] **T7. Script `kiem_thu_bao_cao.py`**: tạo dữ liệu đơn `HOAN_TAT` trong nhiều tháng, kiểm tra các route báo cáo, tự phục hồi dữ liệu mẫu.
- [ ] **T8. Chạy lại `kiem_thu_tuan2.py` và `kiem_thu_khach_ban_hang.py`** để đảm bảo không làm hỏng phần cũ.
- [ ] ✅ **Checkpoint 3**: Tất cả test pass, CSDL về đúng 5/3/5/20/0/0/0/0 sau khi kiểm thử.

### Phase 4 — Hồ sơ báo cáo của A (tuần 3)
- [ ] **T9. Cập nhật `docs/thiet_ke_xu_ly_A.md`**: bổ sung bảng 3 cột cho 3 màn hình báo cáo.
- [ ] **T10. Cập nhật `PROJECT_CONTEXT.md`**: ghi lại trạng thái tuần 3.
- [ ] ✅ **Checkpoint 4**: báo cáo và code khớp nhau, tên bảng/cột trùng `schema.sql`.

## 4. Rủi ro
| Rủi ro | Mức | Xử lý |
|---|---|---|
| Chart.js CDN không load (máy không có internet) | Trung bình | Thử load local nếu có, hoặc vẽ bảng đơn giản thay biểu đồ |
| Truy vấn JOIN nhiều bảng chậm | Thấp | Dữ liệu nhỏ (20 sách, ít đơn) không cần tối ưu |
| Tháng không có đơn nào | Thấp | Hiển thị thông báo "Không có dữ liệu trong tháng này" |
| Làm hỏng code của B (auth.py, dat_sach.py, ban_hang.py) | Cao | Chỉ sửa file của A (admin.py, templates/admin/, _menu.html) |

## 5. Câu hỏi còn mở
- B cần thêm chức năng vào `auth.py` (đăng ký nhân viên/quản lý) không? Nếu có, cần đồng bộ trước tuần 3.
