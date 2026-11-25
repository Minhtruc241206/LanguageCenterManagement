import hashlib
import uuid
from datetime import datetime

from model import CapDo, KhoaHoc, LopHoc, db, NguoiDung, HocVien


def loadCapDo():
    return CapDo.query.all()

def loadKhoaHoc():
    return KhoaHoc.query.all()

def lay_nguoi_dung_theo_id(ma_nd):
    return db.session.get(NguoiDung, ma_nd)

def xac_thuc_nguoi_dung(ten_dang_nhap, mat_khau):
    user = NguoiDung.query.filter_by(tenDangNhap=ten_dang_nhap.strip()).first()
    if not user or not user.trangThai:
        return None

    mat_khau_hash = hashlib.md5(mat_khau.strip().encode('utf-8')).hexdigest()
    if user.matKhau == mat_khau_hash or user.matKhau == mat_khau.strip():
        return user
    return None


def dang_ky_hoc_vien(ho_ten, ten_dang_nhap, mat_khau, email, so_dien_thoai, ngay_sinh=None, dia_chi=None):
    ten_dang_nhap = ten_dang_nhap.strip()
    email = email.strip()

    if NguoiDung.query.filter_by(tenDangNhap=ten_dang_nhap).first():
        return "Tên đăng nhập đã tồn tại, vui lòng chọn tên khác!"

    if NguoiDung.query.filter_by(email=email).first():
        return "Email này đã được đăng ký!"

    so_nd = NguoiDung.query.count() + 1
    while db.session.get(NguoiDung, f"ND{so_nd:02d}"):
        so_nd += 1
    ma_nd = f"ND{so_nd:02d}"

    so_hv = HocVien.query.count() + 1
    while db.session.get(HocVien, f"HV{so_hv:02d}"):
        so_hv += 1
    ma_hv = f"HV{so_hv:02d}"

    mat_khau_hash = hashlib.md5(mat_khau.strip().encode('utf-8')).hexdigest()
    ngay_sinh_date = datetime.strptime(ngay_sinh, '%Y-%m-%d').date() if ngay_sinh else None

    nd = NguoiDung(
        maND=ma_nd,
        tenDangNhap=ten_dang_nhap,
        matKhau=mat_khau_hash,
        hoTen=ho_ten.strip(),
        email=email,
        soDienThoai=so_dien_thoai.strip(),
        vaiTro='HocVien',
        trangThai=1
    )
    db.session.add(nd)
    db.session.flush()

    hv = HocVien(
        maHV=ma_hv,
        ngaySinh=ngay_sinh_date,
        diaChi=dia_chi.strip() if dia_chi else None,
        maND=ma_nd
    )
    db.session.add(hv)
    db.session.commit()

    return None