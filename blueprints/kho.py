"""Người quản lý (quản lý kho): lập phiếu nhập (YC1) + quản lý sách (YC5).   Người phụ trách: A

Tuần 2 làm:
  - /kho/sach          : danh sách, thêm, sửa, xoá, tìm kiếm sách
  - /kho/phieu-nhap    : lập phiếu nhập; đọc quy_dinh (nhap_toi_thieu, nguong_ton_de_nhap)
                         rồi kiểm tra từng dòng; hợp lệ mới lưu + cộng so_luong_ton
Công cụ theo slide: from models import ...; Model.query.filter(...); db.session.add/commit;
@login_required; render_template + base.html (extends/block).
Bảng dùng: sach, the_loai, phieu_nhap, chi_tiet_phieu_nhap, quy_dinh
"""
from flask import Blueprint

bp = Blueprint("kho", __name__, url_prefix="/kho")
