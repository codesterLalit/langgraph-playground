from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from dataclasses import dataclass
import sqlite3
from collections.abc import Callable

app = FastAPI()

class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    thread_id: str = Field(min_length= 1)
    user_role: Optional[str] = "guest"
    id: Optional[int] = None

class ChatResponse(BaseModel):
    thread_id: str
    reply: str
    status: str = "success"


@dataclass
class RuntimeContext:
    user_id:str
    role: str

@dataclass
class ModelRequest:
    prompt: str
    context: RuntimeContext

@dataclass
class ModelResponse:
    text: str

class SQLiteChatRepository:
    def __init__(self, db_path: str = "chat_history.db"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory =sqlite3.Row
        self._init_db()
    
    def _init_db(self) -> None:
        """Private setup metho to ensure table exists"""
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_history(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id TEXT NOT NULL,
                    user_role TEXT NOT NULL,
                    message TEXT NOT NULL
                )                   
            """)
    def save_message(self, message: ChatRequest) -> ChatRequest:
        """Save a message record using safe parameters."""
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (thread_id, user_role, message) VALUES (?, ?, ?)",
            (message.thread_id, message.user_role, message.message,)
        )
        self._conn.commit()
        message.id = cursor.lastrowid
        return message
    
    
class ModelAdapter:
    def invoke(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(text=f"[Echo Adapter]: {request.prompt}")

def context_middleware(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    request.prompt = (
        f"[User ID: {request.context.user_id}] "
        f"[Role: {request.context.role}] "
        f"{request.prompt}"
    )
    return handler(request)

def auth_middleware(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    is_external = request.context.role == "external"
    is_protected = "/admin" in request.prompt
    
    if is_external and is_protected:
        raise PermissionError(
            "External users cannot access protected commands."
        )
    return handler(request)

def model_handler(request: ModelRequest) -> ModelResponse:
    adapter = ModelAdapter()
    return adapter.invoke(request)

context = RuntimeContext(user_id="user-123", role="guest")

request = ModelRequest(
    prompt="Explain FastAPI",
    context=context
)

response = context_middleware(request, model_handler)

repository = SQLiteChatRepository()
adaptor = ModelAdapter()

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    context = RuntimeContext(
        user_id="user-123",
        role=request.user_role or "guest"
    )
    
    model_request = ModelRequest(
        prompt=request.message,
        context=context
    )
    
    try:
        response = context_middleware(
            model_request,
            lambda enriched_request: auth_middleware(
                enriched_request,
                model_handler
            )
        )
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    repository.save_message(request)
    return ChatResponse(thread_id=request.thread_id, reply=response.text)