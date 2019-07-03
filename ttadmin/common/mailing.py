import logging
from smtplib import SMTP_SSL, SMTPException
from email.message import EmailMessage

from django.conf import settings

logger = logging.getLogger()


def send_email(to, body, subject='a message from tilde.town'):
    """Sends an email using external SMTP. Logs on failure."""
    em = EmailMessage()
    em['Subject'] = subject
    em['From'] = 'root@tilde.town'
    em['To'] = to
    em.set_content(body)
    try:
        with SMTP_SSL(port=settings.SMTP_PORT, host=settings.SMTP_HOST) as smtp:
            smtp.login('root@tilde.town', settings.SMTP_PASSWORD)
            smtp.send_message(em)
            smtp.quit()
    except SMTPException as e:
        logger.error(f'failed to send email "{subject}" to {to}: {e}')
        return False

    return True
