from functools import wraps
import secrets

from flask import Flask, g, render_template, redirect, url_for, request, current_app, abort
from flask.sessions import SecureCookieSessionInterface, SessionMixin
from config import Config
from models import db, User
from forms import FlaskForm

from session_store import RedisSessionManager

app = Flask(__name__)

app.config.from_object(Config)
app.session_manager = RedisSessionManager(app.config)

db.init_app(app)


@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=g.get("csrf_token"))

@app.before_request
def before_request():
    CSRF_SESSION_ID = "csrf_session_id"
    SESSION_ID = "session_id"

    if (session_id := request.cookies.get(SESSION_ID)):
        g.user_id = app.session_manager.get_user_from_session(session_id)

    
    csrf_cookie_token = request.cookies.get(CSRF_SESSION_ID)

    if csrf_cookie_token is None:
        if request.method == "GET":
            # First time: generate token and set cookie
            g.csrf_token = secrets.token_hex(16)
            g.set_csrf_cookie = True
        else:
            # No token and not GET → fail
            abort(400, "Missing CSRF token")
    else:
        # Token exists in cookie → reuse it
        g.csrf_token = csrf_cookie_token
    
    if request.method in ['POST', 'PUT', 'DELETE']:
        token = request.headers.get("X-CSRF-Token")
        if not token or token != request.cookies.get(CSRF_SESSION_ID):
            print(token)
            print(request.cookies.get(CSRF_SESSION_ID))
            abort(400, "Invalid or missing CSRF token")

@app.after_request
def after_request(response):
    CSRF_SESSION_ID = "csrf_session_id"
    if getattr(g, "set_csrf_cookie", False):
        response.set_cookie(
            CSRF_SESSION_ID,
            g.csrf_token,
            httponly=True,
            samesite="Lax"
        )
    return response

# Register blueprint
from auth.routes import auth_bp
app.register_blueprint(auth_bp)

def redirect_to_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if getattr(g, "user_id", None):
            return f(*args, **kwargs)

        return redirect(url_for("auth.login"))
    return decorated_function


@app.route("/")
@redirect_to_login
def index():
    return redirect(url_for("auth.login"))


@app.route("/dashboard")
@redirect_to_login
def dashboard():
    user = User.query.filter_by(user_id=g.user_id).first()
    return render_template("dashboard.html", username=user.username)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
