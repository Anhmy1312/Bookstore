"""TIMELINE giao dịch (transaction) khi lập phiếu nhập sách - chạy để xem từng bước.

Chạy (từ thư mục bookstore):
    venv\\Scripts\\python.exe docs\\timeline_transaction_phieu_nhap.py

In ra 2 kịch bản:
  KỊCH BẢN 1: lập phiếu nhập thành công
  KỊCH BẢN 2: lập phiếu nhập bị lỗi ràng buộc -> rollback -> MySQL không đổi gì

Kết quả ghi ra docs\\timeline_transaction_phieu_nhap.txt (UTF-8).
CSDL luôn được đưa về đúng trạng thái ban đầu (5/3/5/20/0/0/0/0).
"""
import io
import logging
import os
import sys
import time
import atexit

# Chạy được từ mọi thư mục: đưa thư mục gốc project vào sys.path
GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, GOC)
os.chdir(GOC)

import app as app_module  # noqa: E402
from extensions import db  # noqa: E402
from models import (ChiTietDonHang, ChiTietPhieuNhap, DonHang, NguoiDung,  # noqa: E402
                    PhieuNhap, QuyDinh, Sach)

DONG = []
BAT_DAU = time.time()
SQL_GHI_DEN = []
FILE_KET_QUA = os.path.join(GOC, "docs", "timeline_transaction_phieu_nhap.txt")


class BatLoiSQL(logging.Handler):
    """Bắt mọi câu SQL do SQLAlchemy gửi đi để in vào timeline."""

    def emit(self, record):
        SQL_GHI_DEN.append(record.getMessage())


def ghi(text=""):
    DONG.append(text)


def buoc(so, tieu_de, code, sql, trang_thai_ram, trang_thai_db, ynghia=""):
    """In 1 mốc thời gian của giao dịch."""
    ghi("")
    ghi("=" * 78)
    ghi(f"BƯỚC {so}: {tieu_de}    [+{time.time() - BAT_DAU:.3f}s]")
    ghi("=" * 78)
    ghi(f"  CODE   : {code}")
    if sql:
        for dong in sql:
            ghi(f"  SQL    : {' '.join(str(dong).split())}")
    else:
        ghi("  SQL    : (chưa có câu lệnh nào được gửi xuống MySQL)")
    ghi(f"  RAM    : {trang_thai_ram}")
    ghi(f"  MYSQL  : {trang_thai_db}")
    if ynghia:
        ghi(f"  Ý NGHĨA : {ynghia}")
    SQL_GHI_DEN.clear()


def trang_thai_db():
    with app.app_context():
        return (f"phieu_nhap={PhieuNhap.query.count()} dòng, "
                f"chi_tiet_phieu_nhap={ChiTietPhieuNhap.query.count()} dòng")


def trang_thai_ton(sach_id):
    with app.app_context():
        sach = db.session.get(Sach, sach_id)
        return sach.so_luong_ton if sach else "?"


logging.getLogger("sqlalchemy.engine.Engine").addHandler(BatLoiSQL())
logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.INFO)

app = app_module.app
c = app.test_client()
c.post("/dang-nhap", data={"ten_dang_nhap": "quanly", "mat_khau": "123456"})

# Chụp lại tồn kho TRƯỚC khi thử, để luôn đưa CSDL về đúng trạng thái mẫu
# (kể cả khi script bị lỗi giữa chừng - atexit vẫn chạy).
with app.app_context():
    TON_SAU = {s.id: s.so_luong_ton for s in Sach.query.all()}


def don_sach_khi_crash():
    """Khôi phục CSDL về trạng thái mẫu: trả tồn kho + xoá phiếu/đơn tạo ra."""
    try:
        with app.app_context():
            db.session.execute(db.delete(ChiTietPhieuNhap))
            db.session.execute(db.delete(ChiTietDonHang))
            db.session.commit()
            db.session.execute(db.delete(PhieuNhap))
            db.session.execute(db.delete(DonHang))
            db.session.commit()
            for sach in Sach.query.all():
                if sach.id in TON_SAU:
                    sach.so_luong_ton = TON_SAU[sach.id]
            db.session.commit()
    except Exception:
        pass


atexit.register(don_sach_khi_crash)

ghi("#" * 78)
ghi("# TIMELINE GIAO DỊCH - LẬP PHIẾU NHẬP SÁCH (quyền quản lý)")
ghi("#" * 78)
ghi("")
ghi("Trong timeline, bốn nội dung luôn đi song song:")
ghi("  CODE  : dòng lệnh trong blueprints/kho.py mà bạn viết")
ghi("  SQL   : câu lệnh SQL THẬT do SQLAlchemy sinh ra rồi gửi sang MySQL")
ghi("  RAM   : trạng thái object Python trong bộ nhớ (session của SQLAlchemy)")
ghi("  MYSQL : trạng thái thật trong CSDL sau khi câu lệnh chạy xong")

with app.app_context():
    db.engine.echo = True

    # ------------------------------------------------------------------
    buoc(0, "Mở trang /kho/phieu-nhap (GET)", "r = c.get('/kho/phieu-nhap')", [],
         "Chưa có gì", trang_thai_db(),
         "Chỉ đọc dữ liệu để hiển thị form. Chưa có gì được ghi.")

    r = c.get("/kho/phieu-nhap")
    buoc(1, "Đọc quy định 150/300 và danh sách sách",
         "QuyDinh.lay_gia_tri(...)   +   Sach.query.order_by(Sach.ten).all()",
         list(SQL_GHI_DEN), "Các object Sach đã nạp vào RAM", trang_thai_db(),
         "Luật 150/300 lấy từ bảng quy_dinh (không viết cứng trong code).")

    sach = Sach.query.filter(Sach.so_luong_ton < 300).order_by(Sach.id).first()
    id_sach = sach.id
    ten_sach = sach.ten
    ton_truoc = sach.so_luong_ton
    SQL_GHI_DEN.clear()

    buoc(2, "Người quản lý bấm 'Lưu phiếu nhập' (POST)",
         "r = c.post('/kho/phieu-nhap', data={...})", [],
         "Chưa có gì", trang_thai_db(),
         "Request mới -> session mới -> có thể thay đổi dữ liệu.")

    buoc(3, "Kiểm tra luật 150/300 cho từng dòng",
         "kiem_tra_cac_dong_nhap(...) -> (loi, dong_hop_le)", list(SQL_GHI_DEN),
         f"Chọn được sách: {ten_sach} (tồn {ton_truoc}), số lượng 150",
         trang_thai_db(),
         "Nếu số lượng < 150 hoặc tồn >= 300 sẽ RETURN NGAY tại đây, không ghi gì vào DB.")

    phieu = PhieuNhap(ngay_nhap=__import__("datetime").date(2026, 10, 22),
                      nguoi_quan_ly_id=2)
    buoc(4, "Tạo đối tượng phiếu trong RAM",
         "phieu = PhieuNhap(ngay_nhap=..., nguoi_quan_ly_id=2)", list(SQL_GHI_DEN),
         "Có object PhieuNhap, id = None (chưa có id)", trang_thai_db(),
         "Mới chỉ là biến Python, MySQL chưa biết gì.")

    db.session.add(phieu)
    buoc(5, "Đưa phiếu vào hàng đợi của session",
         "db.session.add(phieu)", list(SQL_GHI_DEN),
         "Session ghi nhớ: phiếu cần được INSERT", trang_thai_db(),
         "Session theo dõi thay đổi. Chưa có SQL nào chạy.")

    db.session.flush()
    id_phieu = phieu.id
    buoc(6, "FLUSH - đẩy phiếu xuống MySQL để lấy id",
         "db.session.flush()", list(SQL_GHI_DEN),
         f"phieu.id = {id_phieu} (MySQL vừa tự sinh)", trang_thai_db(),
         "QUAN TRỌNG: flush = INSERT thật nhưng CHƯA commit. Hủy phiếu vẫn rollback được.")

    db.session.add(ChiTietPhieuNhap(phieu_nhap_id=id_phieu, sach_id=id_sach, so_luong=150))
    buoc(7, "Thêm từng dòng chi tiết phiếu nhập",
         "db.session.add(ChiTietPhieuNhap(phieu_nhap_id=phieu.id, sach_id=..., so_luong=150))",
         list(SQL_GHI_DEN), "Session cho biết: cần INSERT 1 dòng chi_tiet", trang_thai_db(),
         "Chi nằm trong RAM, chưa INSERT - vì còn phải thêm dòng nữa.")

    sach.so_luong_ton += 150
    buoc(8, "Cộng tồn kho của sách",
         "sach.so_luong_ton += 150", list(SQL_GHI_DEN),
         f"Session ghi nhớ: UPDATE sach so_luong_ton {ton_truoc} -> {ton_truoc + 150}",
         trang_thai_db(),
         "Giá trị mới chỉ nằm trong RAM, chưa UPDATE trong MySQL.")

    db.session.commit()
    buoc(9, "COMMIT - ghi tất cả xuống MySQL",
         "db.session.commit()", list(SQL_GHI_DEN),
         "Session rỗng, hết việc", trang_thai_db(),
         "MySQL nhận 1 lần: INSERT phieu_nhap + INSERT chi_tiet_phieu_nhap + UPDATE sach, "
         "TRONG MỘT TRANSACTION (all-or-nothing).")

    buoc(10, "Kiểm tra kết quả thật trong MySQL",
         "SELECT * FROM phieu_nhap / chi_tiet_phieu_nhap / sach", list(SQL_GHI_DEN),
         "Không còn thay đổi nào",
         f"phieu_nhap={PhieuNhap.query.count()} dòng, tồn sách = {trang_thai_ton(id_sach)} "
         f"(trước {ton_truoc})",
         "Dữ liệu đã nằm thật trong CSDL, không phải chỉ trong RAM.")

    # ------------------------------------------------------------------
    ghi("")
    ghi("#" * 78)
    ghi("# KỊCH BẢN 2: CÓ LỖI RÀNG BUỘC -> ROLLBACK -> MYSQL KHÔNG ĐỔI GÌ")
    ghi("#" * 78)

    db.session.add(ChiTietPhieuNhap(phieu_nhap_id=id_phieu, sach_id=99999, so_luong=150))
    buoc(11, "Thêm 1 dòng chi tiết sai (sách_id không tồn tại)",
         "db.session.add(ChiTietPhieuNhap(..., sach_id=99999, ...))", list(SQL_GHI_DEN),
         "Session cho biết: cần INSERT 1 dòng chi_tiet sai", trang_thai_db(),
         "Chưa INSERT - MySQL chưa biết gì.")

    loi = ""
    try:
        db.session.commit()
    except Exception as ex:
        loi = type(ex).__name__
    buoc(12, "COMMIT - MySQL từ chối, phát sinh IntegrityError",
         "db.session.commit()   ->   except IntegrityError:", list(SQL_GHI_DEN),
         f"Session rỗng, mọi thay đổi bị hủy. Lỗi: {loi}", trang_thai_db(),
         "COMMIT thất bại: INSERT phiếu + INSERT chi tiết + UPDATE tồn đều KHÔNG được ghi.")

    db.session.rollback()
    buoc(13, "ROLLBACK - hủy toàn bộ phần đã làm trong transaction",
         "db.session.rollback()", list(SQL_GHI_DEN),
         "Session quay về trạng thái trước khi bắt đầu", trang_thai_db(),
         "Không còn 'phiếu mao' hay 'tồn kho cộng nhầm'. Đây là lý do phải dùng transaction.")

    # ------------------------------------------------------------------
    ghi("")
    ghi("#" * 78)
    ghi("# DỌN DỮ LIỆU THỬ NGHIỆM - ĐƯA CSDL VỀ ĐÚNG TRẠNG THÁI MẪU")
    ghi("#" * 78)
    SQL_GHI_DEN.clear()
    for ph in PhieuNhap.query.all():
        for ct in ChiTietPhieuNhap.query.filter_by(phieu_nhap_id=ph.id).all():
            s = db.session.get(Sach, ct.sach_id)
            if s:
                s.so_luong_ton -= ct.so_luong
    db.session.commit()
    # Bulk delete: xoá con trước, xoá cha sau (khoá ngoại)
    db.session.execute(db.delete(ChiTietPhieuNhap))
    db.session.execute(db.delete(PhieuNhap))
    db.session.execute(db.delete(ChiTietDonHang))
    db.session.execute(db.delete(DonHang))
    db.session.commit()
    buoc(14, "Xoá chi tiết -> xoá phiếu -> trả tồn kho -> commit",
         "xoa chi_tiet truoc, xoa phieu sau (vi khoa ngoai), tra ton kho",
         list(SQL_GHI_DEN), "Session rỗng", trang_thai_db(),
         "Thứ tự xoá: con trước, cha sau - nếu xoá cha trước MySQL sẽ chặn (lỗi 1451).")

    ghi("")
    ghi("=" * 78)
    ghi("KẾT THÚC - CSDL hiện tại:")
    ghi("=" * 78)
    for ten, model in [("nguoi_dung", NguoiDung), ("quy_dinh", QuyDinh), ("sach", Sach),
                       ("phieu_nhap", PhieuNhap), ("chi_tiet_phieu_nhap", ChiTietPhieuNhap),
                       ("don_hang", DonHang)]:
        ghi(f"  {ten:22} = {model.query.count()} dòng")
    ghi(f"  tồn sách id={id_sach}      = {trang_thai_ton(id_sach)} (trước khi thử: {ton_truoc})")

with io.open(FILE_KET_QUA, "w", encoding="utf-8") as f:
    f.write("\n".join(DONG))
print("OK - xem docs/timeline_transaction_phieu_nhap.txt")

