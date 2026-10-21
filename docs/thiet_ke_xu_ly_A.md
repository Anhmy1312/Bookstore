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
