from datetime import datetime

from flask import Flask, render_template, redirect, flash, request
from flask_login import LoginManager, logout_user, current_user, login_user
from model import app, login_manager
import dao,admin


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


@app.route('/dang-ky/<ma_lop>', methods=['POST'])
def dang_ky_lop(ma_lop):

    if not current_user.hoc_vien:
        flash("Chỉ tài khoản Học viên mới có thể đăng ký lớp học!", "danger")
        return redirect('/')


    thanh_cong, thong_bao = dao.dang_ky_lop_hoc(
        ma_hv=current_user.hoc_vien.maHV,
        ma_lop=ma_lop
    )


    if thanh_cong:
        flash(thong_bao, "success")
        return redirect('/')
    else:
        flash(thong_bao, "danger")
        return redirect('/')


@app.route('/my-courses')
def my_courses():
    if not current_user.is_authenticated:
        flash("Vui lòng đăng nhập để xem khóa học của bạn!", "warning")
        return redirect('/login')

    if not current_user.hoc_vien:
        flash("Chỉ tài khoản Học viên mới có trang Khóa học của tôi!", "danger")
        return redirect('/')

    ds_dang_ky = dao.lay_khoa_hoc_cua_toi(current_user.hoc_vien.maHV)
    return render_template('my_courses.html', ds_dang_ky=ds_dang_ky)


@app.route('/huy-dang-ky/<ma_dk>', methods=['POST'])
def huy_dang_ky(ma_dk):
    if not current_user.is_authenticated or not current_user.hoc_vien:
        flash("Bạn không có quyền thực hiện thao tác này!", "danger")
        return redirect('/login')

    ok, msg = dao.huy_dang_ky_lop(ma_dk, current_user.hoc_vien.maHV)
    flash(msg, "success" if ok else "danger")
    return redirect('/my-courses')



@app.route('/login-admin', methods=['POST'])
def login_admin_process():
    ten_dang_nhap = request.form.get('tenDangNhap', '')
    mat_khau = request.form.get('matKhau', '')

    user = dao.xac_thuc_nguoi_dung(ten_dang_nhap, mat_khau)
    if user and user.vaiTro == 'QuanLy':
        login_user(user)
    else:
        flash("Tài khoản không đúng hoặc không có quyền Quản lý!", "danger")

    return redirect('/admin')


@app.route('/thu-ngan')
def trang_thu_ngan():
    if not current_user.is_authenticated:
        flash("Vui lòng đăng nhập bằng tài khoản Thu ngân!", "warning")
        return redirect('/login')

    if current_user.vaiTro != 'ThuNgan' or not current_user.thu_ngan:
        flash("Chỉ tài khoản Thu ngân mới được truy cập trang này!", "danger")
        return redirect('/')

    kw = request.args.get('kw', '').strip()
    status = request.args.get('status', 'all')
    selected_ma_dk = request.args.get('selected')

    ds_dang_ky = dao.lay_ds_dang_ky_thu_ngan(kw=kw, trang_thai=status)


    dk_dang_chon = None
    if selected_ma_dk:
        dk_dang_chon = next((dk for dk in ds_dang_ky if dk.maDK == selected_ma_dk), None)
    if not dk_dang_chon and ds_dang_ky:
        dk_dang_chon = ds_dang_ky[0]

    return render_template(
        'thu_ngan.html',
        ds_dang_ky=ds_dang_ky,
        dk_dang_chon=dk_dang_chon,
        ma_hd_du_kien=dao.tao_ma_hoa_don_moi(),
        ngay_hien_tai=datetime.now().strftime('%d/%m/%Y'),
        kw=kw,
        status=status
    )

@app.route('/thu-ngan/lap-hoa-don/<ma_dk>', methods=['POST'])
def xu_ly_lap_hoa_don(ma_dk):
    if not current_user.is_authenticated or current_user.vaiTro != 'ThuNgan' or not current_user.thu_ngan:
        flash("Bạn không có quyền thực hiện thao tác này!", "danger")
        return redirect('/login')

    ok, msg = dao.lap_hoa_don(ma_dk, current_user.thu_ngan.maTN)
    flash(msg, "success" if ok else "danger")


    return redirect(f'/thu-ngan?selected={ma_dk}')


@app.route('/giao-vien', methods=['GET', 'POST'])
def trang_giao_vien():
    if not current_user.is_authenticated or current_user.vaiTro != 'GiaoVien':
        flash("Vui lòng đăng nhập bằng tài khoản Giáo viên!", "warning")
        return redirect('/login')

    ma_gv = current_user.giao_vien.maGV
    ds_lop = dao.lay_ds_lop_cua_gv(ma_gv)
    ma_lop = request.args.get('ma_lop')
    tab = request.args.get('tab', 'diem_danh')
    ngay_dd = request.args.get('ngay', datetime.now().strftime('%Y-%m-%d'))

    if request.method == 'POST':
        action = request.form.get('action')
        ma_lop = request.form.get('ma_lop')

        if action == 'luu_diem_danh':
            ngay_dd = request.form.get('ngay_dd')
            ok, msg = dao.luu_diem_danh(ma_lop, ngay_dd, request.form)
            flash(msg, 'success' if ok else 'danger')
            return redirect(f'/giao-vien?ma_lop={ma_lop}&tab=diem_danh&ngay={ngay_dd}')
        else:
            ok, msg = dao.luu_bang_diem(ma_lop, request.form)
            flash(msg, 'success' if ok else 'danger')
            return redirect(f'/giao-vien?ma_lop={ma_lop}&tab=nhap_diem')

    lop_chon = None
    if ma_lop:
        for l in ds_lop:
            if l.maLop == ma_lop:
                lop_chon = l
                break
    if not lop_chon and len(ds_lop) > 0:
        lop_chon = ds_lop[0]

    ds_dk = []
    bang_diem = {}
    bang_diem_danh = {}
    if lop_chon:
        ds_dk = dao.lay_ds_dang_ky_theo_lop(lop_chon.maLop)
        if tab == 'diem_danh':
            bang_diem_danh = dao.lay_diem_danh_theo_ngay(ds_dk, ngay_dd)
        else:
            bang_diem = dao.lay_bang_diem_theo_lop(ds_dk)

    ds_loai_diem = dao.lay_ds_loai_diem()

    return render_template(
        'giao_vien.html',
        ds_lop=ds_lop,
        lop_chon=lop_chon,
        ds_dk=ds_dk,
        ds_loai_diem=ds_loai_diem,
        bang_diem=bang_diem,
        bang_diem_danh=bang_diem_danh,
        tab=tab,
        ngay_dd=ngay_dd
    )


if __name__ == '__main__':
    app.run(debug=True,port=5001)