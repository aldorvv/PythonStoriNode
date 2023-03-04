from django.conf import settings
from django.core.mail import send_mail


class Email:
    def __init__(self, subject, content) -> None:
        self.subject = subject
        self.message = content
        self.from_email = settings.EMAIL_HOST_USER

    def send(self, to):
        send_mail(**self.__dict__, recipient_list=to)
