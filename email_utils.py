'''
email_utils.py code file.
'''

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logger import init
import streamlit as st

logger = init(__name__)

def send_missing_contacts_email(contacts):
    """
    Send an email with the list of contacts that have missing phone numbers.

    Args:
        contacts: List of contact names with missing phone numbers
    """
    try:
        # Get email configuration from Streamlit secrets
        SENDER_EMAIL = st.secrets["EMAIL"]["sender"]
        SENDER_PASSWORD = st.secrets["EMAIL"]["password"]
        RECIPIENT_EMAIL = st.secrets["EMAIL"]["recipient"]
        SMTP_SERVER = st.secrets["EMAIL"]["smtp_server"]
        SMTP_PORT = st.secrets["EMAIL"]["smtp_port"]

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