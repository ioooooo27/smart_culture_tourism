from sqlalchemy import Column, Integer, String, Text, Float
from app.database import Base

class ScenicSpot(Base):
    __tablename__ = "scenic_spot"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="景点名称")
    cover_img = Column(String(255), comment="封面图")
    introduce = Column(Text, comment="景点简介")
    open_time = Column(String(100), comment="开放时间")
    ticket = Column(String(100), comment="票价")
    location = Column(String(100), comment="位置")
    tag = Column(String(200), comment="标签：人文,亲子,徒步,自然风光")
    longitude = Column(Float, comment="经度")
    latitude = Column(Float, comment="纬度")
    status = Column(Integer, default=1, comment="1开放 0关闭")
