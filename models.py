"""Các lớp model, khớp từng bảng trong schema.sql (viết theo slide trang 59-64).

- Lớp cơ sở là db.Model, tên bảng đặt bằng __tablename__.
- Cột khai báo bằng Column; khoá ngoại bằng ForeignKey; quan hệ bằng relationship + backref.
- Bảng đã được tạo bởi schema.sql nên KHÔNG gọi db.create_all() (tránh hai nguồn sự thật).
- Thứ tự khai báo lớp quan trọng: lớp được ForeignKey(...) tham chiếu phải khai báo trước.
"""

from flask_login import UserMixin
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash

from extensions import db


class NguoiDung(db.Model, UserMixin):
    __tablename__ = "nguoi_dung"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_dang_nhap = Column(String(50), nullable=False, unique=True)
    mat_khau_hash = Column(String(255), nullable=False)
    ho_ten = Column(String(100), nullable=False)
    vai_tro = Column(
        Enum("KHACH", "NHANVIEN", "QUANLY", "QUANTRI", name="vai_tro"), nullable=False
    )

    def kiem_tra_mat_khau(self, mat_khau):
        """So mật khẩu người dùng gõ với bản băm trong CSDL."""
        return check_password_hash(self.mat_khau_hash, mat_khau)


class QuyDinh(db.Model):
    __tablename__ = "quy_dinh"

    ten = Column(String(50), primary_key=True)
    gia_tri = Column(Integer, nullable=False)
    mo_ta = Column(String(255))

    @staticmethod 
    def lay_gia_tri(ten):
        """Đọc một quy định, ví dụ QuyDinh.lay_gia_tri('nhap_toi_thieu') -> 150."""
        quy_dinh = db.session.get(QuyDinh, ten)
        return quy_dinh.gia_tri if quy_dinh else None


class TheLoai(db.Model):
    __tablename__ = "the_loai"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(100), nullable=False, unique=True)
    # backref tạo thuộc tính sach.the_loai (slide trang 63-64)
    sach = relationship("Sach", backref="the_loai", lazy=True)


class Sach(db.Model):
    __tablename__ = "sach"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_vach = Column(String(13), nullable=False, unique=True)
    ten = Column(String(200), nullable=False)
    the_loai_id = Column(Integer, ForeignKey(TheLoai.id), nullable=False)
    tac_gia = Column(String(100), nullable=False)
    don_gia = Column(Integer, nullable=False)
    so_luong_ton = Column(Integer, nullable=False, default=0)


class PhieuNhap(db.Model):
    __tablename__ = "phieu_nhap"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ngay_nhap = Column(Date, nullable=False)
    nguoi_quan_ly_id = Column(Integer, ForeignKey(NguoiDung.id), nullable=False)

    nguoi_quan_ly = relationship("NguoiDung", backref="phieu_nhap_da_lap")
    chi_tiet = relationship("ChiTietPhieuNhap", backref="phieu_nhap", lazy=True)


class ChiTietPhieuNhap(db.Model):
    __tablename__ = "chi_tiet_phieu_nhap"

    # Khoá chính kép: mỗi sách chỉ xuất hiện một lần trong một phiếu
    phieu_nhap_id = Column(Integer, ForeignKey(PhieuNhap.id), primary_key=True)
    sach_id = Column(Integer, ForeignKey(Sach.id), primary_key=True)
    so_luong = Column(Integer, nullable=False)

    sach = relationship("Sach", backref="chi_tiet_nhap")


class DonHang(db.Model):
    """Dùng chung cho đơn đặt online (kenh = ONLINE) và hoá đơn tại quầy (kenh = QUAY)."""

    __tablename__ = "don_hang"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kenh = Column(Enum("ONLINE", "QUAY", name="kenh"), nullable=False)
    khach_id = Column(Integer, ForeignKey(NguoiDung.id))  # NULL: khách vãng lai ở quầy
    ten_khach = Column(String(100), nullable=False)
    nhan_vien_id = Column(
        Integer, ForeignKey(NguoiDung.id)
    )  # NULL: khách tự trả online
    hinh_thuc_tt = Column(
        Enum("TRUC_TIEP", "ONLINE", name="hinh_thuc_tt"), nullable=False
    )
    trang_thai = Column(
        Enum("CHO_LAY", "HOAN_TAT", "DA_HUY", name="trang_thai"), nullable=False
    )
    ngay_tao = Column(DateTime, nullable=False, server_default=func.now())
    han_lay_sach = Column(DateTime)  # chỉ đơn TRUC_TIEP mới có

    # Hai khoá ngoại cùng trỏ tới nguoi_dung nên phải chỉ rõ foreign_keys
    khach = relationship(
        "NguoiDung", foreign_keys=[khach_id], backref="don_hang_da_dat"
    )
    nhan_vien = relationship(
        "NguoiDung", foreign_keys=[nhan_vien_id], backref="don_hang_da_thanh_toan"
    )
    chi_tiet = relationship("ChiTietDonHang", backref="don_hang", lazy=True)

    def tinh_tong_tien(self):
        """Tổng tiền không lưu trong CSDL, luôn tính từ các dòng chi tiết."""
        return sum(ct.so_luong * ct.don_gia for ct in self.chi_tiet)


class ChiTietDonHang(db.Model):
    __tablename__ = "chi_tiet_don_hang"

    don_hang_id = Column(Integer, ForeignKey(DonHang.id), primary_key=True)
    sach_id = Column(Integer, ForeignKey(Sach.id), primary_key=True)
    so_luong = Column(Integer, nullable=False)
    don_gia = Column(
        Integer, nullable=False
    )  # giá CHỐT lúc bán, không lấy lại từ bảng sach

    sach = relationship("Sach", backref="chi_tiet_ban")
