"""
数据库配置文件
Go In App - 支持多种数据库模式

支持模式：
1. Vercel Serverless 模式：使用内存数据库（演示）
2. 云数据库模式：使用 Supabase/PlanetScale/火山引擎 RDS
3. 本地开发模式：使用 SQLite 文件
"""

import os

# 数据库配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根目录

# 检测运行环境
VERCEL_ENV = os.getenv('VERCEL', 'false').lower() == 'true'
FLASK_ENV = os.getenv('FLASK_ENV', 'production')

# 数据库模式选择
if VERCEL_ENV:
    # ========== Vercel Serverless 模式 ==========
    # 使用内存数据库（演示用途，每次请求重新创建）
    # 或者使用云数据库（推荐生产环境使用）
    
    # 方案 A：内存数据库（演示）
    DATABASE_PATH = ':memory:'
    
    # 方案 B：云数据库（取消注释并使用）
    # DATABASE_URL = os.getenv('DATABASE_URL', '')
    # if DATABASE_URL:
    #     DATABASE_PATH = DATABASE_URL  # 如：postgresql://user:pass@host:5432/dbname
    # else:
    #     DATABASE_PATH = ':memory:'  # 回退到内存数据库
    
    print(f"🔧 Vercel 环境：使用数据库模式 = {DATABASE_PATH}")
    
elif FLASK_ENV == 'development':
    # ========== 本地开发模式 ==========
    # 使用 SQLite 文件
    DATABASE_PATH = os.path.join(BASE_DIR, 'goin.db')
    print(f"🔧 本地开发环境：使用数据库路径 = {DATABASE_PATH}")
    
else:
    # ========== 生产环境（非 Vercel） ==========
    # 优先使用环境变量，否则使用 SQLite
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    if DATABASE_URL:
        DATABASE_PATH = DATABASE_URL
        print(f"🔧 生产环境：使用云数据库 = {DATABASE_URL}")
    else:
        DATABASE_PATH = os.path.join(BASE_DIR, 'goin.db')
        print(f"🔧 生产环境：使用 SQLite = {DATABASE_PATH}")

# SQLAlchemy 配置
# 如果是 SQLite 路径，需要添加 sqlite:/// 前缀
if DATABASE_PATH == ':memory:':
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
elif DATABASE_PATH.startswith(('postgresql://', 'mysql://', 'sqlite:///')):
    SQLALCHEMY_DATABASE_URI = DATABASE_PATH
else:
    # 本地文件路径
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False  # 开发时可设为 True 查看 SQL 日志

# 数据库配置字典
DB_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': SQLALCHEMY_DATABASE_URI,
    'SQLALCHEMY_TRACK_MODIFICATIONS': SQLALCHEMY_TRACK_MODIFICATIONS,
    'SQLALCHEMY_ECHO': SQLALCHEMY_ECHO
}

# 打印配置信息（调试用）
if os.getenv('DEBUG'):
    print(f"🔍 数据库配置：{DB_CONFIG}")
