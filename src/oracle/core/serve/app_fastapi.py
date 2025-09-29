#!/usr/bin/env python3
"""
Oracle850B FastAPI Server с авто-инжектом системных токенов
OpenAI-совместимый API для Oracle850B (MoE)
Author: MagistrTheOne|Краснодар|2025
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# Модели запросов/ответов
class ChatMessage(BaseModel):
    role: str = Field(..., description="Роль: system, user, assistant")
    content: str = Field(..., description="Содержимое сообщения")


class ChatCompletionRequest(BaseModel):
    model: str = Field(default="oracle850b-moe", description="Модель")
    messages: List[ChatMessage] = Field(..., description="История сообщений")
    max_tokens: Optional[int] = Field(default=2048, description="Максимум токенов")
    temperature: Optional[float] = Field(default=0.7, description="Температура")
    top_p: Optional[float] = Field(default=0.9, description="Top-p")
    stream: Optional[bool] = Field(default=False, description="Стриминг")


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


class Oracle850BServer:
    """Сервер Oracle850B с авто-инжектом системных токенов"""
    
    def __init__(self, model_path: str = "checkpoints/oracle850b"):
        self.model_path = Path(model_path)
        self.default_system = self._load_default_system()
        self.default_intro = self._load_default_intro()
        
    def _load_default_system(self) -> str:
        """Загрузить системный промпт по умолчанию"""
        system_file = self.model_path / "default_system.txt"
        if system_file.exists():
            return system_file.read_text(encoding="utf-8").strip()
        return "Вы - Oracle850B, продвинутая языковая модель с архитектурой MoE."
    
    def _load_default_intro(self) -> str:
        """Загрузить вводный промпт по умолчанию"""
        intro_file = self.model_path / "default_intro.txt"
        if intro_file.exists():
            return intro_file.read_text(encoding="utf-8").strip()
        return "Привет! Я Oracle850B, готова помочь с вашими задачами."
    
    def _inject_system_tokens(self, messages: List[ChatMessage]) -> List[ChatMessage]:
        """Авто-инжект системных токенов Oracle850B"""
        
        # Проверить, есть ли системное сообщение
        has_system = any(msg.role == "system" for msg in messages)
        
        if not has_system:
            # Добавить системное сообщение с токенами Oracle
            system_msg = ChatMessage(
                role="system",
                content=f"<|oracle_sys|>{self.default_system}<|author|>MagistrTheOne|Краснодар|2025"
            )
            messages = [system_msg] + messages
        
        # Добавить вводный токен к первому пользовательскому сообщению
        if messages and messages[0].role == "user":
            messages[0].content = f"<|oracle_intro|>{self.default_intro}\n\n{messages[0].content}"
        
        return messages
    
    async def generate_response(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Генерация ответа (мок-реализация для dry-run)"""
        
        # Инжект системных токенов
        messages = self._inject_system_tokens(request.messages)
        
        # Мок-ответ для dry-run
        response_content = f"Мок-ответ Oracle850B для: {messages[-1].content[:100]}..."
        
        return ChatCompletionResponse(
            id="oracle-850b-mock-001",
            created=int(asyncio.get_event_loop().time()),
            model=request.model,
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": sum(len(msg.content.split()) for msg in messages),
                "completion_tokens": len(response_content.split()),
                "total_tokens": 0
            }
        )


# Инициализация приложения
app = FastAPI(
    title="Oracle850B API",
    description="OpenAI-совместимый API для Oracle850B (MoE)",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация сервера
server = Oracle850BServer()


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Oracle850B API Server",
        "version": "0.1.0",
        "author": "MagistrTheOne|Краснодар|2025",
        "model": "oracle850b-moe"
    }


@app.get("/v1/models")
async def list_models():
    """Список доступных моделей"""
    return {
        "object": "list",
        "data": [{
            "id": "oracle850b-moe",
            "object": "model",
            "created": 1700000000,
            "owned_by": "MagistrTheOne",
            "permission": [],
            "root": "oracle850b-moe",
            "parent": None
        }]
    }


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """Chat Completions API (OpenAI-совместимый)"""
    try:
        response = await server.generate_response(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Проверка здоровья сервера"""
    return {
        "status": "healthy",
        "model": "oracle850b-moe",
        "ready": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
