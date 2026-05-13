from flask import current_app

from app.features.auth.models import User
from app.utils import send_email


def send_confirm_email(user: User, token: str) -> None:
    email_url = current_app.config['MAIL_CONFIRM_URL']
    url = f'{email_url}?token={token}'

    send_email(
        [user.email],
        subject='Confirme seu email',
        template='confirm_email',
        user=user,
        url=url,
    )


def send_reset_password_email(user: User, token: str) -> None:
    email_url = current_app.config['MAIL_RESET_PASSWORD_URL']
    url = f'{email_url}?token={token}'

    send_email(
        [user.email],
        subject='Reset your password',
        template='reset_password',
        user=user,
        url=url,
    )


def send_tfa_otp_email(user: User, code: str) -> None:
    send_email(
        [user.email],
        subject='Seu código de verificação',
        template='otp_code',
        user=user,
        code=code,
    )
