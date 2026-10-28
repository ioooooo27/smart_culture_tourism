from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class WorkOrder(Base):
    __tablename__ = "work_order"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, comment="提交用户id")
    order_type = Column(String(30), comment="类型 complaint投诉 / lost失物招领")
    title = Column(String(100), comment="工单标题")
    content = Column(Text, comment="内容")
    priority = Column(Integer, default=2, comment="优先级1高 2中 3低，智能体自动分配")
    status = Column(Integer, default=0, comment="0待处理 1处理中 2已完成")
    reply = Column(Text, comment="管理员回复")
    img = Column(Text, comment="用户上传的图片，base64")
    create_time = Column(DateTime, default=func.now())
    handle_time = Column(DateTime, nullable=True)
