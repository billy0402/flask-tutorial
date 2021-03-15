from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from . import user
from .forms import EditForm, AdminEditForm
from .. import db
from ..decorators import admin_required
from ..models import User, Role, Post


@user.route('/<username>')
def index(username):
    user = User.query.filter_by(username=username).first_or_404()
    if not user:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user/index.html', user=user, posts=posts)


@user.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated')
        return redirect(
            url_for('.index', username=current_user.username),
        )

    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('user/edit.html', form=form)


@user.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit(id):
    user = User.query.get_or_404(id)
    form = AdminEditForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        user.confirmed = form.confirmed.data
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.index', username=user.username))

    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role
    form.confirmed.data = user.confirmed
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('user/edit.html', form=form, user=user)
