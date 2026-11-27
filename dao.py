import hashlib
import uuid
from datetime import datetime

from sqlalchemy import or_

import utils
from model import CapDo, KhoaHoc, LopHoc, db, NguoiDung, HocVien, DangKy, ThamSoQuyDinh, HoaDon, ChiTietDiem, LoaiDiem, \
    DiemDanh


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


def dang_ky_lop_hoc(ma_hv, ma_lop):

    lop = LopHoc.query.get(ma_lop)
    if not lop:
        return False, "Lớp học không tồn tại!"

    gioi_han_si_so = min(lop.siSoToiDa, lay_si_so_toi_da())
    if lop.siSoHienTai >= gioi_han_si_so:
        return False, f"Lớp {lop.tenLop} đã đủ sĩ số ({lop.siSoHienTai}/{gioi_han_si_so})!"

    da_dk = DangKy.query.filter(
        DangKy.maHV == ma_hv,
        DangKy.maLop == ma_lop
    ).first()
    if da_dk:
        return False, f"Bạn đã đăng ký lớp {lop.tenLop} trước đó rồi!"



    ma_dk = f"DK{datetime.now().strftime('%y%m%d')}{uuid.uuid4().hex[:6].upper()}"

    dk_moi = DangKy(
        maDK=ma_dk,
        maHV=ma_hv,
        maLop=ma_lop,
        hinhThucDangKy='Trực tuyến'
    )

    try:
        lop.siSoHienTai += 1
        db.session.add(dk_moi)
        db.session.commit()
        try:
            email_hv = dk_moi.hoc_vien.nguoi_dung.email
            ho_ten_hv = dk_moi.hoc_vien.nguoi_dung.hoTen
            if email_hv and utils.gui_email_dang_ky(email_hv, ho_ten_hv, dk_moi):
                dk_moi.trangThaiEmail = True
                db.session.commit()
        except Exception as mail_ex:
            print("Lỗi gửi email xác nhận:", mail_ex)
        return True, f"Đăng ký lớp {lop.tenLop} thành công!"
    except Exception as ex:
        db.session.rollback()
        return False, f"Lỗi hệ thống: {str(ex)}"



def lay_khoa_hoc_cua_toi(ma_hv):
    return DangKy.query.filter(
        DangKy.maHV == ma_hv
    ).order_by(DangKy.ngayDangKy.desc()).all()


def huy_dang_ky_lop(ma_dk, ma_hv):

    dk = DangKy.query.filter(
        DangKy.maDK == ma_dk,
        DangKy.maHV == ma_hv
    ).first()

    if not dk:
        return False, "Không tìm thấy thông tin đăng ký này!"


    if dk.hoa_don is not None:
        return False, "Khóa học đã thanh toán học phí nên không thể tự hủy!"

    try:
        lop = dk.lop_hoc
        ten_lop = lop.tenLop if lop else ""


        if lop and lop.siSoHienTai > 0:
            lop.siSoHienTai -= 1

        db.session.delete(dk)
        db.session.commit()
        return True, f"Đã hủy đăng ký lớp {ten_lop} thành công!"
    except Exception as ex:
        db.session.rollback()
        return False, f"Có lỗi xảy ra khi hủy: {str(ex)}"

def lay_tham_so(ma_tham_so, mac_dinh=None):
    ts = ThamSoQuyDinh.query.get(ma_tham_so)
    return ts.giaTri if ts else mac_dinh


def lay_si_so_toi_da():
    try:
        return int(lay_tham_so('SI_SO_TOI_DA', 25))
    except (ValueError, TypeError):
        return 25

def tao_ma_hoa_don_moi():
    ds_hd = HoaDon.query.with_entities(HoaDon.maHD).all()
    max_num = 0
    for (ma,) in ds_hd:
        try:
            num = int(ma.replace('HD', ''))
            if num > max_num:
                max_num = num
        except ValueError:
            continue
    return f"HD{max_num + 1:03d}"


def lay_ds_dang_ky_thu_ngan(kw=None, trang_thai='all'):
    query = DangKy.query.join(HocVien).join(NguoiDung)

    if kw:
        kw = kw.strip()
        query = query.filter(or_(
            DangKy.maDK.contains(kw),
            HocVien.maHV.contains(kw),
            NguoiDung.hoTen.contains(kw)
        ))

    if trang_thai == 'unpaid':
        query = query.outerjoin(HoaDon).filter(HoaDon.maHD == None)
    elif trang_thai == 'paid':
        query = query.join(HoaDon)

    return query.order_by(DangKy.ngayDangKy.desc()).all()


def lap_hoa_don(ma_dk, ma_tn):

    dk = DangKy.query.get(ma_dk)
    if not dk:
        return False, "Không tìm thấy phiếu đăng ký này!"

    if dk.hoa_don is not None:
        return False, f"Phiếu {ma_dk} đã được lập hóa đơn ({dk.hoa_don.maHD}) trước đó!"

    try:
        hoc_phi = dk.lop_hoc.khoa_hoc.cap_do.mucHocPhi
        ma_hd = tao_ma_hoa_don_moi()

        hd = HoaDon(
            maHD=ma_hd,
            maDK=dk.maDK,
            maTN=ma_tn,
            ngayNop=datetime.now(),
            soTien=hoc_phi
        )
        db.session.add(hd)
        db.session.commit()
        return True, f"Đã lập hóa đơn {ma_hd} thành công!"
    except Exception as ex:
        db.session.rollback()
        return False, f"Lỗi khi lập hóa đơn: {str(ex)}"




def lay_ds_lop_cua_gv(ma_gv):
    return LopHoc.query.filter(LopHoc.maGV == ma_gv).all()


def lay_ds_dang_ky_theo_lop(ma_lop):
    return DangKy.query.filter(DangKy.maLop == ma_lop).all()


def lay_ds_loai_diem():
    return LoaiDiem.query.all()


def lay_bang_diem_theo_lop(ds_dk):
    ket_qua = {}
    for dk in ds_dk:
        ds_ct = ChiTietDiem.query.filter(ChiTietDiem.maDK == dk.maDK).all()
        for ct in ds_ct:
            ket_qua[(dk.maDK, ct.maLoaiDiem)] = ct.diemSo
    return ket_qua


def luu_bang_diem(ma_lop, form_data):
    ds_dk = lay_ds_dang_ky_theo_lop(ma_lop)
    ds_loai_diem = lay_ds_loai_diem()

    for dk in ds_dk:
        tong_diem = 0
        tong_he_so = 0
        du_diem = True

        for ld in ds_loai_diem:
            ten_o = f"diem_{dk.maDK}_{ld.maLoaiDiem}"
            gia_tri = form_data.get(ten_o, '').strip()

            if gia_tri != '':
                so_diem = float(gia_tri)
                if so_diem < 0 or so_diem > 10:
                    return False, "Điểm nhập phải nằm trong khoảng từ 0 đến 10!"

                ct = ChiTietDiem.query.filter(
                    ChiTietDiem.maDK == dk.maDK,
                    ChiTietDiem.maLoaiDiem == ld.maLoaiDiem
                ).first()

                if ct:
                    ct.diemSo = so_diem
                    ct.ngayNhap = datetime.now()
                else:
                    ct = ChiTietDiem(
                        maCTD=f"CTD{uuid.uuid4().hex[:6].upper()}",
                        maDK=dk.maDK,
                        maLoaiDiem=ld.maLoaiDiem,
                        diemSo=so_diem,
                        ngayNhap=datetime.now()
                    )
                    db.session.add(ct)

                tong_diem += so_diem * ld.heSo
                tong_he_so += ld.heSo
            else:
                du_diem = False

        if du_diem and tong_he_so > 0:
            dk.diemTrungBinh = round(tong_diem / tong_he_so, 2)
            if dk.diemTrungBinh >= 5.0:
                dk.ketQuaPhanLoai = 'Đạt'
            else:
                dk.ketQuaPhanLoai = 'Không đạt'

    db.session.commit()
    return True, "Đã lưu bảng điểm và cập nhật xếp loại thành công!"


def lay_diem_danh_theo_ngay(ds_dk, ngay_str):
    ngay = datetime.strptime(ngay_str, '%Y-%m-%d').date()
    ket_qua = {}
    for dk in ds_dk:
        dd = DiemDanh.query.filter(
            DiemDanh.maDK == dk.maDK,
            DiemDanh.ngayDiemDanh == ngay
        ).first()
        if dd:
            ket_qua[dk.maDK] = dd
    return ket_qua


def luu_diem_danh(ma_lop, ngay_str, form_data):
    ds_dk = lay_ds_dang_ky_theo_lop(ma_lop)
    ngay = datetime.strptime(ngay_str, '%Y-%m-%d').date()

    for dk in ds_dk:
        trang_thai = form_data.get(f"tt_{dk.maDK}", "Có mặt")
        ghi_chu = form_data.get(f"gc_{dk.maDK}", "").strip()

        dd = DiemDanh.query.filter(
            DiemDanh.maDK == dk.maDK,
            DiemDanh.ngayDiemDanh == ngay
        ).first()

        if dd:
            dd.trangThai = trang_thai
            dd.ghiChu = ghi_chu
        else:
            dd = DiemDanh(
                maDD=f"DD{uuid.uuid4().hex[:6].upper()}",
                maDK=dk.maDK,
                ngayDiemDanh=ngay,
                trangThai=trang_thai,
                ghiChu=ghi_chu
            )
            db.session.add(dd)

    db.session.commit()
    return True, f"Đã lưu điểm danh ngày {ngay_str} thành công!"