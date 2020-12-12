from datetime import date
from typing import Generic, List, TypeVar

from pydantic import BaseModel


class LJModel(BaseModel):
    class Config:
        orm_mode = True


class LJBaseResponse(BaseModel):
    code: int
    message: str = None
    data: LJModel = None


class AppVersion(LJModel):
    id: int
    version: str
    platform: int
    update_content: str
    update_type: int
    update_time: date


class AppVersionResponse(LJBaseResponse):
    data: AppVersion


class LoginRequest(LJModel):
    phone: str


class LoginResult(LJModel):
    id: int
    token: str


class LoginResponse(LJBaseResponse):
    data: LoginResult


class User(LJModel):
    id: int
    nickname: str
    status: int
    gender: int
    avatar: str
    vip_level: str
    whats_up: str
    constellation: str
    provice: str
    city: str
    area: str
    vertifiation_status: int
    vip_expire_time: date = None
    tag: str
    profile_photo_urls: str


class CreateUser(LJModel):
    phone: str
    nickname: str
    device: int
    gender: int
    avatar: str
    birthday: date
    provice: str
    city: str
    area: str
    address: str
    tag: str
    latitude: float
    longitude: float
    whats_up: str


class UpdateUserInfo(LJModel):
    nickname: str = None
    avatar: str = None
    birthday: date = None
    tag: str = None
    whats_up: str = None
    profile_photo_urls: str = None


class VisitUser(LJModel):
    User: User
    visit_times: int
    update_time: date


# 商品
class Product(LJModel):
    id: int
    name: str
    price: float
    original_price: float
    description: str = None
    iap_identifier: str = None


class ProductResponse(LJBaseResponse):
    data: List[Product] = None


# 更新用户位置
class UpdateUserLocation(LJModel):
    provice: str
    city: str
    area: str
    address: str
    latitude: float
    longitude: float


class UserResponse(LJBaseResponse):
    data: User


class UserLikeResponse(LJBaseResponse):
    data: List[User] = None


class ReportUser(LJModel):
    type: int
    content: str = None
    evidence_photo_url: str = None


class ReportPost(LJModel):
    type: int


class ReportComment(LJModel):
    type: int


class Post(LJModel):
    id: int
    create_time: date
    content: str
    cover_url: str
    type: int
    title: str
    media_urls: str
    provice: str
    city: str
    user: User


class CreatePost(LJModel):
    type: int
    content: str
    cover_url: str
    title: str
    media_urls: str
    provice: str
    city: str
    area: str
    latitude: float
    longitude: float
    address: str


class PostListResponse(LJBaseResponse):
    data: List[Post] = None


class PostDetailResponse(LJBaseResponse):
    data: Post


class CreateComment(LJModel):
    user_id: int
    content: str
    type: int
    source_comment_id: int = None
    to_user_id: int


class Comment(LJModel):
    id: int
    post_id: int
    user_id: int
    content: str
    create_time: date
    user: User
    type: str
    source_comment_id: int = None
    to_user_id: int


class PostCommentListResponse(LJBaseResponse):
    data: List[Comment] = None


class PostLike(LJModel):
    id: int
    post_id: int
    post: Post


class PostLikeListResponse(LJBaseResponse):
    data: List[PostLike] = None


class CreateOrder(LJModel):
    product_id: int
    pay_method: int


class UserVistorResponse(LJBaseResponse):
    data: List[VisitUser] = None
