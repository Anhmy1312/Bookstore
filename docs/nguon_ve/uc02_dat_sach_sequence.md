# UC02 – Đặt sách online (Khách hàng) – Sơ đồ tuần tự & hoạt động

> Vẽ bằng Mermaid: dán khối `mermaid` vào <https://mermaid.live> rồi xuất ảnh PNG cho báo cáo
> (Chương 2 – mục 2.2 và 2.3). Nhớ đánh số hình theo thứ tự (Hình 2.x).

## Sơ đồ tuần tự

```mermaid
sequenceDiagram
    autonumber
    actor KH as Khách hàng
    participant UI as Giao diện web
    participant RT as Flask route (dat_sach.py)
    participant GV as Hàm nghiệp vụ (nghiem_vu.py)
    participant DB as MySQL (nha_sach)

    KH->>UI: Đăng nhập (tài khoản KHACH)
    UI->>RT: POST /dang-nhap
    RT->>DB: Đọc nguoi_dung theo ten_dang_nhap + kiem_tra_mat_khau
    DB-->>RT: Thông tin người dùng (vai_tro = KHACH)
    RT-->>UI: Đăng nhập thành công

    KH->>UI: Mở "Sách trong nhà sách", chọn sách + số lượng
    UI->>RT: POST /dat-sach/gio-hang/them
    RT->>DB: Đọc sach.so_luong_ton
    alt Tồn kho đủ
        RT-->>UI: Thêm vào giỏ hàng (session)
    else Tồn kho không đủ
        RT-->>UI: Báo lỗi "chỉ còn N cuốn"
    end

    KH->>UI: Bấm "Đặt sách", chọn hình thức thanh toán
    UI->>RT: POST /dat-sach/dat-hang (hinh_thuc_tt)
    RT->>GV: tao_don_hang(kenh=ONLINE, hinh_thuc_tt, chi_tiet)
    GV->>DB: Đọc quy_dinh (gio_huy_don)
    GV->>DB: Kiểm tra tồn kho từng sách
    alt Không đủ tồn
        GV-->>RT: Lỗi "Sách ... không đủ ... cuốn để đặt"
        RT-->>UI: Báo lỗi, không tạo đơn
    else Đủ tồn
        GV->>DB: INSERT don_hang (kenh=ONLINE, hinh_thuc_tt, trang_thai, ngay_tao, han_lay_sach)
        loop Mỗi dòng sách
            GV->>DB: INSERT chi_tiet_don_hang (don_hang_id, sach_id, so_luong, don_gia chốt)
            GV->>DB: UPDATE sach SET so_luong_ton = so_luong_ton - so_luong
        end
        GV->>DB: COMMIT
        alt Thanh toán TRUC_TIEP tại nhà sách
            GV-->>RT: trang_thai = CHO_LAY, han_lay_sach = ngay_tao + gio_huy_don giờ
            RT-->>UI: "Hãy đến nhà sách trong vòng ... để lấy sách và thanh toán"
        else Thanh toán ONLINE
            GV-->>RT: trang_thai = HOAN_TAT, han_lay_sach = NULL
            RT-->>UI: "Đã thanh toán online, giao hàng miễn phí"
        end
        RT-->>UI: Chuyển tới trang "Đơn của tôi" và xoá giỏ hàng
    end

    KH->>UI: Mở "Đơn của tôi"
    UI->>RT: GET /dat-sach/don-hang
    RT->>GV: huy_don_qua_han()
    GV->>DB: UPDATE don_hang SET trang_thai='DA_HUY' cho đơn CHO_LAY quá hạn + trả lại tồn
    RT-->>UI: Danh sách đơn (trạng thái, hạn lấy sách, nút huỷ)
```

## Sơ đồ hoạt động

```mermaid
flowchart TD
    A([Bắt đầu]) --> B[Khách đăng nhập tài khoản KHACH]
    B --> C[Chọn sách và số lượng]
    C --> D{Hệ thống kiểm tra tồn kho}
    D -- Không đủ --> E[Báo lỗi: chỉ còn N cuốn]
    E --> Z([Kết thúc])
    D -- Đủ --> F[Thêm vào giỏ hàng]
    F --> G[Khách bấm Đặt sách, chọn hình thức thanh toán]
    G --> H[Trực tiếp tại nhà sách]
    G --> I[Thanh toán online]
    H --> J[Hệ thống tạo đơn trạng thái CHO_LAY<br/>hạn lấy sách = giờ đặt + 48 giờ]
    I --> K[Hệ thống tạo đơn trạng thái HOAN_TAT<br/>giao hàng miễn phí]
    J --> L[Hệ thống trừ tồn kho]
    K --> L
    L --> M[Khách đến nhà sách lấy sách và thanh toán]
    M --> N[Nhân viên xác nhận lấy sách và thu tiền<br/>đơn chuyển HOAN_TAT]
    J --> O[Khách không đến trong 48 giờ]
    O --> P[Hệ thống tự huỷ đơn và trả lại tồn kho]
    N --> Z
    P --> Z
```

## Làn (swimlane) theo vai trò

| Làn (vai trò) | Các bước trong làn |
| --- | --- |
| **Khách hàng** | Đăng nhập → chọn sách, số lượng → thêm vào giỏ → bấm "Đặt sách" → chọn hình thức thanh toán → xem "Đơn của tôi" → (nếu còn trong hạn) huỷ đơn |
| **Hệ thống (Flask + MySQL)** | Kiểm tra tồn → ghi `don_hang` + `chi_tiet_don_hang` → trừ tồn → tính `han_lay_sach` → tự huỷ đơn quá hạn và trả lại tồn |
| **CSDL MySQL** | Lưu đơn/chi tiết; cập nhật `sach.so_luong_ton` |
| **Nhân viên bán hàng** | Nhận khách lấy sách → xác nhận và thu tiền (UC04) |
