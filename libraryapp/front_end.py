from flask import Flask, render_template, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.context_processor
def inject_user():
    current_role = request.args.get('role', 'READER').upper()

    class MockRole:
        name = current_role

    class MockUser:
        is_authenticated = True
        name = "Thanh Thuận (Admin)" if current_role == 'ADMIN' else "Thanh Mẫn (Sinh viên)"
        username = "admin_ou" if current_role == 'ADMIN' else "man_student_123"
        email = "thuan@gmail.com" if current_role == 'ADMIN' else "man@ou.edu.vn"
        phone = "0334903055" if current_role == 'ADMIN' else "0123456789"
        user_role = MockRole()

    return dict(current_user=MockUser())


class MockBook:
    def __init__(self, id, title, author, type_name, publish_year, quantity):
        self.id = id
        self.title = title
        self.author = author
        self.type = type_name
        self.publish_year = publish_year
        self.quantity = quantity


@app.route('/', strict_slashes=False)
def view_index():
    return render_template('index.html')


@app.route('/login', strict_slashes=False)
def view_login():
    return render_template('auth/login.html')


@app.route('/register', strict_slashes=False)
def view_register():
    return render_template('auth/register.html')


@app.route('/profile', strict_slashes=False)
def view_profile():
    return render_template('auth/profile.html')


@app.route('/admin', strict_slashes=False)
def view_admin():
    return render_template('admin/index.html')


@app.route('/book/<int:book_id>', strict_slashes=False)
def view_book_detail(book_id):
    book = MockBook(book_id, "Frieren: Beyond Journey's End", "Kanehito Yamada", "Truyện tranh", 2020, 5)
    return render_template('reader/book_detail.html', book=book)


@app.route('/borrow_confirm/<int:book_id>', strict_slashes=False)
def view_borrow_confirm(book_id):
    book = MockBook(book_id, "Frieren: Beyond Journey's End", "Kanehito Yamada", "Truyện tranh", 2020, 5)
    borrow_date = datetime.now().strftime("%d/%m/%Y")
    due_date = (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")
    return render_template('reader/borrow_confirm.html', book=book, borrow_date=borrow_date, due_date=due_date)


if __name__ == '__main__':

    print("DANG CHAY CHE DO TEST GIAO DIEN (KHONG BACKEND)")
    print("Trang chu (Sinh vien):    http://127.0.0.1:5000/?role=reader")
    print("Trang chu (Admin):        http://127.0.0.1:5000/?role=admin")
    print("Trang Quan tri (Admin):   http://127.0.0.1:5000/admin?role=admin")
    print("Chi tiet sach:            http://127.0.0.1:5000/book/1?role=reader")
    print("Ho so:                    http://127.0.0.1:5000/profile?role=reader")
    app.run(debug=True, port=5000)