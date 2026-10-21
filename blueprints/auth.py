"""Dang nhap / dang ky / dang xuat, phan quyen 4 vai tro.   Nguoi phu trich: B

Tuần 2 làm:
  - /dang-nhap, /dang-xuat  (so mật khẩu bằng NguoiDung.kiem_tra_mat_khau)
  - /dang-ky: khách hàng tự tạo tài khoản (vai trò KHACH)
  - /tai-khoan: xem thông tin tài khoản + đổi mật khẩu
  - hàm/decorator yêu cầu đăng nhập với đúng vai trò: KHACH, NHANVIEN, QUANLY, QUANTRI
    (dùng chung file quyen.py, không viết lại decorator ở đây)
Cùng cả theo slide: Flask-Login (login_user, logout_user, login_required, current_user),
NguoiDung.query.filter(NguoiDung.ten_dang_nhap == ...) rồi nguoi_dung.kiem_tra_mat_khau(...).
Bảng dùng: nguoi_dung

LƯU Ý BĂM MẬT KHẨU: tài khoản mẫu trong schema.sql băm bằng pbkdf2:sha256.
Tài khoản tạo mới cũng dùng đúng phương pháp đó (không dùng scrypt mặc định của
werkzeug vì một số máy Python trên macOS không hỗ trợ).
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from extensions import db
from models import NguoiDung
from quyen import vai_tro_required

bp = Blueprint("auth", __name__)

# Đúng phương pháp băm của tài khoản mẫu trong schema.sql
PHUONG_PHAP_BAM = "pbkdf2:sha256"


@bp.route("/dang-nhap", methods=["GET", "POST"])
def dang_nhap():
    """Đăng nhập bằng tên đăng nhập + mật khẩu. Sai thì báo lỗi, không báo lộ thêm."""
    if current_user.is_authenticated:
        return redirect(url_for("trang_chu"))

    loi = None
    if request.method == "POST":
        ten_dang_nhap = request.form.get("ten_dang_nhap", "").strip()
        mat_khau = request.form.get("mat_khau", "")

        # Lưu ý: so sánh với ĐÚNG TÊN CỘT, không so biến với chính nó
        nguoi_dung = db.session.query(NguoiDung).filter(
            NguoiDung.ten_dang_nhap == ten_dang_nhap
        ).first()

        if nguoi_dung is None or not nguoi_dung.kiem_tra_mat_khau(mat_khau):
            loi = "Tên đăng nhập hoặc mật khẩu không đúng."
        else:
            login_user(nguoi_dung)
            flash(f"Xin chào {nguoi_dung.ho_ten}!", "success")
            # Quay lại đúng trang khách định vào trước khi bị chặn (nếu có)
            dich = request.args.get("next", "")
            if dich.startswith("/") and not dich.startswith("//"):
                return redirect(dich)
            return redirect(url_for("trang_chu"))

    return render_template("dang_nhap.html", loi=loi)


@bp.route("/dang-ky", methods=["GET", "POST"])
def dang_ky():
    """Khách hàng tự đăng ký tài khoản (vai trò luôn là KHACH)."""
    if current_user.is_authenticated:
        return redirect(url_for("trang_chu"))

    loi = None
    du_lieu = {"ten_dang_nhap": "", "ho_ten": ""}

    if request.method == "POST":
        du_lieu["ten_dang_nhap"] = request.form.get("ten_dang_nhap", "").strip()
        du_lieu["ho_ten"] = request.form.get("ho_ten", "").strip()
        mat_khau = request.form.get("mat_khau", "")
        xac_nhan = request.form.get("xac_nhan_mat_khau", "")

        if not (du_lieu["ten_dang_nhap"] and du_lieu["ho_ten"] and mat_khau):
            loi = "Vui lòng nhập đầy đủ thông tin."
        elif mat_khau != xac_nhan:
            loi = "Hai mật khẩu không khớp."
        elif len(mat_khau) < 6:
            loi = "Mật khẩu phải có ít nhất 6 ký tự."
        else:
            nguoi_dung = NguoiDung(
                ten_dang_nhap=du_lieu["ten_dang_nhap"],
                mat_khau_hash=generate_password_hash(mat_khau, method=PHUONG_PHAP_BAM),
                ho_ten=du_lieu["ho_ten"],
                vai_tro="KHACH",
            )
            try:
                db.session.add(nguoi_dung)
                db.session.commit()
                flash("Đăng ký thành công, bạn có thể đăng nhập ngay.", "success")
                return redirect(url_for("auth.dang_nhap"))
            except IntegrityError:
                db.session.rollback()
                loi = "Tên đăng nhập đã tồn tại."

    return render_template("dang_ky.html", loi=loi, du_lieu=du_lieu)


@bp.route("/tai-khoan", methods=["GET", "POST"])
@vai_tro_required("KHACH", "NHANVIEN", "QUANLY", "QUANTRI")
def tai_khoan():
    """Xem thông tin tài khoản và đổi mật khẩu."""
    loi = None
    thanh_cong = None

    if request.method == "POST":
        mat_khau_cu = request.form.get("mat_khau_cu", "")
        mat_khau_moi = request.form.get("mat_khau_moi", "")
        xac_nhan = request.form.get("xac_nhan_mat_khau", "")

        if not current_user.kiem_tra_mat_khau(mat_khau_cu):
            loi = "Mật khẩu cũ không đúng."
        elif len(mat_khau_moi) < 6:
            loi = "Mật khẩu mới phải có ít nhất 6 ký tự."
        elif mat_khau_moi != xac_nhan:
            loi = "Hai mật khẩu mới không khớp."
        else:
            current_user.mat_khau_hash = generate_password_hash(mat_khau_moi, method=PHUONG_PHAP_BAM)
            db.session.commit()
            thanh_cong = "Đã đổi mật khẩu thành công."

    return render_template(
        "tai_khoan.html",
        loi=loi,
        thanh_cong=thanh_cong,
        vai_tro_hien_tai={
            "KHACH": "Khách hàng",
            "NHANVIEN": "Nhân viên bán hàng",
            "QUANLY": "Người quản lý (kho)",
            "QUANTRI": "Người quản trị",
        }.get(current_user.vai_tro, current_user.vai_tro),
    )


@bp.route("/dang-xuat")
def dang_xuat():
    logout_user()
    flash("Bạn đã đăng xuất khỏi hệ thống.", "info")
    return redirect(url_for("trang_chu"))
