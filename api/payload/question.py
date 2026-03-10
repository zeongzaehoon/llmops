import asyncio
import uuid

from fastapi import Form, File, UploadFile
from pydantic import BaseModel, Field
from typing import Optional

from utils.constants import *




# ask payload
class askPayload(BaseModel):
    agent: str
    question: Optional[str] = Field(None, alias="prompt")
    vendor: Optional[str] = Field(None, alias="company")
    model: Optional[str] = Field(None, alias="model")
    fixed_answer: Optional[int] = Field(None, alias="fixedAnswer")
    test: Optional[bool] = None
    lang: Optional[str] = None
    info: Optional[dict] = None
    id: Optional[str] = None
    streaming: Optional[bool] = True
    service_type: Optional[str] = Field('ba', alias="serviceType", description="will be deprecated")
    is_mcp: Optional[bool] = Field(None, alias="isMcp")
    graph_id: Optional[str] = Field(None, alias="graphId")
    toolset_id: Optional[str] = Field(None, alias="toolSetId")
    is_demo: Optional[bool] = Field(False, alias="isDemo")
    dashboard_data: Optional[list[dict] | dict] = Field(None, alias="dashboardData")
    segment_data: Optional[list[dict] | dict] = Field(None, alias="segmentData")
    docent_document_id: Optional[str] = Field(None, description="Data for Error")

    class Config:
        populate_by_name = True


class AskDashboardPayload(BaseModel):
    agent: str = Field(...)
    question: str = Field(..., alias="prompt")
    vendor: Optional[str] = Field(None, alias="company")
    model: Optional[str] = Field(None, alias="model")
    dashboard_data: Optional[list[dict] | dict] = Field(None, alias="dashboardData")
    lang: Optional[str] = Field("ko", alias="lang")
    info: Optional[dict] = Field(None)
    segment_doc: Optional[dict] = Field(None, alias="segment")
    report_ids: Optional[list] = Field(None, alias="_ids")
    service_type: Optional[str] = Field('ba', alias="serviceType")


# set_report payload
class setReportPayload(BaseModel):
    agent:str
    report_id:list[str] = Field(..., alias="_ids")
    service_type: str = Field('ba', alias="serviceType")

    class Config:
        populate_by_name = True

class insertInitReportchatRowPayload(BaseModel):
    agent:str
    message:str
    report_id:list[str] = Field(..., alias="_ids")
    info: Optional[dict] = None
    service_type: str = Field('ba', alias="serviceType")

    class Config:
        populate_by_name = True

class getReportChatDatasPayload(BaseModel):
    agent:str
    user_id:str = Field(..., alias="userId")

    class Config:
        populate_by_name = True


class GetModelQueryParams(BaseModel):
    agent: Optional[str] = Field(None)


class referPayload(BaseModel):
    agent:str
    question:Optional[str] = Field(None, alias="prompt")

    class Config:
        populate_by_name = True


class updateRatingPayload(BaseModel):
    id:str
    rating:Optional[int] = None
