# Kế hoạch và phân công — A: Anh Mỹ

**Đề tài 3: Quản lý nhà sách** · Nhóm 2 người · Thời gian: 20/10 – 16/11/2026

| Mục | Nội dung |
|---|---|
| Người phụ trách | **Anh Mỹ** (A) — kho + quản trị |
| Người cùng nhóm | **Nam Lê** (B) — kế hoạch của B: `tasks/ke_hoach_B_NamLe.md` |
| Mảng code | `quyen.py`, `blueprints/kho.py`, `blueprints/admin.py`, `templates/kho/`, `templates/admin/` |
| Use case | UC08 Lập phiếu nhập · UC09 Quản trị sách · UC10–UC11 Thay đổi quy định · UC12–UC13 Thống kê |
| Phần báo cáo | Chương 1 (đặc tả use case) · Chương 2 (toàn bộ) · Chương 3 mục 3.2.2–3.2.4 và 3.2.8–3.2.10 |

## 1. Phân công theo mảng

| Mảng | A — Anh Mỹ | B — Nam Lê |
|---|---|---|
| Khung dự án, CSDL | `app.py`, `config.py`, `extensions.py`, `models.py`, `schema.sql` (8 bảng + dữ liệu mẫu + 5 tài khoản) | Rà đặc tả use case khớp tên bảng/cột; dựng MySQL trên máy B, chạy thử `schema.sql` |
| Đăng nhập, phân quyền | `quyen.py` — decorator 4 vai trò | `blueprints/auth.py`, template đăng nhập / đăng ký / tài khoản |
| Quản lý sách | `blueprints/kho.py` (danh sách, tìm, thêm, sửa, xoá), template `kho/sach_*` | Kiểm thử chéo, báo lỗi |
| Lập phiếu nhập | `blueprints/kho.py` (`/kho/phieu-nhap`), luật 150/300 đọc từ `quy_dinh` | Kiểm thử chéo, báo lỗi |
| Đặt sách online | Kiểm thử chéo luồng 48 giờ / thanh toán online | `blueprints/dat_sach.py`, `nghiem_vu.py`, template `dat_sach/` |
| Bán tại quầy, xác nhận lấy sách | Kiểm thử chéo | `blueprints/ban_hang.py`, template `ban_hang/` |
| Thay đổi quy định | `blueprints/admin.py` (`/admin/quy-dinh`), template `admin/quy_dinh.html` | Kiểm thử chéo |
| Báo cáo thống kê | 3 route `/admin/bao-cao*`, 3 template + Chart.js | Rà số liệu báo cáo |
| Sơ đồ | Sơ đồ lớp, lược đồ CSDL, use case tổng | Sơ đồ hoạt động + tuần tự cho UC02, UC05, xác nhận lấy sách |
| Báo cáo | Chương 1 (giới thiệu, yêu cầu, đặc tả), Chương 2, ghép Chương 3 | Chương 3 phần B (3.2.1, 3.2.5–3.2.7), rà chính tả và đánh số |

## 2. Kế hoạch 4 tuần

### Tuần 1 — 20/10 – 26/10: Khung dự án và cơ sở dữ liệu

| | Nội dung |
|---|---|
| **A** | Dựng khung Flask (`app.py`, `config.py`, `extensions.py`); viết `models.py` 8 lớp khớp `schema.sql`; viết `schema.sql` 8 bảng + dữ liệu mẫu + 5 tài khoản; trang chủ và `/kiem-tra-db`; vẽ use case tổng, sơ đồ lớp, lược đồ CSDL |
| **B** | Viết đặc tả 4 use case trọng tâm (đặt sách, bán sách, lập phiếu nhập, thống kê); đối chiếu tên bảng/cột với `schema.sql`; cài môi trường và chạy thử CSDL trên máy mình |
| **Mốc** | Cả hai chạy được `schema.sql`; `/kiem-tra-db` trả đúng `5 / 3 / 5 / 20` và các bảng giao dịch bằng 0 |

### Tuần 2 — 27/10 – 2/11: Nghiệp vụ chính

| | Nội dung |
|---|---|
| **A** | `quyen.py` phân quyền 4 vai trò; `blueprints/kho.py` — quản lý sách (thêm/sửa/xoá/tìm) và lập phiếu nhập theo luật 150/300; `blueprints/admin.py` — trang sửa quy định; template `kho/`, `admin/quy_dinh.html`; `kiem_thu_tuan2.py` |
| **B** | `blueprints/auth.py` — đăng nhập, đăng ký, tài khoản; `nghiem_vu.py` — tạo đơn, chốt `don_gia`, trừ tồn, tự huỷ đơn quá 48 giờ; `blueprints/dat_sach.py` — giỏ hàng, đặt 2 hình thức thanh toán, đơn của tôi; `blueprints/ban_hang.py` — bán tại quầy, hoá đơn, xác nhận khách lấy sách; template `dat_sach/`, `ban_hang/`; `kiem_thu_khach_ban_hang.py` |
| **Chung** | `templates/_menu.html` — mỗi người thêm mục menu theo vai trò của mình; thống nhất route trước khi code |
| **Mốc** | Quét đủ các trang theo 5 vai trò, không trang nào lỗi 500; A chạy bộ kiểm thử phần B và ngược lại |

### Tuần 3 — 3/11 – 9/11: Báo cáo thống kê và hoàn thiện

| | Nội dung |
|---|---|
| **A** | 3 route báo cáo (`/admin/bao-cao`, doanh thu theo thể loại, tần suất bán sách) + 3 template có Chart.js; `kiem_thu_bao_cao.py`; rà luật tính doanh thu |
| **B** | Hoàn thiện 3 sơ đồ tuần tự và 3 sơ đồ hoạt động của phần mình; rà giao diện khách hàng và bán hàng; kiểm tra số liệu 2 báo cáo |
| **Chung** | Chạy lại cả 3 bộ kiểm thử, đưa CSDL về dữ liệu mẫu; chốt danh sách lỗi và người sửa |
| **Mốc** | Báo cáo chỉ tính đơn `HOAN_TAT`, đúng tháng `ngay_tao`, dùng `don_gia` đã chốt; cả 3 bộ kiểm thử PASS |

### Tuần 4 — 10/11 – 16/11: Báo cáo và nộp bài

| | Nội dung |
|---|---|
| **A** | Viết Chương 1 (giới thiệu, phân tích yêu cầu, 13 use case, 4 bảng đặc tả); viết Chương 2 (sơ đồ lớp, hoạt động, tuần tự, lược đồ CSDL, thiết kế giao diện và xử lý); ghép Chương 3; lập bảng thuật ngữ; rà số liệu toàn báo cáo |
| **B** | Viết Chương 3 phần B: đăng nhập và phân quyền, đặt sách online, bán tại quầy, xác nhận lấy sách; rà chính tả, mục lục, đánh số hình và bảng; kiểm tra chéo Chương 1–2 |
| **Chung** | Chốt nội dung lần cuối, xuất PDF, đóng gói source (không gồm `venv`, `.env`), nộp bài |
| **Mốc** | Báo cáo đủ 3 chương, số hình và bảng khớp mục lục; source chạy được trên máy sạch theo `README.md` |

## 3. Sản phẩm bàn giao

| Thời điểm | A bàn giao | B bàn giao |
|---|---|---|
| Cuối tuần 1 | Khung Flask + `models.py` + `schema.sql` + 3 hình sơ đồ | 4 bảng đặc tả use case; xác nhận CSDL chạy được trên máy B |
| Cuối tuần 2 | `quyen.py`, `kho.py`, `admin.py`, template kho/quy định, kết quả `kiem_thu_tuan2.py` | `auth.py`, `nghiem_vu.py`, `dat_sach.py`, `ban_hang.py`, template, kết quả `kiem_thu_khach_ban_hang.py` |
| Cuối tuần 3 | 3 trang báo cáo + Chart.js, kết quả `kiem_thu_bao_cao.py` | 6 sơ đồ phần B, danh sách lỗi giao diện và số liệu |
| Cuối tuần 4 | Chương 1–2, bản ghép 3 chương, PDF | Chương 3 phần B, biên bản rà soát, xác nhận bản cuối |

## 4. Nguyên tắc phối hợp

1. **Mỗi người sở hữu file của mình** — không sửa `auth.py`, `dat_sach.py`, `ban_hang.py`, `nghiem_vu.py` và template của B; B không sửa `kho.py`, `admin.py`, template kho/quản trị.
2. **`schema.sql` là nguồn sự thật** — đổi cấu trúc bảng phải sửa cả `schema.sql` và `models.py`, báo người kia, rồi cả hai chạy lại `schema.sql`.
3. **Giữ nguyên** tên bảng, tên cột, vai trò `KHACH / NHANVIEN / QUANLY / QUANTRI`, trạng thái `CHO_LAY / HOAN_TAT / DA_HUY`.
4. **Ba số 150 / 300 / 48** luôn đọc từ bảng `quy_dinh`, không viết cứng trong code.
5. **Kiểm thử chéo**: ai làm phần nào thì người kia chạy thử phần đó trước khi chốt tuần.
6. **Chốt đầu tuần**: thứ Ba hàng tuần thống nhất việc của tuần và ai làm gì; cuối tuần đối chiếu mốc hoàn thành.

## 5. Trạng thái đến 17/11/2026

- Tuần 1–3 đã hoàn thành và đã đẩy lên GitHub (`Anhmy1312/Bookstore`).
- Tuần 4: báo cáo `bcDeTai3.docx` đã đủ 3 chương, 10 mục chức năng ở 3.2.
- Việc còn lại: rà soát lần cuối, xuất PDF, đóng gói source và nộp.