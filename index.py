
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import cloudinary.uploader
from appmh import  login_manager, app
import cloudinary
import appmh.untils as untils
from flask import jsonify


    

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

# Upload file mã hóa lên Cloudinary
@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
    
    file = request.files['file']
    file_extension = request.form.get('file_extension')

    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
    
    if file:
        try:
            # Upload file as "raw" (không phải ảnh)
            upload_result = cloudinary.uploader.upload(
                file,
                folder=f"user_{current_user.id}",
                resource_type="raw"
            )
            untils.add_file(
                filename=file.filename,
                file_url=upload_result['secure_url'],
                file_extension=file_extension,
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

    
    


if __name__ == '__main__':
    app.run(debug=True)