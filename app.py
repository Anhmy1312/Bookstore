"""Điểm khởi động của website quản lý nhà sách.  Chạy:  python app.py"""
from flask import Flask, render_template
from sqlalchemy.exc import SQLAlchemyError

from blueprints import admin, auth, ban_hang, dat_sach, kho
from config import Config
from extensions import db, login
from models import (ChiTietDonHang, ChiTietPhieuNhap, DonHang, NguoiDung,
                    PhieuNhap, QuyDinh, Sach, TheLoai)

# Dùng cho trang /kiem-tra-db: (tên bảng, lớp model)
CAC_BANG = [
    ("nguoi_dung", NguoiDung), ("quy_dinh", QuyDinh), ("the_loai", TheLoai),
    ("sach", Sach), ("phieu_nhap", PhieuNhap),
    ("chi_tiet_phieu_nhap", ChiTietPhieuNhap), ("don_hang", DonHang),
    ("chi_tiet_don_hang", ChiTietDonHang),
]


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login.init_app(app)

    # Mỗi blueprint là một file riêng -> hai bạn ít đụng code nhau
    for module in (auth, kho, admin, dat_sach, ban_hang):
        app.register_blueprint(module.bp)

    @login.user_loader
    def load_user(user_id):
        """Flask-Login nạp lại người dùng từ user id lưu trong session (slide trang 85)."""
        return db.session.get(NguoiDung, int(user_id))

    @app.template_filter("vnd")
    def dinh_dang_vnd(so):
        """Bộ lọc riêng cho template (slide trang 27): 95000 -> '95.000 đ'"""
        return "{:,.0f}".format(so).replace(",", ".") + " đ"

    @app.route("/")
    def trang_chu():
        # Tuần 1: chỉ cần thấy 1 bảng đọc từ MySQL. Tuần 2 chuyển sang dat_sach.py.
        sach = Sach.query.order_by(Sach.id).all()
        return render_template("index.html", sach=sach)

    @app.route("/kiem-tra-db")
    def kiem_tra_db():
        """Hai bạn mở trang này trên máy mình: cùng số dòng nghĩa là cùng CSDL mẫu."""
        thong_ke = [(ten_bang, model.query.count()) for ten_bang, model in CAC_BANG]
        return render_template("kiem_tra_db.html", thong_ke=thong_ke)

    @app.errorhandler(SQLAlchemyError)
    def loi_csdl(loi):
        return render_template("loi_db.html", loi=getattr(loi, "orig", loi)), 500

    @app.errorhandler(404)
    def khong_tim_thay(loi):
        return render_template("page_not_found.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
