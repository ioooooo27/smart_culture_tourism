from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="管理员账号")
    password = Column(String(255), nullable=False, comment="密码")
    role = Column(String(30), nullable=False, comment="角色 super_admin / operator")
    create_time = Column(DateTime, default=func.now())


class AgentConfigLog(Base):
    """智能体参数修改日志，毕设硬性要求，记录后台修改智能体参数"""
    __tablename__ = "agent_config_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(50), comment="智能体名称")
    config_content = Column(Text, comment="修改后的参数json")
    admin_id = Column(Integer, comment="操作管理员id")
    create_time = Column(DateTime, default=func.now())
