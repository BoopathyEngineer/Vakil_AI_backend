import os
import time
import uuid
import json
import asyncio
import datetime
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from DrissionPage import ChromiumPage, ChromiumOptions
from concurrent.futures import ThreadPoolExecutor
from app.models.chat import Chat
from app.schemas.chat_schema import ChatRequestSchema 
from app.services.question_suggestion import question_suggestion
from app.services.fetch_image_service import fetch_images
from app.utils.llm_utils import generate_response
from app.utils.data_utils import fetch_videos, fetch_links
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

async def generate_answer_service(query, document_text=None):
    logger.info(f"Request received to generate answer for query: '{query}' [status_code=100]")
    try:
        if document_text:
            from app.services.document_service import answer_from_document
            return await answer_from_document(query, document_text)

        prompt = f"""You are Vakil, an intelligent legal reasoning assistant trained to help users understand Indian legal concepts, documents, and procedures. Your role is to analyze queries, offer insightful clarifications, and guide users toward a deeper understanding of Indian law — not to provide legal advice or perform legal services.

You specialize in explaining provisions from Indian Bare Acts (e.g., IPC, CrPC, CPC, IEA), interpreting legal terminology, summarizing judgments, and helping users navigate legal documents or procedural steps. You always prioritize clarity, context, and accurate interpretation of Indian legal sources.

BEHAVIOR GUIDELINES BASED ON USER INPUT TYPE
If the user asks a personal, situational, or advice-seeking question
(e.g., “What should I do if I get arrested?” or “How do I deal with my landlord?”):
Do NOT answer immediately.
Instead, ask a series of focused, relevant follow-up questions, one at a time.
Simulate a natural conversation to understand the situation fully (aim for 3–5 key details).
Only after collecting enough context, provide a well-reasoned, practical, and empathetic response that explains applicable legal concepts or options.
Never provide specific legal advice — explain what the law says and what factors are relevant.
If the user asks a generic, conceptual, or factual question
(e.g., “What is IPC 420?” or “What is an FIR?”):
Answer directly and clearly.
Use simple, plain language.
Reference relevant sections of Bare Acts or well-known judgments where helpful.
Avoid unnecessary legal jargon, and explain it when used.

RESPONSE STRUCTURE
If the User Query Is Unclear or Situational:
Clarify the Query
Ask one focused follow-up question to understand the user's situation or intent.
Do not provide an answer until enough context is gathered (typically after 3–5 exchanges).
Legal Explanation (after context is clear)
Explain the relevant legal principles or procedures.
Use plain language and refer to applicable Indian laws (e.g., IPC, CrPC, CPC, IEA) or case law if helpful.
Avoid giving specific legal advice; focus on what the law says and what factors are relevant.
Next Steps
Suggest what the user can review (e.g., documents, notices), consider (e.g., deadlines, rights), or ask a lawyer.
Aim to equip the user for informed action or legal discussion.

If the User Query Is Clear and Factual:
Legal Explanation
Provide a direct, concise, and accurate explanation based on Indian law.
Avoid legal jargon unless necessary, and explain it clearly when used.
Optional Exploration
If relevant, invite the user to explore related areas or ask follow-up questions.
Only include this if it adds value to user understanding.
Next Steps
Recommend what the user might read next (e.g., related sections, processes) or clarify further.
Help the user deepen their understanding of the topic.

Interpreting sections of Indian laws (IPC, CrPC, CPC, IEA, etc.)
Explaining legal terminology, procedure, or judgments
Clarifying the meaning or implications of clauses in contracts or legal notices
Providing context for legal rights and responsibilities

YOU MUST AVOID:
Giving legal advice tailored to a specific user case
Taking sides or offering opinions on ongoing disputes or litigation
Drafting legal documents or offering legal representation

PRIORITIZE:
Clear reasoning over quick answers
Legally grounded explanations over assumptions
User understanding and guidance over shortcuts
            
            Always respond in the following JSON format:
            ```json
            {{
                "answer": "<p>Your answer in HTML</p>"
   
            }}

            Query: '{query}'
            """

        response = await generate_response(prompt)
        processed_response = response.replace("```html", "").replace('```json', "").replace("```", "")
        logger.info(f"Successfully generated answer for query: '{query}' [status_code=200]")
        return json.loads(processed_response)
    except Exception as e:
        logger.error(f"Error generating answer for query: '{query}' [status_code=500] - {e}", exc_info=True)
        raise


async def fetch_resources_and_videos(query):
    logger.info(f"Request received to fetch resources and videos for query: '{query}' [status_code=100]")
    try:
        def get_videos():
            start_time = time.time()
            result = fetch_videos(query)
            end_time = time.time()
            return result

        def get_links():
            start_time = time.time()
            result = fetch_links(query)
            end_time = time.time()
            return result

        with ThreadPoolExecutor() as executor:
            links_future = executor.submit(get_links)
            video_future = executor.submit(get_videos)

            links_urls = links_future.result()
            video_urls = video_future.result()

        response = {
            "links": links_urls,
            "video_urls": video_urls,
        }
        logger.info(f"Successfully fetched resources and videos for query: '{query}' [status_code=200]")
        return response
    except Exception as e:
        logger.error(f"Error fetching resources and videos for query: '{query}' [status_code=500] - {e}", exc_info=True)
        raise

async def response_gen(data: ChatRequestSchema,session: Session):
    logger.info(f"Request received to generate response for chat_id: {data.chat_id}, user_id: {data.user_id} [status_code=100]")
    resources_response = {}
    images = []
    suggestion_questions = []
    try:
        if data.chat_id:
            answer_response = await generate_answer_service(data.question, data.document_text)
            if not isinstance(answer_response, dict):
                logger.error(f"Answer response is not a dictionary for chat_id: {data.chat_id} [status_code=500]")
                raise HTTPException(
                    status_code=500, detail="response must be a dictionary"
                )
            response_id = str(uuid.uuid4())
            if answer_response.get('greetings') == 'yes':
                yield json.dumps({"response_mode": "answer", "question": data.question, "answer": answer_response.get('answer'), "resposne_id": response_id, "chat_id": data.chat_id, "user_id": data.user_id})
            
            elif answer_response.get('educational') == 'yes':
                yield json.dumps({"response_mode": "answer", "question": data.question, "answer": answer_response.get('answer'), "resposne_id": response_id, "chat_id": data.chat_id, "user_id": data.user_id})
                
                await asyncio.sleep(1)
                yield json.dumps({"response_mode": "loading", "detail": "gathering suggested questions...", "chat_id": data.chat_id, "user_id": data.user_id})
                suggestion_questions = await question_suggestion(data.question,data.user_id,session)
                yield json.dumps({"response_mode": "suggestion questions", "suggestion_questions": suggestion_questions, "chat_id": data.chat_id, "user_id": data.user_id})
                
            else:
                yield json.dumps({"response_mode": "answer", "question": data.question, "answer": answer_response.get('answer'), "resposne_id": response_id, "chat_id": data.chat_id, "user_id": data.user_id})

            chat_detail = session.query(Chat).filter(Chat.chat_id == data.chat_id).first()
            message=dict(
                message_id = response_id,
                query = data.question,
                answer = answer_response,
                suggestion_questions = suggestion_questions if suggestion_questions else [],
                created_at = datetime.datetime.now().isoformat(),
                updated_at = datetime.datetime.now().isoformat()
            )

            chat_detail.messages.append(message)
            session.add(chat_detail)
            session.commit()
            session.close()
            logger.info(f"Successfully generated and stored response for chat_id: {data.chat_id} [status_code=200]")
            
            return 
        else:
            chat_id = str(uuid.uuid4())
            response_id = str(uuid.uuid4())
            answer_response = await generate_answer_service(data.question, data.document_text)
            if answer_response.get('greetings') == 'yes':
                yield json.dumps({"response_mode": "answer", "question": data.question, "answer": answer_response.get('answer'), "response_id": response_id})
            
            elif answer_response.get('educational') == 'yes':
                yield json.dumps({"response_mode": "answer", "question": data.question, "answer": answer_response.get('answer'), "response_id": response_id, "chat_id": chat_id, "user_id": data.user_id})
                
                await asyncio.sleep(1)
                yield json.dumps({"response_mode": "loading", "detail": "gathering suggested questions...", "chat_id": data.chat_id, "user_id": data.user_id})
                suggestion_questions = await question_suggestion(data.question,data.user_id,session)
                yield json.dumps({"response_mode": "suggestion questions", "suggestion_questions": suggestion_questions, "chat_id": data.chat_id, "user_id": data.user_id})
            
            else:
                yield json.dumps({"response_mode": "answer", "question": data.question, "answer": answer_response.get('answer'), "resposne_id": response_id, "chat_id": data.chat_id, "user_id": data.user_id})

                
            new_message_instance = Chat(
                    chat_id = chat_id,
                    user_id = data.user_id,
                    messages = [{
                                "message_id": response_id,
                                "query": data.question,
                                "answer": answer_response,
                                "suggestion_questions": suggestion_questions if suggestion_questions else [],
                                "created_at": datetime.datetime.now().isoformat(),
                                "updated_at": datetime.datetime.now().isoformat()
                                }])
            session.add(new_message_instance)
            session.commit()    
            session.close()
            logger.info(f"Successfully generated and stored response for new chat_id: {chat_id} [status_code=200]")
            
            return
    except Exception as e:
        logger.error(f"Error in response_gen for chat_id: {getattr(data, 'chat_id', None)} [status_code=500] - {e}", exc_info=True)
        raise
