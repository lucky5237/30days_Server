from fastapi import FastAPI, Depends, Query, HTTPException, Header
from fastapi.exceptions import RequestValidationError, FastAPIError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from sql_app.database import SessionLocal, engine
from sql_app import crud, models, schemas
from sqlalchemy.orm import Session
from typing import List
import config
import requests
from response import SucResponse, BaseErrResponse, ServerErrorResponse
import uvicorn
import redis
from utils.Redis import Redis
from utils.tools import get_constellation
import hashlib
import hmac
import time
import uuid
import random
import datetime
import itunesiap

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def page_params(page: int = 0, size: int = 20):
    return {"page": page, "size": size}


# --- private methods ---

# 验证token是否合法
def token_is_true(version: str = Header(None), device: str = Header(None), timestamp: str = Header(None),
                  token: str = Header(None), sign: str = Header(None)):
    # if len(token) == 0 or time.time() - int(timestamp) > 30 or sign != get_sign(device, version, token, timestamp, config.SALT):
    #     raise HTTPException(status_code=401, detail="无访问权限")
    # else:
    #     userId = Redis.read(token)
    #     if userId:
    #         return userId
    #     else:
    #         raise HTTPException(status_code=401, detail="无访问权限")
    return 3


# 生成签名字符串
def get_sign(device: str, version: str, token: str, timestamp: str, salt: str) -> str:
    a = [device, version, token, timestamp, salt]
    join_str = "".join(a)
    # 创建md5对象
    hl = hashlib.md5()
    hl.update(join_str.encode(encoding='utf-8'))
    return hl.hexdigest()


def getCurrentUserByToken(token: str):
    userId = Redis.read(token)
    if userId:
        return crud.getUserByUserId(get_db(), userId)
    else:
        raise HTTPException(status_code=401, detail="无访问权限")


def getCurrentUserId(token: str):
    userId = Redis.read(token)
    if userId:
        return userId
    else:
        raise HTTPException(status_code=401, detail="无访问权限")


# 更新用户会员信息
def updateVipStatus(userId: int, vip_level: int, vip_expire_time: datetime, db: Session = Depends(get_db)):
    db_user = crud.getUserByUserId(db, userId)
    if db_user:
        db_user.vip_level = vip_level
        db_user.vip_expire_time = vip_expire_time
        db.commit()
        db.refresh(db_user)
        print("更新用户会员状态成功")
    else:
        print("找不到该用户，无法更新用户会员状态")


# override default exception handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(content=BaseErrResponse(code=exc.status_code, message=str(exc.detail)),
                        status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(content=BaseErrResponse(code=400, message=str(exc)), status_code=400)


# --- 用户模块 ---

# 短信验证码校验
@app.get("/smscode/verify")
async def verify_sms_code(zone: str = "86", phone: str = Query(None, min_length=11, max_length=11),
                          code: str = Query(None, min_length=6, max_length=6)):
    verify_url = "https://webapi.sms.mob.com/sms/verify"
    data = {"appkey": config.MOB_APP_KEY,
            "phone": phone, "zone": zone, "code": code}
    req = requests.post(verify_url, data=data, verify=False)
    if req.status_code == 200:
        req_json = req.json()
        status = req_json.get("status", 500)
        msg = req_json.get("error", config.SERVER_ERROR_MESSAGE)
        if status == 200:
            return SucResponse()
        else:
            return BaseErrResponse(code=status, message=msg)

    return ServerErrorResponse()


# 获取用户详情
@app.get("/user/{userId}", response_model=schemas.UserResponse, response_model_exclude_none=True,
         response_model_exclude_unset=True)
async def getUser(userId: int, db: Session = Depends(get_db)):
    user = crud.getUserByUserId(db, userId=userId)
    if user:
        return SucResponse(data=user)
    else:
        raise HTTPException(status_code=404, detail="用户不存在")


# 用户注册
@app.post("/user")
async def register(user: schemas.CreateUser, db: Session = Depends(get_db)):
    if len(user.phone) == 0:
        return BaseErrResponse(code=400, message="手机号不能为空")
    else:
        if (crud.getUserByPhone(db, user.phone)):
            return BaseErrResponse(code=403, message="该手机号已注册！")
        else:
            constellation = get_constellation(
                user.birthday.month, user.birthday.day)
            db_user = models.User(phone=user.phone, nickname=user.nickname, birthday=user.birthday, gender=user.gender,
                                  avatar=user.avatar, provice=user.provice, city=user.city, area=user.area,
                                  address=user.address, latitude=user.latitude, longitude=user.longitude,
                                  whats_up=user.whats_up, constellation=constellation, tag=user.tag,
                                  profile_photo_urls=user.avatar)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return SucResponse()


# 登录
@app.post("/user/login", response_model=schemas.LoginResponse)
async def login(user: schemas.LoginRequest, db: Session = Depends(get_db)):
    db_user = crud.getUserByPhone(db, user.phone)
    if db_user:
        token = str(uuid.uuid1()).upper().replace('-', '')
        Redis.write(token, db_user.id)
        result = schemas.LoginResult(id=db_user.id, token=token)
        # 更新上次登录时间
        db_user.last_login_time = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        db.commit()
        db.refresh(db_user)
        return SucResponse(data=result)
    else:
        raise HTTPException(status_code=404, detail="该用户不存在")


# 修改用户资料
@app.put("/user/{userId}")
async def update_user_info(userId: int, user: schemas.UpdateUserInfo, db: Session = Depends(get_db)):
    db_user = crud.getUserByUserId(db, userId)
    if db_user:
        db_user.birthday = user.birthday
        db_user.constellation = get_constellation(
            user.birthday.month, user.birthday.day)
        db_user.avatar = user.avatar
        db_user.tag = user.tag
        db_user.whats_up = user.whats_up
        db_user.profile_photo_urls = user.profile_photo_urls

        db.commit()
        db.refresh(db_user)
        return SucResponse()
    else:
        raise HTTPException(status_code=404, detail="该用户不存在")


# 修改定位信息和在线状态
@app.put("/user/{userId}/location")
async def update_user_location(userId: int, user: schemas.UpdateUserLocation, db: Session = Depends(get_db)):
    db_user = crud.getUserByUserId(db, userId)
    if db_user:
        db_user.longitude = user.longitude
        db_user.latitude = user.latitude
        db_user.provice = user.provice
        db_user.city = user.city
        db_user.area = user.area
        db_user.last_login_time = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        db_user.address = user.address
        db.commit()
        db.refresh(db_user)
        return SucResponse()
    else:
        return BaseErrResponse(code=404, message="该用户不存在")


# 喜欢用户
@app.post("/user/{desUserId}/like")
async def likeUser(desUserId: int, db: Session = Depends(get_db), sourceUserId: int = Depends(token_is_true)):
    like_record = crud.getUserLikeRecord(db, sourceUserId, desUserId)
    # 存在喜欢或者不喜欢记录的话
    if like_record:
        # 不是喜欢状态的话变成喜欢状态
        if like_record.type != 0:
            like_record.type = 0
            db.commit()
            db.refresh(like_record)
            return SucResponse()
        else:
            return BaseErrResponse(code=403, message="已喜欢该用户")
    else:
        like_record = models.UserLike(
            source_user_id=sourceUserId, destination_user_id=desUserId, type=0)
        db.add(like_record)
        db.commit()
        db.refresh(like_record)
        return SucResponse()


# 不喜欢用户
@app.delete("/user/{desUserId}/like")
async def dislikeUser(desUserId: int, db: Session = Depends(get_db), sourceUserId: int = Depends(token_is_true)):
    like_record = crud.getUserLikeRecord(db, sourceUserId, desUserId)
    # 存在喜欢或者不喜欢记录的话
    if like_record:
        # 不是不喜欢状态的话变成不喜欢状态
        if like_record.type != 1:
            like_record.type = 1
            db.commit()
            db.refresh(like_record)
            return SucResponse()
        else:
            return BaseErrResponse(code=403, message="未喜欢该用户")
    else:
        # 数据库不存在记录的话 也不会新增type=1的记录 不存在即不喜欢
        return BaseErrResponse(code=403, message="未喜欢该用户")


# 谁喜欢了我列表
@app.get("/userList/likeme", response_model=schemas.UserLikeResponse, response_model_exclude_none=True,
         response_model_exclude_unset=True)
async def getLikeMeUserList(page: int = 0, size: int = 20, db: Session = Depends(get_db),
                            sourceUserId: int = Depends(token_is_true)):
    likeUserList = crud.getUserLikeList(db, sourceUserId, page, size)
    return SucResponse(data=likeUserList)


# 获取会员用户列表
@app.get("/userList/vip", response_model=schemas.UserLikeResponse, response_model_exclude_none=True,
         response_model_exclude_unset=True)
async def getVipUserList(page: int = 0, size: int = 20, db: Session = Depends(get_db)):
    vipUserList = crud.getVipUserList(db, page, size)
    random.shuffle(vipUserList)
    # 随机排序
    return SucResponse(data=vipUserList)


# 获取最新用户列表
@app.get("/userList/new", response_model=schemas.UserLikeResponse, response_model_exclude_none=True,
         response_model_exclude_unset=True)
async def getNewUserList(page: int = 0, size: int = 20, db: Session = Depends(get_db)):
    newUserList = crud.getNewUserList(db, page, size)
    random.shuffle(newUserList)
    # 随机排序
    return SucResponse(data=newUserList)


# 获取附近用户列表
@app.get("/userList/nearby", response_model=schemas.UserLikeResponse, response_model_exclude_none=True,
         response_model_exclude_unset=True)
async def getNearbyUserList(page: int = 0, size: int = 20, db: Session = Depends(get_db),
                            userId: int = Depends(token_is_true)):
    currentUser = crud.getUserByUserId(db, userId)
    if currentUser == None:
        raise HTTPException(status_code=404, detail="该用户不存在")
    else:
        if currentUser.latitude == None or currentUser.longitude == None:
            raise HTTPException(status_code=403, detail="无法获取您的位置，请先打开定位")
        else:
            nearbyUserList = crud.getNearbyUserList(db, currentUser, page, size)
            random.shuffle(nearbyUserList)
            # 随机排序
            return SucResponse(data=nearbyUserList)


# --- 访客模块 ---

# 提交访问记录
@app.post("/user/{userId}/visit")
async def submitVisitRecord(userId: int, db: Session = Depends(get_db), sourceUserId: int = Depends(token_is_true)):
    visit_record = crud.getVisitRecordByBothUserId(db, sourceUserId, userId)
    # 存在访问记录
    if visit_record:
        visit_record.visit_times = visit_record.visit_times + 1
        db.commit()
        db.refresh(visit_record)
        return SucResponse()
    else:
        visit_record = models.VisitRecord(
            source_user_id=sourceUserId, destination_user_id=userId)
        db.add(visit_record)
        db.commit()
        db.refresh(visit_record)
        return SucResponse()


# 谁访问了我列表
@app.get("/userList/visitor", response_model=schemas.UserVistorResponse, response_model_exclude_none=True,
         response_model_exclude_unset=True)
async def getVisitMeUserList(page: int = 0, size: int = 20, db: Session = Depends(get_db),
                             sourceUserId: int = Depends(token_is_true)):
    visitorList = crud.getVistorList(db, sourceUserId, page, size)
    return SucResponse(data=visitorList)


# --- 动态模块 ---

# 获取用户动态列表
@app.get("/user/{userId}/post", response_model=schemas.PostListResponse, response_model_exclude_none=True,
         response_model_exclude_unset=True)
async def getUserPostList(userId: int, page: int = 0, size: int = 20, db: Session = Depends(get_db),
                          sourceUserId: int = Depends(token_is_true)):
    postList = crud.getUserPostList(db, userId, page, size, sourceUserId)
    return SucResponse(data=postList)


# 获取最新动态列表
@app.get("/post/new", response_model=schemas.PostListResponse, response_model_exclude_none=True,
         response_model_exclude_unset=True)
async def getNewPostList(page: int = 0, size: int = 20, db: Session = Depends(get_db)):
    newPostList = crud.getNewPostList(db, page, size)
    random.shuffle(newPostList)
    # 随机排序
    return SucResponse(data=newPostList)


# 获取推荐动态列表  todo
@app.get("/post/recommend", response_model=schemas.PostListResponse, response_model_exclude_none=True,
         response_model_exclude_unset=True)
async def getRecommendPostList(page: int = 0, size: int = 20, db: Session = Depends(get_db)):
    recommendPostList = crud.getNewPostList(db, page, size)
    random.shuffle(recommendPostList)
    # 随机排序
    return SucResponse(data=recommendPostList)


# 获取附近动态列表
@app.get("/post/nearby", response_model=schemas.PostListResponse, response_model_exclude_none=True,
         response_model_exclude_unset=True)
async def getNearbyPostList(page: int = 0, size: int = 20, db: Session = Depends(get_db),
                            userId: int = Depends(token_is_true)):
    currentUser = crud.getUserByUserId(db, userId)
    if currentUser.latitude == None or currentUser.longitude == None:
        raise HTTPException(status_code=403, detail="无法获取您的位置，请先打开定位")
    else:
        nearbyPostList = crud.getNearbyPostList(db, currentUser, page, size)
        random.shuffle(nearbyPostList)
        # 随机排序
        return SucResponse(data=nearbyPostList)


# 获取动态详情
@app.get("/post/{postId}", response_model=schemas.PostDetailResponse, response_model_exclude_none=True,
         response_model_exclude_unset=True)
async def getPostDetail(postId: int, db: Session = Depends(get_db)):
    db_post = crud.getPostDetailById(db, postId)
    if db_post is None or db_post.status == 2:
        raise HTTPException(status_code=403, detail="动态不存在")
    else:
        return SucResponse(data=db_post)


# 发布动态
@app.post("/post")
async def postDynamic(post: schemas.CreatePost, db: Session = Depends(get_db), userId: int = Depends(token_is_true)):
    db_post = models.Post(user_id=userId, content=post.content, cover_url=post.cover_url, type=post.type,
                          title=post.title, media_urls=post.media_urls,
                          provice=post.provice, city=post.city, area=post.area, address=post.address,
                          latitude=post.latitude, longitude=post.longitude)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return SucResponse()


# 删除动态
@app.delete("/post/{postId}")
async def deletePost(postId: int, db: Session = Depends(get_db), userId: int = Depends(token_is_true)):
    db_post = crud.getPostDetailById(db, postId)
    if db_post:
        if db_post.user_id == userId:
            db_post.status = 3
            db.commit()
            db.refresh(db_post)
            return SucResponse()
        else:
            return BaseErrResponse(code=403, message="没有权限删除该动态")
    else:
        return BaseErrResponse(code=404, message="该动态不存在")


# 点赞动态
@app.post("/post/{postId}/like")
async def likePost(postId: int, postUserId: int, db: Session = Depends(get_db),
                   sourceUserId: int = Depends(token_is_true)):
    like_record = crud.getPostLikeRecord(db, sourceUserId, postId)
    # 存在记录
    if like_record:
        # 不是点赞的改为点赞状态
        if like_record.status != 1:
            like_record.status = 1
            db.commit()
            db.refresh(like_record)
            return SucResponse()
        else:
            return BaseErrResponse(code=403, message="已点赞该动态")
    else:
        like_record = models.PostLike(
            user_id=sourceUserId, post_user_id=postUserId, post_id=postId, status=1)
        db.add(like_record)
        db.commit()
        db.refresh(like_record)
        return SucResponse()


# 取消点赞动态
@app.delete("/post/{postId}/like")
async def dislikePost(postId: int, db: Session = Depends(get_db), sourceUserId: int = Depends(token_is_true)):
    like_record = crud.getPostLikeRecord(db, sourceUserId, postId)
    # 存在点赞记录
    if like_record:
        # 不是取消点赞状态的改为取消点赞
        if like_record.status != 0:
            like_record.status = 0
            db.commit()
            db.refresh(like_record)
            return SucResponse()
        else:
            return BaseErrResponse(code=403, message="未点赞该动态")
    else:
        # 数据库不存在记录的话 也不会新增type=1的记录 不存在即不喜欢
        return SucResponse()


# --- 评论模块 ---

# 添加评论，回复评论
@app.post("/post/{postId}/comment")
async def addComment(postId: int, comment: schemas.CreateComment, db: Session = Depends(get_db),
                     userId: int = Depends(token_is_true)):
    db_comment = models.Comment(post_id=postId, user_id=userId,
                                content=comment.content, type=comment.type, to_user_id=comment.to_user_id)
    if comment.source_comment_id:
        db_comment.source_comment_id = comment.source_comment_id
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return SucResponse()


# 删除评论
@app.delete("/comment/{commentId}")
async def deleteComment(commentId: int, db: Session = Depends(get_db), userId: int = Depends(token_is_true)):
    db_comment = crud.getCommentDetail(db, commentId)
    if db_comment:
        if db_comment.user_id == userId:
            db.delete(db_comment)
            db.commit()
            return SucResponse()
        else:
            return BaseErrResponse(code=403, message="无权限删除该评论")
    else:
        return BaseErrResponse(code=404, message="该评论不存在")


# 获取动态的评论列表
@app.get("/post/{postId}/comment", response_model=schemas.PostCommentListResponse, response_model_exclude_none=True,
         response_model_exclude_unset=True)
async def getPostCommentList(postId: int, page: int = 0, size: int = 20, db: Session = Depends(get_db)):
    comment_list = crud.getPostCommentList(db, postId, page, size)
    return SucResponse(data=comment_list)


# --- 举报模块 ---

# 举报用户
@app.post("/report/user/{userId}")
async def reportUser(userId: int, report: schemas.ReportUser, db: Session = Depends(get_db),
                     sourceUserId: int = Depends(token_is_true)):
    db_report_user = models.ReportUser(
        source_user_id=sourceUserId, destination_user_id=userId, type=report.type)
    if report.content:
        db_report_user.content = report.content
    if report.evidence_photo_url:
        db_report_user.evidence_photo_url = report.evidence_photo_url
    db.add(db_report_user)
    db.commit()
    db.refresh(db_report_user)
    return SucResponse()


# 举报动态
@app.post("/report/post/{postId}")
async def reportPost(postId: int, report: schemas.ReportPost, db: Session = Depends(get_db),
                     sourceUserId: int = Depends(token_is_true)):
    db_report_post = models.ReportPost(
        source_user_id=sourceUserId, post_id=postId, type=report.type)
    db.add(db_report_post)
    db.commit()
    db.refresh(db_report_post)
    return SucResponse()


# 举报评论
@app.post("/report/comment/{commentId}")
async def reportComment(commentId: int, report: schemas.ReportComment, db: Session = Depends(get_db),
                        sourceUserId: int = Depends(token_is_true)):
    db_report_comment = models.ReportComment(
        source_user_id=sourceUserId, comment_id=commentId, type=report.type)
    db.add(db_report_comment)
    db.commit()
    db.refresh(db_report_comment)
    return SucResponse()


# --- 其它模块 ---

# 版本检测
@app.get("/version/check", response_model=schemas.AppVersionResponse)
async def getNewestAppVersion(db: Session = Depends(get_db), device: int = Header(None)):
    if device != None:
        return SucResponse(data=crud.getAppVersion(db, device))
    else:
        raise HTTPException(
            status_code=400, detail="missing header params 'device'")


# 获取内购价格
@app.get("/product", response_model=schemas.ProductResponse)
async def getProductList(db: Session = Depends(get_db), device: int = Header(None)):
    if device != None:
        return SucResponse(data=crud.getProductList(db, device))
    else:
        raise HTTPException(
            status_code=400, detail="missing header params 'device'")


# 订单模块
# 创建订单
@app.post("/order")
async def createOrder(order: schemas.CreateOrder, db: Session = Depends(get_db), device: int = Header(None),
                      userId: int = Depends(token_is_true)):
    order_no = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))) \
               + str(time.time()).replace('.', '')[-7:]

    db_order = models.Order(order_id=order_no, product_id=order.product_id, pay_method=order.pay_method, source=device,
                            user_id=userId)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return SucResponse()


# 校验订单
@app.post("/order/verify")
async def verifyOrder(receipt: str, orderId: str, db: Session = Depends(get_db), device: int = Header(None),
                      userId: int = Depends(token_is_true)):
    try:
        response = itunesiap.verify(str)
        db_order = crud.getOrderByOrderId(orderId=orderId)
        if db_order:
            # response.receipt.last_login_time
            pass
        else:
            return BaseErrResponse(code=403, message="订单不存在")
    except itunesiap.exc.InvalidReceipt as e:
        return BaseErrResponse(code=403, message="订单校验失败")


# --- 消息模块 ---
# 获取我的评论消息
@app.get("/user/message/comment", response_model=schemas.PostCommentListResponse, response_model_exclude_none=True,
         response_model_exclude_unset=True)
async def getCommentMessageList(db: Session = Depends(get_db), userId: int = Depends(token_is_true), page: int = 0,
                                size: int = 20):
    commentMessageList = crud.getCommentMessageList(db, userId, page, size)
    return SucResponse(data=commentMessageList)


# 获取我的点赞消息
@app.get("/user/message/praise", response_model=schemas.PostLikeListResponse, response_model_exclude_none=True,
         response_model_exclude_unset=True)
async def getLikeMessageList(db: Session = Depends(get_db), userId: int = Depends(token_is_true), page: int = 0,
                             size: int = 20):
    likeMessageList = crud.getLikeMessageList(db, userId, page, size)
    return SucResponse(data=likeMessageList)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
