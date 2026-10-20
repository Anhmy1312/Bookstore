"""Khách hàng đặt sách online (YC2).   Người phụ trách: B

Tuần 2: danh sách sách + giỏ hàng.
Tuần 3: đặt hàng với 2 hình thức thanh toán; đơn TRUC_TIEP có han_lay_sach = ngay_tao + gio_huy_don;
        hàm tự huỷ đơn quá hạn (và cộng lại tồn) chạy mỗi khi mở trang đơn hàng / báo cáo.
Công cụ theo slide: from models import ...; Model.query.filter(...); db.session.add/commit;
@login_required; render_template + base.html (extends/block).
Bảng dùng: sach, don_hang, chi_tiet_don_hang, quy_dinh
"""
from flask import Blueprint

bp = Blueprint("dat_sach", __name__, url_prefix="/dat-sach")
