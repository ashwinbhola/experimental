from flask import Flask, render_template, session, redirect, url_for
from config import Config
from models import db
from auth.routes import auth_bp
from forms import FlaskForm
from flask_session import Session

app = Flask(__name__)

app.config.from_object(Config)

Session(app)

db.init_app(app)

# Register blueprint
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return redirect(url_for("auth.login"))


@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html", username=session["username"])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
