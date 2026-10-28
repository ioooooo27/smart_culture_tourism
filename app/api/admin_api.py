from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from app.database import get_db
from app.models.admin import Admin, AgentConfigLog
from app.models.comment import Comment
from app.models.work_order import WorkOrder
from app.models.food_lodging import FoodLodging
from app.models.scenic import ScenicSpot
from app.models.user import User
from app.schemas.admin_schema import AdminLogin, OrderHandle, ScenicSpotSave
from app.schemas.user_schema import FoodLodgingCreate, FoodLodgingUpdate, CommentUpdate
from app.schemas.agent_schema import AgentConfigUpdate
from app.core.security import verify_password, create_access_token
from app.core.rbac import get_current_admin, require_super_admin
from app.agents.agent_scheduler import scheduler
from loguru import logger

router = APIRouter()

@router.post("/login", summary="管理员登录")
def admin_login(item: AdminLogin, db:Session=Depends(get_db)):
    adm = db.query(Admin).filter(Admin.username == item.username).first()
    if not adm or not verify_password(item.password, adm.password):
        raise HTTPException(status_code=400, detail="账号密码错误")
    token = create_access_token({"sub":str(adm.id)})
    return {"code":200,"token":token,"role":adm.role}

@router.post("/agent/update_config", summary="修改智能体算法参数【毕设核心接口】", dependencies=[Depends(require_super_admin)])
def update_agent_config(req:AgentConfigUpdate, db:Session=Depends(get_db), curr_admin=Depends(get_current_admin)):
    """后台可视化调整各个智能体参数，同时写操作日志到数据库"""
    agent_map = {
        "景点导览智能体": scheduler.guide_agent,
        "路线规划智能体": scheduler.route_agent,
        "游客评论情感分析智能体": scheduler.sentiment_agent,
        "便民调度智能体": scheduler.dispatch_agent
    }
    if req.agent_name not in agent_map:
        raise HTTPException(status_code=400, detail="不存在该智能体")
    target_agent = agent_map[req.agent_name]
    target_agent.set_config(req.config)

    # 数据库记录参数修改日志
    log_item = AgentConfigLog(
        agent_name=req.agent_name,
        config_content=json.dumps(req.config, ensure_ascii=False),
        admin_id=curr_admin.id
    )
    db.add(log_item)
    db.commit()
    logger.info(f"管理员 {curr_admin.username} 修改智能体 {req.agent_name} 参数 {req.config}")
    return {"code":200,"msg":"智能体参数更新成功"}

@router.get("/dashboard/sentiment_stat", summary="大屏：情感统计数据，给Echarts饼图")
def dashboard_sentiment(db:Session=Depends(get_db), _=Depends(get_current_admin)):
    total = db.query(Comment).count()
    pos = db.query(Comment).filter(Comment.sentiment=="正面").count()
    neu = db.query(Comment).filter(Comment.sentiment=="中性").count()
    neg = db.query(Comment).filter(Comment.sentiment=="负面").count()
    return {
        "code":200,
        "data":{
            "total":total,
            "positive":pos,
            "neutral":neu,
            "negative":neg
        }
    }

@router.get("/work_order/list", summary="获取工单列表")
def get_work_order(db:Session=Depends(get_db), _=Depends(get_current_admin)):
    data = db.query(WorkOrder).all()
    return {"code":200,"data":data}

@router.post("/work_order/handle", summary="处理回复工单")
def handle_work_order(item:OrderHandle, db:Session=Depends(get_db), _=Depends(get_current_admin)):
    wo = db.query(WorkOrder).filter(WorkOrder.id == item.order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="工单不存在")
    wo.status = 2
    wo.reply = item.reply
    db.commit()
    return {"code":200,"msg":"工单已处理完成"}

# ============ 美食住宿管理 ============
@router.get("/food/list", summary="管理员获取全部美食住宿")
def admin_food_list(type: str = "", keyword: str = "", db:Session=Depends(get_db), _=Depends(get_current_admin)):
    q = db.query(FoodLodging)
    if type:
        q = q.filter(FoodLodging.type == type)
    if keyword:
        q = q.filter(FoodLodging.title.like(f"%{keyword}%"))
    rows = q.order_by(FoodLodging.create_time.desc()).all()
    return {"code":200,"data":[{
        "id":r.id,"type":r.type,"title":r.title,"desc":r.desc or "",
        "img":r.img or "","address":r.address or "","lng":r.lng or "","lat":r.lat or "",
        "price":r.price or "","username":r.username or "游客","status":r.status,
        "create_time":str(r.create_time)[:19] if r.create_time else ""
    } for r in rows]}

@router.post("/food/create", summary="管理员新增美食住宿")
def admin_food_create(item: FoodLodgingCreate, db:Session=Depends(get_db), _=Depends(get_current_admin)):
    row = FoodLodging(
        user_id=1, username="管理员",
        type=item.type, title=item.title, desc=item.desc, img=item.img,
        address=item.address, lng=item.lng, lat=item.lat, price=item.price
    )
    db.add(row); db.commit()
    return {"code":200,"msg":"新增成功","id":row.id}

@router.put("/food/{rid}", summary="管理员编辑美食住宿")
def admin_food_update(rid: int, item: FoodLodgingUpdate, db:Session=Depends(get_db), _=Depends(get_current_admin)):
    row = db.query(FoodLodging).filter(FoodLodging.id==rid).first()
    if not row: raise HTTPException(404,"不存在")
    for k,v in item.dict(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    return {"code":200,"msg":"修改成功"}

@router.delete("/food/{rid}", summary="管理员删除美食住宿")
def admin_food_delete(rid: int, db:Session=Depends(get_db), _=Depends(get_current_admin)):
    row = db.query(FoodLodging).filter(FoodLodging.id==rid).first()
    if not row: raise HTTPException(404,"不存在")
    db.delete(row); db.commit()
    return {"code":200,"msg":"已删除"}

# ============ 评论管理 ============
@router.get("/comment/list", summary="管理员获取全部评论")
def admin_comment_list(scenic_id: int = 0, keyword: str = "", db:Session=Depends(get_db), _=Depends(get_current_admin)):
    q = db.query(Comment, User).join(User, User.id==Comment.user_id, isouter=True)
    if scenic_id:
        q = q.filter(Comment.scenic_id==scenic_id)
    if keyword:
        q = q.filter(Comment.content.like(f"%{keyword}%"))
    rows = q.order_by(Comment.create_time.desc()).limit(200).all()
    return {"code":200,"data":[{
        "id":c.id,"scenic_id":c.scenic_id,"score":c.score,"content":c.content,
        "sentiment":c.sentiment,"keywords":c.keywords,"audit_status":c.audit_status,
        "nickname":(u.nickname or u.username) if u else "游客",
        "create_time":str(c.create_time)[:19] if c.create_time else ""
    } for c,u in rows]}

@router.put("/comment/{cid}", summary="管理员编辑评论")
def admin_comment_update(cid: int, item: CommentUpdate, db:Session=Depends(get_db), _=Depends(get_current_admin)):
    row = db.query(Comment).filter(Comment.id==cid).first()
    if not row: raise HTTPException(404,"评论不存在")
    if item.content is not None: row.content = item.content
    if item.score is not None: row.score = item.score
    if item.sentiment is not None: row.sentiment = item.sentiment
    db.commit()
    return {"code":200,"msg":"修改成功"}

@router.delete("/comment/{cid}", summary="管理员删除评论")
def admin_comment_delete(cid: int, db:Session=Depends(get_db), _=Depends(get_current_admin)):
    row = db.query(Comment).filter(Comment.id==cid).first()
    if not row: raise HTTPException(404,"评论不存在")
    db.delete(row); db.commit()
    return {"code":200,"msg":"已删除"}

# ============ 景点管理 ============
@router.get("/scenic/list", summary="管理员获取全部景点")
def admin_scenic_list(db:Session=Depends(get_db), _=Depends(get_current_admin)):
    rows = db.query(ScenicSpot).order_by(ScenicSpot.id).all()
    return {"code":200,"data":[{
        "id":r.id,"name":r.name,"cover_img":r.cover_img or "","introduce":r.introduce or "",
        "open_time":r.open_time or "","ticket":r.ticket or "","location":r.location or "",
        "tag":r.tag or "","longitude":r.longitude or 0,"latitude":r.latitude or 0,"status":r.status
    } for r in rows]}

@router.post("/scenic/save", summary="新增/编辑景点")
def admin_scenic_save(item: ScenicSpotSave, sid: int = 0, db:Session=Depends(get_db), _=Depends(get_current_admin)):
    if sid and sid > 0:
        row = db.query(ScenicSpot).filter(ScenicSpot.id==sid).first()
        if row:
            for k,v in item.dict().items():
                setattr(row, k, v)
            db.commit()
            return {"code":200,"msg":"修改成功","id":row.id}
        # 景点已被删除，自动转新增
    row = ScenicSpot(**item.dict())
    db.add(row); db.commit()
    return {"code":200,"msg":"新增成功","id":row.id}

@router.delete("/scenic/{sid}", summary="删除景点")
def admin_scenic_delete(sid: int, db:Session=Depends(get_db), _=Depends(get_current_admin)):
    row = db.query(ScenicSpot).filter(ScenicSpot.id==sid).first()
    if not row: raise HTTPException(404,"景点不存在")
    db.delete(row); db.commit()
    return {"code":200,"msg":"已删除"}

# ============ 图片上传 ============
from fastapi import UploadFile, File
import uuid

@router.post("/upload_img", summary="上传本地图片")
async def upload_img(file: UploadFile = File(...), _=Depends(get_current_admin)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ('.jpg','.jpeg','.png','.gif','.webp'):
        raise HTTPException(400,"只支持jpg/png/gif/webp")
    fname = f"up_{uuid.uuid4().hex[:8]}{ext}"
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"frontend","images")
    os.makedirs(out_dir, exist_ok=True)
    content = await file.read()
    if len(content) > 5*1024*1024:
        raise HTTPException(400,"图片不超过5MB")
    with open(os.path.join(out_dir,fname),"wb") as f:
        f.write(content)
    return {"code":200,"data":"/images/"+fname}

# ============ AI智能填充景点信息 ============
import os, json as _json
from openai import OpenAI as _OpenAI

@router.post("/scenic/auto_fill", summary="AI根据景点名自动填充信息")
async def scenic_auto_fill(name: str, db:Session=Depends(get_db), _=Depends(get_current_admin)):
    api_key = os.getenv("LLM_API_KEY","")
    base_url = os.getenv("LLM_BASE_URL","https://open.bigmodel.cn/api/paas/v4")
    if not api_key or "你的" in api_key:
        raise HTTPException(400,"未配置LLM_API_KEY")
    client = _OpenAI(api_key=api_key, base_url=base_url)
    prompt = f"""请根据景点"{name}"，返回严格的JSON格式（不要markdown代码块，直接返回JSON）：
{{"location":"该景点真实所在城市和详细地址","tag":"标签1,标签2","open_time":"开放时间","ticket":"门票价格","introduce":"80字左右景点真实简介，不要编造城市"}}
只返回JSON，不要其他内容。"""
    try:
        resp = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role":"user","content":prompt}],
            temperature=0.3
        )
        text = resp.choices[0].message.content.strip()
        # 去掉可能的```json包裹
        if text.startswith("```"):
            text = text.split("```")[1].replace("json","",1).strip()
        data = _json.loads(text)
        data["cover_img"] = ""  # 图片由管理员手动上传，AI不自动配
        return {"code":200,"data":data}
    except Exception as e:
        logger.error(f"AI填充失败: {e}")
        raise HTTPException(500,f"AI填充失败: {str(e)[:100]}")


@router.get("/user/list")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.desc()).all()
    return {"code":200,"data":[{
        "id":u.id,"username":u.username,"nickname":u.nickname or u.username,
        "integral":u.integral,"create_time":str(u.create_time)
    } for u in users]}


@router.delete("/user/{uid}")
def delete_user(uid:int, db: Session = Depends(get_db)):
    u = db.query(User).get(uid)
    if not u: raise HTTPException(404,"用户不存在")
    db.delete(u); db.commit()
    return {"code":200,"msg":"已删除"}


@router.put("/user/{uid}")
def update_user(uid:int, body:dict, db: Session = Depends(get_db)):
    u = db.query(User).get(uid)
    if not u: raise HTTPException(404,"用户不存在")
    if "nickname" in body: u.nickname = body["nickname"]
    if body.get("password"): u.password = body["password"]
    if "integral" in body: u.integral = body["integral"]
    db.commit()
    return {"code":200,"msg":"已更新"}


@router.get("/user/{uid}/detail")
def user_detail(uid:int, db: Session = Depends(get_db)):
    u = db.query(User).get(uid)
    if not u: raise HTTPException(404,"用户不存在")
    comments = db.query(Comment).filter(Comment.user_id==uid).all()
    return {"code":200,"data":{
        "id":u.id,"username":u.username,"nickname":u.nickname,
        "password_masked":u.password or "",
        "integral":u.integral,"create_time":str(u.create_time),
        "comments":[{"id":c.id,"scenic_id":c.scenic_id,"score":c.score,"content":c.content,"create_time":str(c.create_time),"sentiment":c.sentiment} for c in comments]
    }}