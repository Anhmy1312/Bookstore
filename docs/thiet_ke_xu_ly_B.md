# Thiết kế giao diện & thiết kế xử lý – Phần B (khách hàng + nhân viên bán hàng)

Dùng cho **Chương 2 – mục 2.5** của báo cáo: mỗi màn hình có ảnh mockup (vẽ bằng
[mockflow.com](https://mockflow.com), **không** chụp màn hình web thật) và bảng 3 cột
*sự kiện | xử lý | dữ liệu đọc/ghi*.

Tên bảng/cột trong bảng này khớp với `schema.sql`, `models.py` và code.

---

## Màn 1 – Đăng ký tài khoản (`/dang-ky`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang | Hiện form: họ tên, tên đăng nhập, mật khẩu, xác nhận mật khẩu | Đọc: không |
| Bấm "Đăng ký" | `auth.dang_ky()`: kiểm tra đủ thông tin, 2 mật khẩu khớp, mật khẩu ≥ 6 ký tự; băm bằng `generate_password_hash(..., method="pbkdf2:sha256")`; tạo tài khoản với `vai_tro = 'KHACH'` | Ghi: `nguoi_dung` |
| Tên đăng nhập đã có | Bắt `IntegrityError` → báo "Tên đăng nhập đã tồn tại." | Không ghi |
| Thành công | Flash thông báo rồi chuyển tới trang đăng nhập | Ghi: `nguoi_dung` |

## Màn 2 – Đăng nhập / Đăng xuất / Tài khoản (`/dang-nhap`, `/dang-xuat`, `/tai-khoan`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Bấm "Đăng nhập" | Tìm người dùng theo `ten_dang_nhap`, kiểm tra `kiem_tra_mat_khau()` với `mat_khau_hash`; `login_user()` lưu phiên; chuyển về trang `next` hoặc trang chủ | Đọc: `nguoi_dung` |
| Sai thông tin | Báo "Tên đăng nhập hoặc mật khẩu không đúng." | Đọc: `nguoi_dung` |
| Bấm "Đăng xuất" | `logout_user()`, xoá phiên, về trang chủ | Xoá: session |
| Mở "Tài khoản" | Hiện tên đăng nhập, họ tên, vai trò | Đọc: `nguoi_dung` |
| Đổi mật khẩu | Kiểm tra mật khẩu cũ, mật khẩu mới ≥ 6 ký tự và khớp xác nhận; băm lại rồi cập nhật `mat_khau_hash` | Ghi: `nguoi_dung` |

## Màn 3 – Danh sách sách cho khách (`/dat-sach/`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang | `dat_sach.danh_sach_sach()`: chỉ lấy sách còn tồn, tìm theo tên/tác giả, lọc theo thể loại; hiện số lượng đã có trong giỏ | Đọc: `sach`, `the_loai` |
| Bấm "Thêm" | `them_vao_gio()`: kiểm tra số lượng ≤ tồn kho, cộng dồn vào giỏ trong session | Ghi: session (`gio_hang`) |
| Thêm vượt tồn | Báo "Sách ... hiện chỉ còn N cuốn, không thể đặt M cuốn." | Không ghi |

## Màn 4 – Giỏ hàng của khách (`/dat-sach/gio-hang`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang | Đọc giỏ trong session, ghép với `sach` để lấy tên/giá, tính tổng tiền | Đọc: `sach` |
| Sửa số lượng | `cap_nhat_gio()`: số lượng = 0 thì xoá khỏi giỏ; vượt tồn thì báo lỗi | Ghi: session |
| Bấm "Xoá" | Xoá sách khỏi giỏ trong session | Ghi: session |
| Bấm "Đặt sách" | Chuyển tới form chọn hình thức thanh toán | – |

## Màn 5 – Đặt sách, chọn hình thức thanh toán (`/dat-sach/dat-hang`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang | Hiện bảng các dòng trong giỏ + tổng tiền + 2 lựa chọn thanh toán | Đọc: `sach` |
| Bấm "Xác nhận đặt sách" | `nghiem_vu.tao_don_hang()`: kiểm tra tồn lần cuối, tạo `don_hang` (`kenh='ONLINE'`, `khach_id`, `ten_khach`, `nhan_vien_id=NULL`, `hinh_thuc_tt`, `trang_thai`, `ngay_tao`, `han_lay_sach`), tạo `chi_tiet_don_hang` với `don_gia` chốt lúc đặt, **trừ tồn**, rồi xoá giỏ | Ghi: `don_hang`, `chi_tiet_don_hang`, cập nhật `sach` |
| Chọn "Trực tiếp tại nhà sách" | `trang_thai='CHO_LAY'`, `han_lay_sach = ngay_tao + gio_huy_don` giờ (đọc từ `quy_dinh`) | Ghi: `don_hang` |
| Chọn "Thanh toán online" | `trang_thai='HOAN_TAT'`, `han_lay_sach=NULL` (đơn này không bao giờ tự huỷ) | Ghi: `don_hang` |
| Không đủ tồn | Báo "Sách ... hiện chỉ còn N cuốn, không đủ M cuốn để đặt." | Không ghi |

## Màn 6 – Đơn của tôi (`/dat-sach/don-hang`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang | Gọi `huy_don_qua_han()` trước (tự huỷ đơn `CHO_LAY` quá hạn và trả lại tồn), rồi lấy các đơn có `khach_id = <người đang đăng nhập>` | Đọc/ghi: `don_hang`, `sach` |
| Bấm "Xem" | Xem chi tiết đơn (từng dòng sách, số lượng, đơn giá chốt, tổng tiền) | Đọc: `don_hang`, `chi_tiet_don_hang` |
| Bấm "Huỷ" (chỉ hiện khi `CHO_LAY`) | Cộng lại `so_luong_ton` cho từng dòng, đặt `trang_thai='DA_HUY'` | Ghi: `don_hang`, `sach` |
| Khách khác mở đơn không của mình | Chuyển hướng về trang "Đơn của tôi" | – |

## Màn 7 – Bán hàng tại quầy (`/ban-hang/`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang | Hiện ô quét mã vạch, danh sách sách còn hàng, bảng giỏ quầy | Đọc: `sach` |
| Quét mã vạch (máy quét mã vạch nhập vào ô rồi Enter) | `them_vao_gio_quay()`: tìm sách theo `ma_vach`, kiểm tra tồn, thêm vào giỏ quầy (session) | Ghi: session (`gio_hang_quay`) |
| Chọn sách từ danh sách | Thêm vào giỏ quầy như trên | Ghi: session |
| Sửa số lượng / Xoá | Cập nhật hoặc xoá trong giỏ quầy | Ghi: session |
| Nhập họ tên khách + bấm "Thanh toán" | `tao_don_hang(kenh='QUAY', khach_id=None, nhan_vien_id=<nv>, hinh_thuc_tt='TRUC_TIEP')` → đơn `trang_thai='HOAN_TAT'`, ghi `chi_tiet_don_hang` (chốt `don_gia`), trừ tồn, xoá giỏ quầy | Ghi: `don_hang`, `chi_tiet_don_hang`, cập nhật `sach` |

## Màn 8 – Hoá đơn (`/ban-hang/hoa-don/<id>`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang | Hiện đầy đủ hoá đơn: họ tên khách, ngày lập, loại hoá đơn, bảng STT – sách – thể loại – số lượng – đơn giá – thành tiền, tổng cộng, tên nhân viên thanh toán (in được) | Đọc: `don_hang`, `chi_tiet_don_hang` |

## Màn 9 – Đơn chờ lấy sách + xác nhận thu tiền (`/ban-hang/don-cho-lay`)

| Sự kiện | Xử lý | Dữ liệu đọc/ghi |
| --- | --- | --- |
| Mở trang | Tự huỷ đơn quá hạn trước, rồi liệt kê đơn `trang_thai='CHO_LAY'` kèm hạn lấy sách | Đọc/ghi: `don_hang`, `sach` |
| Bấm "Xác nhận lấy sách & thu tiền" | `xac_nhan_lay_sach()`: kiểm tra đơn vẫn `CHO_LAY`, đặt `trang_thai='HOAN_TAT'` và `nhan_vien_id` (nhân viên thu tiền) | Ghi: `don_hang` |

---

## Gợi ý vẽ mockup bằng Mockflow cho các màn hình của B

1. Đăng ký tài khoản
2. Đăng nhập
3. Danh sách sách cho khách (+ nút "Thêm vào giỏ")
4. Giỏ hàng của khách
5. Đặt sách – chọn hình thức thanh toán
6. Đơn của tôi
7. Bán tại quầy (ô quét mã vạch + giỏ quầy)
8. Hoá đơn
9. Đơn chờ lấy sách

Sau khi vẽ xong, đặt tên file theo số thứ tự hình trong báo cáo (Hình 2.x) và chèn kèm
bảng 3 cột tương ứng ở trên.
