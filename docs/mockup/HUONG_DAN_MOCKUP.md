# Hướng dẫn vẽ mockup Mockflow – Phần A (kho + quản trị)

> **Yêu cầu đề:** Vẽ mockup bằng [Mockflow](https://mockflow.com), **không** chụp màn hình web thật.
> Mockflow là công cụ online → bạn tạo tài khoản free, vẽ theo hướng dẫn dưới đây.

---

## 1. Danh sách 6 màn hình phần A

| # | Màn hình | Route | File SVG tham khảo |
|---|---|---|---|
| 1 | Đăng nhập | `/dang-nhap` | `hinh_dang_nhap.svg` |
| 2 | Quản lý sách (danh sách) | `/kho/sach` | `hinh_quan_ly_sach.svg` |
| 3 | Thêm / Sửa sách (form) | `/kho/sach/them`, `/kho/sach/{id}/sua` | `hinh_them_sua_sach.svg` |
| 4 | Lập phiếu nhập | `/kho/phieu-nhap` | `hinh_phieu_nhap.svg` |
| 5 | Quy định hệ thống | `/admin/quy-dinh` | `hinh_quy_dinh.svg` |
| 6 | Thống kê báo cáo (tuần 3) | `/admin/bao-cao` | `hinh_bao_cao.svg` |

**Lưu ý:** 4 file SVG trên là **wireframe tham khảo** — bạn mở bằng trình duyệt để xem trước,
rào rê lại trên Mockflow cho đẹp (đề yêu cầu dùng Mockflow, không yêu cầu đẹp như mockup chuẩn).

---

## 2. Hướng dẫn vẽ trên Mockflow (từng bước)

### Bước 1 – Tạo project
1. Vào [mockflow.com](https://mockflow.com) → đăng ký tài khoản free.
2. Bấm **New Project** → chọn **Desktop** (hoặc **Web**) → đặt tên `NhaSach_Mockup`.

### Bước 2 – Thêm màn hình (mỗi màn 1 trang artboard)
1. Bấm **Add Page** (biểu tượng +) → chọn size **Desktop 1280×800**.
2. Đặt tên page theo số thứ tự: `1. Dang nhap`, `2. Quan ly sach`, ...

### Bước 3 – Dùng component có sẵn của Mockflow
Mockflow có sẵn các component拖拽 (kéo-thả):

| Component | Dùng cho |
|---|---|
| **Navigation Bar** (thanh menu) | Mọi màn hình — đặt màu `#212529`, thêm text logo `📚 Nhà sách` |
| **Text Field / Input** | Ô nhập (tên đăng nhập, mã vạch, số lượng...) |
| **Dropdown / Select** | Chọn thể loại, chọn sách |
| **Button** | Nút "Đăng nhập", "Thêm sách", "Lưu phiếu nhập" |
| **Table** | Bảng danh sách sách, bảng dòng nhập, bảng báo cáo |
| **Card / Panel** | Khung form (đăng nhập, thêm sách, quy định) |
| **Alert / Note** | Thanh thông báo quy định (xanh dương nhạt) |
| **Chart / Bar Chart** | Biểu đồ cột ở màn báo cáo |

### Bước 4 – Chỉnh màu theo Bootstrap (để đồng bộ với web thật)

| Màu | Mã | Dùng cho |
|---|---|---|
| Navbar đen | `#212529` | Thanh menu trên cùng |
| Nút chính (xanh dương) | `#0d6efd` | Đăng nhập, Lưu, Xem thống kê |
| Nút thêm (xanh lá) | `#198754` | + Thêm sách |
| Nút huỷ (đỏ) | `#dc3545` | Xoá |
| Nền trang | `#f8f9fa` | Background |
| Viền input | `#ced4da` | Border ô nhập |
| Alert xanh | `#cff4fc` | Thanh quy định |

### Bước 5 – Xuất hình
1. Sau khi vẽ xong từng trang → **Export → PNG** (hoặc SVG).
2. Đặt tên file theo số thứ tự hình trong báo cáo: `hinh_2_1_dang_nhap.png`, `hinh_2_2_quan_ly_sach.png`, ...
3. Chèn vào Word tại Chương 2 – mục 2.5, kèm bảng 3 cột (sự kiện | xử lý | dữ liệu đọc/ghi)
   lấy từ `docs/thiet_ke_xu_ly_A.md`.

---

## 3. Gợi ý từng màn hình

### Màn 1 – Đăng nhập
```
[Navbar đen: 📚 Nhà sách ................. Đăng nhập | Đăng ký]
                    Đăng nhập hệ thống
         ┌──────────────────────────────────┐
         │ Tên đăng nhập                    │
         │ [________________________]       │
         │ Mật khẩu                        │
         │ [________________________]       │
         │ [      Đăng nhập (xanh dương) ]  │
         └──────────────────────────────────┘
       Tài khoản mẫu: quantri · quanly · nhanvien · khachhang
```

### Màn 2 – Quản lý sách
```
[Navbar: 📚 Nhà sách ... Quản lý sách | Phiếu nhập | Tài khoản | Đăng xuất]
Quản lý sách
[Tên sách/mã vạch/tác giả...] [Thể loại ▼] [Tìm kiếm] [+ Thêm sách (xanh lá)]
┌─────┬──────────┬───────────┬──────────┬──────────┬─────────┬────────┬──────────┐
│ STT │ Mã vạch  │ Tên sách  │ Thể loại │ Tác giả  │ Đơn giá │ Tồn    │ Thao tác │
├─────┼──────────┼───────────┼──────────┼──────────┼─────────┼────────┼──────────┤
│ 1   │ 89350... │ Mắt biếc  │ Tiểu...  │ Nguyễn.. │ 95.000  │ 320    │ [Sửa][Xoá]│
└─────┴──────────┴───────────┴──────────┴──────────┴─────────┴────────┴──────────┘
```

### Màn 3 – Thêm/Sửa sách (form)
```
Thêm sách mới
┌──────────────────────────────────────────────────┐
│ Tên sách                                        │
│ [________________________________________]       │
│ Mã vạch              │ Tác giả                  │
│ [______________]     │ [______________]         │
│ Thể loại             │ Đơn giá     │ Tồn kho    │
│ [▼ -- chọn --]       │ [0]        │ [0]        │
│                                              │
│ [Thêm sách (xanh dương)]  [Hủy (viền xám)]    │
└──────────────────────────────────────────────────┘
※ Sửa sách: ô Tồn kho bị khóa (chỉ đổi qua phiếu nhập/bán hàng)
```

### Màn 4 – Lập phiếu nhập
```
Lập phiếu nhập sách
⚠ Quy định: nhập tối thiểu 150 cuốn, chỉ nhập sách tồn < 300 cuốn
┌──────────────────────────────────────────────────────────────────┐
│ Ngày nhập: [2026-10-25]                                          │
│                                                                  │
│ Các dòng sách nhập                                              │
│ ┌─────┬─────────────────────────────────────┬──────────┬─────────┐
│ │ STT │ Sách                               │ Số lượng │ Tồn HT  │
│ ├─────┼─────────────────────────────────────┼──────────┼─────────┤
│ │ 1   │ [▼ -- Chọn sách --]               │ [0]      │ -       │
│ │ 2   │ [▼ -- Chọn sách --]               │ [0]      │ -       │
│ │ ... │ (tổng 6 dòng)                      │          │         │
│ └─────┴─────────────────────────────────────┴──────────┴─────────┘
│ [Lưu phiếu nhập (xanh dương)]  [Về danh sách sách]              │
└──────────────────────────────────────────────────────────────────┘
```

### Màn 5 – Quy định hệ thống
```
Quy định của hệ thống
(Mô tả: lưu trong bảng quy_dinh, sửa xong áp dụng ngay)
┌──────────────────────────────────────────────┐
│ nhap_toi_thieu (Số lượng nhập tối thiểu)     │
│ [150                                     ]   │
│                                              │
│ nguong_ton_de_nhap (Ngưỡng tồn để nhập)     │
│ [300                                     ]   │
│                                              │
│ gio_huy_don (Giờ tự huỷ đơn trực tiếp)      │
│ [48                                      ]   │
│                                              │
│ [Lưu quy định (xanh dương)]                  │
└──────────────────────────────────────────────┘
```

### Màn 6 – Thống kê báo cáo (tuần 3)
```
Thống kê báo cáo
┌─ Chọn tháng: [2026-10 ▼] [Xem thống kê] [Quy định hệ thống] ─┐
│                                                                  │
│ Tổng quan tháng 10/2026                                         │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│ │Tổng doanh thu│  │Tổng đơn hang│  │Tổng sl bán  │              │
│ │ 1,520,000 ₫ │  │   5 đơn     │  │  16 cuốn    │              │
│ │  (xanh dương)│  │  (xanh lá)  │  │  (xanh nhạt)│              │
│ └─────────────┘  └─────────────┘  └─────────────┘               │
│                                                                  │
│ [Báo cáo doanh thu theo thể loại]  [Báo cáo tần suất bán sách] │
│                                                                  │
│ ── Sau khi bấm nút báo cáo doanh thu ──                         │
│ ⚠ Tháng 10/2026 | Tổng doanh thu: 1,520,000 VND                │
│ ┌──────────────────────┐ ┌──────────────────────┐               │
│ │  📊 Biểu đồ cột      │ │ Thể loại │ Doanh thu │               │
│ │  (Chart.js bar)      │ │ Tiểu thuy│ 620,000   │               │
│ │                      │ │ Văn học   │ 450,000   │               │
│ │                      │ │ Kinh te   │ 280,000   │               │
│ └──────────────────────┘ └──────────────────────┘               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Cấp số hình trong báo cáo (gợi ý)

Theo `docs/thiet_ke_xu_ly_A.md`, A vẽ 6 màn → đặt tên hình theo chương:

| Chương | Mục | Hình |
|---|---|---|
| Chương 2 – 2.5 | Màn đăng nhập | Hình 2.1 |
| Chương 2 – 2.5 | Màn quản lý sách | Hình 2.2 |
| Chương 2 – 2.5 | Màn thêm/sửa sách | Hình 2.3 |
| Chương 2 – 2.5 | Màn lập phiếu nhập | Hình 2.4 |
| Chương 2 – 2.5 | Màn quy định hệ thống | Hình 2.5 |
| Chương 2 – 2.5 | Màn thống kê báo cáo | Hình 2.6 |

Mỗi hình chèn kèm **bảng 3 cột** (sự kiện | xử lý | dữ liệu đọc/ghi) tương ứng trong
`docs/thiet_ke_xu_ly_A.md`.

---

## 5. Lưu ý

- **Không chụp màn hình web thật** (đề cấm). Dùng Mockflow hoặc wireframe SVG.
- 4 file SVG trong thư mục này dùng để **xem trước nhanh** — mở bằng Chrome/Edge.
- Nếu Mockflow free giới hạn số trang → vẽ 4 màn chính trước, màn báo cáo có thể vẽ sau.
