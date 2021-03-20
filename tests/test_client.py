import re
import unittest

from app import create_app, db
from app.models import Role, User


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Stranger' in response.get_data(as_text=True))

    def test_register_and_login(self):
        # 註冊新帳號
        response = self.client.post('/auth/register', data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'cat',
            'password2': 'cat',
        })
        self.assertEqual(response.status_code, 302)

        # 用新帳號登入
        response = self.client.post('/auth/login', data={
            'email': 'john@example.com',
            'password': 'cat',
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            re.search(r'Hello,\s+john!', response.get_data(as_text=True)),
        )
        self.assertTrue(
            'You have not confirmed your account yet'
            in response.get_data(as_text=True),
        )

        # 傳送確認權杖
        user = User.query.filter_by(email='john@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(
            f'/auth/confirm/{token}',
            follow_redirects=True,
        )
        user.confirm(token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            'You have confirmed your account'
            in response.get_data(as_text=True),
        )

        # 登出
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            'You have been logged out' in response.get_data(as_text=True),
        )
