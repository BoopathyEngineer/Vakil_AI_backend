import time
import random
from fastapi import HTTPException
from app.crud.user_crud import get_user_otp, fetch_user_email
from app.schemas.auth_schemas import AuthResponseDetails
from app.models.email_models import EmailId
from app.services.email_sent import send_otp_email
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

def get_email_for_verify(email,new_user,session):
    logger.info(f"Request received to verify email: {email} [status_code=100]")
    try:
        otp = random.randint(100000, 999999)
        otp_time = round(time.time())

        user_email = fetch_user_email(session,email)

        if not new_user and user_email:
            session.query(EmailId).filter(EmailId.email_id == email).update({'otp': otp, 'otp_time': otp_time})
            session.commit() 

        elif new_user and not user_email:
            email_id = get_user_otp(session,email)
            if email_id:
                email_id.otp = otp
                email_id.otp_time = otp_time
                session.add(email_id)
                session.commit()    
            elif not email_id:
                new_email_instance = EmailId(
                    email_id = email,
                    otp = otp,
                    otp_time = otp_time,
                )

                session.add(new_email_instance)
                session.commit()
        else:
            logger.warning(f"Verify your email: {email} [status_code=404]")
            raise HTTPException(status_code=404, detail="Verify your email")
        
        session.close()  
        email_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OTP Email</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.8;
            margin: 0;
            padding: 0;
            background-color: white;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background: #ffffff;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .logo {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .logo img {{
            max-width: 120px;
            height: auto;
        }}
        .header {{
            background-color: #031B3A;
            color: #ffffff;
            padding: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: bold;
            position: relative;
        }}
        .header img {{
            max-width: 40px; 
            height: 40px;
            border-radius: 90%;
            object-fit: cover;
            margin-right: 10px;
        }}
        .content {{
            font-size: 16px;
            padding: 20px;
            line-height: 1.6;
        }}
        .otp {{
            font-size: 18px;
            font-weight: bold;
            color: #007BFF;
            text-align: center;
            margin: 20px 0;
        }}
        p {{
            color: black;
            text-align: left;
        }}
        a {{
            color: #007BFF;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            font-size: 12px;
            color: #777;
            padding: 15px;
            text-align: center;
            background-color: #f1f1f1;
            border-top: 1px solid #ddd;
        }}
        .footer a {{
            color: #007bff;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <div><strong>Hello User,</strong></div>

            <p>We received a request to log in to your account. To proceed, please use the One-Time Password (OTP) below:</p>

            <div class="otp">Your OTP is: {otp}</div>

            <div style="text-align: center;">
                This OTP will expire in <strong>5 minutes</strong>.
            </div>

            <p>If you did not request this OTP, please ignore this message or contact us at <a href="mailto:procodeworkit@gmail.com">procodeworkit@gmail.com</a> for assistance.</p>

            <p>Best regards,<br>The Hyperflex Team</p>
        </div>

        <div class="footer">
            <strong>Note:</strong> This is an automated message. Please do not reply to this email.
        </div>
    </div>
</body>
</html>
"""

        send_otp_email(email,email_body)
        AuthResponseDetails.message = "Otp sent to your Email"
        logger.info(f"OTP sent successfully to email: {email} [status_code=200]")
        return AuthResponseDetails
    
    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(f"Error verifying email: {email} [status_code=400] - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail="Error Occured")
