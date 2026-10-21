"""Các hàm nghiệp vụ dùng chung cho nhiều blueprint (đặt sách, bán hàng, báo cáo).

Tách riêng một file để hai bạn không sửa chung một file.   Người phụ trách: B

Hàm quan trọng nhất: `huy_don_qua_han()` - huỷ đơn trực tiếp quá hạn và trả lại tồn kho.
"""
from datetime import datetime, timedelta

from flask import session

from extensions import db
from models import ChiTietDonHang, DonHang, QuyDinh, Sach

# Khoá giỏ hàng trong session
KHOA_GIO_HANG = "gio_hang"        # giỏ của khách đặt online
KHOA_GIO_QUAY = "gio_hang_quay"   # giỏ của nhân viên tại quầy


def lay_gio_hang(ten_khoa):
    """Lấy giỏ hàng trong session: {id_sach (chuỗi): so_luong}."""
    return session.get(ten_khoa, {})


def luu_gio_hang(ten_khoa, gio):
    """Lưu giỏ hàng vào session."""
    session[ten_khoa] = gio
    return gio


def xoa_gio_hang(ten_khoa):
    """Xoá giỏ hàng trong session."""
    session.pop(ten_khoa, None)


def chi_tiet_gio_hang(ten_khoa):
    """Trả về [(sach, so_luong)] của giỏ, bỏ qua sách đã bị xoá khỏi CSDL."""
    gio = lay_gio_hang(ten_khoa)
    ket_qua = []
    for sach_id, so_luong in gio.items():
        sach = db.session.get(Sach, int(sach_id))
        if sach is not None:
            ket_qua.append((sach, so_luong))
    return ket_qua


def tong_tien_gio(ten_khoa):
    """Tổng tiền của giỏ (dùng giá hiện tại của sách - chỉ để hiển thị cho khách)."""
    return sum(sach.don_gia * so_luong for sach, so_luong in chi_tiet_gio_hang(ten_khoa))


def huy_don_qua_han():
    """Huỷ các đơn đặt online trả tại quầy đã quá hạn và cộng lại tồn kho.

    Quy định "quá gio_huy_don giờ mà khách chưa đến lấy sách thì đơn bị huỷ" chỉ áp dụng
    cho đơn `hinh_thuc_tt = 'TRUC_TIEP'`. Đơn thanh toán online không bao giờ tự huỷ.

    Trả về số đơn đã huỷ. Gọi mỗi khi mở trang đơn hàng hoặc trang báo cáo.
    """
    gio_huy = QuyDinh.lay_gia_tri("gio_huy_don")
    if not gio_huy:
        return 0

    han = datetime.now() - timedelta(hours=gio_huy)
    don_hangs = DonHang.query.filter(
        DonHang.trang_thai == "CHO_LAY",
        DonHang.han_lay_sach.isnot(None),
        DonHang.han_lay_sach < han,
    ).all()

    so_don = 0
    for don in don_hangs:
        for ct in don.chi_tiet:
            sach = db.session.get(Sach, ct.sach_id)
            if sach is not None:
                sach.so_luong_ton += ct.so_luong     # trả lại tồn kho
        don.trang_thai = "DA_HUY"
        so_don += 1

    if so_don:
        db.session.commit()
    return so_don


def tao_don_hang(kenh, khach_id, ten_khach, nhan_vien_id, hinh_thuc_tt, chi_tiet):
    """Tạo đơn hàng + chi tiết, trừ tồn kho. Trả về (don_hang, loi).

    - `kenh`: 'ONLINE' (khách đặt) hoặc 'QUAY' (nhân viên bán tại quầy).
    - `hinh_thuc_tt`: 'TRUC_TIEP' (trả tại quầy) hoặc 'ONLINE' (trả trước, giao miễn phí).
    - `chi_tiet`: list [(sach, so_luong)].

    Với đơn trả tại quầy: trạng thái CHO_LAY, hạn lấy sách = giờ đặt + gio_huy_don giờ.
    Với đơn trả trước: trạng thái HOAN_TAT ngay, hạn lấy sách để trống.
    """
    if not chi_tiet:
        return None, "Chưa chọn sách nào để đặt."

    for sach, so_luong in chi_tiet:
        if so_luong <= 0:
            return None, f"Số lượng của sách «{sach.ten}» phải lớn hơn 0."
        if sach.so_luong_ton < so_luong:
            return None, (
                f"Sách «{sach.ten}» hiện chỉ còn {sach.so_luong_ton} cuốn, "
                f"không đủ {so_luong} cuốn để đặt."
            )

    if kenh == "ONLINE":
        trang_thai = "CHO_LAY" if hinh_thuc_tt == "TRUC_TIEP" else "HOAN_TAT"
    else:
        # Bán tại quầy: đã thanh toán ngay
        trang_thai = "HOAN_TAT"

    gio_huy = QuyDinh.lay_gia_tri("gio_huy_don") or 0
    han_lay_sach = None
    if trang_thai == "CHO_LAY":
        han_lay_sach = datetime.now() + timedelta(hours=gio_huy)

    don = DonHang(
        kenh=kenh,
        khach_id=khach_id,
        ten_khach=ten_khach,
        nhan_vien_id=nhan_vien_id,
        hinh_thuc_tt=hinh_thuc_tt,
        trang_thai=trang_thai,
        ngay_tao=datetime.now(),
        han_lay_sach=han_lay_sach,
    )
    db.session.add(don)
    db.session.flush()

    for sach, so_luong in chi_tiet:
        db.session.add(
            ChiTietDonHang(
                don_hang_id=don.id,
                sach_id=sach.id,
                so_luong=so_luong,
                don_gia=sach.don_gia,      # CHỐT giá lúc bán
            )
        )
        sach.so_luong_ton -= so_luong   # trừ tồn ngay khi đặt

    db.session.commit()
    return don, ""

