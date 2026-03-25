"""
数据库模型层 - SQLAlchemy ORM
Go In App 数据持久化系统
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

# ========== 数据库模型 ==========

class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    gender = db.Column(db.String(20), default='other')
    face_photo_url = db.Column(db.Text)  # 人脸照片
    face_avatar_url = db.Column(db.Text)  # AI 头像
    avatar_trait = db.Column(db.String(200))  # 头像特征
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    posts = db.relationship('Post', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    co_create_records = db.relationship('CoCreateRecord', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'gender': self.gender,
            'face_photo_url': self.face_photo_url,
            'face_avatar_url': self.face_avatar_url,
            'avatar_trait': self.avatar_trait,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Post(db.Model):
    """内容帖子表（看看、逛逛）"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.user_id'), nullable=False, index=True)
    content_type = db.Column(db.String(50), nullable=False, index=True)  # novel, comic, moments
    content_data = db.Column(db.Text)  # JSON 字符串，存储具体内容
    location_name = db.Column(db.String(200))  # 地点名称（逛逛用）
    location_data = db.Column(db.Text)  # JSON 字符串，位置信息
    pose_emoji = db.Column(db.String(10))  # 姿势 emoji（逛逛用）
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    is_auto_generated = db.Column(db.Boolean, default=True)  # 是否 AI 自动生成
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 关联关系
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    co_create_records = db.relationship('CoCreateRecord', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content_type': self.content_type,
            'content_data': json.loads(self.content_data) if self.content_data else {},
            'location_name': self.location_name,
            'location_data': json.loads(self.location_data) if self.location_data else {},
            'pose_emoji': self.pose_emoji,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'is_auto_generated': self.is_auto_generated,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Comment(db.Model):
    """评论表"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.user_id'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)  # 回复的评论
    content = db.Column(db.Text, nullable=False)
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 自关联（回复）
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'parent_id': self.parent_id,
            'content': self.content,
            'likes_count': self.likes_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CoCreateRecord(db.Model):
    """共创记录表"""
    __tablename__ = 'co_create_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.user_id'), nullable=False, index=True)
    mode = db.Column(db.String(20), nullable=False)  # relay(接力), challenge(夺擂)
    content_data = db.Column(db.Text)  # JSON 字符串，创作内容
    votes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'mode': self.mode,
            'content_data': json.loads(self.content_data) if self.content_data else {},
            'votes_count': self.votes_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ========== 数据库操作辅助函数 ==========

def init_db(app):
    """初始化数据库（带保护，避免重复初始化）"""
    # 检查是否已经初始化
    if hasattr(app, 'extensions') and 'sqlalchemy' in app.extensions:
        print("⚠️  数据库已初始化，跳过")
        return
    
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("✅ 数据库表创建成功")


def get_or_create_user(user_id, **kwargs):
    """获取或创建用户"""
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        user = User(user_id=user_id, **kwargs)
        db.session.add(user)
        db.session.commit()
    return user


def save_user_data(user_id, data):
    """保存用户数据"""
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        user = User(user_id=user_id)
        db.session.add(user)
    
    # 更新字段
    if 'gender' in data:
        user.gender = data['gender']
    if 'face_photo_url' in data:
        user.face_photo_url = data['face_photo_url']
    if 'face_avatar_url' in data:
        user.face_avatar_url = data['face_avatar_url']
    if 'avatar_trait' in data:
        user.avatar_trait = data['avatar_trait']
    
    db.session.commit()
    return user


def get_user_data(user_id):
    """获取用户数据"""
    user = User.query.filter_by(user_id=user_id).first()
    return user.to_dict() if user else None


def save_post(user_id, post_data):
    """保存帖子"""
    post = Post(
        user_id=user_id,
        content_type=post_data.get('content_type', 'moments'),
        content_data=json.dumps(post_data.get('content_data', {}), ensure_ascii=False),
        location_name=post_data.get('location_name'),
        location_data=json.dumps(post_data.get('location_data', {}), ensure_ascii=False) if post_data.get('location_data') else None,
        pose_emoji=post_data.get('pose_emoji'),
        is_auto_generated=post_data.get('is_auto_generated', True)
    )
    db.session.add(post)
    db.session.commit()
    return post


def get_posts(user_id=None, content_type=None, limit=20, offset=0):
    """获取帖子列表"""
    query = Post.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    if content_type:
        query = query.filter_by(content_type=content_type)
    
    posts = query.order_by(Post.created_at.desc()).offset(offset).limit(limit).all()
    return [post.to_dict() for post in posts]


def increment_like(post_id):
    """增加点赞数"""
    post = Post.query.get(post_id)
    if post:
        post.likes_count += 1
        db.session.commit()
        return post.likes_count
    return 0


def increment_comment(post_id):
    """增加评论数"""
    post = Post.query.get(post_id)
    if post:
        post.comments_count += 1
        db.session.commit()
        return post.comments_count
    return 0


def save_comment(user_id, post_id, content, parent_id=None):
    """保存评论"""
    comment = Comment(
        user_id=user_id,
        post_id=post_id,
        content=content,
        parent_id=parent_id
    )
    db.session.add(comment)
    db.session.commit()
    
    # 更新帖子的评论数
    increment_comment(post_id)
    
    return comment


def get_comments(post_id):
    """获取帖子的评论列表"""
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    return [comment.to_dict() for comment in comments]


def save_co_create_record(post_id, user_id, mode, content_data):
    """保存共创记录"""
    record = CoCreateRecord(
        post_id=post_id,
        user_id=user_id,
        mode=mode,
        content_data=json.dumps(content_data, ensure_ascii=False)
    )
    db.session.add(record)
    db.session.commit()
    return record


def get_co_create_records(post_id):
    """获取帖子的共创记录"""
    records = CoCreateRecord.query.filter_by(post_id=post_id).order_by(CoCreateRecord.created_at.desc()).all()
    return [record.to_dict() for record in records]
