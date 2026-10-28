from loguru import logger
import sys

# 配置日志：控制台输出 + 本地文件保存
logger.remove()
# 控制台打印
logger.add(
    sys.stdout,
    format="<green>{time:YYYY‑MM‑DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    level="INFO"
)
# 日志保存到logs文件夹，自动分割
logger.add(
    "logs/tourism_{time}.log",
    rotation="500 MB",
    retention="10 days",
    encoding="utf‑8",
    level="INFO"
)

__all__ = ["logger"]
