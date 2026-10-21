"""Nhân viên bán tại quầy (YC3), xác nhận khách lấy sách + thu tiền đơn TRUC_TIEP (YC2).   Người phụ trách: B

Tuần 2: bán tại quầy (nhập/quét ma_vach), lưu hoá đơn kenh = 'QUAY', trừ tồn, chốt don_gia.
Tuần 3: xác nhận khách lấy sách + thu tiền (đơn CHO_LAY -> HOAN_TAT), danh sách đơn chờ lấy.
Cùng cả theo slide: from models import ...; Model.query.filter(...); db.session.add/commit;
@login_required; render_template + base.html (extends/block).
Bảng dùng: sach, don_hang, chi_tiet_don_hang

QUY ƯỚC:
  - Đơn tại quầy: kenh = 'QUAY', hinh_thuc_tt = 'TRUC_TIEP', trang_thai = 'HOAN_TAT' ngay
    (khách đã thanh toán tại quầy), khach_id = NULL vì có thể là khách vãng lai.
  - don_gia lấy từ sach.don_gia tại thời điểm bán rồi CHỐT vào chi_tiet_don_hang.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from extensions import db
from models import DonHang, Sach
from nghiem_vu import (KHOA_GIO_QUAY, chi_tiet_gio_hang, huy_don_qua_han, lay_gio_hang,
                       luu_gio_hang, tao_don_hang, tong_tien_gio, xoa_gio_hang)
from quyen import vai_tro_required

bp = Blueprint("ban_hang", __name__, url_prefix="/ban-hang")


@bp.route("/", methods=["GET", "POST"])
@vai_tro_required("NHANVIEN")
def ban_tai_quay():
    """Màn bán hàng tại quầy: quét mã vạch / chọn sách, giỏ hàng, thanh toán."""
    loi = None
    if request.method == "POST":
        hanh_dong = request.form.get("hanh_dong", "")
        if hanh_dong == "them":
            loi = them_vao_gio_quay()
        elif hanh_dong == "cap_nhat":
            loi = cap_nhat_gio_quay()
        elif hanh_dong == "xoa":
            xoa_gio_quay()
        elif hanh_dong == "thanh_toan":
            return thanh_toan()

    return render_template(
        "ban_hang/ban_hang.html",
        chi_tiet=chi_tiet_gio_hang(KHOA_GIO_QUAY),
        tong_tien=tong_tien_gio(KHOA_GIO_QUAY),
        loi=loi,
        sach_list=Sach.query.filter(Sach.so_luong_ton > 0).order_by(Sach.ten).all(),
    )


def them_vao_gio_quay():
    """Thêm sách vào giỏ quầy bằng mã vạch (dùng máy quét mã vạch) hoặc chọn từ danh sách."""
    ma_vach = request.form.get("ma_vach", "").strip()
    sach_id = request.form.get("sach_id", "").strip()
    so_luong = request.form.get("so_luong", "1").strip()

    sach = None
    if ma_vach:
        sach = Sach.query.filter(Sach.ma_vach == ma_vach).first()
        if sach is None:
            return f"Không tìm thấy sách có mã vạch {ma_vach}."
    elif sach_id.isdigit():
        sach = db.session.get(Sach, int(sach_id))
        if sach is None:
            return "Sách không tồn tại."

    if sach is None:
        return "Hãy nhập mã vạch hoặc chọn sách."
    if not so_luong.isdigit() or int(so_luong) <= 0:
        return "Số lượng phải là số nguyên lớn hơn 0."

    gio = lay_gio_hang(KHOA_GIO_QUAY)
    so_luong_moi = gio.get(str(sach.id), 0) + int(so_luong)
    if so_luong_moi > sach.so_luong_ton:
        return f"Sách «{sach.ten}» hiện chỉ còn {sach.so_luong_ton} cuốn."

    gio[str(sach.id)] = so_luong_moi
    luu_gio_hang(KHOA_GIO_QUAY, gio)
    return ""


def cap_nhat_gio_quay():
    """Đổi số lượng trong giỏ quầy (0 = xoá)."""
    sach_id = request.form.get("sach_id", "").strip()
    so_luong = request.form.get("so_luong", "0").strip()
    gio = lay_gio_hang(KHOA_GIO_QUAY)
    if sach_id in gio and so_luong.isdigit():
        so_luong = int(so_luong)
        if so_luong == 0:
            gio.pop(sach_id)
        else:
            sach = db.session.get(Sach, int(sach_id))
            if sach is not None and so_luong > sach.so_luong_ton:
                return f"Sách «{sach.ten}» hiện chỉ còn {sach.so_luong_ton} cuốn."
            gio[sach_id] = so_luong
        luu_gio_hang(KHOA_GIO_QUAY, gio)
    return ""


def xoa_gio_quay():
    """Xoá một sách khỏi giỏ quầy."""
    sach_id = request.form.get("sach_id", "").strip()
    gio = lay_gio_hang(KHOA_GIO_QUAY)
    if sach_id in gio:
        gio.pop(sach_id)
        luu_gio_hang(KHOA_GIO_QUAY, gio)
    return ""


def thanh_toan():
    """Chốt hoá đơn tại quầy: lưu đơn QUAY + chi tiết, trừ tồn, xoá giỏ."""
    ten_khach = request.form.get("ten_khach", "").strip() or "Khách vãng lai"
    chi_tiet = chi_tiet_gio_hang(KHOA_GIO_QUAY)

    don, loi = tao_don_hang(
        kenh="QUAY",
        khach_id=None,                      # khách vãng lai -> khach_id NULL
        ten_khach=ten_khach,
        nhan_vien_id=current_user.id,       # nhân viên thanh toán
        hinh_thuc_tt="TRUC_TIEP",
        chi_tiet=chi_tiet,
    )
    if loi:
        flash(loi, "danger")
        return redirect(url_for("ban_hang.ban_tai_quay"))

    xoa_gio_hang(KHOA_GIO_QUAY)
    flash(f"Đã lập hoá đơn #{don.id}.", "success")
    return redirect(url_for("ban_hang.hoa_don", don_hang_id=don.id))


@bp.route("/hoa-don/<int:don_hang_id>")
@vai_tro_required("NHANVIEN", "QUANTRI", "QUANLY")
def hoa_don(don_hang_id):
    """Xem hoá đơn (nhân viên vừa lập hoặc quản lý/quản trị xem lại)."""
    don = db.session.get(DonHang, don_hang_id)
    if don is None:
        flash("Không tìm thấy hoá đơn.", "danger")
        return redirect(url_for("ban_hang.ban_tai_quay"))
    return render_template("ban_hang/hoa_don.html", don=don)


@bp.route("/don-cho-lay")
@vai_tro_required("NHANVIEN")
def don_cho_lay():
    """Danh sách đơn khách đặt online đang chờ lấy sách (đã tự huỷ đơn quá hạn)."""
    so_don_huy = huy_don_qua_han()
    if so_don_huy:
        flash(f"{so_don_huy} đơn quá hạn đã bị huỷ tự động.", "info")

    don_hangs = (
        DonHang.query.filter_by(trang_thai="CHO_LAY").order_by(DonHang.han_lay_sach).all()
    )
    return render_template("ban_hang/don_cho_lay.html", don_hangs=don_hangs)


@bp.route("/don-cho-lay/<int:don_hang_id>/xac-nhan", methods=["POST"])
@vai_tro_required("NHANVIEN")
def xac_nhan_lay_sach(don_hang_id):
    """UC04: khách đến lấy sách, nhân viên xác nhận và thu tiền -> đơn HOAN_TAT."""
    huy_don_qua_han()
    don = db.session.get(DonHang, don_hang_id)
    if don is None or don.trang_thai != "CHO_LAY":
        flash("Đơn hàng không còn ở trạng thái chờ lấy sách.", "danger")
        return redirect(url_for("ban_hang.don_cho_lay"))

    don.nhan_vien_id = current_user.id   # nhân viên thu tiền
    don.trang_thai = "HOAN_TAT"
    db.session.commit()
    flash(f"Đã xác nhận lấy sách và thu tiền cho đơn #{don.id}.", "success")
    return redirect(url_for("ban_hang.hoa_don", don_hang_id=don.id))
