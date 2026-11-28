from model import app,db
from flask import redirect,request
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.theme import Bootstrap4Theme
from flask_login import current_user, logout_user
from model import CapDo, KhoaHoc, LopHoc, NguoiDung,DangKy, HoaDon, ThamSoQuyDinh,LoaiDiem,ChiTietDiem,HocVien, ThuNgan, QuanLy
from wtforms.validators import ValidationError
import dao
from wtforms import DecimalField, FloatField
from datetime import datetime

class AuthenticatedModelView(ModelView):
    column_display_pk = True
    can_export = True
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.vaiTro == 'QuanLy'

class ThamSoView(AuthenticatedModelView):
    column_list = ['maThamSo', 'tenThamSo', 'giaTri', 'moTa']
    form_columns = ['maThamSo', 'tenThamSo', 'giaTri', 'moTa']

    def on_model_change(self, form, model, is_created):

        if model.maThamSo and model.maThamSo.strip().upper() == 'SI_SO_TOI_DA':
            try:
                if int(model.giaTri) <= 0:
                    raise ValueError
            except ValueError:
                raise ValidationError("Sĩ số tối đa phải là số nguyên dương lớn hơn 0!")

    def after_model_change(self, form, model, is_created):

        if model.maThamSo and model.maThamSo.strip().upper() == 'SI_SO_TOI_DA':
            si_so_moi = int(model.giaTri)
            ds_lop = self.session.query(LopHoc).all()

            for lop in ds_lop:
                if lop.siSoHienTai <= si_so_moi:
                    lop.siSoToiDa = si_so_moi

            self.session.commit()



class CapDoView(AuthenticatedModelView):
    column_list = ['maCapDo', 'tenCapDo', 'mucHocPhi']
    form_columns = ['maCapDo', 'tenCapDo', 'mucHocPhi']
    form_overrides = {
        'mucHocPhi': DecimalField
    }
    column_searchable_list = ['tenCapDo']
    column_labels = {
        'maCapDo': 'Mã cấp độ',
        'tenCapDo': 'Tên cấp độ',
        'mucHocPhi': 'Mức học phí (VNĐ)'
    }


class KhoaHocView(AuthenticatedModelView):
    column_list = ['maKH', 'tenKH', 'thoiLuong', 'cap_do', 'Img']
    form_columns = ['maKH', 'tenKH', 'moTa', 'thoiLuong', 'cap_do', 'Img']
    column_searchable_list = ['tenKH']
    column_filters = ['maCapDo']
    column_labels = {
        'maKH': 'Mã KH',
        'tenKH': 'Tên khóa học',
        'thoiLuong': 'Thời lượng (buổi)',
        'cap_do': 'Cấp độ',
        'Img': 'Đường dẫn ảnh'
    }
class LoaiDiemView(AuthenticatedModelView):
    column_list = ['maLoaiDiem', 'tenLoaiDiem', 'heSo']
    form_columns = ['maLoaiDiem', 'tenLoaiDiem', 'heSo']
    form_overrides = {
        'heSo': FloatField
    }
    column_searchable_list = ['tenLoaiDiem']
    column_labels = {
        'maLoaiDiem': 'Mã loại điểm',
        'tenLoaiDiem': 'Tên loại điểm',
        'heSo': 'Hệ số'
    }

    def on_model_change(self, form, model, is_created):
        if model.heSo is None or model.heSo <= 0 or model.heSo > 1:
            raise ValidationError("Hệ số điểm phải lớn hơn 0 và nhỏ hơn hoặc bằng 1 (ví dụ: 0.1, 0.3, 0.6)!")

class ChiTietDiemView(AuthenticatedModelView):
    column_list = ['maCTD', 'maDK', 'maLoaiDiem', 'diemSo', 'ngayNhap']
    form_columns = ['maCTD', 'maDK', 'maLoaiDiem', 'diemSo', 'ngayNhap']
    form_overrides = {
        'diemSo': FloatField
    }
    column_searchable_list = ['maCTD', 'maDK']
    column_filters = ['maLoaiDiem', 'ngayNhap']
    column_labels = {
        'maCTD': 'Mã chi tiết điểm',
        'maDK': 'Mã đăng ký',
        'maLoaiDiem': 'Mã loại điểm',
        'diemSo': 'Điểm số',
        'ngayNhap': 'Ngày nhập'
    }

    def on_model_change(self, form, model, is_created):
        if model.diemSo is None or model.diemSo < 0 or model.diemSo > 10:
            raise ValidationError("Điểm số phải nằm trong khoảng từ 0 đến 10!")


class LopHocView(AuthenticatedModelView):
    column_list = ['maLop', 'tenLop', 'khoa_hoc', 'giao_vien', 'ngayBatDau', 'ngayKetThuc', 'siSoHienTai', 'siSoToiDa']
    form_columns = ['maLop', 'tenLop', 'khoa_hoc', 'giao_vien', 'ngayBatDau', 'ngayKetThuc', 'siSoHienTai', 'siSoToiDa']
    column_searchable_list = ['tenLop', 'maLop']
    column_filters = ['maKH', 'ngayBatDau']
    column_labels = {
        'maLop': 'Mã lớp',
        'tenLop': 'Tên lớp',
        'khoa_hoc': 'Khóa học',
        'giao_vien': 'Giảng viên',
        'ngayBatDau': 'Ngày bắt đầu',
        'ngayKetThuc': 'Ngày kết thúc',
        'siSoHienTai': 'Sĩ số hiện tại',
        'siSoToiDa': 'Sĩ số tối đa'
    }

    def on_model_change(self, form, model, is_created):
        si_so_quy_dinh = dao.lay_si_so_toi_da()

        if not model.siSoToiDa:
            model.siSoToiDa = si_so_quy_dinh
        elif model.siSoToiDa > si_so_quy_dinh:
            raise ValidationError(
                f"Sĩ số tối đa của lớp không được vượt quá quy định trung tâm ({si_so_quy_dinh} học viên)!"
            )

class NguoiDungView(AuthenticatedModelView):
    column_list = ['maND', 'tenDangNhap', 'hoTen', 'email', 'soDienThoai', 'vaiTro', 'trangThai']
    column_searchable_list = ['tenDangNhap', 'hoTen', 'email']
    column_filters = ['vaiTro', 'trangThai']
    can_create = False



class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')


class StatsView(BaseView):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        year = request.args.get('year', datetime.now().year, type=int)

        stats_kh = dao.thong_ke_doanh_thu_khoa_hoc(kw=kw, from_date=from_date, to_date=to_date)
        stats_thang = dao.thong_ke_doanh_thu_theo_thang(year=year)
        stats_dat = dao.thong_ke_ty_le_dat_theo_khoa_hoc()

        return self.render(
            'admin/stats.html',
            stats_kh=stats_kh,
            stats_thang=stats_thang,
            stats_dat=stats_dat,
            year=year
        )

    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.vaiTro == 'QuanLy'


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.vaiTro == 'QuanLy'


admin = Admin(
    app=app,
    name='QUẢN TRỊ TRUNG TÂM',
    theme=Bootstrap4Theme(),
    index_view=MyAdminIndexView()
)

admin.add_view(CapDoView(CapDo, db.session, name='Cấp độ & Học phí'))
admin.add_view(KhoaHocView(KhoaHoc, db.session, name='Khóa học'))
admin.add_view(LopHocView(LopHoc, db.session, name='Lớp học'))
admin.add_view(NguoiDungView(NguoiDung, db.session, name='Người dùng'))
admin.add_view(AuthenticatedModelView(DangKy, db.session, name='Đăng ký học'))
admin.add_view(LoaiDiemView(LoaiDiem, db.session, name='Loại điểm'))
admin.add_view(ChiTietDiemView(ChiTietDiem, db.session, name='Chi tiết điểm'))
admin.add_view(AuthenticatedModelView(HoaDon, db.session, name='Hóa đơn'))
admin.add_view(ThamSoView(ThamSoQuyDinh, db.session, name='Quy định'))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))
