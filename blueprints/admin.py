"""Nguoi quan tri: thong ke bao cao (YC4) + thay doi quy dinh (YC5).   Nguoi phu trich: A

Tuần 2: trang sửa quy định (nhap_toi_thieu, nguong_ton_de_nhap, gio_huy_don).
Tuần 3: 2 báo cáo theo tháng (bảng + Chart.js). Chỉ tính don trang_thai = 'HOAN_TAT'.
Cùng cả theo slide: from models import ...; Model.query.filter(...); db.session.add/commit;
@login_required; render_template + base.html (extends/block).
Bảng dùng: quy_dinh, don_hang, chi_tiet_don_hang, sach, the_loai

GHI CHÚ CỦA A (20/10): tuần 2 mới làm phần quy định. Phần báo cáo (UC07) để tuần 3.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from extensions import db
from models import QuyDinh
from quyen import vai_tro_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/quy-dinh", methods=["GET", "POST"])
@vai_tro_required("QUANTRI")
def quy_dinh():
    """Xem và sửa 3 quy định của hệ thống (YC5).

    Sửa ở đây thì code nhập sách/bán sách đặt hàng tự động dùng giá trị mới,
    vì các quy định được đọc từ bảng `quy_dinh` chứ không viết cứng trong code.
    """
    quy_dinh_list = QuyDinh.query.order_by(QuyDinh.ten).all()

    if request.method == "POST":
        loi = []
        gia_tri_moi = {}
        for quy_dinh in quy_dinh_list:
            gia_tri = request.form.get(quy_dinh.ten, "").strip()
            if not gia_tri.isdigit():
                loi.append(f"Giá trị của «{quy_dinh.ten}» phải là số nguyên không âm.")
                continue
            gia_tri_moi[quy_dinh.ten] = int(gia_tri)

        if loi:
            for dong_loi in loi:
                flash(dong_loi, "danger")
        else:
            for quy_dinh in quy_dinh_list:
                quy_dinh.gia_tri = gia_tri_moi[quy_dinh.ten]
            db.session.commit()
            flash("Đã cập nhật quy định của hệ thống.", "success")
            return redirect(url_for("admin.quy_dinh"))

    return render_template("admin/quy_dinh.html", quy_dinh_list=quy_dinh_list)
