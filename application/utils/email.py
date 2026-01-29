from flask_mail import Message
from flask import current_app, url_for
from application import mail

def send_mail(subject, recipient, html_body):
    msg = Message(subject=subject, recipients=[recipient])
    msg.html = html_body
    mail.send(msg)
