from fastapi import APIRouter
from bus.schemas import Plan, PolicyDecision

router = APIRouter(prefix="/superego", tags=["Superego"])

@router.post("/check", response_model=PolicyDecision)
async def superego_check(plan: Plan):
    if any("delete" in step.lower() for step in plan.steps):
        return PolicyDecision(result="BLOCK", rules=["No destructive commands"])
    return PolicyDecision(result="ALLOW", rules=["OK"])
