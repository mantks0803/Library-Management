from flask import render_template
from libraryapp import app, login
from libraryapp.routes.login_logout import login_logout_bp
from libraryapp.routes.register import register_bp
from libraryapp.dao.users import get_current_user


app.register_blueprint(login_logout_bp)
app.register_blueprint(register_bp)


@login.user_loader
def load_user(user_id):
    return get_current_user(user_id)


@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True, port=5000)