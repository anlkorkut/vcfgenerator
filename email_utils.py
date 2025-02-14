'''
email_utils.py code file.
'''

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.logger import nb_logger

logger = nb_logger.init(__name__)

# Hardcoded email configuration
SENDER_EMAIL = "erpjunior321@gmail.com"  # Replace with your email
SENDER_PASSWORD = "fhyf micj owgu ocan"   # Replace with your app password
RECIPIENT_EMAIL = "anlkorkut11@gmail.com" # Replace with recipient email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_missing_contacts_email(contacts):
    """
    Send an email with the list of contacts that have missing phone numbers.

    Args:
        contacts: List of contact names with missing phone numbers
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = 'Contacts Missing Phone Numbers'

        # Create email body
        body = "The following contacts are missing phone numbers:\n\n"
        for name in contacts:
            body += f"- {name}\n"
        body += "\nPlease provide phone numbers for these contacts."

        msg.attach(MIMEText(body, 'plain'))

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        logger.info(f"Successfully sent missing contacts email to {RECIPIENT_EMAIL}")
        return True, "Email sent successfully!"

    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        logger.error(error_msg)
        return False, error_msg