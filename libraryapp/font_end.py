from flask import Flask, render_template

app = Flask(__name__)

class MockRole:
    name = 'ADMIN'

class MockUser:
    is_authenticated = True
    name = "test"
    username = "test"
    email = "test@ou.edu.vn"
    phone = "0123456789"
    user_role = MockRole()

@app.context_processor
def inject_user():
    return dict(current_user=MockUser())

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

@app.route('/admin', strict_slashes=False)
def view_admin():
    return render_template('admin/admin.html')

if __name__ == '__main__':
    print("Trang chu:        http://127.0.0.1:5000/")
    print("Dang nhap:        http://127.0.0.1:5000/login")
    print("Dang ky:          http://127.0.0.1:5000/register")
    print("Ho so:            http://127.0.0.1:5000/profile")
    print("Quan tri:         http://127.0.0.1:5000/admin")
    app.run(debug=True, port=5000)