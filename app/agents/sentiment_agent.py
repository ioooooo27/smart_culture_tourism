from app.agents.base_agent import BaseAgent
import jieba
from loguru import logger

class SentimentAgent(BaseAgent):
    agent_name = "游客评论情感分析智能体"
    config = {
        "model_name": "mock",  # 模拟模式：不联网下载模型
        "threshold": 0.5
    }

    def __init__(self):
        # 跳过 huggingface 模型下载，改用本地规则模拟
        logger.info("【情感智能体】当前为模拟模式（跳过模型下载）")

    async def run(self, input_data: dict) -> dict:
        comment = input_data.get("comment_text", "")
        logger.info(f"【情感智能体】分析评论：{comment}")

        # 本地关键词规则判断情感，不依赖任何远程模型
        positive_words = ["好", "赞", "美", "棒", "喜欢", "满意", "好玩", "漂亮", "值得", "推荐", "开心", "不错", "超值", "好评", "舒适", "热情"]
        negative_words = ["差", "失望", "后悔", "不值", "坑", "垃圾", "难吃", "糟糕", "生气", "差评", "骗", "贵", "吵", "脏", "冷", "慢"]

        pos_count = sum(1 for w in positive_words if w in comment)
        neg_count = sum(1 for w in negative_words if w in comment)

        if pos_count > neg_count:
            sentiment = "正面"
        elif neg_count > pos_count:
            sentiment = "负面"
        else:
            sentiment = "中性"

        keywords = jieba.lcut(comment)
        return {
            "sentiment": sentiment,
            "keywords": keywords,
            "agent": self.agent_name
        }
