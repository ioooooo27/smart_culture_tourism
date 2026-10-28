# -*- coding: utf-8 -*-
"""
初始化脚本：创建管理员账号 + 插入演示景点数据
运行：python init_data.py
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, redis_client
from app.models.admin import Admin
from app.models.scenic import ScenicSpot
from app.core.security import get_password_hash
from loguru import logger

# ============ 1. 创建管理员账号 ============
def create_admin():
    db: Session = SessionLocal()
    try:
        exists = db.query(Admin).filter(Admin.username == "admin").first()
        if exists:
            logger.info("管理员账号已存在，跳过创建")
        else:
            admin = Admin(
                username="admin",
                password=get_password_hash("admin123"),
                role="super_admin"
            )
            db.add(admin)
            db.commit()
            logger.info("✅ 管理员账号创建成功：admin / admin123（超级管理员）")
    finally:
        db.close()

# ============ 2. 插入演示景点数据 ============
def create_scenic():
    db: Session = SessionLocal()
    try:
        if db.query(ScenicSpot).count() > 0:
            logger.info("景点数据已存在，跳过插入")
            return
        scenic_list = [
            ScenicSpot(
                name="黄鹤楼", cover_img="", tag="人文,历史地标",
                introduce="江南三大名楼之首，登楼可眺望长江与武汉三镇，享有\"天下江山第一楼\"美誉。",
                open_time="08:00-18:00", ticket="70元", location="武汉市武昌区蛇山",
                longitude=114.307, latitude=30.545, status=1
            ),
            ScenicSpot(
                name="东湖听涛景区", cover_img="", tag="自然风光,亲子",
                introduce="中国最大城中湖东湖的核心景区，湖光山色，绿道环湖，是休闲漫步的绝佳去处。",
                open_time="全天开放", ticket="免费", location="武汉市武昌区东湖路",
                longitude=114.392, latitude=30.565, status=1
            ),
            ScenicSpot(
                name="湖北省博物馆", cover_img="", tag="人文,博物馆",
                introduce="馆藏曾侯乙编钟、越王勾践剑等国宝级文物，感受荆楚大地千年文化底蕴。",
                open_time="09:00-17:00（周一闭馆）", ticket="免费（需预约）", location="武汉市武昌区东湖路160号",
                longitude=114.378, latitude=30.564, status=1
            ),
            ScenicSpot(
                name="武汉大学樱花大道", cover_img="", tag="自然风光,网红打卡",
                introduce="春日樱花烂漫，百年学府与花海相映成趣，被誉为中国最美校园之一。",
                open_time="全天开放", ticket="免费（花期需预约）", location="武汉市武昌区珞珈山",
                longitude=114.366, latitude=30.537, status=1
            ),
            ScenicSpot(
                name="归元禅寺", cover_img="", tag="人文古迹,祈福",
                introduce="武汉著名佛教丛林，五百罗汉堂闻名海内外，香火鼎盛，环境清幽。",
                open_time="08:00-17:00", ticket="10元", location="武汉市汉阳区翠微路20号",
                longitude=114.256, latitude=30.553, status=1
            ),
            ScenicSpot(
                name="木兰天池", cover_img="", tag="自然风光,徒步",
                introduce="峡谷溪流、高山湖泊、森林瀑布，华中地区知名的生态旅游度假胜地。",
                open_time="08:00-17:30", ticket="80元", location="武汉市黄陂区长轩岭镇",
                longitude=114.302, latitude=31.223, status=1
            ),
        ]
        db.add_all(scenic_list)
        db.commit()
        logger.info(f"✅ 插入演示景点 {len(scenic_list)} 条")
    finally:
        db.close()

# ============ 3. 写入Redis模拟人流数据 ============
def init_redis_crowd():
    try:
        for i in range(1, 7):
            # 随机模拟人流 200-1200
            import random
            redis_client.set(f"crowd_{i}", random.randint(200, 1200))
        logger.info("✅ Redis模拟人流数据写入完成（crowd_1 ~ crowd_6）")
    except Exception as e:
        logger.warning(f"⚠️ Redis未启动或连接失败（{e}），便民调度可后续启动Redis后再使用")

if __name__ == "__main__":
    logger.info("========== 开始初始化演示数据 ==========")
    create_admin()
    create_scenic()
    init_redis_crowd()
    logger.info("========== 初始化完成！==========")
    logger.info("管理员账号：admin / admin123")
    logger.info("前端页面：http://127.0.0.1:8000/")
