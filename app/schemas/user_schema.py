from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str
    nickname: str | None = None

class UserLogin(BaseModel):
    username: str
    password: str

class CommentCreate(BaseModel):
    scenic_id: int
    score: int
    content: str
    user_id: int = 1

class WorkOrderSubmit(BaseModel):
    title: str
    content: str
    order_type: str
    img: str = ""

class FoodLodgingCreate(BaseModel):
    type: str = "美食"
    title: str
    desc: str = ""
    img: str = ""
    address: str = ""
    lng: str = ""
    lat: str = ""
    price: str = ""

class FoodLodgingUpdate(BaseModel):
    type: str | None = None
    title: str | None = None
    desc: str | None = None
    img: str | None = None
    address: str | None = None
    lng: str | None = None
    lat: str | None = None
    price: str | None = None
    status: int | None = None

class CommentUpdate(BaseModel):
    content: str | None = None
    score: int | None = None
    sentiment: str | None = None
    status: int | None = None
