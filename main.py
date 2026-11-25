from flask import Flask, render_template, redirect, flash, request
from flask_login import LoginManager, logout_user, current_user, login_user

from model import app, login_manager
import dao


@login_manager.user_loader
def load_user(ma_nd):
    return dao.lay_nguoi_dung_theo_id(ma_nd)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    err_msg = None
    if request.method == 'POST':
        ten_dang_nhap = request.form.get('tenDangNhap', '')
        mat_khau = request.form.get('matKhau', '')

        user = dao.xac_thuc_nguoi_dung(ten_dang_nhap, mat_khau)
        if user:
            login_user(user)
            return redirect('/')
        else:
            err_msg = "Tên đăng nhập hoặc mật khẩu không chính xác!"

    return render_template('login.html', err_msg=err_msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')

    err_msg = None
    if request.method == 'POST':
        ho_ten = request.form.get('hoTen', '')
        ten_dang_nhap = request.form.get('tenDangNhap', '')
        email = request.form.get('email', '')
        so_dien_thoai = request.form.get('soDienThoai', '')
        ngay_sinh = request.form.get('ngaySinh', '')
        dia_chi = request.form.get('diaChi', '')
        mat_khau = request.form.get('matKhau', '')
        xac_nhan_mat_khau = request.form.get('xacNhanMatKhau', '')

        if mat_khau != xac_nhan_mat_khau:
            err_msg = "Mật khẩu xác nhận không khớp!"
        else:
            err_msg = dao.dang_ky_hoc_vien(
                ho_ten=ho_ten,
                ten_dang_nhap=ten_dang_nhap,
                mat_khau=mat_khau,
                email=email,
                so_dien_thoai=so_dien_thoai,
                ngay_sinh=ngay_sinh,
                dia_chi=dia_chi
            )
            if not err_msg:
                flash("Đăng ký tài khoản thành công! Vui lòng đăng nhập.", 'success')
                return redirect('/login')

    return render_template('register.html', err_msg=err_msg)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/')
def loadGiaoDienDangKy():
    ds_cap_do = dao.loadCapDo()
    ds_khoa_hoc = dao.loadKhoaHoc()
    return render_template('index.html', ds_cap_do=ds_cap_do, ds_khoa_hoc=ds_khoa_hoc)

if __name__ == '__main__':
    app.run(debug=True)