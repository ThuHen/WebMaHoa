from appmh import app, db, bcrypt
from appmh.models import  User, File
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
  
def add_file(filename, file_url,file_extension,public_id, user_id):
    try:
        new_file = File(
            filename=filename,
            file_url=file_url,
            file_extension=file_extension,
            public_id=public_id,
            user_id=user_id
        )
        db.session.add(new_file)
        db.session.commit()
        return True, "File added to database successfully."
    except Exception as e:
        db.session.rollback()
        return False, f"Error adding file to database: {str(e)}"

def check_login(username,password):
   user = User.query.filter_by(username=username).first()
   if user and bcrypt.check_password_hash(user.password, password):
         return user
   else:
         return None

def get_user_by_id(user_id):
    return User.query.get(int(user_id))
def get_file_by_id(file_id):
    return File.query.get(int(file_id))
def get_files_by_user_id(user_id):
    return File.query.filter_by(user_id=user_id).all()
def delete_file(file):
    if file:
        db.session.delete(file)
        db.session.commit()
        return True
    return False
