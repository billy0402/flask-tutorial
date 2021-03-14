from threading import Thread

from flask import render_template, current_app
from flask_mail import Message

from . import mail


def async_send_email(app, message):
    with app.app_context():
        mail.send(message)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    message = Message(
        app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
        sender=app.config['FLASKY_MAIL_SENDER'],
        recipients=[to],
    )
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)

    thread = Thread(target=async_send_email, args=[app, message])
    thread.start()
    return thread
