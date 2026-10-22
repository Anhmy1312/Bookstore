"""Kiem thu tuan 2 phan A tren MySQL that.

Chay: venv\\Scripts\\python.exe _kiem_thu_tuan2.py
Ket qua ghi ra _ket_qua_kiem_thu.txt (UTF-8). Script TỰ PHỤC HỒI dữ liệu mẫu về
đúng trạng thái ban đầu (5/3/5/20/0/0/0/0) kể cả khi có bước nào lỗi.
"""

import io
import traceback

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
ANH_CHUP = {}


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
    """Chụp lại bảng sach để phục hồi sau khi thử."""
    with app.app_context():
        return {
            s.id: (
                s.ma_vach,
                s.ten,
                s.the_loai_id,
                s.tac_gia,
                s.don_gia,
                s.so_luong_ton,
            )
            for s in Sach.query.all()
        }


def phuc_hoi_cSDL(anh_chup):
    """Đưa bảng sach + phiếu nhập + quy định về đúng trạng thái ban đầu."""
    with app.app_context():
        # Bước 1: xoá hết chi tiết phiếu nhập / đơn hàng rồi mới xoá phiếu/đơn
        # Dùng bulk delete (db.session.execute(db.delete(...))) chứ không dùng
        # db.session.delete() cho bảng cha: ORM sẽ cố "xoá trắng" khoá ngoại ở bảng con
        # (chi_tiet_*.don_hang_id / phieu_nhap_id là khoá chính) -> AssertionError,
        # làm hàm dọn dừng giữa chừng và để lại dữ liệu sót.
        db.session.execute(db.delete(ChiTietPhieuNhap))
        db.session.execute(db.delete(ChiTietDonHang))
        db.session.commit()
        db.session.execute(db.delete(PhieuNhap))
        db.session.execute(db.delete(DonHang))
        db.session.commit()
        # Bước 2: đưa bảng sach về đúng trạng thái ban đầu
        hien_tai = {s.id: s for s in Sach.query.all()}
        for sach_id, s in hien_tai.items():
            if sach_id not in anh_chup:
                db.session.execute(
                    db.delete(Sach).where(Sach.id == sach_id)
                )  # sách tạo khi thử
        db.session.commit()
        for sach_id, du_lieu in anh_chup.items():
            s = db.session.get(Sach, sach_id)
            if s is None:  # sách bị xoá nhầm -> tạo lại
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
                s.so_luong_ton = du_lieu[5]  # trả tồn về ban đầu
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
    r = client_moi().get("/kiem-tra-db")
    log("   /kiem-tra-db ->", r.status_code)

    # ---------------------------------------------- 1. chưa đăng nhập
    cl = client_moi()
    r = cl.get("/kho/sach", follow_redirects=False)
    log(
        "1. Chua dang nhap GET /kho/sach ->",
        r.status_code,
        "|",
        r.headers.get("Location"),
    )

    # ---------------------------------------------- 2. sai mật khẩu
    r = cl.post(
        "/dang-nhap",
        data={"ten_dang_nhap": "quanly", "mat_khau": "sai"},
        follow_redirects=True,
    )
    log(
        "2. Login sai mat khau ->",
        r.status_code,
        "| bao loi:",
        "không đúng" in r.get_data(as_text=True),
    )

    # ---------------------------------------------- 3. QUANLY vào kho
    cl = client_moi()
    r = dang_nhap(cl, "quanly")
    log(
        "3. Login quanly ->",
        r.status_code,
        "| menu co 'Quản lý sách':",
        "Quản lý sách" in r.get_data(as_text=True),
    )
    r = cl.get("/kho/sach")
    log(
        "   GET /kho/sach ->",
        r.status_code,
        "| so dong sach:",
        r.data.count(b"<tr") - 1,
    )
    r = cl.get("/kho/sach?q=kiều")
    log("   Tim kiem 'kiều' ->", r.status_code, "| so dong:", r.data.count(b"<tr") - 1)
    r = cl.get("/kho/phieu-nhap")
    log(
        "   GET /kho/phieu-nhap ->",
        r.status_code,
        "| co quy dinh 150:",
        "150" in r.get_data(as_text=True),
    )
    r = cl.get("/admin/quy-dinh", follow_redirects=False)
    log(
        "   QUANLY vao /admin/quy-dinh (sai vai tro) ->",
        r.status_code,
        "|",
        r.headers.get("Location"),
    )

    # ---------------------------------------------- 4. QUANTRI vào admin
    cl2 = client_moi()
    r = dang_nhap(cl2, "quantri")
    log("4. Login quantri ->", r.status_code)
    r = cl2.get("/admin/quy-dinh")
    log(
        "   GET /admin/quy-dinh ->",
        r.status_code,
        "| co 3 quy dinh:",
        r.get_data(as_text=True).count("mb-3") >= 3,
    )
    r = cl2.get("/kho/sach", follow_redirects=False)
    log(
        "   QUANTRI vao /kho/sach (sai vai tro) ->",
        r.status_code,
        "|",
        r.headers.get("Location"),
    )

    # ---------------------------------------------- 5. quản lý sách
    MA_VACH_THU = "9999999999999"
    r = cl.post(
        "/kho/sach/them",
        data={
            "ten": "Sách thử nghiệm",
            "ma_vach": MA_VACH_THU,
            "tac_gia": "Tác giả thử",
            "the_loai_id": "1",
            "don_gia": "50000",
            "so_luong_ton": "0",
        },
        follow_redirects=True,
    )
    html = r.get_data(as_text=True)
    with app.app_context():
        sach_thu = Sach.query.filter_by(ma_vach=MA_VACH_THU).first()
        id_thu = sach_thu.id if sach_thu else 0
        log(
            "5. Them sach ->",
            r.status_code,
            "| co trong CSDL:",
            sach_thu is not None,
            "| so sach:",
            Sach.query.count(),
        )

    r = cl.post(
        "/kho/sach/them",
        data={
            "ten": "Trùng mã",
            "ma_vach": MA_VACH_THU,
            "tac_gia": "X",
            "the_loai_id": "1",
            "don_gia": "1000",
            "so_luong_ton": "0",
        },
        follow_redirects=True,
    )
    log(
        "   Them sach trung ma vach -> bao loi:",
        "Mã vạch đã tồn tại" in r.get_data(as_text=True),
    )

    r = cl.post(
        "/kho/sach/%d/sua" % id_thu,
        data={
            "ten": "Sách thử nghiệm (đã sửa)",
            "ma_vach": MA_VACH_THU,
            "tac_gia": "Tác giả thử",
            "the_loai_id": "2",
            "don_gia": "60000",
        },
        follow_redirects=True,
    )
    with app.app_context():
        s = db.session.get(Sach, id_thu)
        log(
            "   Sua sach -> ten:",
            s.ten,
            "| gia:",
            s.don_gia,
            "| the_loai:",
            s.the_loai_id,
        )

    r = cl.post("/kho/sach/%d/xoa" % id_thu, follow_redirects=True)
    with app.app_context():
        log(
            "   Xoa sach chua co giao dich ->",
            "Đã xoá" in r.get_data(as_text=True),
            "| con trong CSDL:",
            db.session.get(Sach, id_thu) is not None,
        )

    # ---------------------------------------------- 6. luật nhập sách
    with app.app_context():
        sach_ok = Sach.query.filter(Sach.so_luong_ton < 300).order_by(Sach.id).first()
        sach_ton_cao = (
            Sach.query.filter(Sach.so_luong_ton >= 300).order_by(Sach.id).first()
        )
        id_ok, id_cao = sach_ok.id, sach_ton_cao.id
        ton_truoc = sach_ok.so_luong_ton
        log(
            "6. Sach ton < 300:",
            sach_ok.ten,
            sach_ok.so_luong_ton,
            "| sach ton >= 300:",
            sach_ton_cao.ten,
            sach_ton_cao.so_luong_ton,
        )

    r = cl.post(
        "/kho/phieu-nhap",
        data={"ngay_nhap": "2026-10-21", "sach_id": [str(id_ok)], "so_luong": ["100"]},
        follow_redirects=True,
    )
    html = r.get_data(as_text=True)
    with app.app_context():
        log(
            "6a. Nhap 100 cuon (duoi 150) -> bao loi:",
            "từ 150 cuốn trở lên" in html,
            "| so phieu nhap:",
            PhieuNhap.query.count(),
        )

    r = cl.post(
        "/kho/phieu-nhap",
        data={"ngay_nhap": "2026-10-21", "sach_id": [str(id_cao)], "so_luong": ["200"]},
        follow_redirects=True,
    )
    html = r.get_data(as_text=True)
    with app.app_context():
        log(
            "6b. Nhap sach ton >= 300 -> bao loi:",
            "chỉ được nhập khi tồn nhỏ hơn" in html,
            "| so phieu nhap:",
            PhieuNhap.query.count(),
        )

    r = cl.post(
        "/kho/phieu-nhap",
        data={"ngay_nhap": "2026-10-21", "sach_id": [str(id_ok)], "so_luong": ["150"]},
        follow_redirects=True,
    )
    html = r.get_data(as_text=True)
    with app.app_context():
        phieu = PhieuNhap.query.order_by(PhieuNhap.id.desc()).first()
        s = db.session.get(Sach, id_ok)
        ct = (
            ChiTietPhieuNhap.query.filter_by(phieu_nhap_id=phieu.id).all()
            if phieu
            else []
        )
        log(
            "6c. Nhap hop le 150 cuon ->",
            "Đã lập phiếu nhập" in html,
            "| phieu:",
            phieu.id if phieu else None,
            "| chi tiet:",
            len(ct),
            "| ngay nhap:",
            phieu.ngay_nhap if phieu else None,
            "| ton moi:",
            s.so_luong_ton,
            "(truoc:",
            ton_truoc,
            ")",
        )

    r = cl.post("/kho/sach/%d/xoa" % id_ok, follow_redirects=True)
    log(
        "6d. Xoa sach da co giao dich -> bao loi:",
        "Sách đã có giao dịch, không thể xoá" in r.get_data(as_text=True),
    )

    # ---------------------------------------------- 7. quy định động
    # Cùng 1 sách + 120 cuốn, thử khi quy định = 150 (bị từ chối) rồi = 100 (được nhận)
    with app.app_context():
        sach_120 = Sach.query.filter(Sach.so_luong_ton < 300).order_by(Sach.id).first()
        id_120 = sach_120.id
        log(
            "7. Sach dung de thu 120 cuon:",
            sach_120.ten,
            "| ton:",
            sach_120.so_luong_ton,
        )

    r = cl.post(
        "/kho/phieu-nhap",
        data={"ngay_nhap": "2026-10-21", "sach_id": [str(id_120)], "so_luong": ["120"]},
        follow_redirects=True,
    )
    log(
        "   Nhap 120 cuon khi quy dinh = 150 ->",
        "Đã lập phiếu nhập" in r.get_data(as_text=True),
        "(phai bi tu choi)",
    )

    r = cl2.post(
        "/admin/quy-dinh",
        data={
            "nhap_toi_thieu": "100",
            "nguong_ton_de_nhap": "300",
            "gio_huy_don": "48",
        },
        follow_redirects=True,
    )
    log(
        "   Doi quy dinh 150 -> 100 ->",
        "Đã cập nhật quy định" in r.get_data(as_text=True),
    )

    r = cl.post(
        "/kho/phieu-nhap",
        data={"ngay_nhap": "2026-10-21", "sach_id": [str(id_120)], "so_luong": ["120"]},
        follow_redirects=True,
    )
    html = r.get_data(as_text=True)
    with app.app_context():
        log(
            "   Nhap 120 cuon khi quy dinh = 100 ->",
            "Đã lập phiếu nhập" in html,
            "(phai duoc chap nhan) | so phieu nhap:",
            PhieuNhap.query.count(),
            "| ton moi:",
            db.session.get(Sach, id_120).so_luong_ton,
        )

    r = cl2.post(
        "/admin/quy-dinh",
        data={
            "nhap_toi_thieu": "150",
            "nguong_ton_de_nhap": "300",
            "gio_huy_don": "48",
        },
        follow_redirects=True,
    )
except Exception:
    DONG.append("EXCEPTION:\n" + traceback.format_exc())
finally:
    phuc_hoi_cSDL(ANH_CHUP)
    log("8. Phuc hoi du lieu mau ->", so_dong())
    with app.app_context():
        log("   Quy dinh:", {q.ten: q.gia_tri for q in QuyDinh.query.all()})
        log(
            "   Ton kho:",
            {s.ten: s.so_luong_ton for s in Sach.query.order_by(Sach.id).all()},
        )

with io.open("_ket_qua_kiem_thu.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(DONG))
print("OK")
