from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from appmh import app, db
from flask_login import UserMixin
from flask import Flask

# app = Flask(__name__)

# app.config['SECRET_KEY'] = '2gufit93fqhdjR34UIF84tuigrejv9y834rygrufjw'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:lethithuhenai@localhost/webmahoa?charset=utf8mb4'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Tắt cảnh báo không cần thiết
# db = SQLAlchemy(app)


# Mô hình người dùng
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
     # Quan hệ: một người dùng có nhiều file
    files = db.relationship('File', backref='user', lazy=True)
    def __str__(self):
        return self.username
# Mô hình file
class File(db.Model):
    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(255), nullable=False)       # Tên file
    file_url = db.Column(db.String(500), nullable=False)       # Đường dẫn file hoặc URL
    file_extension = db.Column(db.String(10), nullable=False)  # Cột đuôi file
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Liên kết với user
    def __str__(self):
        return self.filename
    
# Tạo bảng trong cơ sở dữ liệu nếu chưa tồn tại
if __name__ == '__main__':
    with app.app_context():  # Đưa ứng dụng vào ngữ cảnh
        db.create_all()  # Tạo bảng
    print("Bảng đã được tạo thành công!")
