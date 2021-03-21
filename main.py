import os
import sys

import click
from dotenv import load_dotenv
from flask_migrate import Migrate, upgrade

from app import create_app, db
from app.models import User, Role, Permission, Follow, Post, Comment

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

COV = None
if os.environ.get('FLASKY_COVERAGE'):
    import coverage

    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

app = create_app(os.getenv('FLASK_CONFIG', 'default'))
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Role=Role,
        Permission=Permission,
        Follow=Follow,
        Post=Post,
        Comment=Comment,
    )


@app.cli.command()
@click.option(
    '--coverage/--no-coverage',
    default=False,
    help='Run tests under code coverage.',
)
def test(coverage):
    """
    Run the unit tests
    """
    if coverage and not os.environ.get('FLASKY_COVERAGE'):
        os.environ['FLASKY_COVERAGE'] = 'true'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        base_dir = os.path.abspath(os.path.dirname(__file__))
        cov_dir = os.path.join(base_dir, 'tmp/coverage')
        COV.html_report(directory=cov_dir)
        print(f'HTML version: file://{cov_dir}/index.html')
        COV.erase()


@app.cli.command()
@click.option(
    '--length',
    default=25,
    help='Number of functions to include in the profiler report.',
)
@click.option(
    '--profile-dir',
    default=None,
    help='Directory where profiler data files are saved.',
)
def profile(length, profile_dir):
    """
    Start the application under the code profiler.
    """
    from werkzeug.middleware.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app,
        restrictions=[length],
        profile_dir=profile_dir,
    )
    os.environ['FLASK_RUN_FROM_CLI'] = 'false'
    app.run(debug=False)


@app.cli.command()
def deploy():
    """
    Run deployment tasks
    """
    # 將資料庫遷移至最新版本
    upgrade()

    # 建立或更新使用者角色
    Role.insert_roles()

    # 確認所有使用者都追隨他們自己
    User.add_self_follows()
