from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from appmh import app, db
from flask_login import UserMixin

# Mô hình người dùng
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    def __str__(self):
        return self.name

# Tạo bảng trong cơ sở dữ liệu nếu chưa tồn tại
if __name__ == '__main__':
    with app.app_context():  # Đưa ứng dụng vào ngữ cảnh
        db.create_all()  # Tạo bảng
    print("Bảng đã được tạo thành công!")
