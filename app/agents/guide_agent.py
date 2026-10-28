import os
from loguru import logger
from dotenv import load_dotenv
from openai import OpenAI

# 加载.env配置
load_dotenv()


class GuideAgent:
    def __init__(self):
        self.agent_name = "文旅导游智能体"
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.base_url = os.getenv("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
        self.model = "glm-4-flash"          # 智谱免费模型，毕设够用
        self.max_context = 6000             # 知识库截取长度，防止超token
        self._knowledge = self._load_knowledge()
        self._client = None
        if self.api_key and "你的" not in self.api_key:
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            logger.warning("【导览智能体】未检测到有效的智谱API Key，将使用模拟回答")

    def _load_knowledge(self) -> str:
        """读取项目根目录 knowledge_data 下的全部txt知识库文件"""
        text = ""
        # 优先取当前工作目录下的 knowledge_data（从项目根目录运行main.py时）
        cwd_folder = os.path.join(os.getcwd(), "knowledge_data")
        # 兜底：从文件位置反推项目根目录
        file_folder = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "knowledge_data"
        )
        folder = cwd_folder if os.path.isdir(cwd_folder) else file_folder
        if not os.path.isdir(folder):
            logger.warning(f"【导览智能体】知识库文件夹不存在：{folder}")
            return text
        for filename in os.listdir(folder):
            if filename.endswith(".txt"):
                try:
                    with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
                        text += f.read() + "\n"
                except Exception as e:
                    logger.warning(f"读取知识文件失败 {filename}: {e}")
        logger.info(f"【导览智能体】知识库加载完成，共 {len(text)} 字符")
        return text

    async def run(self, input_data: dict) -> dict:
        user_question = input_data.get("question", "").strip()
        logger.info(f"【导览智能体】用户提问：{user_question}")

        # 未配置API Key时回退模拟回答
        if self._client is None:
            answer = (
                f"【模拟回答】尚未配置智谱API Key，暂时无法调用真实大模型。\n"
                f"请在项目.env文件中填写 LLM_API_KEY，重启后端后即可获得真实AI讲解。\n"
                f"你问的是：{user_question}"
            )
            return {"answer": answer, "agent": self.agent_name}

        try:
            knowledge = self._knowledge[:self.max_context] if self._knowledge else "（知识库为空）"
            system_prompt = (
                "你是智慧文旅平台的【景点导览智能体】，请根据下方景区知识库回答游客问题。要求：\n"
                "1. 回答专业、热情、条理清晰，先直接回答问题，再补充游玩建议；\n"
                "2. 优先使用知识库中的信息（开放时间、门票、交通、美食、注意事项等）；\n"
                "3. 知识库没有的内容，可以结合你的常识补充，但不要编造；\n"
                "4. 控制在200-400字，语气亲切自然。\n\n"
                f"【景区知识库】\n{knowledge}"
            )
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                temperature=0.7,
                max_tokens=800
            )
            answer = resp.choices[0].message.content.strip()
            logger.info(f"【导览智能体】智谱回答成功：{answer[:80]}...")
        except Exception as e:
            logger.error(f"【导览智能体】智谱调用失败：{e}")
            answer = (
                f"（AI服务暂时不可用：{e}）\n"
                f"可能原因：智谱API Key无效、额度耗尽或网络问题，请检查.env配置后重启后端。"
            )
        return {"answer": answer, "agent": self.agent_name}
