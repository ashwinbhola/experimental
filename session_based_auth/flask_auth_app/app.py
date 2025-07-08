from functools import wraps

from flask import Flask, render_template, redirect, url_for, request, current_app
from flask.sessions import SecureCookieSessionInterface, SessionMixin
from config import Config
from models import db, User
from forms import FlaskForm

from session_store import RedisSessionManager

app = Flask(__name__)

app.config.from_object(Config)
app.session_manager = RedisSessionManager(app.config)

db.init_app(app)

# Register blueprint
from auth.routes import auth_bp
app.register_blueprint(auth_bp)

def redirect_to_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if (session_id := request.cookies.get("session_id")):
            user_id = current_app.session_manager.get_user_from_session(session_id)
            if user_id:
                return f(user_id=user_id, *args, **kwargs)

        return redirect(url_for("auth.login"))
    return decorated_function


@app.route('/')
@redirect_to_login
def index(*args, **kwargs):
    return redirect(url_for("auth.login"))


@app.route('/dashboard')
@redirect_to_login
def dashboard(user_id, *args, **kwargs):
    user = User.query.filter_by(user_id=user_id).first()
    return render_template("dashboard.html", username=user.username)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
