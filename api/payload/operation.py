import asyncio

from pydantic import BaseModel, Field
from typing import Optional

from utils.constants import *



class getVersionPayload(BaseModel):
    agent: str = Field(..., description="에이전트")
    kind: str = Field(..., description="종류")
    role_name: Optional[str] = Field(None, alias="roleName")


class getDataPayload(BaseModel):
    agent: str = Field(..., description="에이전트")
    kind: str = Field(..., description="종류")
    id: str = Field(..., description="ID")
    page: Optional[str] = Field(None, description="페이지")


class downloadQuestionPayload(BaseModel):
    id: str = Field(..., description="ID")


class updateMemoPayload(BaseModel):
    agent: str = Field(..., description="에이전트")
    kind: str = Field(..., description="종류")
    id: str = Field(..., description="ID")
    memo: Optional[str] = Field(None, description="메모")


class getTokenSize(BaseModel):
    prompt: str = Field(..., description="문장")
    model: Optional[str] = Field(None, description="모델 이름")


class updateNotSatisfyPayload(BaseModel):
    email: str = Field(..., description="이메일")


class deployPayload(BaseModel):
    password: str = Field(..., description="비밀번호")
    stage: str = Field(..., alias="server")
    agent: Optional[str] = Field(None, description="에이전트")


class rollbackPayload(BaseModel):
    password: str = Field(..., description="비밀번호")
    stage: str = Field(..., alias="server")
    agent: Optional[str] = Field(None, description="에이전트")


class GetModelQueryParams(BaseModel):
    agent: Optional[str] = Field(None, description="에이전트")


class GetCurrentModelQueryParams(BaseModel):
    agent: str = Field(..., description="에이전트")


class SetVendorAndModelPayload(BaseModel):
    agent: str = Field(..., description="에이전트")
    vendor: str = Field(..., alias="company", description="업체")
    model: str = Field(..., description="모델")
