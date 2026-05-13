from smtplib import SMTPException

from flask import current_app, render_template
from flask_mail import Message

from app.extensions import mail


def send_email(to: list[str | tuple[str, str]], *, subject: str, template: str, **context) -> None:
    body = render_template(f'emails/{template}.txt', **context)
    html = render_template(f'emails/{template}.html', **context)

    msg = Message(
        subject=subject,
        recipients=to,
        body=body,
        html=html,
    )

    try:
        with mail.connect() as conn:  # ty:ignore[invalid-context-manager]
            conn.send_message(msg)
    except SMTPException:
        current_app.logger.exception('Erro ao enviar email')
        raise
