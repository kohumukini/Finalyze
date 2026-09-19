from groq import Groq

from typing import Any, Optional

from ..core.config import DEFAULT_TEMPERATURE, GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS
from ..core.logger import get_logger
from ..core.schema import ChunkItem

logger = get_logger(__name__)

client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        logger.info("Groq client successfully loaded")
    except Exception as exc:
        logger.error("Groq client failed to load: %s", exc)
else:
    logger.error("Groq API Key Missing!")


def generate_response(messages: list[dict]) -> str:
    if client is None:
        raise RuntimeError("Groq client has not been initialized")

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages, 
        temperature=DEFAULT_TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )

    return response.choices[0].message.content.strip()

def text_to_xml(tag_name: str, content: str, attributes: Optional[dict[str, Any]]): 
    """General Utility: Wrap any text in xml formatting"""
    if not content.strip(): 
        return "" 
    
    attr_str = "" 
    if attributes: 
        attr_str = " " + " ".join(f'{k}="{v}"' for k, v in attributes.items() if v is not None)
    return f"<{tag_name}{attr_str}>\n{content.strip()}\n</{tag_name}>"
    

def xml_prompt_builder(chunks: list[ChunkItem], user_prompt: str): 
    if not chunks: 
        return "State that there is not adequate information to provide an accurate answer."
    
    xml_blocks = []
    
    for i, chunk in enumerate(chunks): 
        attributes = {
            "id": i + 1, 
            "source": chunk.metadata.source_name
        }
        
        xml_chunk = text_to_xml("chunk", chunk.content, attributes)
        xml_blocks.append(xml_chunk)
    
    inner_text = "\n".join(xml_blocks)
    retrieved_content = text_to_xml("retrieved_context", inner_text)
    
    prompt_blocks = [
        retrieved_content, 
        f"<user_query>\n{user_prompt}\n</user_query>", 
        "Instructions: Answer the <user_query> using ONLY information from <retrieved_context>. If the context does not contain the ansewr, state that you do not know. "
    ]
    
    return "\n\n".join(prompt_blocks)