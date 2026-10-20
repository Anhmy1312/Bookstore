"""Nhân viên bán tại quầy (YC3), xác nhận khách lấy sách + thu tiền đơn TRUC_TIEP (YC2).   Người phụ trách: B

Tuần 2: bán tại quầy (nhập/quét ma_vach), lưu hoá đơn kenh = 'QUAY', trừ tồn, chốt don_gia.
Công cụ theo slide: from models import ...; Model.query.filter(...); db.session.add/commit;
@login_required; render_template + base.html (extends/block).
Bảng dùng: sach, don_hang, chi_tiet_don_hang
"""
from flask import Blueprint

bp = Blueprint("ban_hang", __name__, url_prefix="/ban-hang")
