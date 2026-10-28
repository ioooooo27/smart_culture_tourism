import os, json
from app.agents.base_agent import BaseAgent
from loguru import logger

try:
    from app.database import redis_client
except Exception:
    redis_client = None

try:
    from openai import OpenAI as _OpenAI
except Exception:
    _OpenAI = None


class RouteAgent(BaseAgent):
    agent_name = "路线规划智能体"
    config = {"max_scenic_num": 4, "prefer_weight": 0.6}

    async def run(self, input_data: dict) -> dict:
        total_time = input_data.get("total_time", 6)
        preference = input_data.get("preference", "自然风光")
        weather = input_data.get("weather", "晴天")
        people = input_data.get("people", "独自出行")
        budget = input_data.get("budget", "100-300元")
        start = input_data.get("start", "武昌")
        logger.info(f"【路线智能体】时长:{total_time}h, 偏好:{preference}, 人数:{people}")

        api_key = os.getenv("LLM_API_KEY", "")
        base_url = os.getenv("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")

        if not api_key or "你的" in api_key or _OpenAI is None:
            # 兜底硬编码
            route_list = [
                {"id":2,"name":"东湖听涛","traffic":"🚇 地铁8号线「省博站」B口步行12分钟","crowd":1200,"crowd_text":"1200人 · 适中"},
                {"id":6,"name":"木兰天池","traffic":"🚌 汉口火车站乘大巴到黄陂，转专线","crowd":800,"crowd_text":"800人 · 畅通"},
            ]
            return {"route":route_list,"suggest_time":total_time,
                    "weather_tip":f"当前天气{weather}，建议备好防晒/雨具",
                    "crowd_tip":f"全程{len(route_list)}个景点",
                    "agent":self.agent_name}

        client = _OpenAI(api_key=api_key, base_url=base_url)
        prompt = f"""用户在武汉旅游，游玩时长{total_time}小时，偏好"{preference}"，天气{weather}，{people}，人均预算{budget}，从{start}出发。
请推荐2-4个适合的景点组成路线，返回严格JSON（不要markdown）：
{{"route":[{{"name":"景点名","traffic":"怎么去（地铁/公交）","desc":"一句话亮点"}}],"tip":"整体建议"}}
根据出发区域安排就近景点，根据人数和预算推荐合适的消费场所。只返回JSON。"""
        try:
            resp = client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role":"user","content":prompt}],
                temperature=0.5
            )
            text = resp.choices[0].message.content.strip()
            if text.startswith("```"):
                text = text.split("```")[1].replace("json","",1).strip()
            data = json.loads(text)
            route_list = []
            for s in data.get("route", []):
                route_list.append({
                    "id": 0,
                    "name": s.get("name",""),
                    "traffic": s.get("traffic",""),
                    "crowd": 0,
                    "crowd_text": "",
                })
            return {"route":route_list,"suggest_time":total_time,
                    "weather_tip":f"当前天气{weather}，建议备好防晒/雨具",
                    "crowd_tip":data.get("tip",f"全程{len(route_list)}个景点"),
                    "agent":self.agent_name}
        except Exception as e:
            logger.error(f"路线AI失败: {e}")
            return {"route":[],"suggest_time":total_time,
                    "weather_tip":f"当前天气{weather}",
                    "crowd_tip":"AI暂时无法规划，请稍后重试",
                    "agent":self.agent_name}
