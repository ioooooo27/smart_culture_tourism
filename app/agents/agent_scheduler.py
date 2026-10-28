from app.agents.base_agent import BaseAgent
from app.agents.guide_agent import GuideAgent
from app.agents.route_agent import RouteAgent
from app.agents.sentiment_agent import SentimentAgent
from app.agents.dispatch_agent import DispatchAgent
from loguru import logger

class AgentScheduler:
    def __init__(self):
        # 实例化全部4个智能体
        self.guide_agent = GuideAgent()
        self.route_agent = RouteAgent()
        self.sentiment_agent = SentimentAgent()
        self.dispatch_agent = DispatchAgent()

    async def dispatch_task(self, user_input: dict):
        """
        根据任务类型自动分配智能体，支持多智能体协同
        task_type: qa(景点问答), plan_route(路线规划), analysis_comment(评论情感分析), service_notice(便民调度)
        """
        task_type = user_input.get("task_type")
        logger.info(f"调度器收到任务: {task_type}, 用户输入:{user_input}")
        result = {}

        if task_type == "qa":
            result["guide_result"] = await self.guide_agent.run(user_input)
        elif task_type == "plan_route":
            result["route_result"] = await self.route_agent.run(user_input)
        elif task_type == "analysis_comment":
            result["sentiment_result"] = await self.sentiment_agent.run(user_input)
        elif task_type == "service_notice":
            result["dispatch_result"] = await self.dispatch_agent.run(user_input)
        # 协同场景：同时需要导览+路线推荐
        elif task_type == "route_with_intro":
            result["route_result"] = await self.route_agent.run(user_input)
            result["guide_result"] = await self.guide_agent.run(user_input)
        else:
            result["msg"] = "不支持该任务类型"
        return result

# 全局调度器单例
scheduler = AgentScheduler()
