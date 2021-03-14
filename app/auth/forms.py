from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    Regexp,
    EqualTo,
    ValidationError,
)

from ..models import User


class LoginForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Length(1, 64), Email()],
    )
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Length(1, 64), Email()],
    )
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                r'^[A-Za-z][A-Za-z0-9_.]*$',
                message='Username must only have letters, numbers, dots or underscores',  # noqa E501
            ),
        ],
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            EqualTo('password2', message='Passwords must match'),
        ],
    )
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('This email is already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('This username is already used.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField(
        'New password',
        validators=[
            DataRequired(),
            EqualTo('password2', message='Passwords must match.'),
        ],
    )
    password2 = PasswordField(
        'Confirm new password',
        validators=[DataRequired()],
    )
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        'Email',
        validators=[DataRequired(), Length(1, 64), Email()],
    )
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        'New Password',
        validators=[
            DataRequired(),
            EqualTo('password2', message='Passwords must match'),
        ],
    )
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')


class ChangeEmailForm(FlaskForm):
    email = StringField(
        'New Email',
        validators=[DataRequired(), Length(1, 64), Email()],
    )
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('This email is already registered.')
