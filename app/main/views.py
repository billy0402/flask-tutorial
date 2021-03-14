from flask import render_template, session, redirect, url_for, current_app

from . import main
from .forms import NameForm
from .. import db
from ..email import send_email
from ..models import User


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        username = form.name.data
        user = User.query.filter_by(username=username).first()
        if user:
            session['known'] = True
        else:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
            session['known'] = False

            if current_app.config['FLASKY_ADMIN']:
                send_email(
                    current_app.config['FLASKY_ADMIN'],
                    'New User',
                    'mail/new_user',
                    user=user,
                )
        session['name'] = username
        return redirect(url_for('.index'))
    return render_template(
        'index.html',
        form=form,
        name=session.get('name'),
        known=session.get('known', False),
    )
