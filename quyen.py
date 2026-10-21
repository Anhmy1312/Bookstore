"""Phân quyền theo 4 vai trò - dùng chung cho mọi blueprint.   Người phụ trách: A

Vai trò lấy từ cột `vai_tro` của bảng `nguoi_dung`:
    KHACH      - Khách hàng (đặt sách online)
    NHANVIEN   - Nhân viên bán hàng (bán tại quầy)
    QUANLY     - Người quản lý kho (lập phiếu nhập, quản lý sách)
    QUANTRI    - Người quản trị (thống kê, báo cáo, thay đổi quy định)

Cách dùng trong blueprint:
    from quyen import vai_tro_required

    @bp.route("/sach")
    @vai_tro_required("QUANLY")
    def danh_sach_sach():
        ...

Ghi chú: file này do A tạo để hai bạn không sửa chung một file.
"""
from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def vai_tro_hien_tai():
    """Vai trò của người đang đăng nhập, None nếu chưa đăng nhập."""
    if not current_user.is_authenticated:
        return None
    return getattr(current_user, "vai_tro", None)


def vai_tro_required(*vai_tro_duoc_phep):
    """Chỉ người đã đăng nhập và có vai trò trong danh sách mới truy cập được.

    - Chưa đăng nhập  -> chuyển tới trang đăng nhập, nhớ trang đang muốn vào.
    - Đã đăng nhập nhưng sai vai trò -> báo lỗi rồi về trang chủ.
    """

    def boc_trong(f):
        @wraps(f)
        def kiem_tra(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.dang_nhap", next=request_full_path()))
            if vai_tro_hien_tai() not in vai_tro_duoc_phep:
                flash("Bạn không có quyền truy cập chức năng này.", "danger")
                return redirect(url_for("trang_chu"))
            return f(*args, **kwargs)

        return kiem_tra

    return boc_trong


def request_full_path():
    """Đường dẫn đầy đủ của trang khách đang muốn vào (để quay lại sau khi đăng nhập)."""
    from flask import request

    return request.full_path.rstrip("?")
