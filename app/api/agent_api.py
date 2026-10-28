from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.agents.agent_scheduler import scheduler
from app.schemas.agent_schema import AgentTaskRequest
from loguru import logger

router = APIRouter()

@router.post("/run_task", summary="执行智能体任务")
async def run_agent_task(req: AgentTaskRequest, db: Session = Depends(get_db)):
    """对外统一入口，调度各个AI智能体"""
    input_dict = req.model_dump(exclude_none=True)
    logger.info(f"收到智能体请求: {input_dict}")
    resp = await scheduler.dispatch_task(input_dict)
    return {"code":200, "data": resp}
