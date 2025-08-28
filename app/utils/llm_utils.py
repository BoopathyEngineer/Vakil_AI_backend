import os
from openai import AsyncOpenAI
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

# Configure OpenAI
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1",  # Explicitly set base URL
    timeout=60.0,  # Set timeout in seconds
    max_retries=2  # Set max retries
)

async def generate_response(query):
    try:
        print("step 2")
        logger.info("Request received to generate response using OpenAI model. [status_code=100]")
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}],
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        logger.info("Successfully generated response from OpenAI model. [status_code=200]")
        print("step 3", response_text)
        return response_text
    except Exception as e:
        logger.error(f"Error while generating response: {e} [status_code=500]", exc_info=True)
        raise