from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment="用户id")
    scenic_id = Column(Integer, nullable=False, comment="景点id")
    score = Column(Integer, comment="评分1‑5分")
    content = Column(Text, comment="用户评论文本")
    img_list = Column(Text, comment="图片，逗号分隔")
    sentiment = Column(String(20), comment="情感结果：正面/中性/负面")
    keywords = Column(Text, comment="提取关键词，逗号分隔")
    audit_status = Column(Integer, default=0, comment="0待审核 1通过 2驳回")
    create_time = Column(DateTime, default=func.now())
