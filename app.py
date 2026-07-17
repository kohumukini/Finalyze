import os
from typing import Any, Dict, List

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None

try:
    from groq import Groq
except ImportError:  # pragma: no cover - optional dependency
    Groq = None

if load_dotenv is not None:
    load_dotenv()

app = FastAPI(title="Finalyze RAG Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for the simple prototype backend.
documents: List[Dict[str, Any]] = []
chat_history: List[Dict[str, str]] = []


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/process-document")
def process_document(text: str = Body(..., media_type="text/plain")) -> Dict[str, Any]:
    cleaned_text = text.strip()
    if not cleaned_text:
        raise HTTPException(status_code=400, detail="Text must not be empty.")

    document = {
        "id": len(documents) + 1,
        "text": cleaned_text,
        "word_count": len(cleaned_text.split()),
        "preview": cleaned_text[:200],
    }
    documents.append(document)

    return {"message": "Document processed successfully.", "document": document}


@app.get("/documents")
def list_documents() -> Dict[str, List[Dict[str, Any]]]:
    return {"documents": documents}


@app.post("/chat")
def chat(message: Dict[str, str]) -> Dict[str, str]:
    user_message = (message.get("message") or "").strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message must not be empty.")

    chat_history.append({"role": "user", "content": user_message})

    client = None
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if Groq is not None and groq_api_key:
        client = Groq(api_key=groq_api_key)

    if client is not None:
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for the Finalyze RAG prototype."},
                    *chat_history,
                ],
                temperature=0.7,
                max_tokens=300,
            )
            assistant_response_text = response.choices[0].message.content.strip()
        except Exception:
            assistant_response_text = f"I couldn't reach Groq right now, so I'm echoing your request: {user_message}"
    else:
        assistant_response_text = f"Echo: {user_message}"

    chat_history.append({"role": "assistant", "content": assistant_response_text})
    return {"response": assistant_response_text} 