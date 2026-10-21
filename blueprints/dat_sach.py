"""Khách hàng đặt sách online (YC2).   Người phụ trách: B

Tuần 2: danh sách sách + giỏ hàng.
Tuần 3: đặt hàng với 2 hình thức thanh toán; đơn TRUC_TIEP có han_lay_sach = ngay_tao + gio_huy_don;
        hàm tự huỷ đơn quá hạn (huỷ + cộng lại tồn) chạy mỗi khi mở trang đơn hàng / báo cáo.
Cùng cả theo slide: from models import ...; Model.query.filter(...); db.session.add/commit;
@login_required; render_template + base.html (extends/block).
Bảng dùng: sach, don_hang, chi_tiet_don_hang, quy_dinh

QUY ĐỊNH (đã chốt, xem PROJECT_CONTEXT.md):
  - Khách đặt online cần tài khoản (vai trò KHACH).
  - Hình thức thanh toán: TRUC_TIEP (trả tại nhà sách) hoặc ONLINE (trả trước, giao miễn phí).
  - Quy định 48 giờ CHỈ áp dụng cho đơn TRUC_TIEP. Đơn thanh toán ONLINE không bao giờ tự huỷ.
  - Trừ tồn kho ngay khi đặt hàng; đơn bị huỷ thì cộng lại tồn.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import DonHang, Sach, TheLoai
from nghiem_vu import (KHOA_GIO_HANG, chi_tiet_gio_hang, huy_don_qua_han, lay_gio_hang,
                       luu_gio_hang, tao_don_hang, tong_tien_gio, xoa_gio_hang)
from quyen import vai_tro_required

bp = Blueprint("dat_sach", __name__, url_prefix="/dat-sach")


@bp.route("/")
@vai_tro_required("KHACH")
def danh_sach_sach():
    """Khách xem danh sách sách (tìm theo tên/tác giả, lọc theo thể loại)."""
    tu_khoa = request.args.get("q", "").strip()
    the_loai_id = request.args.get("the_loai_id", "").strip()

    truy_van = Sach.query.filter(Sach.so_luong_ton > 0)
    if tu_khoa:
        truy_van = truy_van.filter(
            db.or_(Sach.ten.ilike(f"%{tu_khoa}%"), Sach.tac_gia.ilike(f"%{tu_khoa}%"))
        )
    if the_loai_id.isdigit():
        truy_van = truy_van.filter(Sach.the_loai_id == int(the_loai_id))

    sach_list = truy_van.order_by(Sach.ten).all()
    return render_template(
        "dat_sach/danh_sach.html",
        sach_list=sach_list,
        the_loai_list=TheLoai.query.order_by(TheLoai.ten).all(),
        tu_khoa=tu_khoa,
        the_loai_id=the_loai_id,
        gio_hang=lay_gio_hang(KHOA_GIO_HANG),
    )


@bp.route("/gio-hang")
@vai_tro_required("KHACH")
def gio_hang():
    """Xem giỏ hàng của khách."""
    return render_template(
        "dat_sach/gio_hang.html",
        chi_tiet=chi_tiet_gio_hang(KHOA_GIO_HANG),
        tong_tien=tong_tien_gio(KHOA_GIO_HANG),
    )


@bp.route("/gio-hang/them", methods=["POST"])
@vai_tro_required("KHACH")
def them_vao_gio():
    """Thêm sách vào giỏ hàng (kiểm tra tồn kho)."""
    sach_id = request.form.get("sach_id", "").strip()
    so_luong = request.form.get("so_luong", "1").strip()

    if not sach_id.isdigit():
        flash("Sách không hợp lệ.", "danger")
        return redirect(url_for("dat_sach.danh_sach_sach"))
    sach = db.session.get(Sach, int(sach_id))
    if sach is None:
        flash("Sách không tồn tại.", "danger")
        return redirect(url_for("dat_sach.danh_sach_sach"))
    if not so_luong.isdigit() or int(so_luong) <= 0:
        flash("Số lượng phải là số nguyên lớn hơn 0.", "danger")
        return redirect(url_for("dat_sach.danh_sach_sach"))

    gio = lay_gio_hang(KHOA_GIO_HANG)
    so_luong_cu = gio.get(str(sach.id), 0)
    so_luong_moi = so_luong_cu + int(so_luong)

    if so_luong_moi > sach.so_luong_ton:
        flash(
            f"Sách «{sach.ten}» hiện chỉ còn {sach.so_luong_ton} cuốn, không thể đặt {so_luong_moi} cuốn.",
            "danger",
        )
        return redirect(request.referrer or url_for("dat_sach.danh_sach_sach"))

    gio[str(sach.id)] = so_luong_moi
    luu_gio_hang(KHOA_GIO_HANG, gio)
    flash(f"Đã thêm «{sach.ten}» vào giỏ hàng.", "success")
    return redirect(request.referrer or url_for("dat_sach.danh_sach_sach"))


@bp.route("/gio-hang/cap-nhat", methods=["POST"])
@vai_tro_required("KHACH")
def cap_nhat_gio():
    """Đổi số lượng một sách trong giỏ (số lượng = 0 thì xoá khỏi giỏ)."""
    sach_id = request.form.get("sach_id", "").strip()
    so_luong = request.form.get("so_luong", "0").strip()
    gio = lay_gio_hang(KHOA_GIO_HANG)

    if sach_id in gio:
        if not so_luong.isdigit():
            flash("Số lượng phải là số nguyên không âm.", "danger")
        else:
            so_luong = int(so_luong)
            sach = db.session.get(Sach, int(sach_id))
            if so_luong == 0:
                gio.pop(sach_id)
                flash("Đã xoá sách khỏi giỏ hàng.", "info")
            elif sach is not None and so_luong > sach.so_luong_ton:
                flash(
                    f"Sách «{sach.ten}» hiện chỉ còn {sach.so_luong_ton} cuốn.",
                    "danger",
                )
            else:
                gio[sach_id] = so_luong
                flash("Đã cập nhật giỏ hàng.", "success")
            luu_gio_hang(KHOA_GIO_HANG, gio)

    return redirect(url_for("dat_sach.gio_hang"))


@bp.route("/gio-hang/xoa", methods=["POST"])
@vai_tro_required("KHACH")
def xoa_vao_gio():
    """Xoá một sách khỏi giỏ hàng."""
    sach_id = request.form.get("sach_id", "").strip()
    gio = lay_gio_hang(KHOA_GIO_HANG)
    if sach_id in gio:
        gio.pop(sach_id)
        luu_gio_hang(KHOA_GIO_HANG, gio)
        flash("Đã xoá sách khỏi giỏ hàng.", "info")
    return redirect(url_for("dat_sach.gio_hang"))


@bp.route("/dat-hang", methods=["GET", "POST"])
@vai_tro_required("KHACH")
def dat_hang():
    """Đặt sách: chọn hình thức thanh toán rồi xác nhận đơn."""
    chi_tiet = chi_tiet_gio_hang(KHOA_GIO_HANG)

    if request.method == "POST":
        hinh_thuc = request.form.get("hinh_thuc_tt", "TRUC_TIEP")
        if hinh_thuc not in ("TRUC_TIEP", "ONLINE"):
            hinh_thuc = "TRUC_TIEP"

        don, loi = tao_don_hang(
            kenh="ONLINE",
            khach_id=current_user.id,
            ten_khach=current_user.ho_ten,
            nhan_vien_id=None,
            hinh_thuc_tt=hinh_thuc,
            chi_tiet=chi_tiet,
        )
        if loi:
            flash(loi, "danger")
        else:
            xoa_gio_hang(KHOA_GIO_HANG)
            if hinh_thuc == "TRUC_TIEP":
                flash(
                    f"Đã đặt sách (đơn #{don.id}). Hãy đến nhà sách trong vòng "
                    f"{don.han_lay_sach.strftime('%H:%M %d/%m')} để lấy sách và thanh toán.",
                    "success",
                )
            else:
                flash(
                    f"Đã thanh toán online (đơn #{don.id}). Hệ thống sẽ giao hàng miễn phí cho bạn.",
                    "success",
                )
            return redirect(url_for("dat_sach.don_hang_cua_toi"))

    return render_template("dat_sach/dat_hang.html", chi_tiet=chi_tiet,
                           tong_tien=tong_tien_gio(KHOA_GIO_HANG))


@bp.route("/don-hang")
@vai_tro_required("KHACH")
def don_hang_cua_toi():
    """Danh sách đơn hàng của khách (tự huỷ đơn quá hạn trước khi hiển thị)."""
    so_don_huy = huy_don_qua_han()
    if so_don_huy:
        flash(f"{so_don_huy} đơn quá hạn đã bị huỷ tự động.", "info")

    don_hangs = (
        DonHang.query.filter_by(khach_id=current_user.id)
        .order_by(DonHang.ngay_tao.desc())
        .all()
    )
    return render_template("dat_sach/don_hang.html", don_hangs=don_hangs)


@bp.route("/don-hang/<int:don_hang_id>")
@vai_tro_required("KHACH")
def chi_tiet_don_hang(don_hang_id):
    """Xem chi tiết một đơn hàng của mình."""
    huy_don_qua_han()
    don = db.session.get(DonHang, don_hang_id)
    if don is None or don.khach_id != current_user.id:
        flash("Không tìm thấy đơn hàng.", "danger")
        return redirect(url_for("dat_sach.don_hang_cua_toi"))
    return render_template("dat_sach/chi_tiet_don_hang.html", don=don)


@bp.route("/don-hang/<int:don_hang_id>/huy", methods=["POST"])
@vai_tro_required("KHACH")
def huy_don(don_hang_id):
    """Khách huỷ đơn của mình khi còn ở trạng thái CHO_LAY (tồn kho được trả lại)."""
    huy_don_qua_han()
    don = db.session.get(DonHang, don_hang_id)
    if don is None or don.khach_id != current_user.id:
        flash("Không tìm thấy đơn hàng.", "danger")
        return redirect(url_for("dat_sach.don_hang_cua_toi"))
    if don.trang_thai != "CHO_LAY":
        flash("Chỉ huỷ được đơn đang chờ lấy sách.", "danger")
        return redirect(url_for("dat_sach.don_hang_cua_toi"))

    for ct in don.chi_tiet:
        sach = db.session.get(Sach, ct.sach_id)
        if sach is not None:
            sach.so_luong_ton += ct.so_luong
    don.trang_thai = "DA_HUY"
    db.session.commit()
    flash("Đã huỷ đơn hàng.", "info")
    return redirect(url_for("dat_sach.don_hang_cua_toi"))
