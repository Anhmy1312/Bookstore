"""Các extension dùng chung.

Slide viết  db = SQLAlchemy(app)  ngay trong file chính. Dự án này chia nhiều file
(models.py, blueprints/...) nên tạo db ở đây trước, rồi app.py gọi db.init_app(app).
Cách này tránh lỗi import vòng.
"""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login = LoginManager()
