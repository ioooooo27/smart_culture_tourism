from app.database import engine, Base
from app.models import *

def create_tables():
    print("开始创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据表创建成功！打开Navicat刷新查看")

if __name__ == "__main__":
    create_tables()
