from flask_mail import Message
from model import mail


def gui_email_dang_ky(email_nhan, ho_ten, dk):

    lop = dk.lop_hoc
    khoa_hoc = lop.khoa_hoc
    hoc_phi = f"{khoa_hoc.cap_do.mucHocPhi:,.0f}".replace(",", ".")
    ngay_bd = lop.ngayBatDau.strftime('%d/%m/%Y') if lop.ngayBatDau else 'Đang cập nhật'

    noi_dung_html = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h3 style="color: #0d6efd;">Xác nhận đăng ký khóa học thành công</h3>
        <p>Chào <strong>{ho_ten}</strong>,</p>
        <p>Bạn đã đăng ký giữ chỗ thành công tại <strong>Trung Tâm Ngoại Ngữ</strong>. Thông tin phiếu đăng ký:</p>
        <ul>
            <li><strong>Mã đăng ký:</strong> {dk.maDK}</li>
            <li><strong>Khóa học:</strong> {khoa_hoc.tenKH} ({khoa_hoc.cap_do.tenCapDo})</li>
            <li><strong>Lớp học:</strong> {lop.tenLop}</li>
            <li><strong>Ngày khai giảng:</strong> {ngay_bd}</li>
            <li><strong>Học phí cần đóng:</strong> <strong style="color: #dc3545;">{hoc_phi} đ</strong></li>
        </ul>
        <p>Vui lòng hoàn tất học phí tại quầy Thu ngân trước ngày khai giảng để chính thức vào lớp.</p>
        <p>Trân trọng,<br><strong>Trung Tâm Ngoại Ngữ</strong></p>
    </div>
    """

    msg = Message(
        subject=f'[Ngoại Ngữ Nhóm 7] Xác nhận đăng ký lớp {lop.tenLop}',
        recipients=[email_nhan],
        html=noi_dung_html
    )
    mail.send(msg)
    return True