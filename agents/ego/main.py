from fastapi import APIRouter
from bus.schemas import Plan, ExecReport

router = APIRouter(prefix="/ego", tags=["Ego"])

@router.post("/execute", response_model=ExecReport)
async def ego_execute(plan: Plan):
    # Très simple exécution simulée : on retourne succès et liste d'artifacts
    artifacts = [f"step_{i+1}_{step.replace(' ','_')}.txt" for i, step in enumerate(plan.steps)]
    return ExecReport(status="OK", artifacts=artifacts)
