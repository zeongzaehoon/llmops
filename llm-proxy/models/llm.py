import asyncio
from pydantic import BaseModel, Field
from typing import Optional



class ChatPayload(BaseModel):
    service: str = Field(...)
    question: str = Field(...)

    vendor: Optional[str] = Field("openai")
    model: Optional[str] = Field("gpt-4o")
    system_message: Optional[str] = Field("-", alias="systemMessage")
    system_message_placeholder: Optional[dict] = Field(None, alias="systemMessagePlaceholder")
    conversation_history: Optional[list] = Field(None, alias="conversationHistory")
    images: Optional[list] = Field([], description="max: 20 images")
    image_types: Optional[list] = Field([], alias="imageTypes", description="only base64 or url")
    image_filename_extensions: Optional[list] = Field([], alias="imageFilenameExtensions", description="input extension if image data is base64. but not required")
    temperature: Optional[float] = Field(None)
    stream: Optional[bool] = Field(True)
    time: Optional[float] = Field(None)
    session_key: Optional[str] = Field(None, alias="sessionKey", description="session key from service side")

    # for gemini filesearch api
    store_name: Optional[str] = Field(None, alias="storeName")
    metadata_filter: Optional[dict | str] = Field(None, alias="metadataFilter")


class ChatMCPPayload(ChatPayload):
    mcp_info: Optional[list] = Field(None, alias="mcpInfo")
    mcp_server: Optional[str | list[str]] = Field(None, alias="mcpServer")
    mcp_token: Optional[str | list[str]] = Field(None, alias="mcpToken")
    mcp_allowed_tools: Optional[list[str] | dict[str, list[str]]] = Field(None, alias="mcpAllowedTools")


class OcrChatPayload(BaseModel):
    # required
    service: str = Field(...)
    question: str = Field(...)

    # not required
    vendor: Optional[str] = Field("openai")
    model: Optional[str] = Field("gpt-4o")
    system_message: Optional[str] = Field("-", alias="systemMessage")
    system_message_placeholder: Optional[dict] = Field(None, alias="systemMessagePlaceholder")
    conversation_history: Optional[list] = Field([], alias="conversationHistory")
    images: Optional[list] = Field([], description="max: 20 images")
    image_types: Optional[list] = Field([], alias="imageTypes")
    image_filename_extensions: Optional[list] = Field([], alias="imageFilenameExtensions", description="input extension if image data is base64. but not required")
    stream: Optional[bool] = Field(True)
    temperature: Optional[float] = Field(None, alias="temperature")
    time: Optional[float] = Field(None, alias="time")
    session_key: Optional[str] = Field(None, alias="sessionKey")


class EmbeddingsPayload(BaseModel):
    text: str | list[str] = Field(...)
    model: str = Field(...)
    service: Optional[str] = Field(None)
    vendor: Optional[str] = Field(None)
    debug_id: Optional[str] = Field(None, alias="debugId")


class AsyncData:
    event = asyncio.Event()
    queue = asyncio.Queue(maxsize=1)
