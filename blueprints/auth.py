"""Dang nhap / dang xuat, phan quyen 4 vai tro.   Nguoi phu trich: B

Tuần 2 làm:
  - /dang-nhap, /dang-xuat  (so mật khẩu bằng NguoiDung.kiem_tra_mat_khau)
  - hàm/decorator yêu cầu đăng nhập với đúng vai trò: KHACH, NHANVIEN, QUANLY, QUANTRI
Cùng cả theo slide: Flask-Login (login_user, logout_user, login_required, current_user),
NguoiDung.query.filter(NguoiDung.ten_dang_nhap == ...) rồi nguoi_dung.kiem_tra_mat_khau(...).
Bảng dùng: nguoi_dung

GHI CHÚ CỦA A (20/10): B viết phần này ở tuần 2 theo kế hoạch. A đã làm tạm phiên bản
tối giản để có nền đăng nhập cho /kho/sach, /kho/phieu-nhap, /admin/quy-dinh chạy được.
Khi B làm tiếp: giữ nguyên 2 route này, thêm phần B cần (ví dụ đăng ký, quên mật khẩu) —
không cần sửa lại phần kiểm tra mật khẩu, nó đã đúng theo slide.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from extensions import db
from models import NguoiDung

bp = Blueprint("auth", __name__)


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


@bp.route("/dang-xuat")
def dang_xuat():
    logout_user()
    flash("Bạn đã đăng xuất khỏi hệ thống.", "info")
    return redirect(url_for("trang_chu"))
