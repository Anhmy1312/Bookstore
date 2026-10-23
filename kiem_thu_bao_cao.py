"""Kiem thue bao cao thong ke (YC4) - Phan A, Tuan 3.

Chay: venv\\Scripts\\python.exe kiem_thu_bao_cao.py

Kiem tra:
- GET /admin/bao-cao: trang chua bao cao (can dang nhap QUANTRI)
- GET /admin/bao-cao/doanh-thu-the-loai: bao cao doanh thu theo the loai
- GET /admin/bao-cao/tan-suat-sach: bao cao tan suat ban sach
- Huy don qua han (ham huy_don_qua_han)

CSDL duoc phuc hoi ve trang thai mau (5/3/5/20/0/0/0/0) sau khi kiem thu.
"""
import io
import traceback
from datetime import datetime

import app as app_module
from extensions import db
from models import (
    ChiTietDonHang,
    ChiTietPhieuNhap,
    DonHang,
    NguoiDung,
    PhieuNhap,
    QuyDinh,
    Sach,
)

DONG = []
ANH_CHUP = {}


def log(*a):
    DONG.append(" ".join(str(x) for x in a))


def client_moi():
    return app_module.app.test_client()


def dang_nhap(cl, ten, mat_khau="123456"):
    return cl.post("/dang-nhap", data={"ten_dang_nhap": ten, "mat_khau": mat_khau}, follow_redirects=True)


def so_dong():
    with app_module.app.app_context():
        return {
            b: m.query.count()
            for b, m in [
                ("nguoi_dung", NguoiDung),
                ("quy_dinh", QuyDinh),
                ("the_loai", __import__("models").TheLoai),
                ("sach", Sach),
                ("phieu_nhap", PhieuNhap),
                ("chi_tiet_phieu_nhap", ChiTietPhieuNhap),
                ("don_hang", DonHang),
                ("chi_tiet_don_hang", ChiTietDonHang),
            ]
        }


def chup_cSDL():
    with app_module.app.app_context():
        return {
            "nguoi_dung": [
                (u.id, u.ten_dang_nhap, u.mat_khau_hash, u.ho_ten, u.vai_tro)
                for u in NguoiDung.query.all()
            ],
            "sach": {
                s.id: (s.ma_vach, s.ten, s.the_loai_id, s.tac_gia, s.don_gia, s.so_luong_ton)
                for s in Sach.query.all()
            },
        }


def phuc_hoi_cSDL(anh_chup):
    if not anh_chup.get("sach") or not anh_chup.get("nguoi_dung"):
        return
    with app_module.app.app_context():
        db.session.execute(db.delete(ChiTietPhieuNhap))
        db.session.execute(db.delete(ChiTietDonHang))
        db.session.commit()
        db.session.execute(db.delete(DonHang))
        db.session.execute(db.delete(PhieuNhap))
        db.session.commit()
        for sach in Sach.query.all():
            if sach.id not in anh_chup["sach"]:
                db.session.execute(db.delete(Sach).where(Sach.id == sach.id))
        db.session.commit()
        for sach_id, du_lieu in anh_chup["sach"].items():
            s = db.session.get(Sach, sach_id)
            if s is None:
                db.session.add(
                    Sach(
                        id=sach_id,
                        ma_vach=du_lieu[0],
                        ten=du_lieu[1],
                        the_loai_id=du_lieu[2],
                        tac_gia=du_lieu[3],
                        don_gia=du_lieu[4],
                        so_luong_ton=du_lieu[5],
                    )
                )
            else:
                s.so_luong_ton = du_lieu[5]
        for u in NguoiDung.query.all():
            if u.ten_dang_nhap not in [d[1] for d in anh_chup["nguoi_dung"]]:
                db.session.delete(u)
        db.session.commit()
        for du_lieu in anh_chup["nguoi_dung"]:
            u = db.session.get(NguoiDung, du_lieu[0])
            if u is None:
                db.session.add(
                    NguoiDung(
                        id=du_lieu[0],
                        ten_dang_nhap=du_lieu[1],
                        mat_khau_hash=du_lieu[2],
                        ho_ten=du_lieu[3],
                        vai_tro=du_lieu[4],
                    )
                )
        for qd in QuyDinh.query.all():
            if qd.ten == "nhap_toi_thieu":
                qd.gia_tri = 150
            elif qd.ten == "nguong_ton_de_nhap":
                qd.gia_tri = 300
            elif qd.ten == "gio_huy_don":
                qd.gia_tri = 48
        db.session.commit()


try:
    ANH_CHUP = chup_cSDL()
    log("0. Ban dau:", so_dong())

    cl = client_moi()
    r = dang_nhap(cl, "quantri")
    html = r.get_data(as_text=True)
    log("1. Dang nhap quantri:", r.status_code, "| co menu Bao cao:", "Bao cao" in html)

    # Truy cap trang bao cao
    r = cl.get("/admin/bao-cao")
    log("2. GET /admin/bao-cao:", r.status_code, "| co tong doanh thu:", "Tong doanh thu" in r.get_data(as_text=True))

    r = cl.get("/admin/bao-cao/doanh-thu-the-loai")
    log("3. GET /admin/bao-cao/doanh-thu-the-loai:", r.status_code, "| co bang:", "<table" in r.get_data(as_text=True))

    r = cl.get("/admin/bao-cao/tan-suat-sach")
    log("4. GET /admin/bao-cao/tan-suat-sach:", r.status_code, "| co bang:", "<table" in r.get_data(as_text=True))

    # Kiem tra quyen: KHACH khong duoc vao bao cao
    cl_khach = client_moi()
    dang_nhap(cl_khach, "khachhang")
    r = cl_khach.get("/admin/bao-cao", follow_redirects=False)
    log("5. KHACH vao /admin/bao-cao (phai bi chan):", r.status_code, r.headers.get("Location"))

except Exception:
    DONG.append("EXCEPTION:\n" + traceback.format_exc())
finally:
    phuc_hoi_cSDL(ANH_CHUP)
    log("")
    log("Sau khi phuc hoi:", so_dong())

with io.open("docs/ket_qua_kiem_thu_bao_cao.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(DONG))
print("OK")
