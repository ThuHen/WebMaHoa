import os
import hashlib
from appmh import app, db, bcrypt
from appmh.models import  User
from flask_login import current_user


def add_user(username, password):
    # Mã hóa mật khẩu
   hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
   user= User( username=username.strip(), password=hashed_password)
   
   try:
      db.session.add(user)
      db.session.commit()
   except Exception as e:
      db.session.rollback()  # Hủy bỏ thay đổi nếu có lỗi
      print(f"Lỗi khi commit vào database: {e}")  # Ghi log lỗi
      return False
   else:
      return True
  
   

def check_login(username,password):
   user = User.query.filter_by(username=username).first()
   if user and bcrypt.check_password_hash(user.password, password):
         return user
   else:
         return None

def get_user_by_id(user_id):
    return User.query.get(int(user_id))