"""Kiem thu luong cua KHACH + BAN HANG tren MySQL that (phan B).

Chay: venv\\Scripts\\python.exe kiem_thu_khach_ban_hang.py
Ket qua: _ket_qua_kiem_thu_b.txt (UTF-8). Script TU PHOI HOI du lieu mau ve
dung trang thai ban dau (5 tai khoan / 3 quy dinh / 5 the loai / 20 sach / 0 don hang).
"""

import io
import traceback
from datetime import datetime, timedelta

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

app = app_module.app
DONG = []
ANH_CHUP = {"nguoi_dung": [], "sach": {}}


def log(*a):
    DONG.append(" ".join(str(x) for x in a))


def client_moi():
    return app.test_client()


def dang_nhap(cl, ten, mat_khau="123456"):
    return cl.post(
        "/dang-nhap",
        data={"ten_dang_nhap": ten, "mat_khau": mat_khau},
        follow_redirects=True,
    )


def so_dong():
    with app.app_context():
        return {
            b: m.query.count()
            for b, m in [
                ("nguoi_dung", NguoiDung),
                ("quy_dinh", QuyDinh),
                ("sach", Sach),
                ("phieu_nhap", PhieuNhap),
                ("chi_tiet_phieu_nhap", ChiTietPhieuNhap),
                ("don_hang", DonHang),
                ("chi_tiet_don_hang", ChiTietDonHang),
            ]
        }


def chup_cSDL():
    with app.app_context():
        return {
            "nguoi_dung": [
                (u.id, u.ten_dang_nhap, u.mat_khau_hash, u.ho_ten, u.vai_tro)
                for u in NguoiDung.query.all()
            ],
            "sach": {
                s.id: (
                    s.ma_vach,
                    s.ten,
                    s.the_loai_id,
                    s.tac_gia,
                    s.don_gia,
                    s.so_luong_ton,
                )
                for s in Sach.query.all()
            },
        }


def phuc_hoi_cSDL(anh_chup):
    # KHÔNG phục hồi khi ảnh chụp rỗng (tránh xoá nhầm toàn bộ dữ liệu mẫu)
    if not anh_chup.get("sach") or not anh_chup.get("nguoi_dung"):
        return
    with app.app_context():
        # Bulk delete cho bảng con trước, rồi bảng cha (ORM delete bảng cha sẽ cố
        # "xoá trắng" khoá ngoại ở bảng con -> AssertionError -> dọn dở dang, sót dữ liệu)
        db.session.execute(db.delete(ChiTietPhieuNhap))
        db.session.execute(db.delete(ChiTietDonHang))
        db.session.commit()
        db.session.execute(db.delete(DonHang))
        db.session.execute(db.delete(PhieuNhap))
        db.session.commit()
        # xoá sách tạo ra khi thử
        for sach in Sach.query.all():
            if sach.id not in anh_chup.get("sach", {}):
                db.session.execute(db.delete(Sach).where(Sach.id == sach.id))
        db.session.commit()
        # trả tồn kho + tạo lại sách bị xoá nhầm
        for sach_id, du_lieu in anh_chup.get("sach", {}).items():
            sach = db.session.get(Sach, sach_id)
            if sach is None:
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
                sach.so_luong_ton = du_lieu[5]
        # xoá tài khoản đăng ký khi thử, trả lại tài khoản mẫu
        for u in NguoiDung.query.all():
            if u.ten_dang_nhap not in [d[1] for d in anh_chup.get("nguoi_dung", [])]:
                db.session.delete(u)
        db.session.commit()
        for du_lieu in anh_chup.get("nguoi_dung", []):
            u = db.session.get(NguoiDung, du_lieu[0])
            if u is None:
                db.session.add(
                    NguoiDung(
                        id=du_lieu[0],
                        ten_dang_nhap=du_lieu[1],
                        mat_khau_hash=du_lieu[2],
                        ho_ten=du_lieu[3],
                        email=du_lieu[4],
                        vai_tro=du_lieu[5],
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

    # ------------------------------------------------ 1. đăng ký khách hàng
    cl_khach = client_moi()
    r = cl_khach.post(
        "/dang-ky",
        data={
            "ho_ten": "Nguyễn Thị Test",
            "ten_dang_nhap": "khachtest",
            "mat_khau": "123456",
            "xac_nhan_mat_khau": "123456",
        },
        follow_redirects=True,
    )
    html = r.get_data(as_text=True)
    with app.app_context():
        u = NguoiDung.query.filter_by(ten_dang_nhap="khachtest").first()
        log(
            "1. Dang ky khach ->",
            r.status_code,
            "| co tai khoan:",
            u is not None,
            "| vai tro:",
            u.vai_tro if u else "-",
        )

    # đăng ký trùng tên đăng nhập
    r = cl_khach.post(
        "/dang-ky",
        data={
            "ho_ten": "X",
            "ten_dang_nhap": "khachtest",
            "mat_khau": "123456",
            "xac_nhan_mat_khau": "123456",
        },
        follow_redirects=True,
    )
    log("   Dang ky trung ten -> bao loi:", "đã tồn tại" in r.get_data(as_text=True))

    r = dang_nhap(cl_khach, "khachtest", "123456")
    log(
        "   Dang nhap tai khoan moi ->",
        r.status_code,
        "| co menu KHACH:",
        "Giỏ hàng" in r.get_data(as_text=True),
    )

    # ------------------------------------------------ 2. khách xem sách + giỏ hàng
    r = cl_khach.get("/dat-sach/")
    log(
        "2. GET /dat-sach/ ->",
        r.status_code,
        "| so dong sach:",
        r.data.count(b"<tr") - 1,
    )

    with app.app_context():
        sach = Sach.query.filter(Sach.so_luong_ton > 0).order_by(Sach.id).first()
        id_sach, ton = sach.id, sach.so_luong_ton
        log("   Sach thu:", sach.ten, "id", id_sach, "ton", ton)

    r = cl_khach.post(
        "/dat-sach/gio-hang/them",
        data={"sach_id": str(id_sach), "so_luong": "2"},
        follow_redirects=True,
    )
    log("   Them vao gio ->", "Đã thêm" in r.get_data(as_text=True))
    r = cl_khach.get("/dat-sach/gio-hang")
    log(
        "   GET gio hang ->",
        r.status_code,
        "| co sach trong gio:",
        sach.ten in r.get_data(as_text=True),
    )

    # thêm vượt tồn
    r = cl_khach.post(
        "/dat-sach/gio-hang/them",
        data={"sach_id": str(id_sach), "so_luong": "9999"},
        follow_redirects=True,
    )
    log("   Them vuot ton -> bao loi:", "chỉ còn" in r.get_data(as_text=True))

    # cập nhật số lượng
    r = cl_khach.post(
        "/dat-sach/gio-hang/cap-nhat",
        data={"sach_id": str(id_sach), "so_luong": "3"},
        follow_redirects=True,
    )
    with app.app_context():
        from nghiem_vu import KHOA_GIO_HANG, lay_gio_hang

        with cl_khach.session_transaction() as sess:
            gio = sess.get(KHOA_GIO_HANG, {})
        log("   Cap nhat SL -> gio hang:", gio)

    # ------------------------------------------------ 3. đặt hàng trực tiếp (48 giờ)
    r = cl_khach.post(
        "/dat-sach/dat-hang", data={"hinh_thuc_tt": "TRUC_TIEP"}, follow_redirects=True
    )
    html = r.get_data(as_text=True)
    with app.app_context():
        don = DonHang.query.filter_by(kenh="ONLINE").order_by(DonHang.id.desc()).first()
        s = db.session.get(Sach, id_sach)
        log(
            "3. Dat hang TRUC_TIEP ->",
            "Đã đặt sách" in html,
            "| trang thai:",
            don.trang_thai,
            "| han lay sach:",
            don.han_lay_sach,
            "| khoang cach (gio):",
            round((don.han_lay_sach - don.ngay_tao).total_seconds() / 3600, 2),
            "| ton moi:",
            s.so_luong_ton,
            "(truoc",
            ton,
            ")",
        )
        id_don_truc_tiep = don.id
        don_id = don.id

    # ------------------------------------------------ 4. đặt hàng thanh toán online
    cl_khach.post(
        "/dat-sach/gio-hang/them", data={"sach_id": str(id_sach), "so_luong": "1"}
    )
    r = cl_khach.post(
        "/dat-sach/dat-hang", data={"hinh_thuc_tt": "ONLINE"}, follow_redirects=True
    )
    html = r.get_data(as_text=True)
    with app.app_context():
        don = (
            DonHang.query.filter_by(kenh="ONLINE", hinh_thuc_tt="ONLINE")
            .order_by(DonHang.id.desc())
            .first()
        )
        log(
            "4. Dat hang thanh toan ONLINE ->",
            "thanh toán online" in html.lower(),
            "| trang thai:",
            don.trang_thai,
            "| han lay sach:",
            don.han_lay_sach,
        )
        id_don_online = don.id

    # ------------------------------------------------ 5. nhân viên bán tại quầy (quét mã vạch)
    cl_nv = client_moi()
    dang_nhap(cl_nv, "nhanvien")
    with app.app_context():
        sach = db.session.get(Sach, id_sach)
        ma_vach = sach.ma_vach
        ton_truoc_quay = sach.so_luong_ton
    r = cl_nv.post(
        "/ban-hang/",
        data={"hanh_dong": "them", "ma_vach": ma_vach, "so_luong": "1"},
        follow_redirects=True,
    )
    log(
        "5. Quet ma vach ->",
        r.status_code,
        "| co loi:",
        "Không tìm thấy" in r.get_data(as_text=True),
    )
    r = cl_nv.post(
        "/ban-hang/",
        data={"hanh_dong": "thanh_toan", "ten_khach": "Khách vãng lai"},
        follow_redirects=True,
    )
    html = r.get_data(as_text=True)
    with app.app_context():
        don = DonHang.query.filter_by(kenh="QUAY").order_by(DonHang.id.desc()).first()
        s = db.session.get(Sach, id_sach)
        log(
            "   Lap hoa don quay ->",
            "Đã lập hoá đơn" in html,
            "| kenh:",
            don.kenh,
            "| trang thai:",
            don.trang_thai,
            "| khach_id:",
            don.khach_id,
            "| nhan_vien_id:",
            don.nhan_vien_id,
            "| don gia chot:",
            don.chi_tiet[0].don_gia,
            "| ton moi:",
            s.so_luong_ton,
            "(truoc",
            ton_truoc_quay,
            ")",
        )

    # ------------------------------------------------ 6. nhân viên xác nhận lấy sách (UC04)
    r = cl_nv.get("/ban-hang/don-cho-lay")
    log(
        "6. Danh sach don cho lay ->",
        r.status_code,
        "| co don #%d:" % id_don_truc_tiep,
        ("#%d" % id_don_truc_tiep) in r.get_data(as_text=True),
    )
    r = cl_nv.post(
        "/ban-hang/don-cho-lay/%d/xac-nhan" % id_don_truc_tiep, follow_redirects=True
    )
    with app.app_context():
        don = db.session.get(DonHang, id_don_truc_tiep)
        log(
            "   Xac nhan lay sach -> trang thai:",
            don.trang_thai,
            "| nhan_vien_id:",
            don.nhan_vien_id,
        )

    # ------------------------------------------------ 7. tự huỷ đơn quá hạn (48 giờ)
    with app.app_context():
        gio_huy = QuyDinh.lay_gia_tri("gio_huy_don") or 48
        don = db.session.get(DonHang, id_don_truc_tiep)
        don.trang_thai = "CHO_LAY"
        # đặt hạn lấy sách về quá khứ quá gio_huy_don giờ để giả lập đơn quá hạn
        don.han_lay_sach = datetime.now() - timedelta(hours=gio_huy + 1)
        s = db.session.get(Sach, id_sach)
        don.chi_tiet[0].so_luong = 1
        ton_truoc_huy = s.so_luong_ton
        db.session.commit()
    r = cl_khach.get("/dat-sach/don-hang")
    html = r.get_data(as_text=True)
    with app.app_context():
        don = db.session.get(DonHang, id_don_truc_tiep)
        s = db.session.get(Sach, id_sach)
        log(
            "7. Tu huy don qua han ->",
            "bị huỷ tự động" in html,
            "| trang thai:",
            don.trang_thai,
            "| ton moi:",
            s.so_luong_ton,
            "(truoc",
            ton_truoc_huy,
            "-> phai lon hon)",
        )

    # ------------------------------------------------ 8. khách tự huỷ đơn
    # tạo thêm 1 đơn TRUC_TIEP mới để huỷ thủ công
    cl_khach.post(
        "/dat-sach/gio-hang/them", data={"sach_id": str(id_sach), "so_luong": "1"}
    )
    cl_khach.post("/dat-sach/dat-hang", data={"hinh_thuc_tt": "TRUC_TIEP"})
    with app.app_context():
        don = (
            DonHang.query.filter_by(
                kenh="ONLINE", hinh_thuc_tt="TRUC_TIEP", trang_thai="CHO_LAY"
            )
            .order_by(DonHang.id.desc())
            .first()
        )
        id_don_huy = don.id if don else None
        ton_truoc = db.session.get(Sach, id_sach).so_luong_ton if don else 0
    if id_don_huy:
        r = cl_khach.post(
            "/dat-sach/don-hang/%d/huy" % id_don_huy, follow_redirects=True
        )
        with app.app_context():
            don = db.session.get(DonHang, id_don_huy)
            ton_sau = db.session.get(Sach, id_sach).so_luong_ton
            log(
                "8. Khach tu huy don #%d -> trang thai:" % id_don_huy,
                don.trang_thai,
                "| ton:",
                ton_truoc,
                "->",
                ton_sau,
                "(phai lon hon)",
            )
    else:
        log("8. Khach tu huy don -> KHONG tao duoc don CHO_LAY de huy")

    # ------------------------------------------------ 9. khách khác không xem đơn của người khác
    cl_khach2 = client_moi()
    dang_nhap(cl_khach2, "khachhang2")
    r = cl_khach2.get("/dat-sach/don-hang/%d" % id_don_online, follow_redirects=False)
    log(
        "9. Khach khac mo don cua nguoi khac ->",
        r.status_code,
        r.headers.get("Location"),
    )

    # ------------------------------------------------ 10. phân quyền
    r = cl_khach.get("/kho/sach", follow_redirects=False)
    log("10. KHACH vao /kho/sach ->", r.status_code, r.headers.get("Location"))
    r = cl_nv.get("/ban-hang/", follow_redirects=False)
    log("    NHANVIEN vao /ban-hang/ ->", r.status_code)
    r = cl_khach.get("/ban-hang/", follow_redirects=False)
    log("    KHACH vao /ban-hang/ ->", r.status_code, r.headers.get("Location"))

except Exception:
    DONG.append("EXCEPTION:\n" + traceback.format_exc())
finally:
    phuc_hoi_cSDL(ANH_CHUP)
    log("11. Phoi hoi du lieu mau ->", so_dong())
    with app.app_context():
        log(
            "    Ton kho:",
            {s.ten: s.so_luong_ton for s in Sach.query.order_by(Sach.id).all()},
        )

with io.open("_ket_qua_kiem_thu_b.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(DONG))
print("OK")
