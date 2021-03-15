from random import randint

from faker import Faker
from sqlalchemy.exc import IntegrityError

from . import db
from .models import User, Post


def users(count=100):
    faker = Faker()
    i = 0
    while i < count:
        user = User(
            email=faker.email(),
            username=faker.user_name(),
            password='password',
            confirmed=True,
            name=faker.name(),
            location=faker.city(),
            about_me=faker.text(),
            member_since=faker.past_date(),
        )
        db.session.add(user)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    faker = Faker()
    user_count = User.query.count()
    for i in range(count):
        user = User.query.offset(randint(0, user_count - 1)).first()
        post = Post(
            body=faker.text(),
            timestamp=faker.past_date(),
            author=user,
        )
        db.session.add(post)
    db.session.commit()
