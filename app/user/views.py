from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    request,
    current_app,
)
from flask_login import login_required, current_user

from . import user
from .forms import EditForm, AdminEditForm
from .. import db
from ..decorators import admin_required, permission_required
from ..models import User, Role, Post, Permission


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


@user.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid user.')
        return redirect(url_for('.index'))

    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.index', username=username))

    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}.')
    return redirect(url_for('.index', username=username))


@user.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid user.')
        return redirect(url_for('.index'))

    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.index', username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username} anymore.')
    return redirect(url_for('.index', username=username))


@user.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid user.')
        return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page,
        per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False,
    )
    follows = [
        {'user': item.follower, 'timestamp': item.timestamp}
        for item in pagination.items
    ]
    return render_template(
        'user/followers.html',
        user=user,
        title='Followers of',
        endpoint='.followers',
        pagination=pagination,
        follows=follows,
    )


@user.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Invalid user.')
        return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page,
        per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False,
    )
    follows = [
        {'user': item.followed, 'timestamp': item.timestamp}
        for item in pagination.items
    ]
    return render_template(
        'user/followers.html',
        user=user,
        title="Followed by",
        endpoint='.followed_by',
        pagination=pagination,
        follows=follows,
    )
