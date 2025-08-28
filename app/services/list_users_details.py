from fastapi import HTTPException
from app.models.user_models import User 
from app.schemas.user_schemas import UserHistory
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

def list_users_details(data,session):
    logger.info(f"Request received to list users with data: {data} [status_code=100]")
    try:
        id = data.get('id')
        role = data.get('role')
        list_users = []

        if role == 1:
            admins = session.query(User).filter(User.role == 2).order_by(User.updated_at.desc()).all()

            for admin in admins:
                details = UserHistory(
                    id = admin.id,
                    role = admin.role,
                    username = admin.username,
                    dob = admin.dob,
                    phone_number = admin.phone_no, 
                    email = admin.email,
                    university = admin.university,
                )
                list_users.append(details)
            
            logger.info(f"Successfully listed {len(list_users)} admins [status_code=200]")
            return list_users

        elif role == 2:
            university = data.get('university')
            students = session.query(User).filter(User.university == university,User.role == 3).order_by(User.updated_at.desc()).all()
            for student in students:
                details = UserHistory(
                    id = student.id,
                    role = student.role,
                    username = student.username,
                    dob = student.dob,
                    phone_number = student.phone_no, 
                    email = student.email,
                    university = student.university,
                )
                list_users.append(details)
            
            logger.info(f"Successfully listed {len(list_users)} students for university: {university} [status_code=200]")
            return list_users
                
    except Exception as e:
        logger.error(f"Error listing users [status_code=500] - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
