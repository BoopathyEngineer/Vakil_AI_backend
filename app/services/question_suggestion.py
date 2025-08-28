from fastapi.exceptions import HTTPException
from app.services.create_chat import validate_user
from app.utils.llm_utils import generate_response
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

async def question_suggestion(prompt,user_id,session):
    try:
        if not prompt or not user_id:
            logger.warning("Prompt and user_id are required for question suggestion [status_code=400]")
            raise HTTPException(status_code=400, detail="Prompt and user_id are required")
        
        user = validate_user(int(user_id), session)
        if not user:
            logger.warning(f"User not found for user_id: {user_id} [status_code=404]")
            raise HTTPException(status_code=404, detail="User not found")
        
        prompt = f"""Generate 5 related questions for the given query.
        Query: '{prompt}'
        Note:
        - Provide concise and contextually relevant questions.
        - Ensure the questions are useful follow-ups for the user's search.
        - Return the output as a plain list of questions without any numbering or bullet points.
        - Do NOT include serial numbers, bullet points, or any additional text in the response.
        """
        
        response_text = await generate_response(prompt)
        questions = [q.strip() for q in response_text.split("\n") if q.strip()][:5]
        
        if not questions:
            logger.warning(f"Failed to generate questions for user_id: {user_id} [status_code=500]")
            raise HTTPException(status_code=500, detail="Failed to generate questions")
        
        logger.info(f"Successfully generated {len(questions)} question suggestions for user_id: {user_id} [status_code=200]")
        return questions
    except Exception as e:
        logger.error(f"Error generating question suggestions for user_id: {user_id} [status_code=500] - {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
