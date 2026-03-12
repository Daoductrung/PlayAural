"""Asynchronous SMTP mailer utility."""

import smtplib
import asyncio
import logging
from email.message import EmailMessage
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..persistence.database import SmtpConfig


class SmtpMailer:
    """Handles sending emails asynchronously using standard smtplib."""

    @staticmethod
    async def send_email(
        config: "SmtpConfig",
        to_email: str,
        subject: str,
        body: str,
        html_body: str = None
    ) -> tuple[bool, str]:
        """
        Sends an email asynchronously based on the provided SMTP configuration.
        Returns a tuple of (success_boolean, error_message).
        """
        if not config or not config.host:
            return False, "SMTP is not configured."

        msg = EmailMessage()
        msg.set_content(body)
        if html_body:
            msg.add_alternative(html_body, subtype='html')

        msg['Subject'] = subject
        msg['From'] = f"{config.from_name} <{config.from_email}>"
        msg['To'] = to_email

        # Run the synchronous smtplib in a thread pool so it doesn't block the async event loop
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(
                None,
                SmtpMailer._send_email_sync,
                config,
                msg
            )
        except Exception as e:
            logging.exception("Failed to dispatch SMTP email task:")
            return False, str(e)

    @staticmethod
    def _send_email_sync(config: "SmtpConfig", msg: EmailMessage) -> tuple[bool, str]:
        """Synchronous part of sending email (runs in a separate thread)."""
        try:
            if config.encryption_type.lower() == 'ssl':
                # Implicit SSL (usually port 465)
                with smtplib.SMTP_SSL(config.host, config.port, timeout=10) as server:
                    if config.username and config.password:
                        server.login(config.username, config.password)
                    server.send_message(msg)
            else:
                # Standard SMTP or STARTTLS (usually port 587 or 25)
                with smtplib.SMTP(config.host, config.port, timeout=10) as server:
                    server.ehlo()
                    if config.encryption_type.lower() == 'tls':
                        # Use default SSL context for STARTTLS to ensure secure connection
                        import ssl
                        context = ssl.create_default_context()
                        server.starttls(context=context)
                        server.ehlo()
                    if config.username and config.password:
                        server.login(config.username, config.password)
                    server.send_message(msg)
            return True, ""
        except smtplib.SMTPException as e:
            logging.exception("SMTPException occurred while sending email:")
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            logging.exception("Unexpected connection error occurred while sending email:")
            return False, f"Connection error: {str(e)}"
