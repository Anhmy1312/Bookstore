# UC07 – Xem thống kê báo cáo – Sơ đồ hoạt động (Activity Diagram)

> Vẽ bằng Mermaid: <https://mermaid.live>. Đưa vào báo cáo Chương 2 – mục 2.2.

```mermaid
flowchart TD
    A([Bắt đầu]) --> B[Người quản trị mở trang Thống kê báo cáo]
    B --> C[Chọn tháng và loại báo cáo]
    C --> D{Báo cáo nào?}
    D -- Doanh thu theo thể loại --> E[Hệ thống truy vấn don_hang + chi_tiet_don_hang<br/>chỉ lấy đơn HOAN_TAT trong tháng đã chọn]
    D -- Tần suất bán theo sách --> F[Hệ thống truy vấn SUM so_luong theo từng sách<br/>chỉ lấy đơn HOAN_TAT trong tháng đã chọn]
    E --> G[Hệ thống tính tỷ lệ và tổng doanh thu tháng]
    F --> H[Hệ thống tính tỷ lệ theo tổng số lượng bán tháng]
    G --> I[Hiển thị bảng báo cáo]
    H --> I
    I --> J[Vẽ biểu đồ Chart.js]
    J --> K[Người quản trị xem và tải/đóng]
    K --> Z([Kết thúc])
```

## Làn (swimlane) theo vai trò

| Làn (vai trò) | Các bước trong làn |
| --- | --- |
| **Người quản trị** | Mở trang Thống kê → chọn tháng → chọn loại báo cáo → xem bảng + biểu đồ |
| **Hệ thống (Flask + MySQL)** | Nhận tham số tháng → truy vấn CSDL → tính tỷ lệ, tổng → trả bảng + dữ liệu biểu đồ |
| **CSDL MySQL** | Cung cấp `don_hang`, `chi_tiet_don_hang`, `sach`, `the_loai` để tổng hợp |
