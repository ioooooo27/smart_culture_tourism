from app.agents.base_agent import BaseAgent
from app.database import redis_client
from loguru import logger

class DispatchAgent(BaseAgent):
    agent_name = "便民调度智能体"
    config = {
        "crowd_warn_threshold": 800
    }

    async def run(self, input_data: dict) -> dict:
        scenic_id = input_data.get("scenic_id")
        # 读取redis实时人流
        current_crowd = int(redis_client.get(f"crowd_{scenic_id}") or 0)
        logger.info(f"【调度智能体】景区{scenic_id},实时人流：{current_crowd}")
        if current_crowd > self.config["crowd_warn_threshold"]:
            tip = "⚠️当前人流量过大，建议错峰游玩"
        else:
            tip = "✅人流正常，适合游览"
        return {
            "scenic_id":scenic_id,
            "current_crowd":current_crowd,
            "service_tip":tip,
            "agent": self.agent_name
        }
