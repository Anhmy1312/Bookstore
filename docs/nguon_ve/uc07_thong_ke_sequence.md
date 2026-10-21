# UC07 – Xem thống kê báo cáo – Sơ đồ tuần tự (Sequence Diagram)

> Vẽ bằng Mermaid: <https://mermaid.live>. Đưa vào báo cáo Chương 2 – mục 2.3.
> Lưu ý: phần này A sẽ code ở **tuần 3**; sơ đồ được vẽ trước theo kế hoạch tuần 2.

```mermaid
sequenceDiagram
    autonumber
    actor QT as Người quản trị
    participant UI as Giao diện web
    participant RT as Flask route (admin.py)
    participant DB as MySQL (nha_sach)

    QT->>UI: Mở menu "Thống kê báo cáo"
    UI->>RT: GET /admin/bao-cao
    RT->>DB: Đọc quy_dinh (nếu có khoảng thời gian mặc định)
    RT-->>UI: Form chọn tháng + loại báo cáo

    QT->>UI: Chọn tháng + báo cáo doanh thu theo thể loại
    UI->>RT: GET /admin/bao-cao?thang=2026-10&loai=doanh_thu

    RT->>DB: SELECT the_loai.ten, SUM(chi_tiet_don_hang.so_luong * chi_tiet_don_hang.don_gia)<br/>FROM don_hang JOIN chi_tiet_don_hang JOIN sach JOIN the_loai<br/>WHERE don_hang.trang_thai = 'HOAN_TAT' AND don_hang.ngay_tao trong tháng<br/>GROUP BY the_loai.id
    DB-->>RT: Danh sách (thể loại, doanh thu, số lượt bán)
    RT->>RT: Tính tỷ lệ = doanh thu thể loại / tổng doanh thu tháng<br/>Tính tổng doanh thu tháng
    RT-->>UI: Bảng báo cáo + dữ liệu JSON cho biểu đồ
    UI-->>QT: Bảng (thể loại, doanh thu, số lượt bán, tỷ lệ, tổng doanh thu)<br/>+ biểu đồ Chart.js

    QT->>UI: Chọn báo cáo tần suất bán theo tháng
    UI->>RT: GET /admin/bao-cao?thang=2026-10&loai=tan_suat
    RT->>DB: SELECT sach.ten, the_loai.ten, SUM(so_luong)<br/>... WHERE trang_thai='HOAN_TAT' GROUP BY sach.id
    DB-->>RT: Danh sách (sách, thể loại, số lượng bán)
    RT->>RT: Tính tỷ lệ = số lượng bán của sách / tổng số lượng bán tháng
    RT-->>UI: Bảng + biểu đồ
    UI-->>QT: Bảng (tên sách, thể loại, số lượng, tỷ lệ) + biểu đồ Chart.js
```

## Quy ước đã chốt cho báo cáo (dùng chung với B)

| Quy ước | Nội dung |
| --- | --- |
| Chỉ tính đơn | `don_hang.trang_thai = 'HOAN_TAT'` (đơn `CHO_LAY` và `DA_HUY` không tính) |
| Mốc tháng | Theo `don_hang.ngay_tao` |
| Giá dùng để tính | `chi_tiet_don_hang.don_gia` (giá đã chốt lúc bán), **không** lấy `sach.don_gia` |
| Tổng tiền | Không lưu trong CSDL, tính bằng `SUM(so_luong * don_gia)` |
| Cột "số lượt thuê" trong mẫu | Hiểu là **"số lượt bán"** = tổng số cuốn đã bán của thể loại trong tháng (giả định đã ghi ở Chương 1) |
| Tỷ lệ báo cáo 1 | doanh thu thể loại / tổng doanh thu tháng |
| Tỷ lệ báo cáo 2 | số lượng bán của sách / tổng số lượng bán trong tháng |
