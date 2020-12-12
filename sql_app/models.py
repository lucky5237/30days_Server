# coding: utf-8
from sqlalchemy import Column, DECIMAL, Date, DateTime, Float, ForeignKey, Integer, String, TIMESTAMP, text
from sqlalchemy.dialects.mysql import TINYINT, VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class AppVersion(Base):
    __tablename__ = 'app_version'

    id = Column(Integer, primary_key=True)
    version = Column(String(20), nullable=False)
    platform = Column(TINYINT(1), nullable=False, comment='1-ios2-安卓3-其他')
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
    update_content = Column(String(255), nullable=False, comment='更新说明')
    update_type = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='1-不强制更新2-强制更新')


class CommentLike(Base):
    __tablename__ = 'comment_like'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, nullable=False, comment='动态id')
    user_id = Column(Integer, nullable=False, comment='发起点赞/取消点赞的用户的id')
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
    status = Column(TINYINT(1), nullable=False, comment='0-取消点赞，1-点赞')
    comment_id = Column(Integer, nullable=False, comment='点赞的评论id')
    comment_user_id = Column(Integer, nullable=False, comment='点赞的评论所属的userid')


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)


class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True)
    order_id = Column(String(24), nullable=False, comment='订单id')
    product_id = Column(Integer, nullable=False, comment='关联内购商品表id')
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
    pay_method = Column(TINYINT(1), nullable=False, comment='0-iap 1-wechat 2-alipay')
    user_id = Column(Integer, nullable=False, comment='购买的用户id')
    status = Column(TINYINT(1),server_default=text("'0'"), nullable=False, comment='0-未支付 1-支付成功')
    pay_time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), comment='支付时间')
    pay_price = Column(DECIMAL(10, 2), comment='实际支付金额')
    source = Column(TINYINT(1), comment='0-ios 1-安卓 2-其他')


class PostLike(Base):
    __tablename__ = 'post_like'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, nullable=False, comment='动态id')
    post_user_id = Column(Integer, nullable=False, comment='动态所属的userid')
    user_id = Column(Integer, nullable=False, comment='点赞/取消点赞的用户id')
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
    status = Column(TINYINT(1), nullable=False, comment='0-取消点赞，1-点赞')

class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, comment='商品名称')
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
    price = Column(DECIMAL(10, 2), nullable=False, comment='现价')
    original_price = Column(DECIMAL(10, 2), comment='原价')
    description = Column(String(255), comment='商品描述')
    iap_identifier = Column(VARCHAR(20), comment='ios 内购id')
    device = Column(TINYINT(1),comment='1-ios,2-安卓，3-其它', nullable=False, server_default=text("1"))


class ReportComment(Base):
    __tablename__ = 'report_comment'

    id = Column(Integer, primary_key=True)
    source_user_id = Column(Integer, nullable=False, comment='主动发起的userid')
    comment_id = Column(Integer, nullable=False, comment='举报的评论id')
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='举报时间')
    type = Column(TINYINT(1),nullable=False, comment='举报类型0-涉及不健康词汇1-涉及侮辱词汇2-涉及政治敏感词汇3-其他')
    status = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='0-未处理 1-已处理，无法核实举报 2-已处理，已核实')
    deal_time = Column(TIMESTAMP, comment='处理时间')


class ReportPost(Base):
    __tablename__ = 'report_post'

    id = Column(Integer, primary_key=True)
    source_user_id = Column(Integer, nullable=False, comment='主动发起的userid')
    post_id = Column(Integer, nullable=False, comment='对方userid')
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='举报时间')
    type = Column(TINYINT(1),nullable=False, comment='举报类型0-涉及不健康词汇1-涉及侮辱词汇2-涉及政治敏感词汇3-其他')
    status = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='0-未处理 1-已处理，无法核实举报 2-已处理，已核实')
    deal_time = Column(TIMESTAMP, comment='处理时间')


class ReportUser(Base):
    __tablename__ = 'report_user'

    id = Column(Integer, primary_key=True)
    source_user_id = Column(Integer, nullable=False, comment='主动发起的userid')
    destination_user_id = Column(Integer, nullable=False, comment='对方userid')
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='举报时间')
    type = Column(TINYINT(1), nullable=False,comment='举报类型0-举报头像1-举报昵称2-举报言论3-其他')
    status = Column(TINYINT(1), server_default=text("'0'"),nullable=False, comment='0-未处理 1-已处理，无法核实举报 2-已处理，已核实')
    content = Column(String(255), comment='举报额外描述')
    evidence_photo_url = Column(String(255), comment='图片证据url')
    deal_time = Column(TIMESTAMP, comment='处理时间')


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, comment='标签名字')
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='注册时间')
    update_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, comment='id')
    phone = Column(VARCHAR(30), nullable=False, comment='手机号')
    region_code = Column(VARCHAR(15), nullable=False, server_default=text("'86'"), comment='区号')
    status = Column(TINYINT(1), nullable=False, server_default=text("'1'"), comment='1-注册未填写资料2-正常3-禁言4-封号5-注销')
    ip = Column(String(20), comment='ip')
    device = Column(TINYINT(1), nullable=False, server_default=text("'1'"), comment='1-ios 2-android 3-其它')
    is_real = Column(TINYINT(1), nullable=False, server_default=text("'2'"), comment='1-机器人 2-真实用户')
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='注册时间')
    last_login_time = Column(TIMESTAMP, comment='注册时间')
    update_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
    nickname = Column(VARCHAR(20), nullable=False, comment='昵称')
    birthday = Column(Date, nullable=False, comment='生日')
    gender = Column(TINYINT(1), nullable=False, comment='性别 1-男 2-女')
    avatar = Column(VARCHAR(50), nullable=False, comment='头像')
    provice = Column(String(50), comment='省份')
    city = Column(String(50), comment='城市')
    latitude = Column(Float(10,6), comment='定位精度')
    longitude = Column(Float(10,6), comment='定位维度')
    area = Column(String(50), comment='区')
    address = Column(String(255), comment='详细定位地址')
    vip_level = Column(TINYINT(1), nullable=False, server_default=text("'1'"), comment='1-普通用户2-vip 3-svip')
    vip_expire_time = Column(DateTime, comment='会员过期时间')
    whats_up = Column(VARCHAR(25), comment='个性签名')
    constellation = Column(VARCHAR(3), nullable=False, comment='星座')
    tag = Column(VARCHAR(100), comment='标签 a|b|c')
    vertifiation_status = Column(TINYINT(1), nullable=False, server_default=text("'1'"), comment='1-未认证2-认证中3-认证失败4-认证成功')
    profile_photo_urls = Column(String(255), comment='个人照片所有url  a,b,c,d,...')


class UserFollow(Base):
    __tablename__ = 'user_follow'

    id = Column(Integer, primary_key=True)
    source_user_id = Column(Integer, nullable=False, comment='主动发起的userid')
    destination_user_id = Column(Integer, nullable=False, comment='对方userid')
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='操作时间')


class UserFriend(Base):
    __tablename__ = 'user_friend'

    id = Column(Integer, primary_key=True)
    user_a_id = Column(Integer, nullable=False)
    user_b_id = Column(Integer, nullable=False)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='匹配时间')


class UserLike(Base):
    __tablename__ = 'user_like'

    id = Column(Integer, primary_key=True)
    source_user_id = Column(Integer, nullable=False, comment='主动发起的userid')
    destination_user_id = Column(Integer, nullable=False, comment='对方userid')
    update_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='操作时间')
    type = Column(TINYINT(1), comment='0-喜欢 1-不喜欢 2-超级喜欢')


class UserProfilePhoto(Base):
    __tablename__ = 'user_profile_photo'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, comment='fk->user')
    url = Column(String(50), nullable=False, comment='图片地址')
    status = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='0-正常 1-审核中 2-审核不通过')
    order = Column(TINYINT(1), nullable=False, comment='照片顺序')
    create_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
    type = Column(TINYINT(1), nullable=False, server_default=text("'0'"), comment='0-图片1-视频')


class VisitRecord(Base):
    __tablename__ = 'visit_record'

    id = Column(Integer, primary_key=True)
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
    source_user_id = Column(Integer, nullable=False, comment='主动发起的userid')
    destination_user_id = Column(Integer, nullable=False, comment='对方userid')
    visit_times = Column(Integer, nullable=False, server_default=text("'1'"), comment='访问次数')


class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.id'), nullable=False, index=True, comment='发动态的用户id')
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
    content = Column(String(255), comment='内容')
    cover_url = Column(String(50), nullable=False, comment='封面url')
    type = Column(TINYINT(1), nullable=False, comment='0-图片，1-视频')
    title = Column(String(20), comment='标题')
    status = Column(TINYINT(1), server_default=text("'1'"), nullable=False, comment='0-正常 1-审核中 2-审核不通过 3-已删除')
    media_urls = Column(VARCHAR(255), nullable=False, comment='包含的所有图片或者视频url地址，url1,urls2,...')
    provice = Column(VARCHAR(50), comment='省份')
    city = Column(VARCHAR(50), comment='城市')
    area = Column(VARCHAR(50), nullable=False, comment='区')
    latitude = Column(Float(asdecimal=True), comment='定位维度')
    longitude = Column(Float(asdecimal=True), comment='定位经度')
    address = Column(VARCHAR(255), comment='详细定位地址')
    topic_ids = Column(String(100), comment='参与的话题id 1,2,3,...')

    user = relationship('User')


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    post_id = Column(ForeignKey('post.id'), nullable=False, index=True, comment='动态id')
    user_id = Column(ForeignKey('user.id'), nullable=False, index=True, comment='评论的用户id')
    create_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment='创建时间')
    update_time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment='更新时间')
    status = Column(TINYINT(1),server_default=text("'0'"), nullable=False, comment='0-正常 1-审核中 2-审核不通过')
    content = Column(String(255), nullable=False, comment='评论的内容')
    type = Column(TINYINT(1), nullable=False, comment='0-评论动态 (一级评论)1-回复一级评论（二级评论） 2-回复二级评论')
    source_comment_id = Column(ForeignKey('comment.id'), index=True, comment='如果type= 1 || type == 2 表示原来评论id如果type = 0 为空')
    to_user_id = Column(ForeignKey('user.id'), index=True, comment='如果type= 1 || type == 2 表示原评论所属的userid如果type = 0 表示动态所属的userid')

    # post = relationship('Post')
    # source_comment = relationship('Comment', remote_side=[id])
    # to_user = relationship('User', primaryjoin='Comment.to_user_id == User.id')
    # user = relationship('User', primaryjoin='Comment.user_id == User.id')
