from flask import Flask, render_template, redirect, url_for, request, current_app
from flask.sessions import SecureCookieSessionInterface, SessionMixin
from config import Config
from models import db
from forms import FlaskForm

from session_store import RedisSessionManager

app = Flask(__name__)

app.config.from_object(Config)
app.session_manager = RedisSessionManager(app.config)

db.init_app(app)

# Register blueprint
from auth.routes import auth_bp
app.register_blueprint(auth_bp)


@app.route('/')
def index():
    if (session_id := request.cookies.get("session_id")):
        # Access session_manager through current_app for safety in routes
        user_id = current_app.session_manager.get_user_from_session(session_id)
        if user_id:
            return redirect(url_for("dashboard"))
    return redirect(url_for("auth.login"))


@app.route('/dashboard')
def dashboard():
    if (session_id := request.cookies.get("session_id")):
        user_id = current_app.session_manager.get_user_from_session(session_id)
        if user_id:
            return render_template("dashboard.html", username=user_id)
    return redirect(url_for("auth.login"))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
