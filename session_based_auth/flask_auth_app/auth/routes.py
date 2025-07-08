from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User
from forms import LoginForm, RegisterForm


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if (session_id := request.cookies.get("session_id")):
        user_id = current_app.session_manager.get_user_from_session(session_id)
        if user_id:
            return redirect(url_for("dashboard"))

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
    
    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if (session_id := request.cookies.get("session_id")):
        user_id = current_app.session_manager.get_user_from_session(session_id)
        if user_id:
            return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not check_password_hash(user.password_hash, form.password.data):
            flash("Invalid username or password.", "danger")
            return redirect(url_for("auth.login"))

        user_id = user.user_id
        print(f"User exists!: {user_id}")
        session_id = current_app.session_manager.generate_session_id()
        current_app.session_manager.store_session_in_redis(session_id, user_id)

        print("Success")
        flash("Login successful.", "success")

        resp = make_response(redirect(url_for("dashboard")))
        current_app.session_manager.set_session_cookie(resp, session_id)
        return resp
    
    return render_template("login.html", form=form)


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