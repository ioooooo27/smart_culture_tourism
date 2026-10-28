from pydantic import BaseModel
from typing import Dict, Any

# 后台修改智能体参数接收模型
class AgentConfigUpdate(BaseModel):
    agent_name: str
    config: Dict[str, Any]

# 用户调用智能体请求体
class AgentTaskRequest(BaseModel):
    task_type: str
    question: str | None = None
    total_time: int | None = None
    preference: str | None = None
    comment_text: str | None = None
    scenic_id: int | None = None
    crowd: str | None = None
    weather: str | None = None
