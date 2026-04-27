from email.message import EmailMessage
import smtplib


def send_fiscal_email(
    smtp_host: str | None,
    smtp_port: int,
    smtp_user: str | None,
    smtp_password: str | None,
    sender: str | None,
    recipient: str,
    subject: str,
    xml: str,
) -> None:
    if not smtp_host or not sender:
        raise ValueError("SMTP no configurado")
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content("Adjuntamos su comprobante electrónico.")
    message.add_attachment(xml.encode("utf-8"), maintype="application", subtype="xml", filename="comprobante.xml")
    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        server.starttls()
        if smtp_user and smtp_password:
            server.login(smtp_user, smtp_password)
        server.send_message(message)
