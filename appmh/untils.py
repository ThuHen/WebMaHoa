from appmh import app, db, bcrypt
from appmh.models import  User, File
from flask_login import current_user
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes


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

def encrypt_file(plaintext: bytes, password) -> bytes:
    passphrasebytes = password.encode()  # Chuyển mật khẩu sang mảng byte
    salt = get_random_bytes(8)  # 8 byte salt
    key_iv = PBKDF2(passphrasebytes, salt, dkLen=48, count=10000)  # 32 byte key + 16 byte IV
    key = key_iv[:32]
    iv = key_iv[32:]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Padding kiểu PKCS#7
    pad_len = 16 - (len(plaintext) % 16)
    padded = plaintext + bytes([pad_len] * pad_len)

    encrypted = cipher.encrypt(padded)
    return b"Salted__" + salt + encrypted  # Chuẩn OpenSSL: b"Salted__" + salt + ciphertext

pbkdf2iterations = 10000  # Số vòng lặp của PBKDF2
def decrypt_file(cipherbytes: bytes, password) -> bytes:
    # Đảm bảo dữ liệu đầu vào là bytes
    if not isinstance(cipherbytes, bytes):
        raise ValueError("Input must be a bytes object.")

    # Kiểm tra nếu dữ liệu có ít nhất 16 byte để chứa "Salted__"
    if len(cipherbytes) < 16:
        raise ValueError("File không hợp lệ. Dữ liệu quá ngắn để chứa header.")

    # Bỏ qua phần header "Salted__" (8 byte) và lấy salt (8 byte tiếp theo)
    pbkdf2salt = cipherbytes[8:16]

    # Tạo passphrase key từ passphrase cố định
    passphrasebytes = password.encode()  # Chuyển mật khẩu sang mảng byte

    # Dùng PBKDF2 để tạo key (32 byte) và IV (16 byte)
    key_iv = PBKDF2(passphrasebytes, pbkdf2salt, dkLen=48, count=pbkdf2iterations)
    key = key_iv[:32]
    iv = key_iv[32:]

    # Tạo cipher AES với key và IV
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Lấy ciphertext (dữ liệu mã hóa) từ phần còn lại của file
    ciphertext = cipherbytes[16:]  # Bỏ qua phần header "Salted__" đầu tiên

    # Giải mã dữ liệu
    decrypted = cipher.decrypt(ciphertext)

    # Loại bỏ padding kiểu PKCS#7
    # Loại bỏ padding kiểu PKCS#7
    pad_len = decrypted[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError("Sai padding. Có thể mật khẩu sai hoặc dữ liệu bị lỗi.")
    plaintext = decrypted[:-pad_len]

    return plaintext
