# UC05 – Lập phiếu nhập sách – Sơ đồ tuần tự (Sequence Diagram)

> Vẽ bằng Mermaid: dán nội dung khối `mermaid` vào <https://mermaid.live> rồi xuất ảnh PNG
> để đưa vào báo cáo (Chương 2 – mục 2.3 Sơ đồ tuần tự).

```mermaid
sequenceDiagram
    autonumber
    actor QL as Người quản lý (kho)
    participant UI as Giao diện web
    participant RT as Flask route (kho.py)
    participant DB as MySQL (nha_sach)

    QL->>UI: Mở trang "Lập phiếu nhập"
    UI->>RT: GET /kho/phieu-nhap
    RT->>DB: Đọc quy_dinh (nhap_toi_thieu, nguong_ton_de_nhap)
    DB-->>RT: 150, 300
    RT-->>UI: Form: ngày nhập + các dòng (sách, số lượng)
    UI-->>QL: Hiển thị quy định đang áp dụng

    QL->>UI: Chọn ngày nhập, chọn sách + số lượng từng dòng
    QL->>UI: Bấm "Lưu phiếu nhập"
    UI->>RT: POST /kho/phieu-nhap (ngay_nhap, sach_id[], so_luong[])

    RT->>DB: Đọc quy_dinh + đọc so_luong_ton của từng sách
    DB-->>RT: ngưỡng nhập, ngưỡng tồn, tồn kho

    loop Mỗi dòng trong phiếu
        alt Số lượng < nhap_toi_thieu hoặc tồn >= nguong_ton_de_nhap
            RT-->>UI: Báo lỗi: "số lượng nhập phải từ 150 cuốn trở lên" / "chỉ được nhập khi tồn nhỏ hơn 300"
            UI-->>QL: Hiển thị thông báo lỗi, không lưu gì
        else Dòng hợp lệ
            RT->>RT: Ghi nhớ (sach, so_luong)
        end
    end

    alt Không có dòng hợp lệ
        RT-->>UI: Báo lỗi
    else Có dòng hợp lệ
        RT->>DB: INSERT phieu_nhap (ngay_nhap, nguoi_quan_ly_id)
        loop Mỗi dòng hợp lệ
            RT->>DB: INSERT chi_tiet_phieu_nhap (phieu_nhap_id, sach_id, so_luong)
            RT->>DB: UPDATE sach SET so_luong_ton = so_luong_ton + so_luong
        end
        RT->>DB: COMMIT (cả phiếu + chi tiết + tồn trong 1 transaction)
        DB-->>RT: OK
        RT-->>UI: Flash "Đã lập phiếu nhập #id" → chuyển về trang phiếu nhập
        UI-->>QL: Thông báo thành công
    end
```
