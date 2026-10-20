"""Người quản trị: thống kê báo cáo (YC4) + thay đổi quy định (YC5).   Người phụ trách: A

Tuần 2: trang sửa quy định (nhap_toi_thieu, nguong_ton_de_nhap, gio_huy_don).
Tuần 3: 2 báo cáo theo tháng (bảng + Chart.js). Chỉ tính đơn trang_thai = 'HOAN_TAT'.
Công cụ theo slide: from models import ...; Model.query.filter(...); db.session.add/commit;
@login_required; render_template + base.html (extends/block).
Bảng dùng: quy_dinh, don_hang, chi_tiet_don_hang, sach, the_loai
"""
from flask import Blueprint

bp = Blueprint("admin", __name__, url_prefix="/admin")
