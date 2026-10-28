from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    nickname = Column(String(50), comment="昵称")
    avatar = Column(String(255), comment="头像地址")
    integral = Column(Integer, default=0, comment="打卡积分")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
