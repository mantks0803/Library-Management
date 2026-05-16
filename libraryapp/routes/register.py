from flask import Blueprint, render_template, redirect, request
import libraryapp.dao.users as users_dao

register_bp = Blueprint("register", __name__)

@register_bp.route("/register", methods=["GET"])
def register_view():
    return render_template("auth/register.html",form={})

@register_bp.route("/register", methods=["POST"])
def register_process():
    username = request.form.get("username")
    if not users_dao.validate_username(username):
        return render_template("auth/register.html", err_msg="Tên đăng nhập đã tồn tại, vui lòng chọn tên khác!")

    phone = request.form.get("phone")
    if not users_dao.validate_phone(phone):
        return render_template("auth/register.html", err_msg="Số điện thoại không hợp lệ!")

    password = request.form.get("password")
    confirm = request.form.get("confirm")
    if not users_dao.validate_password(password, confirm):
        return render_template("auth/register.html", err_msg="Mật khẩu không khớp, vui lòng nhập lại!", form=request.form)

    name = request.form.get("name")
    email = request.form.get("email")

    try:
        users_dao.add_user(name=name, phone=phone, email=email, username=username, password=password)
        #succes
        return redirect("/login?success=1")
    except ValueError as e:
        return render_template("auth/register.html", form=request.form, err_msg=str(e))
    except Exception as ex:
        print(ex)
        return render_template("auth/register.html", err_msg="Lỗi hệ thống, vui lòng thử lại sau!")