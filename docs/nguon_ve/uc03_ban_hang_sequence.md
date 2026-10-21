# UC03 – Bán sách tại quầy (Nhân viên bán hàng) – Sơ đồ tuần tự & hoạt động

> Vẽ bằng Mermaid: <https://mermaid.live>.

## Sơ đồ tuần tự

```mermaid
sequenceDiagram
    autonumber
    actor NV as Nhân viên bán hàng
    participant UI as Giao diện quầy
    participant RT as Flask route (ban_hang.py)
    participant GV as Hàm nghiệp vụ (nghiem_vu.py)
    participant DB as MySQL (nha_sach)

    NV->>UI: Mở màn "Bán tại quầy"
    UI->>RT: GET /ban-hang/
    RT->>DB: Đọc danh sách sách còn hàng
    RT-->>UI: Form quét mã vạch + bảng giỏ hàng quầy

    loop Mỗi lần quét mã vạch
        NV->>UI: Quét mã vạch (hoặc chọn sách) + số lượng
        UI->>RT: POST /ban-hang/ (hanh_dong = them, ma_vach, so_luong)
        RT->>DB: Tìm sach theo ma_vach, đọc so_luong_ton
        alt Tồn kho đủ
            RT-->>UI: Thêm vào giỏ hàng quầy (session)
        else Không tìm thấy mã vạch / hết hàng
            RT-->>UI: Báo lỗi
        end
    end

    NV->>UI: Nhập họ tên khách (khách vãng lai để trống) và bấm "Thanh toán"
    UI->>RT: POST /ban-hang/ (hanh_dong = thanh_toan, ten_khach)
    RT->>GV: tao_don_hang(kenh=QUAY, khach_id=NULL, nhan_vien_id, hinh_thuc_tt=TRUC_TIEP)
    GV->>DB: Kiểm tra tồn kho từng sách
    alt Không đủ tồn
        GV-->>RT: Lỗi
        RT-->>UI: Báo lỗi, giỏ hàng giữ nguyên
    else Đủ tồn
        GV->>DB: INSERT don_hang (kenh=QUAY, hinh_thuc_tt=TRUC_TIEP, trang_thai=HOAN_TAT, nhan_vien_id)
        loop Mỗi dòng sách
            GV->>DB: INSERT chi_tiet_don_hang (so_luong, don_gia chốt lúc bán)
            GV->>DB: UPDATE sach SET so_luong_ton = so_luong_ton - so_luong
        end
        GV->>DB: COMMIT
        GV-->>RT: Đơn #id
        RT-->>UI: Chuyển tới trang hoá đơn để in
    end
```

## Sơ đồ hoạt động

```mermaid
flowchart TD
    A([Bắt đầu]) --> B[Nhân viên mở màn Bán tại quầy]
    B --> C[Quét mã vạch hoặc chọn sách, nhập số lượng]
    C --> D{Hệ thống tìm sách theo mã vạch}
    D -- Không có --> E[Báo lỗi mã vạch không hợp lệ]
    E --> C
    D -- Có --> F{Tồn kho còn đủ?}
    F -- Không --> G[Báo lỗi hết hàng]
    G --> C
    F -- Đủ --> H[Thêm vào giỏ hàng quầy]
    H --> C
    H --> I[Nhân viên nhập họ tên khách và bấm Thanh toán]
    I --> J[Hệ thống kiểm tra tồn lần cuối]
    J -- Không đủ --> K[Báo lỗi, giữ nguyên giỏ hàng]
    K --> I
    J -- Đủ --> L[Ghi don_hang kenh QUAY, trang_thai HOAN_TAT, nhan_vien_id]
    L --> M[Ghi chi_tiet_don_hang với don_gia chốt lúc bán]
    M --> N[Trừ tồn kho]
    N --> O[Hiện hoá đơn để in]
    O --> Z([Kết thúc])
```

## Làn (swimlane) theo vai trò

| Làn (vai trò) | Các bước trong làn |
| --- | --- |
| **Nhân viên bán hàng** | Mở màn bán hàng → quét mã vạch từng cuốn → sửa/xoá giỏ quầy → nhập họ tên khách → bấm "Thanh toán" → in hoá đơn |
| **Hệ thống (Flask + MySQL)** | Tìm sách theo `ma_vach` → kiểm tra tồn → ghi `don_hang` (`kenh='QUAY'`, `trang_thai='HOAN_TAT'`, `nhan_vien_id`) + `chi_tiet_don_hang` → trừ `sach.so_luong_ton` |
| **CSDL MySQL** | Lưu hoá đơn và chi tiết, cập nhật tồn kho |
