import os
from dotenv import load_dotenv
load_dotenv(override=True)

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
FROM_EMAIL = os.getenv("FROM_EMAIL")
PASSWORD = os.getenv("PASSWORD")

def send_otp_email(email,message):
    logger.info(f"Request received to send OTP email to: {email} [status_code=100]")
    subject = "Your OTP Code"
    if PASSWORD is None:
        logger.error("EMAIL_PASSWORD environment variable is not set [status_code=500]")
        print("Error: The EMAIL_PASSWORD environment variable is not set.")
        return
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'html'))
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()  
        server.login(FROM_EMAIL, PASSWORD)
        server.sendmail(FROM_EMAIL, email, msg.as_string())
        return {"message": "Mail sent"} 
    except Exception as e:
        logger.error(f"Error sending OTP email to: {email} [status_code=500] - {e}", exc_info=True)
        raise