from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegisterForm(FlaskForm):
    class Meta:
        csrf = False
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    email_id = StringField("Email ID", validators=[DataRequired(), Length(min=3, max=50)])
    password = StringField("Password", validators=[DataRequired(), Length(min=8, max=256)])
    confirm_password = StringField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    class Meta:
        csrf = False
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    password = StringField("Password", validators=[DataRequired(), Length(min=8, max=256)])
    submit = SubmitField("Login")