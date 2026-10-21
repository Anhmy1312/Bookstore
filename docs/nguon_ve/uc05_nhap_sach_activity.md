# UC05 – Lập phiếu nhập sách – Sơ đồ hoạt động (Activity Diagram)

> Vẽ bằng Mermaid: <https://mermaid.live>. Đưa vào báo cáo Chương 2 – mục 2.2 Sơ đồ hoạt động.

```mermaid
flowchart TD
    A([Bắt đầu]) --> B[Người quản lý mở trang Lập phiếu nhập]
    B --> C[Hệ thống đọc quy_dinh: nhap_toi_thieu, nguong_ton_de_nhap]
    C --> D[Hiển thị form phiếu nhập]
    D --> E[Người quản lý chọn ngày nhập, sách và số lượng từng dòng]
    E --> F[Người quản lý bấm Lưu phiếu nhập]
    F --> G{Hệ thống đọc tồn kho của từng sách}
    G --> H{Số lượng >= nhap_toi_thieu?}
    H -- Không --> I[Hệ thống báo lỗi: số lượng nhập tối thiểu]
    I --> Z([Kết thúc: không lưu phiếu])
    H -- Có --> J{Tồn kho < nguong_ton_de_nhap?}
    J -- Không --> K[Hệ thống báo lỗi: tồn kho đã đủ, không được nhập]
    K --> Z
    J -- Có --> L{Còn dòng nào khác?}
    L -- Có --> G
    L -- Không --> M[Hệ thống tạo phiếu_nhap]
    M --> N[Hệ thống tạo chi_tiet_phieu_nhap cho từng dòng]
    N --> O[Hệ thống cộng dồn so_luong_ton của các sách]
    O --> P[Hệ thống COMMIT]
    P --> Q[Thông báo: Đã lập phiếu nhập thành công]
    Q --> Z
```

## Làn (swimlane) theo vai trò – dùng khi vẽ bằng draw.io / StarUML

| Làn (vai trò) | Các bước trong làn |
| --- | --- |
| **Người quản lý (kho)** | Mở trang phiếu nhập → chọn ngày nhập → chọn sách + số lượng từng dòng → bấm "Lưu phiếu nhập" → (nếu lỗi) đọc thông báo và sửa lại → nhận thông báo thành công |
| **Hệ thống (Flask + MySQL)** | Đọc `quy_dinh` → kiểm tra từng dòng theo luật 150/300 → tạo `phieu_nhap` → tạo `chi_tiet_phieu_nhap` → cộng `sach.so_luong_ton` → COMMIT (hoặc báo lỗi) |
| **CSDL MySQL** | Lưu `phieu_nhap`, `chi_tiet_phieu_nhap`; cập nhật `sach.so_luong_ton` |

