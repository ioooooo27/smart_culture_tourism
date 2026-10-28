from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class FoodLodging(Base):
    """美食住宿 UGC 圈子：用户和管理员都能发布"""
    __tablename__ = "food_lodging"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, default=1, comment="发布用户id")
    username = Column(String(64), comment="发布人昵称快照")
    type = Column(String(20), nullable=False, comment="类型：美食/住宿")
    title = Column(String(128), nullable=False, comment="标题")
    desc = Column(Text, comment="内容描述")
    img = Column(Text, comment="图片，逗号分隔")
    address = Column(String(255), comment="地址")
    lng = Column(String(32), comment="经度")
    lat = Column(String(32), comment="纬度")
    price = Column(String(64), comment="人均/价格")
    status = Column(Integer, default=1, comment="1正常 0下架")
    create_time = Column(DateTime, default=func.now())
