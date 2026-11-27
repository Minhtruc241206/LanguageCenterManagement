import json
import os
from datetime import datetime, date
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Double, ForeignKey, true, Boolean
from flask_login import UserMixin, LoginManager
from flask_mail import Mail
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()


app.config["SQLALCHEMY_DATABASE_URI"] ="mysql+pymysql://root:root@localhost/LanguageCenterManagement?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = 'nhom7-language-center-secret-key'
login_manager = LoginManager(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('Trung Tâm Ngoại Ngữ Nhóm 7', os.environ.get('MAIL_USERNAME'))

mail = Mail(app)

class NguoiDung(db.Model, UserMixin):
    __tablename__ = 'NGUOI_DUNG'
    maND = db.Column(db.String(20), primary_key=True)
    tenDangNhap = db.Column(db.String(50), unique=True, nullable=False)
    matKhau = db.Column(db.String(255), nullable=False)
    hoTen = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    soDienThoai = db.Column(db.String(15))
    vaiTro = db.Column(db.String(20), nullable=False)
    trangThai = db.Column(db.Boolean, default=True, nullable=False)

    def get_id(self):
        return self.maND


class HocVien(db.Model):
    __tablename__ = 'HOC_VIEN'
    maHV = db.Column(db.String(20), primary_key=True)
    ngaySinh = db.Column(db.Date)
    diaChi = db.Column(db.String(255))
    maND = db.Column(db.String(20), db.ForeignKey('NGUOI_DUNG.maND'), unique=True, nullable=False)

    nguoi_dung = db.relationship('NguoiDung', backref=db.backref('hoc_vien', uselist=False))


class GiaoVien(db.Model):
    __tablename__ = 'GIAO_VIEN'
    maGV = db.Column(db.String(20), primary_key=True)
    chuyenMon = db.Column(db.String(100))
    bangCap = db.Column(db.String(100))
    maND = db.Column(db.String(20), db.ForeignKey('NGUOI_DUNG.maND'), unique=True, nullable=False)

    nguoi_dung = db.relationship('NguoiDung', backref=db.backref('giao_vien', uselist=False))


class ThuNgan(db.Model):
    __tablename__ = 'THU_NGAN'
    maTN = db.Column(db.String(20), primary_key=True)
    maND = db.Column(db.String(20), db.ForeignKey('NGUOI_DUNG.maND'), unique=True, nullable=False)

    nguoi_dung = db.relationship('NguoiDung', backref=db.backref('thu_ngan', uselist=False))


class QuanLy(db.Model):
    __tablename__ = 'QUAN_LY'
    maQL = db.Column(db.String(20), primary_key=True)
    maND = db.Column(db.String(20), db.ForeignKey('NGUOI_DUNG.maND'), unique=True, nullable=False)

    nguoi_dung = db.relationship('NguoiDung', backref=db.backref('quan_ly', uselist=False))


class CapDo(db.Model):
    __tablename__ = 'CAP_DO'
    maCapDo = db.Column(db.String(20), primary_key=True)
    tenCapDo = db.Column(db.String(50), unique=True, nullable=False)
    mucHocPhi = db.Column(db.Float, nullable=False)

    ds_khoa_hoc = db.relationship('KhoaHoc', backref='cap_do', lazy=True)


class KhoaHoc(db.Model):
    __tablename__ = 'KHOA_HOC'
    maKH = db.Column(db.String(20), primary_key=True)
    tenKH = db.Column(db.String(100), nullable=False)
    moTa = db.Column(db.Text)
    thoiLuong = db.Column(db.Integer, nullable=False)
    maCapDo = db.Column(db.String(20), db.ForeignKey('CAP_DO.maCapDo'), nullable=False)
    Img=db.Column(db.String(300), nullable=True)

    ds_lop = db.relationship('LopHoc', backref='khoa_hoc', lazy=True)


class LopHoc(db.Model):
    __tablename__ = 'LOP_HOC'
    maLop = db.Column(db.String(20), primary_key=True)
    tenLop = db.Column(db.String(100), nullable=False)
    ngayBatDau = db.Column(db.Date, nullable=False)
    ngayKetThuc = db.Column(db.Date, nullable=False)
    siSoToiDa = db.Column(db.Integer, default=25, nullable=False)
    siSoHienTai = db.Column(db.Integer, default=0, nullable=False)
    maKH = db.Column(db.String(20), db.ForeignKey('KHOA_HOC.maKH'), nullable=False)
    maGV = db.Column(db.String(20), db.ForeignKey('GIAO_VIEN.maGV'), nullable=False)

    giao_vien = db.relationship('GiaoVien', backref='ds_lop_day', lazy=True)


class DangKy(db.Model):
    __tablename__ = 'DANG_KY'
    maDK = db.Column(db.String(20), primary_key=True)
    ngayDangKy = db.Column(db.DateTime, default=datetime.now, nullable=False)
    hinhThucDangKy = db.Column(db.String(30), default='Trực tuyến', nullable=False)
    trangThaiEmail = db.Column(db.Boolean, default=False, nullable=False)
    diemTrungBinh = db.Column(db.Float, nullable=True)
    ketQuaPhanLoai = db.Column(db.String(20), nullable=True)
    maHV = db.Column(db.String(20), db.ForeignKey('HOC_VIEN.maHV'), nullable=False)
    maLop = db.Column(db.String(20), db.ForeignKey('LOP_HOC.maLop'), nullable=False)

    __table_args__ = (db.UniqueConstraint('maHV', 'maLop', name='uq_hv_lop'),)

    hoc_vien = db.relationship('HocVien', backref='ds_dang_ky', lazy=True)
    lop_hoc = db.relationship('LopHoc', backref='ds_dang_ky', lazy=True)


class HoaDon(db.Model):
    __tablename__ = 'HOA_DON'
    maHD = db.Column(db.String(20), primary_key=True)
    ngayNop = db.Column(db.DateTime, default=datetime.now, nullable=False)
    soTien = db.Column(db.Float, nullable=False)
    trangThaiThanhToan = db.Column(db.String(30), default='Đã thanh toán', nullable=False)
    maDK = db.Column(db.String(20), db.ForeignKey('DANG_KY.maDK'), unique=True, nullable=False)
    maTN = db.Column(db.String(20), db.ForeignKey('THU_NGAN.maTN'), nullable=False)

    dang_ky = db.relationship('DangKy', backref=db.backref('hoa_don', uselist=False))
    thu_ngan = db.relationship('ThuNgan', backref='ds_hoa_don', lazy=True)


class LoaiDiem(db.Model):
    __tablename__ = 'LOAI_DIEM'
    maLoaiDiem = db.Column(db.String(20), primary_key=True)
    tenLoaiDiem = db.Column(db.String(50), nullable=False)
    heSo = db.Column(db.Float, nullable=False)
    dangSuDung = db.Column(db.Boolean, default=True, nullable=False)


class ChiTietDiem(db.Model):
    __tablename__ = 'CHI_TIET_DIEM'
    maCTD = db.Column(db.String(20), primary_key=True)
    diemSo = db.Column(db.Float, nullable=False)
    ngayNhap = db.Column(db.Date, default=date.today, nullable=False)
    maDK = db.Column(db.String(20), db.ForeignKey('DANG_KY.maDK'), nullable=False)
    maLoaiDiem = db.Column(db.String(20), db.ForeignKey('LOAI_DIEM.maLoaiDiem'), nullable=False)

    __table_args__ = (db.UniqueConstraint('maDK', 'maLoaiDiem', name='uq_dk_loaidiem'),)

    dang_ky = db.relationship('DangKy', backref='ds_diem', lazy=True)
    loai_diem = db.relationship('LoaiDiem', lazy=True)


class DiemDanh(db.Model):
    __tablename__ = 'DIEM_DANH'
    maDD = db.Column(db.String(20), primary_key=True)
    ngayDiemDanh = db.Column(db.Date, default=date.today, nullable=False)
    trangThai = db.Column(db.String(30), nullable=False)
    ghiChu = db.Column(db.String(255))
    maDK = db.Column(db.String(20), db.ForeignKey('DANG_KY.maDK'), nullable=False)

    dang_ky = db.relationship('DangKy', backref='ds_diem_danh', lazy=True)


class ThamSoQuyDinh(db.Model):
    __tablename__ = 'THAM_SO_QUY_DINH'
    maThamSo = db.Column(db.String(30), primary_key=True)
    tenThamSo = db.Column(db.String(100), nullable=False)
    giaTri = db.Column(db.String(50), nullable=False)
    moTa = db.Column(db.String(255))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # with open('data/tham_so_quy_dinh.json', 'r', encoding='utf-8') as f:
        #     for item in json.load(f):
        #         if not db.session.get(ThamSoQuyDinh, item['maThamSo']):
        #             db.session.add(ThamSoQuyDinh(**item))
        #
        # # 2. Cấp độ
        # with open('data/cap_do.json', 'r', encoding='utf-8') as f:
        #     for item in json.load(f):
        #         if not db.session.get(CapDo, item['maCapDo']):
        #             db.session.add(CapDo(**item))
        #
        # # 3. Loại điểm
        # with open('data/loai_diem.json', 'r', encoding='utf-8') as f:
        #     for item in json.load(f):
        #         if not db.session.get(LoaiDiem, item['maLoaiDiem']):
        #             db.session.add(LoaiDiem(**item))
        #
        # # 4. Người dùng
        # with open('data/nguoi_dung.json', 'r', encoding='utf-8') as f:
        #     for item in json.load(f):
        #         if not db.session.get(NguoiDung, item['maND']):
        #             db.session.add(NguoiDung(**item))
        # db.session.commit()
        #
        # # 5. Quản lý, Thu ngân, Giáo viên, Học viên (phụ thuộc NGUOI_DUNG)
        # with open('data/quan_ly.json', 'r', encoding='utf-8') as f:
        #     for item in json.load(f):
        #         if not db.session.get(QuanLy, item['maQL']):
        #             db.session.add(QuanLy(**item))
        #
        # with open('data/thu_ngan.json', 'r', encoding='utf-8') as f:
        #     for item in json.load(f):
        #         if not db.session.get(ThuNgan, item['maTN']):
        #             db.session.add(ThuNgan(**item))
        #
        # with open('data/giao_vien.json', 'r', encoding='utf-8') as f:
        #     for item in json.load(f):
        #         if not db.session.get(GiaoVien, item['maGV']):
        #             db.session.add(GiaoVien(**item))
        #
        # with open('data/hoc_vien.json', 'r', encoding='utf-8') as f:
        #     for item in json.load(f):
        #         if not db.session.get(HocVien, item['maHV']):
        #             hv = HocVien(
        #                 maHV=item['maHV'],
        #                 ngaySinh=datetime.strptime(item['ngaySinh'], '%Y-%m-%d').date(),
        #                 diaChi=item['diaChi'],
        #                 maND=item['maND']
        #             )
        #             db.session.add(hv)
        # db.session.commit()
        #
        # with open('data/khoa_hoc.json', 'r', encoding='utf-8') as f:
        #     for item in json.load(f):
        #         if not db.session.get(KhoaHoc, item['maKH']):
        #             db.session.add(KhoaHoc(**item))
        # db.session.commit()
        #
        # with open('data/lop_hoc.json', 'r', encoding='utf-8') as f:
        #     for item in json.load(f):
        #         if not db.session.get(LopHoc, item['maLop']):
        #             db.session.add(LopHoc(**item))
        # db.session.commit()

        print("Đã tạo đủ 14 bảng thành công!")