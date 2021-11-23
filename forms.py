from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, StringField, PasswordField
from wtforms.validators import InputRequired

class UserForm(FlaskForm):
    username = StringField("username",validators=[InputRequired()])
    password = PasswordField("password",validators=[InputRequired()])
    email = StringField("email", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField("username",validators=[InputRequired()])
    password = PasswordField("password",validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    title = StringField("Title",validators=[InputRequired()])
    content = TextAreaField("Content", validators=[InputRequired()])
