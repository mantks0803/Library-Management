from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def test_index():

    return render_template('index.html')


@app.route('/login')
def test_login():
    return render_template('auth/login.html')



@app.route('/register')
def test_register():
    return render_template('auth/register.html')
#http://127.0.0.1:5000/register,login -> để xem các trang tương ứng
if __name__ == '__main__':
    app.run(debug=True, port=5000)