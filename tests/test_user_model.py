import time
import unittest

from app import create_app, db
from app.models import User, Permission, Role, AnonymousUser


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        user = User(password='cat')
        self.assertTrue(user.password_hash is not None)

    def test_no_password_getter(self):
        user = User(password='cat')
        with self.assertRaises(AttributeError):
            user.password

    def test_password_verification(self):
        user = User(password='cat')
        self.assertTrue(user.verify_password('cat'))
        self.assertFalse(user.verify_password('dog'))

    def test_password_salts_are_random(self):
        user = User(password='cat')
        user2 = User(password='cat')
        self.assertNotEqual(user.password_hash, user2.password_hash)

    def test_valid_confirmation_token(self):
        user = User(password='cat')
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        self.assertTrue(user.confirm(token))

    def test_invalid_confirmation_token(self):
        user = User(password='cat')
        user2 = User(password='dog')
        db.session.add(user)
        db.session.add(user2)
        db.session.commit()
        token = user.generate_confirmation_token()
        self.assertFalse(user2.confirm(token))

    def test_expired_confirmation_token(self):
        user = User(password='cat')
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(user.confirm(token))

    def test_valid_reset_token(self):
        user = User(password='cat')
        db.session.add(user)
        db.session.commit()
        token = user.generate_reset_token()
        self.assertTrue(User.reset_password(token, 'dog'))
        self.assertTrue(user.verify_password('dog'))

    def test_invalid_reset_token(self):
        user = User(password='cat')
        db.session.add(user)
        db.session.commit()
        token = user.generate_reset_token()
        self.assertFalse(User.reset_password(token + 'a', 'dog'))
        self.assertTrue(user.verify_password('cat'))

    def test_valid_email_change_token(self):
        user = User(email='john@example.com', password='cat')
        db.session.add(user)
        db.session.commit()
        token = user.generate_email_change_token('susan@example.org')
        self.assertTrue(user.change_email(token))
        self.assertTrue(user.email == 'susan@example.org')

    def test_invalid_email_change_token(self):
        user = User(email='john@example.com', password='cat')
        user2 = User(email='susan@example.org', password='dog')
        db.session.add(user)
        db.session.add(user2)
        db.session.commit()
        token = user.generate_email_change_token('david@example.net')
        self.assertFalse(user2.change_email(token))
        self.assertTrue(user2.email == 'susan@example.org')

    def test_duplicate_email_change_token(self):
        user = User(email='john@example.com', password='cat')
        user2 = User(email='susan@example.org', password='dog')
        db.session.add(user)
        db.session.add(user2)
        db.session.commit()
        token = user2.generate_email_change_token('john@example.com')
        self.assertFalse(user2.change_email(token))
        self.assertTrue(user2.email == 'susan@example.org')

    def test_user_role(self):
        user = User(email='john@example.com', password='cat')
        self.assertTrue(user.can(Permission.FOLLOW))
        self.assertTrue(user.can(Permission.COMMENT))
        self.assertTrue(user.can(Permission.WRITE))
        self.assertFalse(user.can(Permission.MODERATE))
        self.assertFalse(user.can(Permission.ADMIN))

    def test_moderator_role(self):
        role = Role.query.filter_by(name='Moderator').first()
        user = User(email='john@example.com', password='cat', role=role)
        self.assertTrue(user.can(Permission.FOLLOW))
        self.assertTrue(user.can(Permission.COMMENT))
        self.assertTrue(user.can(Permission.WRITE))
        self.assertTrue(user.can(Permission.MODERATE))
        self.assertFalse(user.can(Permission.ADMIN))

    def test_administrator_role(self):
        role = Role.query.filter_by(name='Administrator').first()
        user = User(email='john@example.com', password='cat', role=role)
        self.assertTrue(user.can(Permission.FOLLOW))
        self.assertTrue(user.can(Permission.COMMENT))
        self.assertTrue(user.can(Permission.WRITE))
        self.assertTrue(user.can(Permission.MODERATE))
        self.assertTrue(user.can(Permission.ADMIN))

    def test_anonymous_user(self):
        user = AnonymousUser()
        self.assertFalse(user.can(Permission.FOLLOW))
        self.assertFalse(user.can(Permission.COMMENT))
        self.assertFalse(user.can(Permission.WRITE))
        self.assertFalse(user.can(Permission.MODERATE))
        self.assertFalse(user.can(Permission.ADMIN))
