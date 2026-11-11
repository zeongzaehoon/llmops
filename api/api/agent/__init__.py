"""Agent router package — aggregates per-domain sub-routers (paths unchanged)."""
from fastapi import APIRouter

from .model import agent as _model
from .prompt import agent as _prompt
from .server import agent as _server
from .agents import agent as _agents
from .toolset import agent as _toolset
from .graph import agent as _graph

agent = APIRouter()
for _sub in (_model, _prompt, _server, _agents, _toolset, _graph):
    agent.include_router(_sub)
