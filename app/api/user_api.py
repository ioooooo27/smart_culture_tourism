from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.comment import Comment
from app.models.scenic import ScenicSpot
from app.models.work_order import WorkOrder
from app.models.food_lodging import FoodLodging
from app.schemas.user_schema import UserCreate, UserLogin, CommentCreate, WorkOrderSubmit, FoodLodgingCreate
from app.core.security import get_password_hash, verify_password, create_access_token
from app.agents.agent_scheduler import scheduler
from loguru import logger

router = APIRouter()

@router.post("/register", summary="用户注册")
def user_register(item: UserCreate, db: Session=Depends(get_db)):
    exist = db.query(User).filter(User.username == item.username).first()
    if exist:
        raise HTTPException(status_code=400, detail="用户名已存在")
    new_user = User(
        username=item.username,
        password=item.password,  # 明文存储方便演示
        nickname=item.nickname or item.username
    )
    db.add(new_user)
    db.commit()
    return {"code":200, "msg":"注册成功"}

@router.post("/login", summary="用户登录")
def user_login(item: UserLogin, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.username == item.username).first()
    if not user or user.password != item.password:
        raise HTTPException(status_code=400, detail="账号密码错误")
    token = create_access_token({"sub":str(user.id)})
    return {"code":200, "token":token, "user_id":user.id, "nickname":user.nickname}

@router.post("/publish_comment", summary="发布评价，自动调用情感分析智能体")
async def publish_comment(item: CommentCreate, db:Session=Depends(get_db)):
    # 保存原始评论
    new_comment = Comment(
        user_id=getattr(item,'user_id',1) or 1,
        scenic_id=item.scenic_id,
        score=item.score,
        content=item.content
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    # 调用情感分析智能体
    agent_result = await scheduler.dispatch_task({
        "task_type":"analysis_comment",
        "comment_text": item.content
    })
    sentiment_data = agent_result["sentiment_result"]

    # 将AI分析结果回写到数据库
    new_comment.sentiment = sentiment_data["sentiment"]
    new_comment.keywords = ",".join(sentiment_data["keywords"])
    db.commit()

    return {"code":200, "msg":"评价发布完成，已完成情感分析","ai_result":sentiment_data}

@router.get("/scenic/list", summary="获取景点列表")
def get_scenic_list(db:Session=Depends(get_db)):
    list_data = db.query(ScenicSpot).filter(ScenicSpot.status==1).all()
    return {"code":200, "data":list_data}

@router.get("/search_img", summary="根据关键词搜一张景点图")
def search_img(keyword: str = ""):
    import urllib.request, urllib.parse, ssl, re
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        q = urllib.parse.quote(keyword + ' 景点')
        url = f'https://cn.bing.com/images/search?q={q}&form=HDRSC2'
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req, timeout=8, context=ctx).read().decode('utf-8', errors='ignore')
        urls = re.findall(r'murl&quot;:&quot;(.*?)&quot;', html)
        if not urls:
            urls = re.findall(r'"murl":"(.*?)"', html)
        for u in urls[:5]:
            if u.startswith('http') and not u.endswith('.gif'):
                return {"code":200, "data":u}
    except:
        pass
    return {"code":200, "data":""}

@router.get("/crowd_map", summary="获取所有景点实时人流")
def crowd_map(db:Session=Depends(get_db)):
    import random
    spots = db.query(ScenicSpot).filter(ScenicSpot.status==1).all()
    result = {}
    for s in spots:
        # 根据景点id生成稳定的模拟人流
        random.seed(s.id * 7 + 3)
        result[s.name] = random.randint(200, 1800)
    return {"code":200, "data":result}

@router.get("/comment/list", summary="获取历史评论")
def get_comment_list(scenic_id:int=0, db:Session=Depends(get_db)):
    q = db.query(Comment, User).join(User, User.id==Comment.user_id)
    if scenic_id and scenic_id>0:
        q = q.filter(Comment.scenic_id==scenic_id)
    rows = q.order_by(Comment.create_time.desc()).limit(50).all()
    data = []
    for c, u in rows:
        data.append({
            "id": c.id,
            "scenic_id": c.scenic_id,
            "score": c.score,
            "content": c.content,
            "sentiment": c.sentiment,
            "keywords": c.keywords,
            "create_time": str(c.create_time)[:19] if c.create_time else "",
            "nickname": (u.nickname or u.username) if u else "游客"
        })
    return {"code":200, "data":data}

@router.post("/submit_work_order", summary="提交投诉/失物招领工单（可带图片）")
def submit_work_order(item:WorkOrderSubmit, db:Session=Depends(get_db)):
    wo = WorkOrder(
        user_id=1,
        order_type=item.order_type,
        title=item.title,
        content=item.content,
        img=item.img or ""
    )
    db.add(wo)
    db.commit()
    return {"code":200,"msg":"工单提交成功","order_id":wo.id}

# ============ 美食住宿 UGC ============
@router.get("/food/list", summary="美食住宿圈子列表")
def food_list(type: str = "", db: Session = Depends(get_db)):
    q = db.query(FoodLodging).filter(FoodLodging.status == 1)
    if type:
        q = q.filter(FoodLodging.type == type)
    rows = q.order_by(FoodLodging.create_time.desc()).all()
    return {"code":200,"data":[{
        "id":r.id,"type":r.type,"title":r.title,"desc":r.desc or "",
        "img":r.img or "","address":r.address or "","lng":r.lng or "","lat":r.lat or "",
        "price":r.price or "","username":r.username or "游客",
        "create_time":str(r.create_time)[:19] if r.create_time else ""
    } for r in rows]}

@router.post("/food/create", summary="用户发布美食/住宿")
def food_create(item: FoodLodgingCreate, db: Session = Depends(get_db)):
    row = FoodLodging(
        user_id=1, username="游客",
        type=item.type, title=item.title, desc=item.desc, img=item.img,
        address=item.address, lng=item.lng, lat=item.lat, price=item.price
    )
    db.add(row); db.commit()
    return {"code":200,"msg":"发布成功","id":row.id}
