from abc import ABC, abstractmethod
from loguru import logger

class BaseAgent(ABC):
    agent_name: str
    config: dict = {}

    def set_config(self, config_dict: dict):
        """后台动态修改智能体参数"""
        self.config.update(config_dict)
        logger.info(f"[{self.agent_name}] 更新配置: {self.config}")

    @abstractmethod
    async def run(self, input_data: dict) -> dict:
        """智能体执行任务的抽象方法，子类必须重写"""
        pass
