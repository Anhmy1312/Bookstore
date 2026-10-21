"""Nguoi quan ly (quan ly kho): lap phieu nhap (YC1) + quan ly sach (YC5).   Nguoi phu trich: A

Tuần 2 làm:
  - /kho/sach          : danh sách, thêm, sửa, xoá, tìm kiếm sách
  - /kho/phieu-nhap    : lập phiếu nhập; đọc quy_dinh (nhap_toi_thieu, nguong_ton_de_nhap)
                         rồi kiểm tra từng dòng; hợp lệ mới lưu + cộng so_luong_ton
Cùng cả theo slide: from models import ...; Model.query.filter(...); db.session.add/commit;
@login_required; render_template + base.html (extends/block).
Bảng dùng: sach, the_loai, phieu_nhap, chi_tiet_phieu_nhap, quy_dinh

LUẬT NGHIỆP VỤ (kiểm tra trong code, KHÔNG viết cứng số 150/300):
  - Mỗi dòng phiếu nhập phải có so_luong >= quy_dinh.nhap_toi_thieu
  - Chỉ được nhập đầu sách có so_luong_ton < quy_dinh.nguong_ton_de_nhap
"""
from datetime import date

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import (ChiTietDonHang, ChiTietPhieuNhap, PhieuNhap, QuyDinh, Sach, TheLoai)
from quyen import vai_tro_required

bp = Blueprint("kho", __name__, url_prefix="/kho")


# ======================================================================
# QUẢN LÝ SÁCH (YC5)
# ======================================================================
@bp.route("/sach")
@vai_tro_required("QUANLY")
def danh_sach_sach():
    """Danh sách sách + tìm kiếm theo tên/mã vạch và lọc theo thể loại."""
    tu_khoa = request.args.get("q", "").strip()
    the_loai_id = request.args.get("the_loai_id", "").strip()

    truy_van = Sach.query
    if tu_khoa:
        truy_van = truy_van.filter(
            db.or_(
                Sach.ten.ilike(f"%{tu_khoa}%"),
                Sach.ma_vach.ilike(f"%{tu_khoa}%"),
                Sach.tac_gia.ilike(f"%{tu_khoa}%"),
            )
        )
    if the_loai_id.isdigit():
        truy_van = truy_van.filter(Sach.the_loai_id == int(the_loai_id))

    sach_list = truy_van.order_by(Sach.id).all()
    return render_template(
        "kho/sach_danh_sach.html",
        sach_list=sach_list,
        the_loai_list=TheLoai.query.order_by(TheLoai.ten).all(),
        tu_khoa=tu_khoa,
        the_loai_id=the_loai_id,
    )


@bp.route("/sach/them", methods=["GET", "POST"])
@vai_tro_required("QUANLY")
def them_sach():
    """Thêm đầu sách mới."""
    if request.method == "POST":
        ten = request.form.get("ten", "").strip()
        ma_vach = request.form.get("ma_vach", "").strip()
        tac_gia = request.form.get("tac_gia", "").strip()
        the_loai_id = request.form.get("the_loai_id", "").strip()
        don_gia = request.form.get("don_gia", "").strip()
        so_luong_ton = request.form.get("so_luong_ton", "0").strip()

        loi = kiem_tra_thong_tin_sach(ten, ma_vach, tac_gia, the_loai_id, don_gia, so_luong_ton)
        if loi:
            flash(loi, "danger")
        else:
            sach = Sach(
                ten=ten,
                ma_vach=ma_vach,
                tac_gia=tac_gia,
                the_loai_id=int(the_loai_id),
                don_gia=int(don_gia),
                so_luong_ton=int(so_luong_ton),
            )
            try:
                db.session.add(sach)
                db.session.commit()
                flash(f"Đã thêm sách «{ten}».", "success")
                return redirect(url_for("kho.danh_sach_sach"))
            except IntegrityError:
                db.session.rollback()
                flash("Mã vạch đã tồn tại, vui lòng dùng mã khác.", "danger")

    return render_template(
        "kho/sach_form.html",
        sach=None,
        the_loai_list=TheLoai.query.order_by(TheLoai.ten).all(),
    )


@bp.route("/sach/<int:sach_id>/sua", methods=["GET", "POST"])
@vai_tro_required("QUANLY")
def sua_sach(sach_id):
    """Sửa thông tin đầu sách (không cho sửa số lượng tồn - tồn chỉ đổi qua phiếu nhập/bán)."""
    sach = db.session.get(Sach, sach_id)
    if sach is None:
        flash("Không tìm thấy sách cần sửa.", "danger")
        return redirect(url_for("kho.danh_sach_sach"))

    if request.method == "POST":
        ten = request.form.get("ten", "").strip()
        ma_vach = request.form.get("ma_vach", "").strip()
        tac_gia = request.form.get("tac_gia", "").strip()
        the_loai_id = request.form.get("the_loai_id", "").strip()
        don_gia = request.form.get("don_gia", "").strip()

        loi = kiem_tra_thong_tin_sach(ten, ma_vach, tac_gia, the_loai_id, don_gia, "0", sach)
        if loi:
            flash(loi, "danger")
        else:
            sach.ten = ten
            sach.ma_vach = ma_vach
            sach.tac_gia = tac_gia
            sach.the_loai_id = int(the_loai_id)
            sach.don_gia = int(don_gia)
            try:
                db.session.commit()
                flash(f"Đã cập nhật sách «{ten}».", "success")
                return redirect(url_for("kho.danh_sach_sach"))
            except IntegrityError:
                db.session.rollback()
                flash("Mã vạch đã tồn tại, vui lòng dùng mã khác.", "danger")

    return render_template(
        "kho/sach_form.html",
        sach=sach,
        the_loai_list=TheLoai.query.order_by(TheLoai.ten).all(),
    )


@bp.route("/sach/<int:sach_id>/xoa", methods=["POST"])
@vai_tro_required("QUANLY")
def xoa_sach(sach_id):
    """Xoá sách. Sách đã có giao dịch (phiếu nhập/đơn hàng) thì không xoá được."""
    sach = db.session.get(Sach, sach_id)
    if sach is None:
        flash("Không tìm thấy sách cần xoá.", "danger")
        return redirect(url_for("kho.danh_sach_sach"))

    ten_sach = sach.ten

    # Kiểm tra sách đã có giao dịch chưa, để báo đúng lý do thay vì để MySQL lỗi 1451
    da_nhap = db.session.query(ChiTietPhieuNhap).filter_by(sach_id=sach_id).first()
    da_ban = db.session.query(ChiTietDonHang).filter_by(sach_id=sach_id).first()
    if da_nhap is not None or da_ban is not None:
        flash("Sách đã có giao dịch, không thể xoá.", "danger")
        return redirect(url_for("kho.danh_sach_sach"))

    try:
        # Dùng xoá hàng loạt (bulk delete) để SQLAlchemy không tự xoá trắng khoá ngoại
        db.session.execute(db.delete(Sach).where(Sach.id == sach_id))
        db.session.commit()
        flash(f"Đã xoá sách «{ten_sach}».", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Sách đã có giao dịch, không thể xoá.", "danger")
    return redirect(url_for("kho.danh_sach_sach"))


def kiem_tra_thong_tin_sach(ten, ma_vach, tac_gia, the_loai_id, don_gia, so_luong_ton, sach=None):
    """Kiểm tra dữ liệu form sách. Trả về chuỗi lỗi, rỗng nghĩa là hợp lệ."""
    if not ten or not ma_vach or not tac_gia:
        return "Phải nhập đầy đủ tên sách, mã vạch và tác giả."
    if not the_loai_id.isdigit() or db.session.get(TheLoai, int(the_loai_id)) is None:
        return "Thể loại không hợp lệ."
    if not don_gia.isdigit() or int(don_gia) < 0:
        return "Đơn giá phải là số không nhỏ hơn 0."
    if so_luong_ton and (not so_luong_ton.isdigit() or int(so_luong_ton) < 0):
        return "Số lượng tồn phải là số không nhỏ hơn 0."
    # Mã vạch phải duy nhất (nếu đang sửa thì trừ chính sách đang sửa ra)
    truy_van = db.session.query(Sach).filter(Sach.ma_vach == ma_vach)
    if sach is not None:
        truy_van = truy_van.filter(Sach.id != sach.id)
    if truy_van.first() is not None:
        return "Mã vạch đã tồn tại, vui lòng dùng mã khác."
    return ""


# ======================================================================
# LẬP PHIẾU NHẬP SÁCH (YC1)
# ======================================================================
@bp.route("/phieu-nhap", methods=["GET", "POST"])
@vai_tro_required("QUANLY")
def phieu_nhap():
    """Lập phiếu nhập: ngày nhập + các dòng (sách, số lượng).

    Luật (đọc từ bảng quy_dinh để YC5 sửa được từ giao diện):
      1. mỗi dòng số lượng >= nhap_toi_thieu
      2. chỉ được nhập đầu sách có tồn hiện tại < nguong_ton_de_nhap
    """
    so_luong_toi_thieu = QuyDinh.lay_gia_tri("nhap_toi_thieu") or 0
    nguong_ton = QuyDinh.lay_gia_tri("nguong_ton_de_nhap")
    loi = None

    if request.method == "POST":
        ngay_nhap = request.form.get("ngay_nhap", "").strip() or date.today().isoformat()
        try:
            ngay_nhap = date.fromisoformat(ngay_nhap)
        except ValueError:
            loi = "Ngày nhập không hợp lệ (định dạng yyyy-mm-dd)."

        danh_sach_id = request.form.getlist("sach_id")
        danh_sach_sl = request.form.getlist("so_luong")

        dong_hop_le = []
        if not loi:
            if len(danh_sach_id) != len(danh_sach_sl):
                loi = "Dữ liệu các dòng không khớp nhau, vui lòng tải lại trang."
            else:
                loi, dong_hop_le = kiem_tra_cac_dong_nhap(
                    danh_sach_id, danh_sach_sl, so_luong_toi_thieu, nguong_ton
                )

        if not loi and not dong_hop_le:
            loi = "Chưa nhập dòng sách nào."

        # Hợp lệ: lưu phiếu + chi tiết + cộng tồn, tất cả trong một transaction
        if not loi:
            phieu = PhieuNhap(ngay_nhap=ngay_nhap, nguoi_quan_ly_id=current_user.id)
            db.session.add(phieu)
            try:
                db.session.flush()  # lấy phieu.id trước khi tạo chi tiết
                for sach, so_luong in dong_hop_le:
                    db.session.add(
                        ChiTietPhieuNhap(
                            phieu_nhap_id=phieu.id,
                            sach_id=sach.id,
                            so_luong=so_luong,
                        )
                    )
                    sach.so_luong_ton += so_luong
                db.session.commit()
                flash(
                    f"Đã lập phiếu nhập #{phieu.id} với {len(dong_hop_le)} dòng sách.",
                    "success",
                )
                return redirect(url_for("kho.phieu_nhap"))
            except IntegrityError:
                db.session.rollback()
                loi = "Không lưu được phiếu nhập (dữ liệu trùng lặp hoặc vi phạm ràng buộc)."

    return render_template(
        "kho/phieu_nhap.html",
        so_luong_toi_thieu=so_luong_toi_thieu,
        nguong_ton=nguong_ton,
        sach_list=Sach.query.order_by(Sach.ten).all(),
        loi=loi,
        ngay_nhap=request.form.get("ngay_nhap", date.today().isoformat()),
    )


def kiem_tra_cac_dong_nhap(danh_sach_id, danh_sach_sl, so_luong_toi_thieu, nguong_ton):
    """Kiểm tra từng dòng phiếu nhập.

    Trả về (loi, danh_sach_dong_hop_le) với danh_sach_dong_hop_le = [(sach, so_luong), ...]
    """
    dong_hop_le = []
    da_dung = set()

    for stt, (sach_id, so_luong) in enumerate(zip(danh_sach_id, danh_sach_sl), start=1):
        if not sach_id.strip() and not so_luong.strip():
            continue  # dòng trống, bỏ qua
        if not sach_id.isdigit():
            return f"Dòng {stt}: chưa chọn sách.", []
        sach = db.session.get(Sach, int(sach_id))
        if sach is None:
            return f"Dòng {stt}: sách không tồn tại.", []

        if sach.id in da_dung:
            return f"Dòng {stt}: sách «{sach.ten}» bị lặp trong cùng phiếu.", []
        da_dung.add(sach.id)

        if not so_luong.strip().isdigit() or int(so_luong) <= 0:
            return f"Dòng {stt} ({sach.ten}): số lượng phải là số nguyên lớn hơn 0.", []

        so_luong = int(so_luong)
        if so_luong < so_luong_toi_thieu:
            return (
                f"Dòng {stt} ({sach.ten}): số lượng nhập phải từ {so_luong_toi_thieu} cuốn trở lên "
                f"(bạn nhập {so_luong}).",
                [],
            )
        if nguong_ton is not None and sach.so_luong_ton >= nguong_ton:
            return (
                f"Dòng {stt} ({sach.ten}): tồn kho hiện tại là {sach.so_luong_ton} cuốn, "
                f"chỉ được nhập khi tồn nhỏ hơn {nguong_ton}.",
                [],
            )

        dong_hop_le.append((sach, so_luong))

    # Trả về None (không có lỗi) kèm danh sách dòng hợp lệ
    return None, dong_hop_le
