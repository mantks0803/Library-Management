from flask import Flask, render_template
from datetime import datetime, timedelta

app = Flask(__name__)



class MockRole:
    name = 'READER'


class MockUser:
    is_authenticated = True
    name = "(UI Test)"
    username = "man_student_123"
    email = "man@ou.edu.vn"
    phone = "0123456789"
    user_role = MockRole()


class MockBook:
    def __init__(self, id, title, author, type_name, publish_year, quantity):
        self.id = id
        self.title = title
        self.author = author
        self.type = type_name
        self.publish_year = publish_year
        self.quantity = quantity


@app.context_processor
def inject_user():
    return dict(current_user=MockUser())


#old
@app.route('/')
def view_index():
    return render_template('index.html')


@app.route('/login')
def view_login():
    return render_template('auth/login.html')


@app.route('/register')
def view_register():
    return render_template('auth/register.html')


@app.route('/profile')
def view_profile():
    return render_template('auth/profile.html')


@app.route('/admin')
def view_admin():
    return render_template('admin/admin.html')


#test route
@app.route('/book/<int:book_id>')
def view_book_detail(book_id):
    # Tạo 1 cuốn sách giả dựa vào Model của Backend
    book = MockBook(book_id, "Frieren: Beyond Journey's End", "Kanehito Yamada", "Truyện tranh", 2020, 5)
    return render_template('reader/book_detail.html', book=book)


@app.route('/borrow_confirm/<int:book_id>')
def view_borrow_confirm(book_id):
    book = MockBook(book_id, "Frieren: Beyond Journey's End", "Kanehito Yamada", "Truyện tranh", 2020, 5)

    # Tính toán ngày mượn (hôm nay) và hạn trả (cộng thêm 7 ngày)
    borrow_date = datetime.now().strftime("%d/%m/%Y")
    due_date = (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")

    return render_template('reader/borrow_confirm.html', book=book, borrow_date=borrow_date, due_date=due_date)


if __name__ == '__main__':


    print("Trang chu:        http://127.0.0.1:5000/")
    print("Dang nhap:        http://127.0.0.1:5000/login")
    print("Dang ky:          http://127.0.0.1:5000/register")
    print("Ho so:            http://127.0.0.1:5000/profile")
    print("Quan tri:         http://127.0.0.1:5000/admin")
    print("Chi tiet sach:    http://127.0.0.1:5000/book/1")
    print("==================================================")
    app.run(debug=True, port=5000)