from flask import Blueprint, render_template
from flask_login import current_user
from libraryapp.utils import permission
from libraryapp.dao.users import get_current_user
from libraryapp.dao.books import get_book
from libraryapp.dao.readers import get_reader
from libraryapp.dao.borrow_history import get_borrow_slip, get_all_reader_borrow_details
from datetime import datetime

history_bp = Blueprint('borrow_history', __name__)

@history_bp.route('/history', methods=['GET'])
@permission()
def render_borrow_history():
    user = get_current_user(current_user.id)
    reader = get_reader(user.id)

    history_list = []

    if reader:
        # Lấy tất cả chi tiết phiếu mượn của reader
        book_slip_details = get_all_reader_borrow_details(reader.id)

        # Nhóm chi tiết theo borrow_slip_id
        slips_dict = {}
        for detail in book_slip_details:
            book = get_book(detail.book_id)
            borrow_slip = get_borrow_slip(detail.borrow_slip_id)

            # Xác định trạng thái
            if detail.is_returned:
                status = 'Đã trả'
            elif borrow_slip and borrow_slip.due_date < datetime.now():
                status = 'Quá hạn'
            else:
                status = 'Đang mượn'

            # Tạo khóa phiếu mượn
            slip_key = borrow_slip.id if borrow_slip else 'unknown'

            # Nếu chưa có phiếu này trong dict, tạo mới
            if slip_key not in slips_dict:
                slips_dict[slip_key] = {
                    'slip_id': borrow_slip.id if borrow_slip else 'N/A',
                    'borrow_date': borrow_slip.borrow_date.strftime('%d/%m/%Y') if borrow_slip else 'N/A',
                    'due_date': borrow_slip.due_date.strftime('%d/%m/%Y') if borrow_slip else 'N/A',
                    'books': []
                }

            # Thêm sách vào phiếu mượn này
            slips_dict[slip_key]['books'].append({
                'detail_id': detail.id,
                'title': book.title if book else 'N/A',
                'return_date': detail.return_date.strftime('%d/%m/%Y') if detail.return_date else None,
                'status': status
            })

        # Chuyển dict thành list
        history_list = list(slips_dict.values())

    return render_template("reader/history.html",
                          user=user,
                          reader=reader,
                          history_list=history_list)


