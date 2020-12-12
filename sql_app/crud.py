from sqlalchemy.orm import Session
import math
from math import cos, sin, pi
from . import models, schemas

EARTH_REDIUS = 6378.137

def rad(d):
    return float (d) * pi / 180.0

def getDistance(lat1, lng1, lat2, lng2):
    radLat1 = rad(lat1)
    radLat2 = rad(lat2)
    a = radLat1 - radLat2
    b = rad(lng1) - rad(lng2)
    s = 2 * math.asin(math.sqrt(math.pow(sin(a/2), 2) + cos(radLat1) * cos(radLat2) * math.pow(sin(b/2), 2)))
    s = s * EARTH_REDIUS
    return s


def getAppVersion(db: Session, type: int):
    return db.query(models.AppVersion).filter(models.AppVersion.platform == type).order_by(models.AppVersion.create_time.desc()).first()


def getUserByUserId(db: Session, userId: int):
    return db.query(models.User).filter(models.User.id == userId).first()


def getUserListByUserIds(db: Session, userIds: list):
    return db.query(models.User).filter(models.User.id.in_(list)).first()


def getUserByPhone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()


def getUserLikeRecord(db: Session, sourceUserId: int, desUserId: int):
    return db.query(models.UserLike).filter(models.UserLike.source_user_id == sourceUserId , models.UserLike.destination_user_id == desUserId).first()


def getUserLikeList(db: Session, sourceUserId: int, page: int, size: int):
    return db.query(models.User).join(models.UserLike,models.User.id == models.UserLike.source_user_id).filter(models.UserLike.destination_user_id == sourceUserId , models.UserLike.type == 0).order_by(models.User.update_time.desc()).offset(page * size).limit(size).all()


def getVisitRecordByBothUserId(db: Session, sourceUserId: int, desUserId: int):
    return db.query(models.VisitRecord).filter(models.VisitRecord.source_user_id == sourceUserId , models.VisitRecord.destination_user_id == desUserId).first()


def getVistorList(db: Session, sourceUserId: int, page: int, size: int):
    return db.query(models.User, models.VisitRecord.visit_times, models.VisitRecord.update_time).join(models.VisitRecord,models.User.id == models.VisitRecord.source_user_id).filter(models.VisitRecord.destination_user_id == sourceUserId).order_by(models.VisitRecord.update_time.desc()).offset(page * size).limit(size).all()


def getProductList(db: Session, device: int):
    return db.query(models.Product).filter(models.Product.device == device).order_by(models.Product.price.asc()).all()


def getUserPostList(db: Session, userId: int, page: int, size: int, currentUserId: int):
    query = db.query(models.Post).filter(models.Post.user_id == userId)
    if (currentUserId != userId):
        query = query.filter(models.Post.status == 0)
    else:
        query = query.filter((models.Post.status == 0) | (models.Post.status == 1))

    return query.order_by(models.Post.create_time.desc()).offset(page * size).limit(size).all()


def getPostDetailById(db: Session, postId: int):
    return db.query(models.Post).filter(models.Post.id == postId).first()


def getPostLikeRecord(db: Session, sourceUserId: int, postId: int):
    return db.query(models.PostLike).filter(models.PostLike.user_id == sourceUserId, models.PostLike.post_id == postId).first()


def getCommentDetail(db: Session, commentId: int):
    return db.query(models.Comment).filter(models.Comment.id == commentId).first()


def getPostCommentList(db: Session, postId: int, page: int, size: int):
    return db.query(models.Comment).filter(models.Comment.post_id == postId , models.Comment.status != 2).order_by(models.Comment.create_time.desc()).all()


def getCommentMessageList(db: Session, userId: int, page: int, size: int):
    return db.query(models.Comment).filter(models.Comment.status == 0 , models.Comment.to_user_id == userId).order_by(models.Comment.create_time.desc()).offset(page * size).limit(size).all()


def getLikeMessageList(db: Session, userId: int, page: int, size: int):
    return db.query(models.PostLike).filter(models.PostLike.post_user_id == userId , models.PostLike.status == 1).order_by(models.PostLike.create_time.desc()).offset(page * size).limit(size).all()

def getVipUserList(db: Session, page: int, size: int):
    return db.query(models.User).filter(models.User.vip_level != 1, models.User.gender == 1, models.User.status == 2).order_by(models.User.last_login_time.desc()).offset(page * size).limit(size).all()

def getNewUserList(db: Session, page: int, size: int, gender: int = None):
    return db.query(models.User).filter((models.User.gender == gender , models.User.status == 2) if gender else models.User.status == 2).order_by(models.User.create_time.desc()).offset(page * size).limit(size).all()

def getNearbyUserList(db: Session, user: models.User, page: int, size: int, gender: int = None):
    query =  db.query(models.User).filter(models.User.status == 2,models.User.id != user.id).filter(models.User.city == user.city,models.User.provice == user.provice)
    if gender:
       query = query.filter(models.User.gender == gender)
    return query.order_by(models.User.last_login_time.desc()).offset(page * size).limit(size).all()

def getNewPostList(db: Session, page: int, size: int, gender: int = None):
    query = db.query(models.Post).filter(models.Post.status == 0 | models.Post.status == 1)
    if gender:
        query = query.filter(models.Post.user.gender == gender)
    return query.order_by(models.Post.create_time.desc()).offset(page * size).limit(size).all()

def getNearbyPostList(db: Session, user: models.User, page: int, size: int, gender: int = None):
    query = db.query(models.Post).filter(models.Post.status == 0 | models.Post.status == 1).filter(models.Post.city == user.city,models.Post.provice == user.provice,models.Post.user_id != user.id)
    if gender:
       query = query.filter(models.Post.user.gender == gender)
    return query.order_by(models.Post.create_time.desc()).offset(page * size).limit(size).all()

def getRecommendPostList(db: Session, page: int, size: int, gender: int = None):
    query = db.query(models.Post).join(models.PostLike,models.PostLike.post_id == models.Post.id).filter(models.Post.status == 0 | models.Post.status == 1)
    if gender:
       query = query.filter(models.Post.user.gender == gender)
    return query.order_by(models.Post.create_time.desc()).offset(page * size).limit(size).all()

def getOrderByOrderId(db: Session,orderId:str):
    return db.query(models.Order).filter(models.Order.order_id == orderId).first()
