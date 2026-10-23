# Thiết kế giao diện & thiết kế xử lý – Phần A (kho + quản trị)

Dùng cho **Chương 2 – mục 2.5** của báo cáo: mỗi màn hình có ảnh mockup (vẽ bằng
[mockflow.com](https://mockflow.com), **không** chụp màn hình web thật) và bảng 3 cột
*sự kiện | xử lý | dữ liệu đọc/ghi*.

Tên bảng/cột trong bảng này phải khớp với `schema.sql`, `models.py` và code.

---

## Màn 1 – Đăng nhập (`/dang-nhap`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang | Hiện form tên đăng nhập + mật khẩu, gợi ý tài khoản mẫu | Đọc: không |
| Bấm "Đăng nhập" | `auth.dang_nhap()`: tìm người dùng theo `ten_dang_nhap`, kiểm tra mật khẩu bằng `NguoiDung.kiem_tra_mat_khau()` (so sánh với `mat_khau_hash`) | Đọc: `nguoi_dung` (theo `ten_dang_nhap`) |
| Sai tên/mật khẩu | Hiện thông báo "Tên đăng nhập hoặc mật khẩu không đúng.", không ghi vào CSDL | Đọc: `nguoi_dung` |
| Đúng | `login_user()`, lưu phiên vào cookie đã ký, chuyển về trang định vào trước đó (`next`) hoặc trang chủ | Ghi: session (không ghi CSDL) |
| Bấm "Đăng xuất" | `logout_user()`, xoá phiên, về trang chủ | Xoá: session |

## Màn 2 – Danh sách sách / Quản lý sách (`/kho/sach`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang | `kho.danh_sach_sach()`: lấy toàn bộ sách, cho phép lọc theo tên/mã vạch/tác giả và theo thể loại | Đọc: `sach`, `the_loai` |
| Gõ từ khoá, chọn thể loại, bấm "Tìm kiếm" | Lọc bằng `ilike` (tên, mã vạch, tác giả) và theo `the_loai_id` | Đọc: `sach`, `the_loai` |
| Bấm "+ Thêm sách" | Mở form nhập tên, mã vạch, tác giả, thể loại, đơn giá, số lượng tồn | Đọc: `the_loai` |
| Bấm "Thêm sách" | Kiểm tra dữ liệu rồi `db.session.add(Sach(...))` + `commit()`; nếu trùng `ma_vach` bắt `IntegrityError` và báo "Mã vạch đã tồn tại" | Ghi: `sach` |
| Bấm "Sửa" | Mở form đã điền sẵn; **không cho sửa số lượng tồn** (tồn chỉ đổi qua phiếu nhập/bán hàng) | Đọc: `sach`, `the_loai` |
| Bấm "Lưu thay đổi" | Cập nhật các cột, `commit()`; trùng mã vạch thì báo lỗi | Ghi: `sach` |
| Bấm "Xoá" (có xác nhận) | Kiểm tra sách đã có giao dịch chưa: nếu có `chi_tiet_phieu_nhap`/`chi_tiet_don_hang` thì báo "Sách đã có giao dịch, không thể xoá"; nếu không thì xoá | Ghi/Xoá: `sach` |

## Màn 3 – Lập phiếu nhập sách (`/kho/phieu-nhap`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang | Đọc `quy_dinh` để hiện quy định đang áp dụng; tải danh sách sách để chọn | Đọc: `quy_dinh`, `sach` |
| Chọn ngày nhập, chọn sách + số lượng từng dòng, bấm "Lưu phiếu nhập" | `kho.phieu_nhap()` kiểm tra **từng dòng**: số lượng ≥ `nhap_toi_thieu`; tồn hiện tại < `nguong_ton_de_nhap`; sách không lặp trong cùng phiếu | Đọc: `quy_dinh`, `sach` |
| Có dòng vi phạm | Báo đúng dòng và lý do, **không lưu gì** | Không ghi |
| Tất cả dòng hợp lệ | Tạo `phieu_nhap`, tạo `chi_tiet_phieu_nhap` cho từng dòng và cộng `sach.so_luong_ton`, `commit()` trong một transaction | Ghi: `phieu_nhap`, `chi_tiet_phieu_nhap`, cập nhật `sach` |

## Màn 4 – Quy định hệ thống (`/admin/quy-dinh`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang (người quản trị) | Hiện 3 quy định kèm mô tả: `nhap_toi_thieu`, `nguong_ton_de_nhap`, `gio_huy_don` | Đọc: `quy_dinh` |
| Sửa giá trị rồi bấm "Lưu quy định" | Kiểm tra là số nguyên không âm, cập nhật và `commit()` | Ghi: `quy_dinh` |
| Giá trị sai (không phải số / âm) | Báo lỗi, không lưu | Không ghi |
| Sau khi sửa | Mọi chức năng khác đọc giá trị mới ngay vì đọc từ bảng `quy_dinh` (không viết cứng trong code) | Đọc: `quy_dinh` |

## Màn 5 – Trang tổng quan báo cáo (`/admin/bao-cao`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang (người quản trị) | `admin.thong_ke()`: mặc định tháng hiện tại; đếm tổng đơn `HOAN_TAT`, tổng số lượng bán, tổng doanh thu (`don_gia × so_luong`) trong tháng | Đọc: `don_hang`, `chi_tiet_don_hang` |
| Chọn tháng khác, bấm "Xem thống kê" | Nhận tham số `thang=YYYY-MM` qua query string, tính lại 3 con số tổng quan | Đọc: `don_hang`, `chi_tiet_don_hang` |
| Bấm "Báo cáo doanh thu theo thể loại" | Chuyển sang `/admin/bao-cao/doanh-thu-the-loai?thang=...` | Không ghi |
| Bấm "Báo cáo tần suất bán sách" | Chuyển sang `/admin/bao-cao/tan-suat-sach?thang=...` | Không ghi |
| Người không phải QUANTRI mở trang | Decorator `@vai_tro_required("QUANTRI")` chặn, chuyển về `/` | Không đọc |

## Màn 6 – Báo cáo doanh thu theo thể loại (`/admin/bao-cao/doanh-thu-the-loai`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang | `admin.thong_ke_doanh_thu_the_loai()`: JOIN 4 bảng `chi_tiet_don_hang → don_hang → sach → the_loai`, lọc `trang_thai='HOAN_TAT'` + tháng của `ngay_tao`, GROUP BY thể loại | Đọc: `chi_tiet_don_hang`, `don_hang`, `sach`, `the_loai` |
| Hiển thị bảng | Mỗi dòng: thể loại, số đơn (`COUNT DISTINCT don_hang.id`), số lượng bán (`SUM so_luong`), doanh thu (`SUM so_luong × don_gia`), tỷ lệ % (doanh_thu thể loại / tổng doanh thu × 100) | Không ghi |
| Hiển thị biểu đồ | Chart.js vẽ biểu đồ cột từ `chart_labels` (tên thể loại) và `chart_values` (doanh thu), đã tính sẵn trong Python rồi truyền template (tránh lỗi `map` generator trong Jinja2) | Không ghi |
| Tháng không có đơn HOAN_TAT | Hiện thông báo "Không có dữ liệu doanh thu trong tháng ..." | Không ghi |

## Màn 7 – Báo cáo tần suất bán sách (`/admin/bao-cao/tan-suat-sach`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang | `admin.thong_ke_tan_suat_sach()`: JOIN 4 bảng, lọc `HOAN_TAT` + tháng, GROUP BY sách, ORDER BY số lượng bán giảm dần | Đọc: `chi_tiet_don_hang`, `don_hang`, `sach`, `the_loai` |
| Hiển thị bảng | Mỗi dòng: tên sách, thể loại, số lượng bán, tỷ lệ % (so_luong_ban / tổng số lượng × 100) | Không ghi |
| Hiển thị biểu đồ | Chart.js biểu đồ cột top sách bán chạy, dữ liệu truyền từ Python qua `chart_labels`/`chart_values` | Không ghi |
| Tháng không có đơn HOAN_TAT | Hiện thông báo "Không có dữ liệu bán sách trong tháng ..." | Không ghi |

---

## Quy tắc chung của báo cáo (YC4) — ghi nhớ khi sửa code

1. Chỉ tính đơn `don_hang.trang_thai = 'HOAN_TAT'` (không tính `CHO_LAY`, `DA_HUY`).
2. Doanh thu = `SUM(chi_tiet_don_hang.so_luong × chi_tiet_don_hang.don_gia)` — dùng `don_gia` đã chốt lúc bán, **không** lấy lại `sach.don_gia` (giá có thể đã đổi sau đó).
3. Lọc theo tháng của `don_hang.ngay_tao` bằng `extract("year"/"month", ...)`.
4. Số `Decimal` do MySQL trả về phải `float(...)` trước khi chia tính tỷ lệ (lỗi đã gặp: `Decimal / float` gây `TypeError`).

---

## Gợi ý vẽ mockup bằng Mockflow (đề yêu cầu, không chụp màn hình web thật)

Các màn hình cần vẽ (khoảng 10 màn cho cả nhóm, A vẽ 4 màn trên):

1. Đăng nhập – ô tên đăng nhập, mật khẩu, nút "Đăng nhập"
2. Danh sách sách – ô tìm kiếm, lọc thể loại, bảng sách, nút "Thêm sách"
3. Thêm / Sửa sách – form trường: tên, mã vạch, tác giả, thể loại, đơn giá, tồn kho
4. Lập phiếu nhập – ngày nhập + bảng các dòng (STT, sách, số lượng) + nút "Lưu phiếu nhập"
5. Quy định – 3 ô nhập số + nút "Lưu quy định"
6. (B vẽ) Danh sách sách cho khách + giỏ hàng
7. (B vẽ) Đặt sách – chọn hình thức thanh toán
8. (B vẽ) Bán tại quầy – quét mã vạch, giỏ hàng quầy
9. (B vẽ) Hoá đơn quầy
10. (A vẽ, tuần 3) Báo cáo doanh thu theo thể loại + biểu đồ

Sau khi vẽ xong, đặt tên file theo số thứ tự hình trong báo cáo (Hình 2.1, 2.2, ...) và
chèn kèm bảng 3 cột tương ứng ở trên.
