from flask import Blueprint, render_template, redirect, request, flash
import libraryapp.dao.users as users_dao

register_bp = Blueprint("register", __name__)

@register_bp.route("/register", methods=["GET"])
def register_view():
    return render_template("auth/register.html",form={})

@register_bp.route("/register", methods=["POST"])
def register_process():
    username = request.form.get("username")
    phone = request.form.get("phone")
    password = request.form.get("password")
    confirm = request.form.get("confirm")
    name = request.form.get("name")
    email = request.form.get("email")

    try:
        users_dao.add_user(
            name=name,
            phone=phone,
            email=email,
            username=username,
            password=password,
            confirm=confirm
        )

        flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
        return redirect("/login")
    except ValueError as e:
        return render_template(
            "auth/register.html",
            form=request.form,
            err_msg=str(e)
        )
    except Exception as ex:
        print(ex)
        return render_template(
            "auth/register.html",
            form=request.form,
            err_msg="Lỗi hệ thống, vui lòng thử lại sau!"
        )
