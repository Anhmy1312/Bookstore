# Kế hoạch tuần 2 – Phần A (kho + quản trị) — Đề tài 3 Quản lý nhà sách

Thời gian: 27/10 – 2/11/2026. Nhóm: **A = kho + quản trị** (`kho.py`, `admin.py`; UC05, UC07).
Người thực hiện phiên này: **A**. B lo `auth.py`, `dat_sach.py`, `ban_hang.py` (UC02, UC03).

## 1. Mục tiêu tuần 2 (giữ nguyên theo kế hoạch trong `AnhMy.docx`)
- Mỗi người vẽ **sequence diagram, activity diagram, mockup** cho use case của mình rồi mới code.
- A: quản lý sách, lập phiếu nhập, trang sửa quy định.
- Tự kiểm tra theo đề: *nhập 100 cuốn bị từ chối; nhập sách tồn ≥ 300 bị từ chối; đổi 150 → 100 trên trang quy định rồi nhập thử thấy áp dụng ngay.*

## 2. Quyết định kiến trúc
| Vấn đề | Quyết định | Lý do |
|---|---|---|
| Phân quyền 4 vai trò | File MỚI `bookstore/quyen.py` (decorator `vai_tro_required`) | Không đụng file của B, dễ ghép |
| Đăng nhập chưa có (B chưa viết) | Làm **tối giản** trong `auth.py` + `templates/dang_nhap.html` | Cần nền để A test; ghi chú cho B ở cuối |
| Menu theo vai trò | Thêm 1 khối nhỏ vào `base.html` (file của B) | Ràng buộc nav là chung |
| Luật 150/300/48 | Đọc `quy_dinh` qua `QuyDinh.lay_gia_tri()` | Đề yêu cầu YC5 sửa được từ giao diện |
| Kiểm tra luật nhập | Kiểm tra trong code Flask **trước** khi ghi CSDL, báo lỗi thân thiện | Handler `SQLAlchemyError` hiện hiện "Không đọc được CSDL" cho mọi lỗi |
| Xoá sách | Bắt `IntegrityError` (MySQL 1451) → "Sách đã có giao dịch, không thể xoá" | Điểm dễ vấp đã biết |
| Mã vạch trùng | Bắt `IntegrityError` (1062) → "Mã vạch đã tồn tại" | `ma_vach` UNIQUE |

## 3. Danh sách việc (mỗi việc là 1 lát nhỏ, kiểm chứng được)

### Phase 0 — Nền dùng chung
- [ ] **T0. Commit tuần 1 lên git** (repo `main` hiện chưa có commit nào) — mốc an toàn để diff/rollback.
- [ ] **T1. `quyen.py`**: decorator `vai_tro_required(*vai_tro)` + `vai_tro_hien_tai()`.
- [ ] **T2. `auth.py` (nền tối giản)**: `/dang-nhap`, `/dang-xuat`, `templates/dang_nhap.html`.
- [ ] **T3. `base.html`**: menu theo vai trò + nút đăng xuất + tên người dùng.
- ✅ **Checkpoint 0**: đăng nhập được cả 5 vai trò; truy cập sai vai trò bị chặn; `/kiem-tra-db` vẫn đúng.

### Phase 1 — `kho.py`: quản lý sách (YC5)
- [ ] **T4. `/kho/sach`**: danh sách + tìm kiếm (tên, mã vạch, thể loại) + thêm + sửa + xoá (bắt lỗi 1451/1062).
  - Template: `templates/kho/sach_danh_sach.html`, `templates/kho/sach_form.html`.
- ✅ **Checkpoint 1**: thêm/sửa/xoá chạy đúng trên MySQL thật; xoá sách đã bán bị chặn đúng thông báo.

### Phase 2 — `kho.py`: lập phiếu nhập (YC1)
- [ ] **T5. `/kho/phieu-nhap`**: form nhiều dòng (ngày nhập; STT, sách, thể loại, tác giả, số lượng); kiểm tra `so_luong >= nhap_toi_thieu` và `so_luong_ton < nguong_ton_de_nhap`; transaction: tạo `phieu_nhap` + `chi_tiet_phieu_nhap` + cộng `so_luong_ton`.
  - Template: `templates/kho/phieu_nhap.html`.
- ✅ **Checkpoint 2**: nhập 100 cuốn bị từ chối; nhập sách tồn ≥ 300 bị từ chối; nhập hợp lệ thì tồn tăng đúng, `phieu_nhap` + `chi_tiet_phieu_nhap` có dữ liệu.

### Phase 3 — `admin.py`: sửa quy định (YC5)
- [ ] **T6. `/admin/quy-dinh`**: sửa `nhap_toi_thieu`, `nguong_ton_de_nhap`, `gio_huy_don`; giá trị ≥ 0.
  - Template: `templates/admin/quy_dinh.html`.
- ✅ **Checkpoint 3**: đổi 150 → 100 thì nhập 120 cuốn được chấp nhận ngay (luật đọc động, không viết cứng); đổi lại 150.

### Phase 4 — Hồ sơ báo cáo của A (tuần 2)
- [ ] **T7. Sơ đồ**: sequence + activity cho UC05 (Nhập sách) và UC07 (Thống kê) → `docs/nguon_ve/*.md` (Mermaid, dùng được mermaid.ai).
- [ ] **T8. Mockup + thiết kế xử lý**: bảng 3 cột (sự kiện | xử lý | dữ liệu đọc/ghi) cho các màn hình của A → `docs/thiet_ke_xu_ly_A.md`.
- ✅ **Checkpoint 4**: nội dung khớp với code đã chạy; tên bảng/cột trùng `schema.sql`.

## 4. Rủi ro
| Rủi ro | Mức | Xử lý |
|---|---|---|
| `auth.py`, `base.html` là file B → ghi đè công việc của B | Trung bình | Code tối giản, dễ mở rộng; ghi rõ trong báo cáo cho B và trong `PROJECT_CONTEXT.md` |
| Nhập sách vi phạm luật bị báo nhầm "lỗi CSDL" | Trung bình | Kiểm tra luật trong code, không dựa vào CHECK của MySQL |
| Xoá sách có giao dịch → MySQL 1451 | Cao (dễ gặp) | Bắt `IntegrityError` + `db.session.rollback()` + thông báo rõ |
| `ma_vach` trùng | Trung bình | Bắt lỗi 1062, báo rõ |
| Rò dữ liệu thử trong CSDL `nha_sach` | Trung bình | Dọn dữ liệu test sau mỗi đợt kiểm thử, giữ nguyên 5/3/5/20 |

## 5. Câu hỏi còn mở (không chặn tiến độ)
- B đã viết `auth.py` riêng chưa? Nếu có → giữ code của B, chỉ giữ `quyen.py` + các route của A.
- `base.html`: B có thể thêm phần menu riêng không? Nếu xung đột → đặt menu vào template riêng `templates/_menu.html` và include 1 dòng.
