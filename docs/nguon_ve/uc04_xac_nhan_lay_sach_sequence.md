# UC04 – Xác nhận khách lấy sách và thu tiền (Nhân viên bán hàng)

> Use case nhỏ, không đặc tả riêng – được gộp vào luồng 4b của UC02 (đề xuất đã chốt ở
> `PROJECT_CONTEXT.md` mục 3.11). Vẽ bằng Mermaid: <https://mermaid.live>.

## Sơ đồ tuần tự

```mermaid
sequenceDiagram
    autonumber
    actor KH as Khách hàng
    actor NV as Nhân viên bán hàng
    participant UI as Giao diện
    participant RT as Flask route (ban_hang.py)
    participant GV as Hàm nghiệp vụ (nghiem_vu.py)
    participant DB as MySQL (nha_sach)

    KH->>NV: Đến quầy, nói "Tôi đặt sách online, đơn #12"
    NV->>UI: Mở "Đơn chờ lấy sách"
    UI->>RT: GET /ban-hang/don-cho-lay
    RT->>GV: huy_don_qua_han()
    GV->>DB: Huỷ các đơn CHO_LAY đã quá hạn (trả lại tồn kho)
    GV-->>RT: số đơn đã huỷ
    RT->>DB: SELECT don_hang WHERE trang_thai = 'CHO_LAY'
    RT-->>UI: Danh sách đơn chờ lấy (khách, hạn lấy sách, tổng tiền)
    UI-->>NV: Hiện danh sách đơn

    NV->>UI: Bấm "Xác nhận lấy sách & thu tiền" cho đơn #12
    UI->>RT: POST /ban-hang/don-cho-lay/12/xac-nhan
    RT->>GV: huy_don_qua_han() (kiểm tra lần cuối còn trong hạn không)
    GV->>DB: Đọc don_hang #12
    alt Đơn vẫn ở trạng thái CHO_LAY
        RT->>DB: UPDATE don_hang SET trang_thai='HOAN_TAT', nhan_vien_id = <nv>
        RT-->>UI: Chuyển tới trang hoá đơn để in
        UI-->>KH: Giao sách, hoá đơn đã thanh toán
    else Đơn đã quá hạn (vừa bị huỷ)
        RT-->>UI: Báo lỗi "Đơn hàng không còn ở trạng thái chờ lấy sách"
    end
```

## Sơ đồ hoạt động

```mermaid
flowchart TD
    A([Bắt đầu]) --> B[Khách đến quầy đón sách]
    B --> C[Nhân viên mở danh sách đơn chờ lấy sách]
    C --> D[Hệ thống tự huỷ các đơn quá hạn 48 giờ]
    D --> E{Nhân viên chọn đúng đơn của khách?}
    E -- Không --> C
    E -- Có --> F{Đơn còn trong hạn và ở trạng thái CHO_LAY?}
    F -- Không --> G[Báo khách đơn đã bị huỷ]
    G --> Z([Kết thúc])
    F -- Có --> H[Nhân viên xác nhận lấy sách và thu tiền]
    H --> I[Hệ thống đặt trạng thái HOAN_TAT và ghi nhân viên thanh toán]
    I --> J[In hoá đơn và giao sách]
    J --> Z
```

## Làn (swimlane) theo vai trò

| Làn (vai trò) | Các bước trong làn |
| --- | --- |
| **Khách hàng** | Đến quầy đón sách → nhận sách và hoá đơn |
| **Nhân viên bán hàng** | Mở danh sách đơn chờ lấy → tìm đơn của khách → bấm "Xác nhận lấy sách & thu tiền" → thu tiền và giao sách |
| **Hệ thống (Flask + MySQL)** | Tự huỷ đơn quá hạn → kiểm tra trạng thái đơn → `UPDATE don_hang SET trang_thai='HOAN_TAT', nhan_vien_id=...` |
| **CSDL MySQL** | Cập nhật trạng thái đơn và nhân viên thanh toán |
