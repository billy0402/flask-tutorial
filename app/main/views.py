from flask import (
    url_for,
    render_template,
    redirect,
    request,
    current_app,
    abort,
    flash,
    make_response,
)
from flask_login import current_user, login_required

from . import main
from .forms import PostForm
from .. import db
from ..models import Permission, Post


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and \
            form.validate_on_submit():
        post = Post(
            body=form.body.data,
            author=current_user._get_current_object(),
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))

    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False,
    )
    posts = pagination.items
    return render_template(
        'index.html',
        form=form,
        posts=posts,
        show_followed=show_followed,
        pagination=pagination,
    )


@main.route('/all')
@login_required
def show_all():
    response = make_response(redirect(url_for('.index')))
    response.set_cookie(
        'show_followed',
        '',
        max_age=30 * 24 * 60 * 60,  # 30 days
    )
    return response


@main.route('/followed')
@login_required
def show_followed():
    response = make_response(redirect(url_for('.index')))
    response.set_cookie(
        'show_followed',
        '1',
        max_age=30 * 24 * 60 * 60,  # 30 days
    )
    return response


@main.route('/post/<int:id>')
def show(id):
    post = Post.query.get_or_404(id)
    return render_template('show.html', posts=[post])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.show', id=post.id))
    form.body.data = post.body
    return render_template('edit.html', form=form)
