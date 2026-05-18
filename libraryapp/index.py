from libraryapp.routes import home, login_logout, register, book_detail, borrow_cart, borrow_history, return_slips, book_management, slip_management
from libraryapp.dao.users import get_current_user
from libraryapp.api import api_users, api_cart
from libraryapp import app, login
# from libraryapp.admin import *

@login.user_loader
def load_user(user_id):
    return get_current_user(user_id)

def register_routes():
    app.register_blueprint(home.home_bp)
    app.register_blueprint(login_logout.login_logout_bp)
    app.register_blueprint(register.register_bp)
    app.register_blueprint(book_detail.book_bp)
    app.register_blueprint(borrow_cart.borrow_bp)
    app.register_blueprint(borrow_history.history_bp)
    app.register_blueprint(return_slips.return_slips_bp)
    app.register_blueprint(book_management.book_management_bp)
    app.register_blueprint(slip_management.slip_management_bp)

def register_api():
    app.register_blueprint(api_users.api_users_bp)
    app.register_blueprint(api_cart.api_cart_bp)

if __name__ == '__main__':
    register_routes()
    register_api()
    app.run(debug=True)