from pydantic import BaseModel
from typing import List, Optional

class Idea(BaseModel):
    title: str
    rationale: str
    risks: Optional[str] = None

class Plan(BaseModel):
    steps: List[str]

class PolicyDecision(BaseModel):
    result: str  # ALLOW | REWRITE | BLOCK
    rules: List[str] = []

class ExecReport(BaseModel):
    status: str
    artifacts: List[str]

class SelfSnapshot(BaseModel):
    state: str
    health: str
