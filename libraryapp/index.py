from libraryapp.routes import home, login_logout, register, infor_user

from libraryapp.api import api_users
from libraryapp import app, login
from libraryapp import admin

@login.user_loader
def load_user(user_id):
    return infor_user.get_current_user(user_id)

def register_routes():
    app.register_blueprint(home.home_bp)
    app.register_blueprint(login_logout.login_logout_bp)
    app.register_blueprint(register.register_bp)
    app.register_blueprint(infor_user.infor_user_bp)

def register_api():
    app.register_blueprint(api_users.api_users_bp)


if __name__ == '__main__':
    register_routes()
    register_api()
    app.run(debug=True)