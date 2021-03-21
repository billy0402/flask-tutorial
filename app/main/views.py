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
from flask_sqlalchemy import get_debug_queries

from . import main
from .forms import PostForm, CommentForm
from .. import db
from ..decorators import permission_required
from ..models import Permission, Post, Comment


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: {}\nParameters{}\nDuration{}\nContext{}\n'.format(
                    query.statement,
                    query.parameters,
                    query.duration,
                    query.context,
                ),
            )
    return response


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


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def show(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            post=post,
            author=current_user._get_current_object(),
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('.show', id=post.id, page=-1))

    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page,
        per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False,
    )
    comments = pagination.items
    return render_template(
        'show.html',
        posts=[post],
        form=form,
        comments=comments,
        pagination=pagination,
    )


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


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False,
    )
    comments = pagination.items
    return render_template(
        'moderate.html',
        comments=comments,
        pagination=pagination,
        page=page,
    )


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    return redirect(url_for('.moderate', page=page))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    return redirect(url_for('.moderate', page=page))


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)

    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)

    shutdown()
    return 'Shutting down...'
