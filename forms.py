from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Optional
from wtforms.fields import DateField, TimeField

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class NoteForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=1, max=500)])
    category = StringField('Category', validators=[Optional()])  # Новое поле для категории, необязательное
    reminder_date = DateField('Reminder Date', validators=[Optional()], format='%Y-%m-%d')
    reminder_time = TimeField('Reminder Time', validators=[Optional()], format='%H:%M') # Новое поле для времени напоминания, необязательное
    submit = SubmitField('Save Note')