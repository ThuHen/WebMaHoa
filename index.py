
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import cloudinary.uploader
from appmh import db, bcrypt, login_manager, app
from appmh.models import User
import cloudinary
import appmh.untils as utils


    

# Trang chủ (home)

@app.route('/')
def home():
    return render_template('home.html')

# Trang đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    err_msg=""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            utils.add_user(username=username,password=password)
            return redirect(url_for('user_signin'))
            
        except Exception as ex:
            err_msg='He thong co loi: '+str(ex)

    return render_template('register.html',err_msg=err_msg)

        

    return render_template('register.html')

# Trang đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    err_msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user=utils.check_login(username=username,password=password)
        if user:
            login_user(user)
            next= request.args.get('next','home')
            return redirect(url_for(next))
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
    return utils.get_user_by_id(user_id=user_id)


if __name__ == '__main__':
    app.run(debug=True)