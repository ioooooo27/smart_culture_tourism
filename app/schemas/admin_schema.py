from pydantic import BaseModel

class AdminLogin(BaseModel):
    username: str
    password: str

class OrderHandle(BaseModel):
    order_id: int
    reply: str

class ScenicSpotSave(BaseModel):
    name: str
    cover_img: str = ""
    introduce: str = ""
    open_time: str = ""
    ticket: str = ""
    location: str = ""
    tag: str = ""
    longitude: float = 0
    latitude: float = 0
    status: int = 1
