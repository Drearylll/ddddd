"""
Go In 项目数据模型
"""

from services.database import db
from datetime import datetime


# 防止重复定义
try:
    class UserIntent(db.Model):
        """用户意图记录表（用于后续生成打卡照）"""
        
        __tablename__ = 'user_intents'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.String(64), index=True, nullable=False)
        
        # 意图类型
        intent_type = db.Column(db.String(50), nullable=False)  # want_to_visit, want_to_do, mood, other
        
        # 意图内容
        location = db.Column(db.String(200))  # 地点
        activity = db.Column(db.String(200))  # 活动
        mood = db.Column(db.String(100))  # 情绪
        
        # 关键词
        keywords = db.Column(db.Text)  # JSON 数组
        
        # 原始数据
        raw_data = db.Column(db.Text)  # 完整的意图数据 JSON
        
        # 时间戳
        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
        processed = db.Column(db.Boolean, default=False)  # 是否已用于生成打卡照
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'intent_type': self.intent_type,
                'location': self.location,
                'activity': self.activity,
                'mood': self.mood,
                'keywords': self.keywords,
                'created_at': self.created_at.isoformat(),
                'processed': self.processed
            }
except Exception:
    # 如果已经定义过，跳过
    pass


try:
    class Moment(db.Model):
        """打卡记录表"""
        
        __tablename__ = 'moments'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.String(64), index=True, nullable=False)
        
        # 图片信息
        image_url = db.Column(db.Text, nullable=False)
        caption = db.Column(db.Text)  # 文案
        
        # 关联的意图
        intent_id = db.Column(db.Integer, db.ForeignKey('user_intents.id'))
        intent = db.relationship('UserIntent', backref=db.backref('moments', lazy='dynamic'))
        
        # 元数据
        prompt = db.Column(db.Text)  # 生成用的 Prompt
        metadata_json = db.Column(db.Text)  # 其他元数据 JSON
        
        # 社交互动
        like_count = db.Column(db.Integer, default=0)
        comment_count = db.Column(db.Integer, default=0)
        
        # 时间戳
        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'image_url': self.image_url,
                'caption': self.caption,
                'intent_id': self.intent_id,
                'like_count': self.like_count,
                'comment_count': self.comment_count,
                'created_at': self.created_at.isoformat()
            }
except Exception:
    pass


try:
    class Like(db.Model):
        """点赞记录表"""
        
        __tablename__ = 'likes'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.String(64), index=True, nullable=False)
        moment_id = db.Column(db.Integer, db.ForeignKey('moments.id'), nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        # 唯一约束：同一用户不能重复点赞同一条
        __table_args__ = (
            db.UniqueConstraint('user_id', 'moment_id', name='unique_user_moment_like'),
        )
except Exception:
    pass


try:
    class Comment(db.Model):
        """评论记录表"""
        
        __tablename__ = 'comments'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.String(64), index=True, nullable=False)
        moment_id = db.Column(db.Integer, db.ForeignKey('moments.id'), nullable=False)
        content = db.Column(db.Text, nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        # 关联
        moment = db.relationship('Moment', backref=db.backref('comments', lazy='dynamic'))
        
        def to_dict(self):
            return {
                'id': self.id,
                'user_id': self.user_id,
                'moment_id': self.moment_id,
                'content': self.content,
                'created_at': self.created_at.isoformat()
            }
except Exception:
    pass
