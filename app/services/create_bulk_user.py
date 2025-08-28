import re
import io
import pandas as pd
from datetime import datetime
from fastapi.exceptions import HTTPException
from app.crud.user_crud import get_user_details
from app.models.user_models import User
from app.models.email_models import EmailId
from app.schemas.auth_schemas import AuthResponseDetails
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

async def create_bulk_user(file,data,session):
    logger.info("Request received to create bulk users [status_code=100]")
    try:
        university = data.get('university')
        COLUMNS_NEEDED = ["Username", "Date of Birth", "Phone Number", "Email"]
        PHONE_REGEX = re.compile(r"^\d{10}$")
        EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")

        # Check file extension
        if not file.filename.endswith((".xls", ".xlsx")):
            logger.warning("Invalid file extension for bulk user upload [status_code=400]")
            raise HTTPException(status_code=400, detail={'status_code': 400, 'message': f"Only Excel files (.xls, .xlsx) are allowed."})

        # Read the uploaded Excel file into a Pandas DataFrame
        contents = await file.read()
        excel_data = io.BytesIO(contents)

        # Load Excel file into DataFrame
        df = pd.read_excel(excel_data, sheet_name=None, engine="openpyxl")  # Read all sheets

        # Extract first sheet
        first_sheet_name = list(df.keys())[0]
        data = df[first_sheet_name][COLUMNS_NEEDED]
        data_records = data.to_dict(orient="records")

        for idx, record in enumerate(data_records, start=1):
            detail = ''
            # Phone number validation
            phone = str(record['Phone Number']).strip()
            if not PHONE_REGEX.match(phone):
                logger.warning(f"Invalid phone number at row {idx} [status_code=400]")
                raise HTTPException(status_code=400, detail=f"Invalid phone number at row {idx}. Must be 10 digits.")

            # Email validation
            email = str(record['Email']).strip()
            if not EMAIL_REGEX.match(email):
                logger.warning(f"Invalid email format at row {idx} [status_code=400]")
                raise HTTPException(status_code=400, detail=f"Invalid email format at row {idx}.")

            dob_raw = str(record['Date of Birth']).strip()
            date_formats = ["%d-%m-%y", "%d-%m-%Y", "%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d", "%Y/%d/%m", "%Y-%d-%m", "%Y-%m-%d %H:%M:%S"]

            dob = None
            for fmt in date_formats:
                try:
                    
                    dob = datetime.strptime(dob_raw, fmt).date()
                    if dob >= datetime.today().date():
                        logger.warning(f"Invalid Date of Birth at row {idx} (future/today) [status_code=400]")
                        raise HTTPException(status_code=400, detail=f"Date of Birth at row {idx} cannot be today or a future date.")
                    break
                except ValueError:
                    continue

            # If all formats failed
            if dob is None:
                logger.warning(f"Invalid Date of Birth format at row {idx} [status_code=400]")
                raise HTTPException(status_code=400, detail=f"Invalid Date of Birth format at row {idx} {dob}.")

            if get_user_details(session, {'phone_no': phone}):
                detail += 'mobile'
            if get_user_details(session, {'email': email}):
                if detail == '':
                    detail += 'email'
                else:
                    detail += ' & email'
            if detail != '':
                logger.warning(f"Duplicate user data at row {idx}: {detail} already exists [status_code=400]")
                raise HTTPException(status_code=400, detail=detail + ' already exists')  

            new_user = User(
                            username=record['Username'],
                            dob=dob,
                            phone_no=phone,
                            email=email,
                            role=3,
                            university=university,
                            )
            session.add(new_user)   
            session.commit()
            session.close()

            new_email_instance = EmailId(email_id = email)
            session.add(new_email_instance)
            session.commit()
        
        response = AuthResponseDetails(status_code=200,message=f"Data uploaded successfully")
        logger.info("Bulk user creation successful [status_code=200]")
        return response

    except Exception as e:
        logger.error(f"Error occurred during bulk user creation [status_code=500] - {e}", exc_info=True)
        raise HTTPException(status_code=400, detail={'status_code': 400, 'message': f"Error Occured: {str(e)}"})
