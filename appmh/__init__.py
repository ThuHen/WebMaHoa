import cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Cấu hình secret_key cho bảo mật session
app.config['SECRET_KEY'] = '2gufit93fqhdjR34UIF84tuigrejv9y834rygrufjw'

# Cấu hình cơ sở dữ liệu (MySQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Bang6822%40@localhost/webmahoa?charset=utf8mb4'
# Cấu hình cơ sở dữ liệu (MySQL) cho AWS RDS
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:Bang6822%40@databasewebmh.cfquieprbdtk.us-east-1.rds.amazonaws.com/webmahoa?charset=utf8mb4'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Tắt cảnh báo không cần thiết
# Khởi tạo các thư viện
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Cấu hình trang đăng nhập khi người dùng chưa đăng nhập
login_manager.login_message_category = 'info'  # Cấu hình thông điệp khi người dùng chưa đăng nhập


# Configuration
cloudinary.config(
    cloud_name = "dpm4nv09i",
    api_key = "559583468352841",
    api_secret = "S6U1gZmPA622tYhYFbQ-mp2g1H8", 
    secure=True
)






