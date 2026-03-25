"""
数据库配置文件
Go In App - SQLite + SQLAlchemy
"""

import os

# 数据库配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根目录

# Vercel 部署时使用临时目录，本地开发使用项目目录
if os.getenv('VERCEL'):
    # Vercel 环境：使用内存数据库或临时目录
    DATABASE_PATH = '/tmp/goin.db'
else:
    # 本地环境：使用项目目录
    DATABASE_PATH = os.path.join(BASE_DIR, 'goin.db')

# SQLAlchemy 配置
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False  # 开发时可设为 True 查看 SQL 日志

# 数据库配置字典
DB_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': SQLALCHEMY_DATABASE_URI,
    'SQLALCHEMY_TRACK_MODIFICATIONS': SQLALCHEMY_TRACK_MODIFICATIONS,
    'SQLALCHEMY_ECHO': SQLALCHEMY_ECHO
}
