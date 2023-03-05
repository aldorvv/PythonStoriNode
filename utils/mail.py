from pathlib import Path

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


class Email:
    def __init__(self, subject) -> None:
        self.subject = subject
        self.from_email = settings.EMAIL_HOST_USER
        self.html = None

    def compose(self, template, context):
        path = Path.cwd().joinpath(f"templates/{template}")
        print(path)
        self.html = render_to_string(str(path), context)

    def send_to(self, to):
        msg = EmailMessage(self.subject, self.html, self.from_email, [to])
        msg.content_subtype = "html"
        msg.send()
