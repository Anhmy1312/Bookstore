"""Đăng nhập / đăng xuất, phân quyền 4 vai trò.   Người phụ trách: B

Tuần 2 làm:
  - /dang-nhap, /dang-xuat  (so mật khẩu bằng NguoiDung.kiem_tra_mat_khau)
  - hàm/decorator yêu cầu đăng nhập và đúng vai trò: KHACH, NHANVIEN, QUANLY, QUANTRI
Công cụ theo slide: Flask-Login (login_user, logout_user, login_required, current_user),
NguoiDung.query.filter(NguoiDung.ten_dang_nhap == ...) rồi nguoi_dung.kiem_tra_mat_khau(...).
Bảng dùng: nguoi_dung
"""
from flask import Blueprint

bp = Blueprint("auth", __name__)
