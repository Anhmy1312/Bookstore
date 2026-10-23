"""Nguoi quan tri: thong ke bao cao (YC4) + thay doi quy dinh (YC5).   Nguoi phu trich: A

Tuần 2: trang sua quy dinh.
Tuần 3: 2 bao cao theo thang (bang + Chart.js). Chi tinh don trang_thai = 'HOAN_TAT'.
Cung ca theo slide: from models import ...; Model.query.filter(...); db.session.add/commit;
@login_required; render_template + base.html (extends/block).
Bang dung: quy_dinh, don_hang, chi_tiet_don_hang, sach, the_loai

GHI CHU CUA A (20/10): tuan 2 moi lam phan quy dinh. Phuan bao cao (UC07) de tuan 3.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import extract, func

from extensions import db
from models import TheLoai, Sach, NguoiDung, DonHang, ChiTietDonHang, QuyDinh
from quyen import vai_tro_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/quy-dinh", methods=["GET", "POST"])
@vai_tro_required("QUANTRI")
def quy_dinh():
    """Xem va sua 3 quy dinh he thong (YC5).

    Sua o day thi code nhap sach/ban sach dat hang tu dong dung gia tri moi,
    vi cac quy dinh duoc doc tu bang `quy_dinh` chong khong viet cung trong code.
    """
    quy_dinh_list = QuyDinh.query.order_by(QuyDinh.ten).all()

    if request.method == "POST":
        loi = []
        gia_tri_moi = {}
        for quy_dinh in quy_dinh_list:
            gia_tri = request.form.get(quy_dinh.ten, "").strip()
            if not gia_tri.isdigit():
                loi.append(f"Gia tri cua «{quy_dinh.ten}» phai la so nguyen khong am.")
                continue
            gia_tri_moi[quy_dinh.ten] = int(gia_tri)

        if loi:
            for dong_loi in loi:
                flash(dong_loi, "danger")
        else:
            for quy_dinh in quy_dinh_list:
                quy_dinh.gia_tri = gia_tri_moi[quy_dinh.ten]
            db.session.commit()
            flash("Da cap nhat quy dinh he thong.", "success")
            return redirect(url_for("admin.quy_dinh"))

    return render_template("admin/quy_dinh.html", quy_dinh_list=quy_dinh_list)


# =====================================================================
# TUAN 3 - BAO CAO THONG KE (YC4)
# Quy tac vang:
#   - Chi tinh don trang_thai = 'HOAN_TAT'
#   - Theo thang cua ngay_tao
#   - Dung don_gia da chot trong chi_tiet_don_hang (KHONG lay lai tu bang sach)
# =====================================================================


def _parse_thang(thang_str):
    """Chuyen chuoi 'YYYY-MM' thanh (nam, thang). Neu khong co -> thang hien tai."""
    from datetime import datetime

    if not thang_str:
        now = datetime.now()
        return now.year, now.month
    try:
        nam, thang = map(int, thang_str.split("-"))
        return nam, thang
    except (ValueError, AttributeError):
        now = datetime.now()
        return now.year, now.month


def _tong_doanh_thu_thang(nam, thang):
    """Tong doanh thu cua thang (chi don HOAN_TAT, tinh theo don_gia da chot)."""
    tong = (
        db.session.query(func.sum(ChiTietDonHang.so_luong * ChiTietDonHang.don_gia))
        .select_from(ChiTietDonHang)
        .join(DonHang, ChiTietDonHang.don_hang_id == DonHang.id)
        .filter(DonHang.trang_thai == "HOAN_TAT")
        .filter(extract("year", DonHang.ngay_tao) == nam)
        .filter(extract("month", DonHang.ngay_tao) == thang)
        .scalar()
    )
    return float(tong or 0)


@bp.route("/bao-cao")
@vai_tro_required("QUANTRI")
def thong_ke():
    """Trang chua bao cao: chon thang, hien tong quan (tong doanh thu, tong don, tong sach ban)."""
    from datetime import datetime

    nam, thang = _parse_thang(request.args.get("thang"))

    tong_doanh_thu = _tong_doanh_thu_thang(nam, thang)

    tong_don = (
        db.session.query(func.count(DonHang.id))
        .filter(DonHang.trang_thai == "HOAN_TAT")
        .filter(extract("year", DonHang.ngay_tao) == nam)
        .filter(extract("month", DonHang.ngay_tao) == thang)
        .scalar()
    )
    tong_don = int(tong_don or 0)

    tong_so_luong = (
        db.session.query(func.sum(ChiTietDonHang.so_luong))
        .select_from(ChiTietDonHang)
        .join(DonHang, ChiTietDonHang.don_hang_id == DonHang.id)
        .filter(DonHang.trang_thai == "HOAN_TAT")
        .filter(extract("year", DonHang.ngay_tao) == nam)
        .filter(extract("month", DonHang.ngay_tao) == thang)
        .scalar()
    )
    tong_so_luong = int(tong_so_luong or 0)

    return render_template(
        "admin/bao_cao.html",
        nam=nam,
        thang=thang,
        tong_doanh_thu=tong_doanh_thu,
        tong_don=tong_don,
        tong_so_luong=tong_so_luong,
    )


@bp.route("/bao-cao/doanh-thu-the-loai")
@vai_tro_required("QUANTRI")
def thong_ke_doanh_thu_the_loai():
    """Bao cao doanh thu theo thang cho tung the loai (chi don HOAN_TAT)."""
    from datetime import datetime

    nam, thang = _parse_thang(request.args.get("thang"))

    tong_doanh_thu = _tong_doanh_thu_thang(nam, thang)

    q = (
        db.session.query(
            TheLoai.ten.label("ten_the_loai"),
            func.count(DonHang.id.distinct()).label("so_don"),
            func.sum(ChiTietDonHang.so_luong).label("so_luong_ban"),
            func.sum(ChiTietDonHang.so_luong * ChiTietDonHang.don_gia).label("doanh_thu"),
        )
        .select_from(ChiTietDonHang)
        .join(DonHang, ChiTietDonHang.don_hang_id == DonHang.id)
        .join(Sach, ChiTietDonHang.sach_id == Sach.id)
        .join(TheLoai, Sach.the_loai_id == TheLoai.id)
        .filter(DonHang.trang_thai == "HOAN_TAT")
        .filter(extract("year", DonHang.ngay_tao) == nam)
        .filter(extract("month", DonHang.ngay_tao) == thang)
        .group_by(TheLoai.id, TheLoai.ten)
        .order_by(func.sum(ChiTietDonHang.so_luong * ChiTietDonHang.don_gia).desc())
    )
    stats = q.all()

    # Tinh ty le
    du_lieu = []
    for row in stats:
        doanh_thu = float(row.doanh_thu or 0)
        ty_le = (doanh_thu / tong_doanh_thu * 100) if tong_doanh_thu else 0
        du_lieu.append(
            {
                "ten_the_loai": row.ten_the_loai,
                "so_don": int(row.so_don or 0),
                "so_luong_ban": int(row.so_luong_ban or 0),
                "doanh_thu": doanh_thu,
                "ty_le": round(ty_le, 2),
            }
        )

    return render_template(
        "admin/bao_cao_doanh_thu_the_loai.html",
        nam=nam,
        thang=thang,
        stats=du_lieu,
        tong_doanh_thu=tong_doanh_thu,
        tong_so_luong_ban=sum(d["so_luong_ban"] for d in du_lieu),
        chart_labels=[d["ten_the_loai"] for d in du_lieu],
        chart_values=[float(d["doanh_thu"]) for d in du_lieu],
    )


@bp.route("/bao-cao/tan-suat-sach")
@vai_tro_required("QUANTRI")
def thong_ke_tan_suat_sach():
    """Bao cao tan suat ban sach theo thang (chi don HOAN_TAT)."""
    from datetime import datetime

    nam, thang = _parse_thang(request.args.get("thang"))

    tong_so_luong = (
        db.session.query(func.sum(ChiTietDonHang.so_luong))
        .select_from(ChiTietDonHang)
        .join(DonHang, ChiTietDonHang.don_hang_id == DonHang.id)
        .filter(DonHang.trang_thai == "HOAN_TAT")
        .filter(extract("year", DonHang.ngay_tao) == nam)
        .filter(extract("month", DonHang.ngay_tao) == thang)
        .scalar()
    )
    tong_so_luong = int(tong_so_luong or 0)

    q = (
        db.session.query(
            Sach.ten.label("ten_sach"),
            TheLoai.ten.label("ten_the_loai"),
            func.sum(ChiTietDonHang.so_luong).label("so_luong_ban"),
        )
        .select_from(ChiTietDonHang)
        .join(Sach, ChiTietDonHang.sach_id == Sach.id)
        .join(DonHang, ChiTietDonHang.don_hang_id == DonHang.id)
        .join(TheLoai, Sach.the_loai_id == TheLoai.id)
        .filter(DonHang.trang_thai == "HOAN_TAT")
        .filter(extract("year", DonHang.ngay_tao) == nam)
        .filter(extract("month", DonHang.ngay_tao) == thang)
        .group_by(Sach.id, Sach.ten, TheLoai.id, TheLoai.ten)
        .order_by(func.sum(ChiTietDonHang.so_luong).desc())
    )
    stats = q.all()

    du_lieu = []
    for row in stats:
        so_luong_ban = int(row.so_luong_ban or 0)
        ty_le = (so_luong_ban / tong_so_luong * 100) if tong_so_luong else 0
        du_lieu.append(
            {
                "ten_sach": row.ten_sach,
                "ten_the_loai": row.ten_the_loai,
                "so_luong_ban": so_luong_ban,
                "ty_le": round(ty_le, 2),
            }
        )

    return render_template(
        "admin/bao_cao_tan_suat_sach.html",
        nam=nam,
        thang=thang,
        stats=du_lieu,
        tong_so_luong=tong_so_luong,
        chart_labels=[d["ten_sach"] for d in du_lieu],
        chart_values=[int(d["so_luong_ban"]) for d in du_lieu],
    )
