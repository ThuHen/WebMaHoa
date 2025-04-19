
from flask import render_template, request, redirect, send_file, url_for, jsonify
from flask_login import  login_user, logout_user, current_user, login_required
import cloudinary.uploader
from appmh import login_manager, app
import cloudinary
import appmh.untils as untils
import os
from io import BytesIO
import cloudinary.uploader
import requests
# pip install pycryptodome
    

# Trang chủ (home)

@app.route('/')
def home():

    if current_user.is_authenticated:

        return render_template('home.html',user_id=current_user.id)
    else:
        return render_template('home.html',user_id=None)

# Trang đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    err_msg=""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            untils.add_user(username=username,password=password)
            return redirect(url_for('user_signin'))
            
        except Exception as ex:
            err_msg='He thong co loi: '+str(ex)

    return render_template('register.html',err_msg=err_msg)


# Trang đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    err_msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user=untils.check_login(username=username,password=password)
        if user:
            login_user(user)
            return redirect(url_for('home'))  # Chuyển hướng về trang chủ sau khi đăng nhập thành công
        else:
            err_msg='Username hoac password khong chinh xac!'
    return render_template('login.html', err_msg=err_msg)

# Trang đăng xuất
@app.route('/logout')
@login_required  # Chỉ cho phép đăng xuất khi người dùng đã đăng nhập
def logout():
    logout_user()  # Đăng xuất người dùng
    
    return redirect(url_for('login'))  # Chuyển hướng về trang đăng nhập

# Cấu hình Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return untils.get_user_by_id(user_id=user_id)

@app.route('/api/files', methods=['GET'])
@login_required
def get_file_list():
    try:
        files = untils.get_files_by_user_id(current_user.id)
        result = [{
            'id': f.id,
            'filename': f.filename,
            'file_url': f.file_url,
            'file_extension': f.file_extension
        } for f in files] if files else []
        return jsonify(result), 200
    except Exception as e:
        # Nếu cần log kỹ: import traceback; traceback.print_exc()
        return jsonify({'error': str(e)}), 500

            
@app.route("/api/delete", methods=["POST"])
@login_required
def delete_file():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON payload"}), 400
    file_id = data.get("file_id")
    
    if not file_id:
        return jsonify({"success": False, "message": "Missing file_id"}), 400

    file = untils.get_file_by_id(file_id=file_id)
    if not file:
        return jsonify({"success": False, "message": "File not found"}), 404

    try:
        # Xóa file khỏi Cloudinary nếu có public_id
        if file.public_id:
            cloudinary.uploader.destroy(file.public_id, resource_type="raw")

        # Xóa khỏi database
        if untils.delete_file(file):
            return jsonify({"success": True, "message": "File deleted successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Error deleting file from database"}), 500

    except Exception as e:
        return jsonify({"success": False, "message": f"Unexpected error: {str(e)}"}), 500
@app.route("/encrypt-and-upload", methods=["POST"])
def encrypt_and_upload():
    
    if 'file' not in request.files :
        return jsonify(success=False, message="Lỗi up file lên server"), 400

    file = request.files['file']
    filename = request.form.get("filename")
    
    file_ext = request.form.get("file_extension")

    if file.filename == '':
        return jsonify(success=False, message="Không có tên file."), 400
    

    if file:
        try:
            # Đọc nội dung file
            file_content = file.read()
            
            # Mã hóa file
            encrypted_file = untils.encrypt_file(file_content) if file_content else None  # Mã hóa với dữ liệu tải về
            if not encrypted_file:
                return jsonify(success=False, message="Error encrypting file"), 500
            
            # Đọc nội dung file đã mã hóa vào BytesIO
            encrypted_file_io = BytesIO(encrypted_file)
            
            # Upload file đã giải mã lên Cloudinary
            upload_result = cloudinary.uploader.upload(
                encrypted_file_io,
                folder=f"user_{current_user.id}",
                resource_type="raw",
            )
            
            # Thêm thông tin file vào database
            untils.add_file(
                filename=filename,
                file_url=upload_result['secure_url'],
                file_extension=file_ext,
                public_id=upload_result['public_id'],
                user_id=current_user.id
                
            )
            
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'url': upload_result['secure_url']
            }), 200
        except Exception as ex:
            return jsonify({
                'success': False,
                'message': 'Error uploading file: ' + str(ex)
            }), 500
            

@app.route('/decrypt-file', methods=['POST'])
def decrypt_file():
    data = request.get_json()
    if not data:
        return jsonify(success=False, message="Invalid JSON payload"), 400
    
    file_url = data.get('file_url')  # Lấy file_url từ JSON payload
    print("Received file_url:", file_url)
    if not file_url:
        return jsonify(success=False, message="No file URL provided"), 400

    try:
        # Tải file từ URL
        response = requests.get(file_url)
        if response.status_code != 200:
            return jsonify(success=False, message="Error downloading file"), 500
        
        encrypted_file_content = response.content
        
        # Giải mã file
        decrypted_file = untils.decrypt_file(encrypted_file_content) if encrypted_file_content else None
        if not decrypted_file:
            return jsonify(success=False, message="Error decrypting file"), 500

        # Trả file về client dưới dạng file đính kèm
        return send_file(
            BytesIO(decrypted_file),
            as_attachment=True,
            download_name="decrypted_file",
            mimetype="application/octet-stream"
        )
    except Exception as ex:
        return jsonify(success=False, message="Error decrypting file: " + str(ex)), 500
if __name__ == '__main__':
    app.run(debug=True)