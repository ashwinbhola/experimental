from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User
from forms import LoginForm, RegisterForm


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
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
    
    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not check_password_hash(user.password_hash, form.password.data):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))

        session.clear()
        session["user_id"] = user.user_id
        session["username"] = user.username
        session.permanent = True
        flash("Login successful.", "success")
        return redirect(url_for("dashboard"))
        
        flash('Invalid username or password.', 'danger')
    
    return render_template("login.html", form=form)


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))