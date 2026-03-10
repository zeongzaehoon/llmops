from pydantic import BaseModel, Field, model_validator
from typing import Optional



class GetModelQueryParams(BaseModel):
    agent: Optional[str] = Field(None)


class GetCurrentModelQueryParams(BaseModel):
    agent: str = Field(...)


class SetVendorAndModelPayload(BaseModel):
    agent: str = Field(...)
    vendor: str = Field(..., alias="company")
    model: str = Field(...)


class InsertPromptPayload(BaseModel):
    prompt: str = Field(...)
    agent: str = Field(...)
    memo: Optional[str] = Field(None)


class GetVersionPayload(BaseModel):
    agent: str = Field(...)
    kind: str = Field(...)
    role_name: Optional[str] = Field(None, alias="roleName")


class GetPromptPayload(BaseModel):
    id: str = Field(...)


class GetDataPayload(BaseModel):
    agent: str = Field(...)
    kind: str = Field(...)
    id: str = Field(...)
    page: Optional[str] = Field(None)


class GetTokenSizePayload(BaseModel):
    prompt: str = Field(...)


class UpdateMemoPayload(BaseModel):
    agent: str = Field(...)
    kind: str = Field(...)
    id: str = Field(...)
    memo: Optional[str] = Field(None)


class DownloadQuestionPayload(BaseModel):
    id: str = Field(...)


class DeployPayload(BaseModel):
    password: str = Field(...)
    stage: str = Field(..., alias="server")
    agent: Optional[str] = Field(None)


class RollbackPayload(BaseModel):
    password: str = Field(...)
    stage: str = Field(..., alias="server")
    agent: Optional[str] = Field(None)


class EnrollMCPServerPayload(BaseModel):
    name: str = Field(...)
    uri: str = Field(...)
    token: str = Field(...)
    description: Optional[str] = Field(None)


class CreateAgentPayload(BaseModel):
    agent: str = Field(..., description="에이전트 식별자 (예: main, cs)")
    name: str = Field(..., description="에이전트 표시명")
    description: Optional[str] = Field(None)


class UpdateAgentPayload(BaseModel):
    id: str = Field(...)
    name: Optional[str] = Field(None)
    description: Optional[str] = Field(None)


class DeleteAgentPayload(BaseModel):
    id: str = Field(...)


class CreateMCPToolsetPayload(BaseModel):
    agent: str = Field(...)
    name: str = Field(...)
    mcp_info: list[dict] | None = Field(..., alias="mcpInfo")
    description: Optional[str] = Field(None)


class GetMCPServerToolsPayload(BaseModel):
    id: str = Field(...)


class GetMCPToolsetPayload(BaseModel):
    agent: Optional[str] = Field(None)


class UpdateMCPServerPayload(BaseModel):
    id: str = Field(...)
    name: Optional[str] = Field(None)
    uri: Optional[str] = Field(None)
    description: Optional[str] = Field(None)

    @model_validator(mode='after')
    def check_at_least_one_field(self):
        if not any([self.name, self.uri, self.description]):
            raise ValueError('At least one field (name, uri, description) must be provided')
        return self


class UpdateMCPToolsetPayload(BaseModel):
    id: str = Field(...)
    name: Optional[str] = Field(None)
    mcp_info: Optional[list[dict] | None] = Field(None, alias="mcpInfo", description="[{'serverId': '', tools: ['toolName_1', 'toolName_2']}]")
    description: Optional[str] = Field(None)


class AdaptToolsetOnServicePayload(BaseModel):
    id: str = Field(...)
    agent: str = Field(...)


class DeleteMCPServerPayload(BaseModel):
    id: str = Field(...)


class DeleteMCPToolsetPayload(BaseModel):
    id: str = Field(...)


# Multi Agent Graph
class AgentNodePayload(BaseModel):
    agent: str = Field(...)
    role: Optional[str] = Field("")


class EdgeNodePayload(BaseModel):
    source: str = Field(..., alias="from", description="출발 에이전트명")
    target: str = Field(..., alias="to", description="도착 에이전트명")
    condition: Optional[str] = Field(None, description="조건 (LLM이 평가할 프롬프트). None이면 무조건 통과")
    on_failure: Optional[str] = Field("end", alias="onFailure", description="조건 실패 시: retry | end | 에이전트명")
    max_retries: Optional[int] = Field(2, alias="maxRetries", description="retry 시 최대 재시도 횟수")

    class Config:
        populate_by_name = True


class CreateMultiAgentGraphPayload(BaseModel):
    name: str = Field(...)
    graph_type: str = Field(..., alias="graphType")
    agents: list[AgentNodePayload] = Field(...)
    edges: Optional[list[EdgeNodePayload]] = Field(None, description="custom graphType 전용 엣지 목록")
    description: Optional[str] = Field(None)
    max_iterations: Optional[int] = Field(3, alias="maxIterations")

    class Config:
        populate_by_name = True


class GetMultiAgentGraphPayload(BaseModel):
    id: str = Field(...)


class UpdateMultiAgentGraphPayload(BaseModel):
    id: str = Field(...)
    name: Optional[str] = Field(None)
    graph_type: Optional[str] = Field(None, alias="graphType")
    agents: Optional[list[AgentNodePayload]] = Field(None)
    edges: Optional[list[EdgeNodePayload]] = Field(None)
    description: Optional[str] = Field(None)
    max_iterations: Optional[int] = Field(None, alias="maxIterations")

    class Config:
        populate_by_name = True


class DeleteMultiAgentGraphPayload(BaseModel):
    id: str = Field(...)
