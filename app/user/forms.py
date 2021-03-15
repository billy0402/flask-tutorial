from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    TextAreaField,
    BooleanField,
    SelectField,
)
from wtforms.validators import (
    Length,
    DataRequired,
    Email,
    Regexp,
    ValidationError,
)

from ..models import Role, User


class EditForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class AdminEditForm(FlaskForm):
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
    role = SelectField('Role', coerce=int)
    confirmed = BooleanField('Confirmed')
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role.choices = [
            (role.id, role.name)
            for role in Role.query.order_by(Role.name).all()
        ]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('This email is already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('This username is already used.')
