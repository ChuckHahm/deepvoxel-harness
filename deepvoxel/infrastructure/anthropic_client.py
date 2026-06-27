import anthropic
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def get_client() -> anthropic.Anthropic:
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    logger.debug("Anthropic client initialized")
    return client
