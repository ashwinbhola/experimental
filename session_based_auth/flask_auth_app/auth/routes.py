from functools import wraps

from flask import Blueprint, current_app, g, render_template, request, redirect, url_for, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User
from forms import LoginForm, RegisterForm


auth_bp = Blueprint("auth", __name__)

def logged_in_redirect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if getattr(g, "user_id", None):
            return redirect(url_for("dashboard"))

        return f(*args, **kwargs)
    return decorated_function


def render_register_form(form):
    return render_template("register.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
@logged_in_redirect
def register():

    form = RegisterForm()

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("auth.register"))
        
        if User.query.filter_by(email_id=form.email_id.data).first():
            flash("Email ID already exists.", "danger")
            return redirect(url_for("auth.register"))
        
        hashed_pw = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email_id=form.email_id.data,
            password_hash=hashed_pw
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))
    
    
    return render_register_form(form)


def render_login_form(form):
    return render_template("login.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
@logged_in_redirect
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not check_password_hash(user.password_hash, form.password.data):
            flash("Invalid username or password.", "danger")
            return redirect(url_for("auth.login"))

        user_id = user.user_id
        session_id = current_app.session_manager.generate_session_id()
        current_app.session_manager.store_session_in_redis(session_id, user_id)

        flash("Login successful.", "success")

        resp = make_response(redirect(url_for("dashboard")))
        current_app.session_manager.set_session_cookie(resp, session_id)
        return resp
    
    return render_login_form(form)


@auth_bp.route('/logout')
def logout():
    session_id = request.cookies.get('session_id')
    if session_id:
        current_app.session_manager.delete_session_from_redis(session_id)
        print(f"Session {session_id} deleted from Redis.")
    
    response = make_response(redirect(url_for("auth.login")))
    # Optionally, clear the cookie from the browser explicitly
    response.set_cookie("session_id", "", expires=0, httponly=True, samesite="Lax")
    print("User logged out and cookie cleared.")
    flash("Logged out successfully.", "info")
    return response