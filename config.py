"""Cấu hình: đọc từ file .env (nếu có) rồi đến biến môi trường.

Mỗi máy có mật khẩu MySQL khác nhau nên KHÔNG viết cứng ở đây.
Cách dùng: copy .env.example thành .env rồi sửa DB_PASSWORD.
"""

import os
from urllib.parse import quote

from dotenv import load_dotenv

load_dotenv()  # đọc file .env cạnh app.py (không có file cũng không sao)

_host = os.environ.get("DB_HOST", "127.0.0.1")
_port = os.environ.get("DB_PORT", "3306")
_user = os.environ.get("DB_USER", "root")
_password = os.environ.get("DB_PASSWORD", "")
_name = os.environ.get("DB_NAME", "nha_sach")


class Config:
    # Dùng cho session / Flask-Login (slide trang 34)
    SECRET_KEY = os.environ.get("SECRET_KEY", "cnpm-nha_sach-secret")

    # Dạng mysql+pymysql://user:password@host/db?charset=utf8mb4 (slide trang 57).
    # quote(...) để mật khẩu có ký tự đặc biệt như @ vẫn dùng được (slide trang 58);
    # safe="" để cả dấu "/" trong mật khẩu cũng được mã hoá.
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{_user}:{quote(_password, safe='')}"
        f"@{_host}:{_port}/{_name}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Tự kiểm tra kết nối trước khi dùng, tránh lỗi "MySQL server has gone away"
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
