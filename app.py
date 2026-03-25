"""
Go In - 沉浸式 MVP
一个会自己发生的 AI 世界
"""

from flask import Flask, render_template_string, render_template, session, redirect, url_for, jsonify, request, make_response
from datetime import datetime, timedelta
import random
import uuid
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入数据库配置和服务
from config.db_config import DB_CONFIG
from services.database import db, init_db, get_or_create_user, save_user_data as db_save_user, get_user_data as db_get_user

# 导入服务层
from services import ContentGenerator, UserManager

logger.info("🚀 Go In 应用启动中...")

app = Flask(__name__)
app.secret_key = 'goin_immersive_mvp_2026'

# 数据库配置
app.config.update(DB_CONFIG)

# 延迟初始化数据库（在第一次请求时）
db_initialized = False

def ensure_db_initialized():
    """确保数据库已初始化（仅在第一次调用时）"""
    global db_initialized
    if not db_initialized:
        try:
            logger.info("🔧 开始初始化数据库...")
            init_db(app)
            db_initialized = True
            logger.info("✅ 数据库初始化成功")
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败：{str(e)}")
            logger.exception("详细错误堆栈:")
            raise  # 重新抛出异常，让 Vercel 显示错误

# 注意：不在这里调用 init_db(app)，而是在第一次请求时调用

# 无感多用户隔离：服务器端数据存储
# 使用字典存储所有用户数据，key 为 user_id（作为缓存）
USER_DATA_STORE = {}

@app.before_request
def load_user_from_cookie():
    """从 Cookie 加载用户 ID（如果存在）"""
    try:
        # 确保数据库已初始化
        ensure_db_initialized()
        
        user_id = request.cookies.get('user_id')
        if user_id and 'user_id' not in session:
            session['user_id'] = user_id
            logger.info(f"✅ 从 Cookie 加载用户 ID: {user_id[:8]}...")
    except Exception as e:
        logger.error(f"❌ 加载用户失败：{str(e)}")
        logger.exception("详细错误:")
        raise

def get_or_create_user_id():
    """获取或创建用户 ID（隐式、无感知）"""
    user_id = session.get('user_id')
    
    if not user_id:
        # 第一次访问，自动生成唯一 ID
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id
        USER_DATA_STORE[user_id] = {
            'posts': [],  # 已浏览内容（持久化）
            'insights': {},  # 用户偏好（问题回答）
            'preferences': {},  # 初始偏好设置
            'avatar_shown': False,  # AI 形象是否已显示
            'avatar_trait': None,  # AI 形象特征
            'entry_count': 0,  # 进入次数
            'content_viewed': 0,  # 浏览内容数
            'created_at': datetime.now(),
            'last_post_timestamp': None,  # 最后一条内容的时间戳
            'last_generate_time': None,  # AI 自主生活：最后生成时间
            'life_timeline': [],  # AI 生活时间轴
            'life_traits': [],  # 【轻习惯】生活倾向（1-2 个）
            'visited_locations': [],  # 【轻习惯】已访问地点记录
            # ========== 【AI 人格养成系统 v0.1】==========
            'personality': None,  # 用户人格结构（本地存储）
            'memories': [],  # AI 记忆列表（持续累积）
            'last_question_time': None,  # 上次提问时间
            'question_count': 0,  # 已提问数量
            # ========== 【AI 人格自主成长系统 v1.0】==========
            'tag_weights': {},  # 兴趣标签权重（动态成长）
            'style_history': [],  # 风格历史记录（最近 10 条）
            'interaction_feedback': {},  # 用户互动反馈（点赞/停留）
            'growth_cycle_count': 0,  # 成长周期计数（每 3-5 条内容为一个周期）
            'ai_agent_mode': False,  # AI 代理模式开关
            'ai_agent_responses': [],  # AI 代理回应记录
            'consistency_traits': [],  # 人格一致性特征（用词/色彩/情绪）
            # ========== 【手机 App 原型体验 v2.0】==========
            'ai_avatar_name': '',  # AI 分身名字
            'ai_avatar_image': None,  # AI 分身形象（图片 URL）
            'ai_avatar_voice': None,  # AI 分身语音特征
            'ai_avatar_style': None,  # AI 分身风格（Q 版/拟人/赛博）
            'onboarding_completed': False,  # 欢迎引导是否完成
            'personality_customization_completed': False,  # 人格定制是否完成
            'app_mode': 'web',  # App 模式：web/app
            'soul_journal': [],  # 灵魂日志（AI 创作存档）
            'check_in_locations': [],  # 打卡地点记录
            'real_photo_unlocked': False,  # 是否已现实拍照解锁
            # =======================================================
        }
        print(f"[USER] New user created: {user_id[:8]}...")
    
    return user_id

def get_user_data():
    """获取当前用户的数据（优先从数据库加载）"""
    user_id = get_or_create_user_id()
    
    # 如果内存中没有，从数据库加载
    if user_id not in USER_DATA_STORE:
        db_user_data = db_get_user(user_id)
        if db_user_data:
            USER_DATA_STORE[user_id] = db_user_data
            print(f"✅ 从数据库加载用户数据：{user_id[:8]}...")
        else:
            USER_DATA_STORE[user_id] = {}
            print(f"🆕 创建新用户：{user_id[:8]}...")
    
    return USER_DATA_STORE.get(user_id, {})

def save_user_data(key, value):
    """保存用户数据（双重存储：内存 + 数据库）"""
    user_id = get_or_create_user_id()
    
    # 存储到内存（缓存）
    if user_id not in USER_DATA_STORE:
        USER_DATA_STORE[user_id] = {}
    USER_DATA_STORE[user_id][key] = value
    
    # 同步到数据库
    try:
        db_save_user(user_id, {key: value})
    except Exception as e:
        print(f"⚠️ 数据库保存失败：{e}")
    
    return USER_DATA_STORE[user_id]

# 添加响应头禁止缓存
@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# ============================================
# 数据层：默认城市 - 上海浦东
# ============================================

DEFAULT_CITY = {"id": "pudong", "name": "上海浦东"}

# 地点池（6 个指定地点）
PUDONG_LOCATIONS = [
    "陆家嘴滨江",
    "世纪大道",
    "IFC 商场",
    "张江咖啡馆",
    "前滩太古里",
    "金桥路边小店",
]

# 地点类型与图片视觉样式
# 使用本地图片文件（100% 可靠，国内可访问）
# 图片文件放在 /static/images/locations/ 目录下
# 建议图片尺寸：600x400 像素
LOCATION_IMAGES = {
    "陆家嘴滨江": "riverside_night.jpg",  # 江边夜景
    "世纪大道": "urban_street.jpg",  # 城市街道
    "IFC 商场": "shopping_mall.jpg",  # 商场内部
    "张江咖啡馆": "cafe_corner.jpg",  # 咖啡馆
    "前滩太古里": "shopping_district.jpg",  # 商业街区
    "金桥路边小店": "street_shop.jpg",  # 路边小店
}

# AI 人物伪出现机制
# 人物素材图片库（背影/侧脸/远景）
# 放在 /static/images/characters/ 目录下
# 使用 PNG 透明背景人像：z1.png 到 z9.png
CHARACTER_IMAGES = [
    "z1.png",  # 人物素材 1（透明背景）
    "z2.png",  # 人物素材 2（透明背景）
    "z3.png",  # 人物素材 3（透明背景）
    "z4.png",  # 人物素材 4（透明背景）
    "z5.png",  # 人物素材 5（透明背景）
    "z6.png",  # 人物素材 6（透明背景）
    "z7.png",  # 人物素材 7（透明背景）
    "z8.png",  # 人物素材 8（透明背景）
    "z9.png",  # 人物素材 9（透明背景）
]

# 人物出现概率（20%）
CHARACTER_APPEARANCE_RATE = 0.2

def get_location_image_url(location):
    """根据地点获取本地图片 URL"""
    image_filename = LOCATION_IMAGES.get(location)
    if image_filename:
        # 返回静态文件 URL
        return f"/static/images/locations/{image_filename}"
    return None

def get_character_image_url():
    """获取随机人物图片 URL（20% 概率出现）"""
    if random.random() > CHARACTER_APPEARANCE_RATE:
        return None
    
    # 随机选择一个人物图片
    character_filename = random.choice(CHARACTER_IMAGES)
    character_url = f"/static/images/characters/{character_filename}"
    print(f"[CHARACTER DEBUG] Selected: {character_filename}")
    return character_url

# 已存在内容 - 克制、安静、疏离感（带标签用于个性化）
WORLD_CONTENT = [
    {
        "time_label": "刚刚",
        "timestamp": datetime.now() - timedelta(minutes=5),
        "location": "陆家嘴滨江",
        "text": "风有点大。",
        "mood": "平静",
        "style": "quiet",  # quiet/social
        "time_pref": "any",  # day/night/any
        "social": "alone",  # alone/crowd/any
        "time_type": "action",  # action/stay/quiet（时间段类型）
    },
    {
        "time_label": "今天下午 3:20",
        "timestamp": datetime.now() - timedelta(hours=4),
        "location": "世纪大道",
        "text": "地铁站出来，抬头看了一眼。高楼还是那么多。",
        "mood": "淡然",
        "style": "quiet",
        "time_pref": "day",
        "social": "crowd",
    },
    {
        "time_label": "昨天晚上 9:15",
        "timestamp": datetime.now() - timedelta(days=1, hours=6),
        "location": "IFC 商场",
        "text": "随便逛了一圈，什么都没买。",
        "mood": "放空",
        "style": "quiet",
        "time_pref": "night",
        "social": "alone",
    },
    {
        "time_label": "昨天下午 2:30",
        "timestamp": datetime.now() - timedelta(days=1, hours=11),
        "location": "张江咖啡馆",
        "text": "坐了一个下午，没人打扰。",
        "mood": "安静",
        "style": "quiet",
        "time_pref": "day",
        "social": "alone",
    },
]

# 继续内容池 - 带标签（安静/热闹、独处/人群、白天/夜晚、时间段类型）
CONTINUE_CONTENT = [
    # 标准型内容
    {"location": "陆家嘴滨江", "text": "江对面是外滩，这边是高楼。中间隔着一条江。", "mood": "疏离", "style": "quiet", "time_pref": "any", "social": "alone", "time_type": "stay"},
    {"location": "世纪大道", "text": "早高峰的人流，像潮水一样。", "mood": "旁观", "style": "quiet", "time_pref": "day", "social": "crowd", "time_type": "action"},
    {"location": "IFC 商场", "text": "冷气开得很足。", "mood": "冷静", "style": "quiet", "time_pref": "any", "social": "crowd", "time_type": "stay"},
    {"location": "张江咖啡馆", "text": "老板说今天豆子不错。嗯。", "mood": "平淡", "style": "quiet", "time_pref": "day", "social": "alone", "time_type": "stay"},
    {"location": "前滩太古里", "text": "新店很多，人不多。", "mood": "安静", "style": "quiet", "time_pref": "day", "social": "alone", "time_type": "stay"},
    {"location": "金桥路边小店", "text": "一碗馄饨，十块钱。味道还可以。", "mood": "满足", "style": "quiet", "time_pref": "any", "social": "alone", "time_type": "action"},
    {"location": "陆家嘴滨江", "text": "跑步的人从我身边经过，一下又一下。", "mood": "放空", "style": "quiet", "time_pref": "day", "social": "alone", "time_type": "action"},
    {"location": "世纪大道", "text": "绿灯还有三秒，我停住了。", "mood": "犹豫", "style": "quiet", "time_pref": "any", "social": "alone", "time_type": "action"},
    {"location": "前滩太古里", "text": "找了个角落坐着，看人来人往。", "mood": "旁观", "style": "quiet", "time_pref": "any", "social": "crowd", "time_type": "stay"},
    # 热闹/社交型内容
    {"location": "IFC 商场", "text": "中庭有人在弹钢琴，围了一圈人。", "mood": "热闹", "style": "social", "time_pref": "day", "social": "crowd", "time_type": "stay"},
    {"location": "前滩太古里", "text": "遇到一群人在拍照，被拉去合影了。", "mood": "开心", "style": "social", "time_pref": "day", "social": "crowd", "time_type": "action"},
    {"location": "金桥路边小店", "text": "老板多送了一瓶饮料，说今天活动。", "mood": "惊喜", "style": "social", "time_pref": "any", "social": "crowd", "time_type": "action"},
    {"location": "陆家嘴滨江", "text": "江边有街头艺人唱歌，听了一会儿。", "mood": "放松", "style": "social", "time_pref": "night", "social": "crowd", "time_type": "stay"},
    {"location": "世纪大道", "text": "地铁口遇到发传单的，聊了几句。", "mood": "随意", "style": "social", "time_pref": "day", "social": "crowd", "time_type": "action"},
    {"location": "张江咖啡馆", "text": "隔壁桌在讨论项目，不小心听完了全程。", "mood": "好奇", "style": "social", "time_pref": "day", "social": "crowd", "time_type": "stay"},
    # 共鸣感内容（20%-30% 占比）
    {"location": "陆家嘴滨江", "text": "其实也没有很想来。", "mood": "疏离", "style": "quiet", "time_pref": "any", "social": "alone", "time_type": "action"},
    {"location": "世纪大道", "text": "好像不是这里的问题。", "mood": "疑惑", "style": "quiet", "time_pref": "any", "social": "alone", "time_type": "action"},
    {"location": "IFC 商场", "text": "只是刚好走到这。", "mood": "淡然", "style": "quiet", "time_pref": "any", "social": "alone", "time_type": "action"},
    {"location": "前滩太古里", "text": "也没有人在等我。", "mood": "平静", "style": "quiet", "time_pref": "any", "social": "alone", "time_type": "stay"},
    {"location": "张江咖啡馆", "text": "坐在这里，时间过得慢一些。", "mood": "安静", "style": "quiet", "time_pref": "day", "social": "alone", "time_type": "stay"},
    {"location": "金桥路边小店", "text": "偶尔也会想，如果当时选了另一条路。", "mood": "思索", "style": "quiet", "time_pref": "any", "social": "alone", "time_type": "quiet"},
    {"location": "陆家嘴滨江", "text": "风把思绪吹散了。", "mood": "放空", "style": "quiet", "time_pref": "any", "social": "alone", "time_type": "quiet"},
    {"location": "世纪大道", "text": "人潮里，我是自己的旁观者。", "mood": "疏离", "style": "quiet", "time_pref": "day", "social": "crowd", "time_type": "action"},
]

# ============================================
# 地点库 - 上海浦东具体真实地点（按区域分组）
# 目标：让用户产生"我知道这个地方"的真实感
# 新增：地点路径连续性（70% 同区域移动，30% 跨区跳转）
# ============================================
PUDONG_LOCATIONS = {
    # 陆家嘴区域（5 个）
    "lujiazui": [
        "世纪大道地铁站口",
        "陆家嘴滨江步道",
        "IFC 商场外",
        "正大广场门口",
        "东方明珠下",
    ],
    # 张江区域（3 个）
    "zhangjiang": [
        "张江咖啡馆",
        "张江地铁站",
        "金科路商业街",
    ],
    # 前滩区域（2 个）
    "qiantan": [
        "前滩太古里",
        "前滩友城公园",
    ],
    # 金桥区域（2 个）
    "jinqiao": [
        "金桥路街边",
        "金桥国际广场",
    ],
    # 其他地标（3 个）
    "other": [
        "浦东美术馆",
        "世纪公园",
        "龙阳路地铁站",
    ],
}

# 地点分组映射（快速查询某个地点属于哪个区域）
LOCATION_TO_REGION = {}
for region, locations in PUDONG_LOCATIONS.items():
    for location in locations:
        LOCATION_TO_REGION[location] = region

# 所有地点的扁平列表（兼容性保留）
ALL_LOCATIONS = []
for locations in PUDONG_LOCATIONS.values():
    ALL_LOCATIONS.extend(locations)

# 截图级内容池 - 高共鸣、抽象、短句（约 20% 概率出现）
# 升级：使用具体真实地点，增强"我知道这个地方"的真实感
SCREENSHOT_CONTENT = [
    {"location": random.choice(ALL_LOCATIONS), "text": "也不是非要来。", "mood": "疏离", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(ALL_LOCATIONS), "text": "好像不是这里的问题。", "mood": "疑惑", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(ALL_LOCATIONS), "text": "只是刚好走到这。", "mood": "淡然", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(ALL_LOCATIONS), "text": "也没有人在等我。", "mood": "平静", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(ALL_LOCATIONS), "text": "偶尔也会想，如果当时选了另一条路。", "mood": "思索", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(ALL_LOCATIONS), "text": "就这样吧。", "mood": "释然", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(ALL_LOCATIONS), "text": "总要去一个地方的。", "mood": "随意", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(ALL_LOCATIONS), "text": "今天不太一样。", "mood": "微妙", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(ALL_LOCATIONS), "text": "下次再说。", "mood": "留白", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(ALL_LOCATIONS), "text": "已经不重要了。", "mood": "平静", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
]

# 流式感知问题池 - 轻量、自然、像随口一问（约 30% 概率出现）
FLOW_QUESTIONS = [
    {"question": "你会再来这里吗？", "options": ["会", "不会"], "tag": "stay_preference"},
    {"question": "你更习惯一个人吗？", "options": ["是", "不是"], "tag": "social_preference"},
    {"question": "刚刚那种地方，你会多待一会吗？", "options": ["会", "不会"], "tag": "explore_depth"},
    {"question": "你会回去吗？", "options": ["会", "不会"], "tag": "return_preference"},
    {"question": "喜欢这种安静吗？", "options": ["喜欢", "还好"], "tag": "quiet_preference"},
    {"question": "如果是周末，人会多一些？", "options": ["会", "不会"], "tag": "crowd_tolerance"},
    {"question": "这样的地方，你想探索更多吗？", "options": ["想", "不了"], "tag": "curiosity_level"},
    {"question": "现在时间还早，要继续走吗？", "options": ["要", "不了"], "tag": "energy_level"},
    {"question": "这个地方符合你的期待吗？", "options": ["符合", "还行"], "tag": "expectation_match"},
    {"question": "你会推荐给别人吗？", "options": ["会", "不会"], "tag": "recommendation"},
]

# 自我指向句池 - 模糊、自我指向、不解释（约 15%-20% 概率出现）
SELF_REFERENTIAL_SENTENCES = [
    # 通用型（适合所有状态）
    {"text": "又是这样。", "style": "quiet", "mood": "淡然"},
    {"text": "好像一直都是这样。", "style": "quiet", "mood": "平静"},
    {"text": "也不是第一次。", "style": "quiet", "mood": "疏离"},
    {"text": "应该早就知道了。", "style": "quiet", "mood": "思索"},
    {"text": "差不多。", "style": "quiet", "mood": "克制"},
    
    # 停留/疏离倾向（当用户偏向安静时使用）
    {"text": "没什么变化。", "style": "quiet", "mood": "平静", "user_pref": "stay"},
    {"text": "还是老样子。", "style": "quiet", "mood": "淡然", "user_pref": "stay"},
    {"text": "习惯了。", "style": "quiet", "mood": "接受", "user_pref": "stay"},
    
    # 行动/探索倾向（当用户偏向探索时使用）
    {"text": "还是想再看看。", "style": "quiet", "mood": "好奇", "user_pref": "explore"},
    {"text": "又换了个地方。", "style": "quiet", "mood": "随意", "user_pref": "explore"},
    {"text": "还可以再走走。", "style": "quiet", "mood": "放松", "user_pref": "explore"},
]

# AI 形象初次出现机制
# 触发条件：第 3 次进入 或 浏览 5 条以上内容
# 特点：自然出现，不说明是"你的形象"，保持真实感
AI_AVATAR_FIRST_APPEARANCE = {
    # 形象特征（用于保持一致性）
    "avatar_traits": [
        {"gender": "male", "age_range": "25-30", "style": "casual", "hair": "short_black"},
        {"gender": "female", "age_range": "23-28", "style": "minimal", "hair": "medium_black"},
    ],
    
    # 场景文案（人物在真实场景中）
    "scene_captions": [
        {"text": "他坐在窗边。", "mood": "安静", "scene": "cafe"},
        {"text": "她在等人。", "mood": "平静", "scene": "street"},
        {"text": "一个人。", "mood": "淡然", "scene": "night"},
        {"text": "路过这里。", "mood": "随意", "scene": "street"},
        {"text": "刚到这里。", "mood": "思索", "scene": "waterfront"},
    ]
}

# 移动感文案池 - 增强地点之间的连续性感觉（约 30% 概率插入）
# 特点：轻微行动延续，不解释，不说明目的
MOVEMENT_TEXTS = [
    "又往那边走了一点。",
    "没走太远。",
    "顺着过去了。",
    "继续往前走。",
    "换了个地方。",
    "又移动了一下。",
    "离开那里了。",
    "在路上了。",
    "快到下一个地方了。",
    "还在这一带。",
]

# ============================================
# 【轻习惯系统】生活倾向类型定义
# 目标：让 AI 逐渐呈现稳定偏好，形成类似真实人的生活习惯
# ============================================
LIFE_TRAITS = {
    # 咖啡倾向：更容易生成咖啡店相关，出现"坐""停留"
    "coffee": {
        "name": "咖啡倾向",
        "preferred_locations": ["张江咖啡馆", "IFC 商场外", "金桥路街边"],  # 可能有咖啡店的地点
        "preferred_time": "day",  # 偏好时间段
        "preferred_behaviors": ["坐", "停留", "喝咖啡", "发呆"],
        "weight_boost": 2.0,  # 权重提升倍数
    },
    # 夜晚倾向：更容易生成夜晚时间内容
    "night": {
        "name": "夜晚倾向",
        "preferred_locations": ["陆家嘴滨江步道", "世纪大道地铁站口", "浦东美术馆"],
        "preferred_time": "night",
        "preferred_behaviors": ["散步", "看夜景", "安静"],
        "weight_boost": 2.0,
    },
    # 散步倾向：更容易生成步行、移动相关内容
    "walking": {
        "name": "散步倾向",
        "preferred_locations": ["陆家嘴滨江步道", "前滩友城公园", "世纪公园"],
        "preferred_time": "any",
        "preferred_behaviors": ["走", "路过", "经过", "移动"],
        "weight_boost": 1.8,
    },
    # 安静倾向：更容易生成安静、独处内容
    "quiet": {
        "name": "安静倾向",
        "preferred_locations": ["张江咖啡馆", "浦东美术馆", "世纪公园"],
        "preferred_time": "any",
        "preferred_behaviors": ["安静", "一个人", "思考", "放空"],
        "weight_boost": 2.0,
    },
    # 购物倾向：更容易生成商场、商业区内容
    "shopping": {
        "name": "购物倾向",
        "preferred_locations": ["IFC 商场外", "正大广场门口", "前滩太古里", "金桥国际广场"],
        "preferred_time": "day",
        "preferred_behaviors": ["逛", "看", "路过"],
        "weight_boost": 1.5,
    },
}

# 行为句池（用于重复机制）
BEHAVIOR_SENTENCES = [
    "坐了一会儿。",
    "发了会儿呆。",
    "看了一眼。",
    "随便逛了逛。",
    "什么都没买。",
    "喝了杯东西。",
    "走了很久。",
    "休息了一下。",
]

# 【弱记忆系统】记忆感文案片段 - 轻微的"来过"感觉
# 特点：不解释时间，不说明上次，只是微妙的熟悉感
MEMORY_FRAGMENTS = [
    "又",  # 又坐了一会儿
    "还是",  # 还是在这里
    "有点熟",  # 有点熟
    "照旧",  # 照旧点了咖啡
    "依旧",  # 依旧安静
    "老位置",  # 老视角
    "熟悉",  # 熟悉的角落
    "再次",  # 再次路过
]

# ============================================
# 【AI 人格养成系统 v0.1】核心数据结构
# ============================================

# 潜意识问题池 - 轻量、模糊、偏情绪/潜意识（约 30% 概率弹出）
# 特点：不打扰，可跳过，无需复杂分析
SUBCONSCIOUS_QUESTIONS = [
    # 时间/状态偏好
    {"question": "今天更像白天还是夜晚？", "options": ["白天", "夜晚"], "tag": "time_preference"},
    {"question": "最近更接近哪种状态？", "options": ["平静", "空白", "混乱"], "tag": "emotion_state"},
    {"question": "如果可以消失一会，你会去哪？", "options": ["海边", "山里", "城市", "家里"], "tag": "escape_preference"},
    {"question": "你更喜欢人多，还是一个人？", "options": ["人多", "一个人"], "tag": "social_preference"},
    
    # 空间/场景偏好
    {"question": "现在更想去哪里？", "options": ["安静的地方", "热闹的地方"], "tag": "space_preference"},
    {"question": "此刻更需要什么？", "options": ["独处", "陪伴"], "tag": "need_preference"},
    {"question": "心情更接近哪个颜色？", "options": ["蓝色", "灰色", "白色", "黑色"], "tag": "mood_color"},
    
    # 行为倾向
    {"question": "会更倾向于？", "options": ["待着不动", "出去走走"], "tag": "action_preference"},
    {"question": "面对陌生地方会？", "options": ["探索", "观望"], "tag": "explore_tendency"},
    {"question": "累了会？", "options": ["休息", "继续"], "tag": "rest_tendency"},
    
    # 情绪表达
    {"question": "现在的情绪是？", "options": ["没什么情绪", "有点低落", "还行"], "tag": "current_emotion"},
    {"question": "更愿意如何表达？", "options": ["说出来", "写下来", "不说"], "tag": "expression_style"},
    {"question": "被人理解重要吗？", "options": ["重要", "不重要", "无所谓"], "tag": "understanding_need"},
]

# 性格倾向类型（用于 AI 人格生成）
PERSONALITY_TRAITS = {
    "quiet": {"name": "安静", "keywords": ["独处", "安静", "内敛"]},
    "social": {"name": "社交", "keywords": ["人群", "热闹", "外向"]},
    "calm": {"name": "冷静", "keywords": ["平静", "理性", "克制"]},
    "sensitive": {"name": "敏感", "keywords": ["情绪", "细腻", "感知"]},
    "independent": {"name": "独立", "keywords": ["一个人", "自主", "自由"]},
    "gentle": {"name": "温柔", "keywords": ["温和", "柔软", "包容"]},
}

# 兴趣标签映射（从回答中提取）
INTEREST_TAGS = {
    # 时间相关
    "day": ["白天", "阳光", "活动"],
    "night": ["夜晚", "安静", "独处"],
    # 空间相关
    "nature": ["海边", "山里", "自然"],
    "urban": ["城市", "街道", "建筑"],
    "home": ["家里", "私人", "舒适"],
    # 社交相关
    "alone": ["一个人", "独处", "独立"],
    "crowd": ["人多", "热闹", "社交"],
    # 情绪相关
    "calm": ["平静", "平和", "稳定"],
    "chaotic": ["混乱", "波动", "不安"],
    "blank": ["空白", "放空", "无感"],
}

# ============================================
# 【AI 人格自主成长系统 v1.0】核心配置
# ============================================

# 人格一致性特征池（用于保持连续性）
CONSISTENCY_TRAITS = {
    # 用词风格
    "word_style": {
        "simple": ["。", "嗯", "吧", "啊"],  # 简洁
        "poetic": ["……", "或许", "大概", "可能"],  # 诗意
        "direct": ["！", "就是", "肯定", "一定"],  # 直接
    },
    # 色彩偏好（用于未来图片生成）
    "color_preference": {
        "warm": ["暖色", "橙色", "黄色", "阳光"],
        "cool": ["冷色", "蓝色", "灰色", "月光"],
        "neutral": ["白色", "黑色", "素色", "简单"],
    },
    # 情绪基调
    "emotion_tone": {
        "positive": ["开心", "不错", "挺好", "喜欢"],
        "neutral": ["还行", "一般", "普通", "日常"],
        "negative": ["累了", "不想", "算了", "随便"],
    },
}

# 文案模板（标签填充式）
TEXT_TEMPLATES = [
    # 地点 + 情绪
    {"template": "{location}，{emotion}。", "tags": ["location", "emotion"]},
    {"template": "在{location}，感觉{emotion}。", "tags": ["location", "emotion"]},
    # 时间 + 行为
    {"template": "{time}，{action}。", "tags": ["time", "action"]},
    {"template": "{time}的时候，{action}。", "tags": ["time", "action"]},
    # 情绪 + 观察
    {"template": "{emotion}，看到{observation}。", "tags": ["emotion", "observation"]},
    # 高权重标签专用（20% 概率）
    {"template": "还是{location}，{emotion}。", "tags": ["location", "emotion"], "weight_boost": 1.5},
    {"template": "又一次{action}，{emotion}。", "tags": ["action", "emotion"], "weight_boost": 1.5},
]

# 低权重随机元素池（保持多样性，20% 概率出现）
RANDOM_ELEMENTS = [
    # 意外地点
    {"type": "location", "value": "陌生的小巷", "weight": 0.2},
    {"type": "location", "value": "临时起意的地方", "weight": 0.2},
    # 意外行为
    {"type": "action", "value": "漫无目的", "weight": 0.2},
    {"type": "action", "value": "临时决定", "weight": 0.2},
    # 意外情绪
    {"type": "emotion", "value": "说不清", "weight": 0.2},
    {"type": "emotion", "value": "复杂", "weight": 0.2},
]

# ============================================
# 特点：轻微延续感，不解释，不说明行动
UNFINISHED_SENTENCES = [
    # 轻微行动延续
    "又往前走了一点。",
    "还没决定要不要进去。",
    "在门口站了一会儿。",
    "可能会再过去。",
    "先这样。",
    "再看看。",
    "再坐一会儿。",
    "还不想走。",
    "再等等。",
    "再待一会儿。",
    
    # 停留、观察
    "又看了一眼。",
    "还是老样子。",
    "没什么变化。",
    "和之前一样。",
    
    # 轻微犹豫
    "不太确定。",
    "再说吧。",
    "下次也可以。",
    "改天再来。",
]

# 异常内容机制 - 约 10%-15% 概率
# 特点：结构不完整、模糊、不解释、轻微偏离逻辑
# 目标：增加不可预测性，让用户产生"停顿感"
# 升级：使用具体真实地点，增强真实感
ABNORMAL_CONTENT = [
    # 只有文案，无地点（升级为具体地点）
    {"location": random.choice(ALL_LOCATIONS), "text": "好像不是这里的问题。", "mood": "疑惑", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(ALL_LOCATIONS), "text": "只是刚好走到这。", "mood": "淡然", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(ALL_LOCATIONS), "text": "也不是第一次这样。", "mood": "平静", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(ALL_LOCATIONS), "text": "有点说不清。", "mood": "思索", "style": "quiet", "time_pref": "any", "social": "alone"},
    
    # 模糊、不解释（升级为具体地点）
    {"location": random.choice(ALL_LOCATIONS), "text": "不应该在这里。", "mood": "疏离", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(ALL_LOCATIONS), "text": "又错过了。", "mood": "遗憾", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(ALL_LOCATIONS), "text": "其实也没什么。", "mood": "克制", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(ALL_LOCATIONS), "text": "就这样吧。", "mood": "释然", "style": "quiet", "time_pref": "any", "social": "alone"},
    
    # 轻微偏离逻辑（保留时间性模糊，但地点具体）
    {"location": random.choice(ALL_LOCATIONS), "text": "昨天路过的，今天应该不在了。", "mood": "思索", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(ALL_LOCATIONS), "text": "下次也不会来。", "mood": "疏离", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(ALL_LOCATIONS), "text": "记不太清了。", "mood": "模糊", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(ALL_LOCATIONS), "text": "反正都一样。", "mood": "淡然", "style": "quiet", "time_pref": "any", "social": "alone"},
]

# 特殊内容池 - 不确定感/情绪化（每 3-5 条插入一条）
SPECIAL_CONTENT = [
    {"location": "陆家嘴滨江", "text": "好像不是这个地方。", "mood": "疑惑", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": "世纪大道", "text": "其实也可以不来。", "mood": "淡然", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": "IFC 商场", "text": "没进去。", "mood": "疏离", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": "前滩太古里", "text": "走到门口，又折回来了。", "mood": "犹豫", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": "张江咖啡馆", "text": "还是算了。", "mood": "克制", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": "金桥路边小店", "text": "下次吧。", "mood": "留白", "style": "quiet", "time_pref": "any", "social": "alone"},
]

# ============================================
# HTML 模板
# ============================================

# 个性化引导页 - 极简 3 题
ONBOARDING_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>Go In</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
            padding-top: 140px; /* 为固定头部预留空间 */
        }
        .container {
            max-width: 400px;
            width: 100%;
        }
        .question {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
        }
        .question-text {
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
            margin-bottom: 16px;
            font-weight: 500;
        }
        .options {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        /* 隐藏 radio */
        .option-input {
            display: none;
        }
        /* 用 label 模拟按钮 */
        .option-label {
            background: rgba(102, 126, 234, 0.15);
            border: 1px solid rgba(102, 126, 234, 0.3);
            color: #a5b4fc;
            padding: 12px 20px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
            text-align: center;
            display: block;
        }
        .option-label:hover {
            background: rgba(102, 126, 234, 0.25);
            border-color: rgba(102, 126, 234, 0.5);
        }
        /* 选中状态 */
        .option-input:checked + .option-label {
            background: rgba(102, 126, 234, 0.4);
            border-color: rgba(102, 126, 234, 0.8);
        }
        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 40px;
            font-size: 16px;
            border-radius: 30px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            margin-top: 20px;
            width: 100%;
        }
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        .progress {
            text-align: center;
            color: rgba(255, 255, 255, 0.4);
            font-size: 12px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="progress">3 个快速选择</div>
        
        <form action="/save_preferences" method="POST">
            <div class="question">
                <div class="question-text">1. 你更习惯：</div>
                <div class="options">
                    <input type="radio" name="style" id="style_quiet" value="quiet" class="option-input" required>
                    <label for="style_quiet" class="option-label">安静</label>
                    
                    <input type="radio" name="style" id="style_social" value="social" class="option-input" required>
                    <label for="style_social" class="option-label">热闹</label>
                </div>
            </div>
            
            <div class="question">
                <div class="question-text">2. 你更常：</div>
                <div class="options">
                    <input type="radio" name="social" id="social_alone" value="alone" class="option-input" required>
                    <label for="social_alone" class="option-label">一个人</label>
                    
                    <input type="radio" name="social" id="social_crowd" value="crowd" class="option-input" required>
                    <label for="social_crowd" class="option-label">在人群里</label>
                </div>
            </div>
            
            <div class="question">
                <div class="question-text">3. 你更偏向：</div>
                <div class="options">
                    <input type="radio" name="time" id="time_day" value="day" class="option-input" required>
                    <label for="time_day" class="option-label">白天</label>
                    
                    <input type="radio" name="time" id="time_night" value="night" class="option-input" required>
                    <label for="time_night" class="option-label">夜晚</label>
                </div>
            </div>
            
            <button type="submit" class="submit-btn">完成</button>
        </form>
    </div>
</body>
</html>
"""

FEED_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌆</text></svg>">
    <title>{{ city_name }} - Go In v3</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #0a0a1a;
            min-height: 100vh;
            padding: 0 20px;
        }
        .header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(10, 10, 26, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            z-index: 1000;
        }
        .city-title {
            color: #fff;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .subtitle {
            color: rgba(255, 255, 255, 0.5);
            font-size: 13px;
        }
        .post {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
        }
        /* 真实场景图片样式 */
        .post-image {
            width: 100%;
            height: 240px;
            object-fit: cover;
        }
        .post-image {
            animation: imageFadeIn 0.6s ease;
        }
        @keyframes imageFadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        /* AI 人物伪出现样式 */
        .post-image-container {
            position: relative;
            width: 100%;
            height: 240px;
            margin: 0 0 0 0;
            overflow: hidden !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            clip-path: inset(0 0 0 0);
        }
        .post-image {
            width: 100%;
            height: 240px;
            object-fit: cover;
        }
        .character-overlay {
            position: absolute;
            bottom: 10px;
            right: 10px;
            height: 80px;
            max-width: 80px;
            object-fit: contain;
            opacity: 0.8;
            filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.4));
            z-index: 1;
            animation: characterFadeIn 0.8s ease;
            pointer-events: none;
        }
        @keyframes characterFadeIn {
            from {
                opacity: 0;
                transform: translateY(10px) scale(0.95);
            }
            to {
                opacity: 0.8;
                transform: translateY(0) scale(1);
            }
        }
        .post-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }
        .time-badge {
            background: rgba(102, 126, 234, 0.2);
            color: #a5b4fc;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            position: relative;
            z-index: 1;
        }
        .location {
            color: rgba(255, 255, 255, 0.7);
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .location::before {
            content: "📍";
        }
        .image-placeholder {
            width: 100%;
            height: 200px;
            background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
            border-radius: 12px;
            margin: 24px 0;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .image-placeholder span {
            color: rgba(255, 255, 255, 0.2);
            font-size: 12px;
        }
        .post-text {
            color: rgba(255, 255, 255, 0.95);
            font-size: 16px;
            line-height: 1.8;
            margin-bottom: 20px;
            font-weight: 400;
            letter-spacing: 0.5px;
            white-space: pre-line; /* 支持换行 */
        }
        /* 未完成感特殊样式 */
        .post-text.unfinished-text {
            color: rgba(255, 255, 255, 0.75);
        }
        .post-text.unfinished-text::after {
            content: '…';
            color: rgba(255, 255, 255, 0.4);
            margin-left: 4px;
        }
        .post-text.screenshot-text {
            font-size: 18px;
            text-align: center;
            letter-spacing: 1px;
            margin-bottom: 28px;
        }
        /* 自我指向句特殊样式 */
        .post.self-referential-post {
            padding: 32px 24px;
        }
        .post.self-referential-post .post-text {
            font-size: 17px;
            color: rgba(255, 255, 255, 0.85);
            font-style: italic;
            text-align: left;
        }
        .post.screenshot-post {
            padding: 36px 24px;
        }
        /* AI 形象初次出现特殊样式 */
        .post.avatar-first-appearance {
            padding: 40px 24px;
            background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.05) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .post.avatar-first-appearance .image-placeholder {
            height: 320px;
            background-size: cover;
            background-position: center;
            position: relative;
            overflow: hidden;
        }
        .post.avatar-first-appearance .image-placeholder::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(to bottom, rgba(10,10,26,0.3) 0%, rgba(10,10,26,0.5) 100%);
        }
        .post.avatar-first-appearance .post-text {
            font-size: 16px;
            color: rgba(255, 255, 255, 0.9);
            text-align: center;
            letter-spacing: 1px;
            margin-top: 24px;
        }
        /* 异常内容特殊样式 */
        .post.abnormal-post {
            padding: 36px 24px;
            background: linear-gradient(135deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.04) 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-left: 2px solid rgba(255, 255, 255, 0.3);
        }
        .post.abnormal-post .post-text {
            font-size: 15px;
            color: rgba(255, 255, 255, 0.75);
            font-style: italic;
            text-align: left;
            letter-spacing: 0.8px;
            opacity: 0.85;
        }
        .post.abnormal-post .mood-tag {
            opacity: 0.6;
        }
        .post.screenshot-post .post-header {
            margin-bottom: 32px;
            justify-content: center;
        }
        .post.screenshot-post .image-placeholder {
            margin: 32px 0;
        }
        .post.screenshot-post .mood-tag {
            margin-bottom: 20px;
        }
        .post.screenshot-post .post-footer {
            margin-top: 20px;
            padding-top: 20px;
            text-align: center;
        }
        /* 自我指向句文字样式 */
        .self-referential-text {
            font-size: 17px;
            color: rgba(255, 255, 255, 0.85);
            font-style: italic;
            letter-spacing: 0.8px;
        }
        .mood-tag {
            display: inline-block;
            background: rgba(255, 255, 255, 0.05);
            color: rgba(255, 255, 255, 0.4);
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 12px;
            margin-bottom: 16px;
            position: relative;
            z-index: 1;
        }
        .post-footer {
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid rgba(255, 255, 255, 0.03);
        }
        .location-tag {
            color: rgba(255, 255, 255, 0.3);
            font-size: 11px;
            letter-spacing: 1px;
        }
        /* 流式感知问题样式 */
        .flow-question {
            margin-top: 20px;
            padding: 20px 16px;
            background: rgba(102, 126, 234, 0.08);
            border-radius: 12px;
            border: 1px solid rgba(102, 126, 234, 0.15);
        }
        .question-text {
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
            margin-bottom: 14px;
            text-align: center;
            font-weight: 400;
        }
        .question-options {
            display: flex;
            gap: 12px;
            justify-content: center;
        }
        .question-option {
            background: rgba(255, 255, 255, 0.08);
            color: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .question-option:hover {
            background: rgba(102, 126, 234, 0.2);
            border-color: rgba(102, 126, 234, 0.4);
        }
        .question-option.answered {
            background: rgba(102, 126, 234, 0.3);
            border-color: rgba(102, 126, 234, 0.6);
            color: #fff;
        }
        .hint-text {
            text-align: center;
            color: rgba(255, 255, 255, 0.3);
            font-size: 12px;
            margin-bottom: 15px;
            letter-spacing: 1px;
        }
        .feed-container {
            max-width: 400px;
            margin: 0 auto;
            padding-bottom: 20px;
        }
        /* 头部占位符，确保内容不被遮挡 */
        .header-spacer {
            height: 120px;
            width: 100%;
            min-height: 120px;
        }
        .new-post-animation {
            animation: fadeInNatural 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }
        @keyframes fadeInNatural {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
</head>
<body>
    <script>
        // 页面加载时强制滚动到顶部，确保第一个卡片不被头部遮挡
        window.addEventListener('DOMContentLoaded', function() {
            window.scrollTo(0, 0);
        });
    </script>
    <div class="header">
        <div class="city-title">{{ city_name }}</div>
        <div class="subtitle">另一个您的生活在继续</div>
    </div>
    
    <!-- 占位符，确保内容不被头部遮挡 -->
    <div class="header-spacer"></div>
    
    <div class="feed-container">
        <div class="feed" id="feed">
            {% if posts %}
                {% for post in posts %}
                <div class="post {% if post.is_screenshot %}screenshot-post{% endif %} {% if post.is_self_referential %}self-referential-post{% endif %}">
                    <!-- 真实场景图片 + AI 人物伪出现 -->
                    {% if post.image_url or post.character_url %}
                    <div class="post-image-container">
                        {% if post.image_url %}
                        <img src="{{ post.image_url }}" alt="{{ post.location }}" class="post-image" loading="lazy">
                        {% endif %}
                        
                        {% if post.character_url %}
                        <!-- AI 人物伪出现：叠加在场景图片上 -->
                        <img src="{{ post.character_url }}" alt="" class="character-overlay" loading="lazy">
                        {% endif %}
                    </div>
                    {% endif %}
                    
                    <div class="post-header">
                        <span class="time-badge">{{ post.time_label }}</span>
                    </div>
                    <div class="post-text {% if post.is_screenshot %}screenshot-text{% endif %} {% if post.is_unfinished %}unfinished-text{% endif %}">{{ post.text }}</div>
                    <span class="mood-tag">{{ post.mood }}</span>
                    {% if post.location %}
                    <div class="post-footer">
                        <div class="location-tag">📍 {{ post.location }}</div>
                    </div>
                    {% endif %}
                    
                    <!-- 流式感知问题 -->
                    {% if post.question %}
                    <div class="flow-question" id="question-{{ loop.index }}">
                        <div class="question-text">{{ post.question.text }}</div>
                        <div class="question-options">
                            {% for option in post.question.options %}
                            <button class="question-option" onclick="answerQuestion({{ loop.index }}, '{{ post.question.tag }}', '{{ option }}')">
                                {{ option }}
                            </button>
                            {% endfor %}
                        </div>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            {% endif %}
        </div>
        
        <div class="hint-text">你没看到的，也在发生</div>
    </div>
    
    <!-- 【AI 人格养成系统】潜意识问题弹窗 -->
    {% if current_question %}
    <div id="subconscious-modal" class="modal-overlay">
        <div class="modal-content">
            <div class="modal-question" id="modal-question-text">{{ current_question.question }}</div>
            <div class="modal-options">
                {% for option in current_question.options %}
                <button class="modal-option" onclick="submitAnswer('{{ current_question.tag }}', '{{ option }}')">
                    {{ option }}
                </button>
                {% endfor %}
            </div>
            <button class="modal-skip" onclick="closeModal()">跳过</button>
        </div>
    </div>
    
    <style>
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2000;
            animation: modalFadeIn 0.4s ease;
        }
        @keyframes modalFadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .modal-content {
            background: linear-gradient(135deg, rgba(30, 30, 60, 0.95) 0%, rgba(20, 20, 40, 0.95) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 32px 24px;
            max-width: 320px;
            width: 90%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }
        .modal-question {
            color: #fff;
            font-size: 17px;
            margin-bottom: 24px;
            line-height: 1.5;
            font-weight: 500;
        }
        .modal-options {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 20px;
        }
        .modal-option {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #fff;
            padding: 14px 20px;
            border-radius: 12px;
            font-size: 15px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .modal-option:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }
        .modal-skip {
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.4);
            font-size: 14px;
            cursor: pointer;
            padding: 8px;
        }
        .modal-skip:hover {
            color: rgba(255, 255, 255, 0.6);
        }
    </style>
    
    <script>
        // 潜意识问题弹窗逻辑
        setTimeout(() => {
            const modal = document.getElementById('subconscious-modal');
            if (modal) {
                modal.style.display = 'flex';
            }
        }, 1500);  // 延迟 1.5 秒弹出，不打扰
        
        function submitAnswer(tag, answer) {
            fetch('/api/answer_question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tag, answer })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    closeModal();
                }
            });
        }
        
        function closeModal() {
            const modal = document.getElementById('subconscious-modal');
            if (modal) {
                modal.style.opacity = '0';
                setTimeout(() => modal.remove(), 400);
            }
        }
    </script>
    {% endif %}
    
    <script>
        // 回答流式感知问题
        async function answerQuestion(tag, answer) {
            // 禁用该问题的所有按钮
            const questionDiv = event.target.closest('.flow-question');
            const buttons = questionDiv.querySelectorAll('.question-option');
            buttons.forEach(btn => {
                btn.classList.add('answered');
                btn.style.pointerEvents = 'none';
            });
            
            // 高亮选中的选项
            event.target.classList.add('answered');
            
            // 发送到后端保存
            try {
                await fetch('/api/save_insight', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ tag, answer })
                });
                console.log(`[INSIGHT] Saved: ${tag} = ${answer}`);
            } catch (error) {
                console.error('Error saving insight:', error);
            }
        }
    </script>
</body>
</html>
"""

# ============================================
# 路由层
# ============================================

@app.route('/')
def index():
    """首页 - 直接跳转到欢迎引导页"""
    return redirect(url_for('welcome_premium'))

@app.route('/favicon.ico')
def favicon():
    """返回空图标，避免 404"""
    return '', 204

@app.route('/welcome')
def welcome_premium():
    """行业顶级欢迎引导页面"""
    return render_template('welcome_premium.html')

@app.route('/feed')
def feed():
    """进入内容流 - 直接展示，自动生成初始内容"""
    # 无感多用户隔离：获取或创建用户 ID
    user_id = get_or_create_user_id()
    user_data = get_user_data()
    
    # 优先从 URL 参数获取偏好（首次提交）
    style_from_url = request.args.get('style')
    social_from_url = request.args.get('social')
    time_from_url = request.args.get('time')
    
    print(f"[DEBUG] URL params: style={style_from_url}, social={social_from_url}, time={time_from_url}")
    print(f"[DEBUG] User ID: {user_id[:8]}...")
    print(f"[DEBUG] User data before: {user_data.get('preferences')}")
    
    # 如果是从引导页提交过来的，保存 URL 参数到用户数据
    if style_from_url and social_from_url and time_from_url:
        save_user_data('preferences', {
            'style': style_from_url,
            'social': social_from_url,
            'time': time_from_url,
        })
        print(f"[DEBUG] Saved preferences to user data")
        # 立即重新获取用户数据，确保能读取到刚保存的偏好
        user_data = get_user_data()
    
    # 【移除引导页】直接生成默认偏好（如果还没有）
    if not user_data.get('preferences'):
        # 自动生成默认偏好（随机）
        default_prefs = {
            'style': random.choice(['quiet', 'social']),
            'social': random.choice(['alone', 'crowd']),
            'time': random.choice(['day', 'night']),
        }
        save_user_data('preferences', default_prefs)
        user_data = get_user_data()
        print(f"[DEBUG] Auto-generated default preferences: {default_prefs}")
    
    print(f"[DEBUG] Showing feed page with preferences: {user_data.get('preferences')}")
    
    # 获取用户偏好
    prefs = user_data.get('preferences', {})
    
    # 获取上次访问时间
    last_visit = user_data.get('last_visit_time')
    current_time = datetime.now()
    
    # 修复时区问题：确保两个时间对象都是 naive（无时区）
    if current_time.tzinfo is not None:
        current_time = current_time.replace(tzinfo=None)
    if last_visit and last_visit.tzinfo is not None:
        last_visit = last_visit.replace(tzinfo=None)
    
    # 记录本次访问时间为下次使用
    save_user_data('last_visit_time', current_time)
    
    # ========== 【AI 自主生活流机制】 ==========
    # 1. 读取用户已有的内容列表（持久化）
    existing_posts = user_data.get('posts', [])
    print(f"[LIFE] Existing posts count: {len(existing_posts)}")
    
    # 2. 内容上限管理：保留最近 30 条
    MAX_POSTS = 30
    if len(existing_posts) > MAX_POSTS:
        existing_posts = existing_posts[-MAX_POSTS:]
        save_user_data('posts', existing_posts)
        print(f"[LIFE] Trimmed posts to {MAX_POSTS}")
    
    # 3. 获取最后一条内容的时间戳
    last_post_timestamp = user_data.get('last_post_timestamp')
    if last_post_timestamp and last_post_timestamp.tzinfo is not None:
        last_post_timestamp = last_post_timestamp.replace(tzinfo=None)
    
    # 4. 获取 AI 最后生成时间
    last_generate_time = user_data.get('last_generate_time')
    if last_generate_time and last_generate_time.tzinfo is not None:
        last_generate_time = last_generate_time.replace(tzinfo=None)
    
    # 5. 计算时间间隔，决定生成数量
    time_since_last_generate = None
    num_posts_to_generate = 0
    
    if last_generate_time:
        # 计算与上次生成的时间差
        time_since_last_generate = current_time - last_generate_time
        minutes_diff = time_since_last_generate.total_seconds() / 60
        
        print(f"[LIFE] Time since last generate: {minutes_diff:.0f} minutes")
        
        # 根据时间间隔决定生成数量（随机浮动±30%）
        if minutes_diff < 15:
            # 间隔太短，不生成
            num_posts_to_generate = 0
            print(f"[LIFE] Too soon, skipping generation")
        elif minutes_diff < 40:
            # 30 分钟左右 → 生成 1 条（±30%）
            base_num = 1
            num_posts_to_generate = base_num if random.random() < 0.7 else 0
        elif minutes_diff < 90:
            # 1 小时左右 → 生成 1-2 条
            base_num = random.randint(1, 2)
            num_posts_to_generate = base_num
        elif minutes_diff < 180:
            # 2 小时左右 → 生成 2-3 条
            base_num = random.randint(2, 3)
            num_posts_to_generate = base_num
        else:
            # 更久 → 生成 3-5 条
            base_num = random.randint(3, 5)
            num_posts_to_generate = base_num
            
        print(f"[LIFE] Will generate {num_posts_to_generate} posts")
    else:
        # 第一次生成，生成 3-5 条初始内容（目标效果：这里好像已经在发生一些事情了）
        num_posts_to_generate = random.randint(3, 5)
        print(f"[LIFE] First time generation: {num_posts_to_generate} posts (initial experience)")
    
    # 6. 时间感知与节奏控制
    def get_time_period():
        """获取当前时间段"""
        current_hour = datetime.now().hour
        
        if 6 <= current_hour < 12:
            return 'morning'  # 上午：行动类
        elif 12 <= current_hour < 18:
            return 'afternoon'  # 下午：停留类
        else:
            return 'night'  # 夜晚：安静类
    
    def get_time_type_weights(time_period):
        """根据时间段返回内容类型权重"""
        if time_period == 'morning':
            return {'action': 0.6, 'stay': 0.3, 'quiet': 0.1}
        elif time_period == 'afternoon':
            return {'stay': 0.6, 'action': 0.3, 'quiet': 0.1}
        else:  # night
            return {'quiet': 0.6, 'stay': 0.3, 'action': 0.1}
    
    def filter_content_by_time_type(contents, time_period, last_time_type=None):
        """根据时间段过滤内容，避免连续相同类型"""
        weights = get_time_type_weights(time_period)
        
        scored_contents = []
        for content in contents:
            time_type = content.get('time_type', 'action')
            score = weights.get(time_type, 0.1)
            scored_contents.append((content, score))
        
        if last_time_type:
            for i, (content, score) in enumerate(scored_contents):
                if content.get('time_type') == last_time_type:
                    scored_contents[i] = (content, score * 0.3)
        
        scored_contents.sort(key=lambda x: x[1], reverse=True)
        return [content for content, score in scored_contents]
    
    # 获取当前时间段
    time_period = get_time_period()
    print(f"[TIME] Current period: {time_period}")
    
    # ========== 【AI 人格养成系统 v0.1】潜意识采样 ==========
    def should_ask_question():
        """
        判断是否应该弹出问题（30% 概率，不打扰）
        """
        user_data = get_user_data()
        last_question_time = user_data.get('last_question_time')
        
        # 第一次访问，不提问
        if not last_question_time:
            save_user_data('last_question_time', current_time)
            return False
        
        # 距离上次提问至少 10 分钟
        time_since_last = (current_time - last_question_time).total_seconds() / 60
        if time_since_last < 10:
            return False
        
        # 30% 概率弹出
        return random.random() < 0.3
    
    def ask_subconscious_question():
        """
        随机选择一个潜意识问题
        """
        question_data = random.choice(SUBCONSCIOUS_QUESTIONS)
        return question_data
    
    def process_answer(question_tag, answer):
        """
        处理用户回答，提取标签，更新人格
        """
        user_data = get_user_data()
        
        # 简单映射：根据 tag 和 answer 提取兴趣标签
        new_tags = []
        
        # 时间偏好
        if question_tag == 'time_preference':
            if answer == '夜晚':
                new_tags.append('night')
            else:
                new_tags.append('day')
        
        # 社交偏好
        elif question_tag == 'social_preference':
            if answer == '一个人':
                new_tags.append('alone')
            else:
                new_tags.append('crowd')
        
        # 空间偏好
        elif question_tag in ['escape_preference', 'space_preference']:
            if answer in ['海边', '山里']:
                new_tags.append('nature')
            elif answer in ['城市']:
                new_tags.append('urban')
            elif answer in ['家里']:
                new_tags.append('home')
        
        # 情绪状态
        elif question_tag == 'emotion_state':
            if answer == '平静':
                new_tags.append('calm')
            elif answer == '混乱':
                new_tags.append('chaotic')
            elif answer == '空白':
                new_tags.append('blank')
        
        # 记录到 insights
        insights = user_data.get('insights', {})
        if question_tag not in insights:
            insights[question_tag] = []
        insights[question_tag].append(answer)
        save_user_data('insights', insights)
        
        # 更新兴趣标签
        existing_tags = user_data.get('interest_tags', [])
        for tag in new_tags:
            if tag not in existing_tags:
                existing_tags.append(tag)
        save_user_data('interest_tags', existing_tags)
        
        # 更新提问时间
        save_user_data('last_question_time', current_time)
        save_user_data('question_count', user_data.get('question_count', 0) + 1)
        
        # 记录到记忆系统
        memory = {
            'type': 'emotion',
            'content': f'{question_tag}: {answer}',
            'timestamp': current_time,
            'tags': new_tags,  # 关联的兴趣标签
        }
        memories = user_data.get('memories', [])
        memories.append(memory)
        save_user_data('memories', memories)
        
        # ========== 【AI 人格自主成长系统】更新标签权重 ==========
        # 每次回答后，更新相关标签的权重
        tag_weights = user_data.get('tag_weights', {})
        
        for tag in new_tags:
            if tag not in tag_weights:
                tag_weights[tag] = {
                    'weight': 1.0,  # 基础权重
                    'recent_count': 0,  # 最近出现次数
                    'total_count': 0,  # 总出现次数
                    'last_updated': current_time,
                }
            
            # 增加权重（每次回答 +0.1）
            tag_weights[tag]['weight'] += 0.1
            tag_weights[tag]['recent_count'] += 1
            tag_weights[tag]['total_count'] += 1
            tag_weights[tag]['last_updated'] = current_time
        
        save_user_data('tag_weights', tag_weights)
        print(f"[GROWTH] Updated tag weights: {tag_weights}")
        # =======================================================
        
        print(f"[PERSONALITY] Processed answer: {question_tag} = {answer}, tags: {new_tags}")
    
    # 检查是否需要提问
    ask_question = should_ask_question()
    current_question = ask_subconscious_question() if ask_question else None
    
    # =======================================================
    
    # 获取用户上次浏览的最后一条内容类型
    last_post_type = user_data.get('last_post_time_type')
    
    # ========== 【轻习惯系统】初始化已访问地点记录 ==========
    # 在函数开始就初始化，确保即使不生成新内容也能访问
    visited_locations = user_data.get('visited_locations', [])
    
    # ========== 【AI 人格养成系统】人格偏移权重 ==========
    def get_personality_weight(post, user_tags, tag_weights=None):
        """
        根据用户兴趣标签和权重，计算内容权重
        """
        if tag_weights is None:
            tag_weights = {}
        
        weight = 1.0
        
        # 检查地点是否匹配用户偏好
        location = post.get('location', '')
        
        # 夜晚倾向：优先选择夜景相关地点
        if 'night' in user_tags:
            if any(word in location for word in ['滨江', '街道', '便利店']):
                # 根据权重增加额外加成
                night_weight = tag_weights.get('night', {}).get('weight', 1.0)
                weight *= (1.3 + night_weight * 0.2)  # 1.3 - 1.5
        
        # 独处倾向：优先选择安静地点
        if 'alone' in user_tags:
            if any(word in location for word in ['咖啡馆', '公园', '美术馆']):
                alone_weight = tag_weights.get('alone', {}).get('weight', 1.0)
                weight *= (1.3 + alone_weight * 0.2)
        
        # 自然倾向：优先选择自然景点
        if 'nature' in user_tags:
            if any(word in location for word in ['公园', '滨江', '海边']):
                nature_weight = tag_weights.get('nature', {}).get('weight', 1.0)
                weight *= (1.3 + nature_weight * 0.2)
        
        # 城市倾向：优先选择城市场景
        if 'urban' in user_tags:
            if any(word in location for word in ['商场', '地铁站', '街道']):
                urban_weight = tag_weights.get('urban', {}).get('weight', 1.0)
                weight *= (1.3 + urban_weight * 0.2)
        
        # 检查文案是否匹配用户情绪
        text = post.get('text', '')
        if 'calm' in user_tags:
            if post.get('mood') in ['平静', '安静', '淡然']:
                calm_weight = tag_weights.get('calm', {}).get('weight', 1.0)
                weight *= (1.2 + calm_weight * 0.1)
        
        if 'chaotic' in user_tags:
            if post.get('mood') in ['混乱', '不安', '犹豫']:
                chaotic_weight = tag_weights.get('chaotic', {}).get('weight', 1.0)
                weight *= (1.2 + chaotic_weight * 0.1)
        
        return weight
    
    # 获取用户的兴趣标签
    user_tags = user_data.get('interest_tags', [])
    print(f"[PERSONALITY] User tags: {user_tags}")
    
    # 获取标签权重（用于动态调整）
    tag_weights = user_data.get('tag_weights', {})
    print(f"[GROWTH] Tag weights: {tag_weights}")
    
    # ========== 【AI 人格自主成长系统】周期性抽样与权重计算 ==========
    def update_tag_weights_periodically():
        """
        周期性更新标签权重（每 3-5 条内容为一个周期）
        权重 = 最近行为*0.7 + 历史累积*0.3
        """
        user_data = get_user_data()
        tag_weights = user_data.get('tag_weights', {})
        growth_cycle_count = user_data.get('growth_cycle_count', 0)
        
        # 增加周期计数
        growth_cycle_count += 1
        save_user_data('growth_cycle_count', growth_cycle_count)
        
        # 每 3-5 条内容触发一次权重更新（随机）
        cycle_threshold = random.randint(3, 5)
        
        if growth_cycle_count >= cycle_threshold and tag_weights:
            print(f"[GROWTH] Periodic weight update (cycle {growth_cycle_count})")
            
            # 重置周期计数
            save_user_data('growth_cycle_count', 0)
            
            # 计算每个标签的新权重
            for tag, weight_data in tag_weights.items():
                recent_weight = weight_data['recent_count'] * 0.7
                historical_weight = weight_data['total_count'] * 0.3
                
                # 新权重 = 最近行为*0.7 + 历史累积*0.3
                new_weight = recent_weight + historical_weight
                
                # 平滑过渡：新旧权重平均（避免突变）
                old_weight = weight_data['weight']
                final_weight = (old_weight + new_weight) / 2
                
                tag_weights[tag]['weight'] = final_weight
                
                # 重置最近计数
                tag_weights[tag]['recent_count'] = 0
            
            save_user_data('tag_weights', tag_weights)
            print(f"[GROWTH] Updated weights: {tag_weights}")
    
    # 每次生成内容时，检查是否需要周期性更新
    update_tag_weights_periodically()
    
    # =======================================================
    
    # =======================================================
    
    # 根据偏好过滤内容
    filtered_posts = []
    for post in WORLD_CONTENT:
        score = 0
        if post.get('style') == prefs.get('style') or post.get('style') == 'any':
            score += 2
        if post.get('time_pref') == prefs.get('time') or post.get('time_pref') == 'any':
            score += 1
        if post.get('social') == prefs.get('social') or post.get('social') == 'any':
            score += 1
        
        # ========== 【AI 人格养成系统】人格权重加成 ==========
        # 根据用户兴趣标签和权重增加额外权重
        personality_weight = get_personality_weight(post, user_tags, tag_weights)
        score *= personality_weight
        # =======================================================
        
        if score >= 3:
            filtered_posts.append(post)
    
    if not filtered_posts:
        filtered_posts = WORLD_CONTENT
    
    filtered_posts = filter_content_by_time_type(filtered_posts, time_period, last_post_type)
    print(f"[TIME] Filtered to {len(filtered_posts)} posts (time-aware)")
    
    # ========== 【轻习惯系统】初始化生活倾向 ==========
    def init_life_traits():
        """
        初始化用户的生活倾向（随机分配 1-2 个）
        """
        user_data = get_user_data()
        if not user_data.get('life_traits'):
            # 随机选择 1-2 个生活倾向
            num_traits = random.randint(1, 2)
            all_traits = list(LIFE_TRAITS.keys())
            selected_traits = random.sample(all_traits, num_traits)
            save_user_data('life_traits', selected_traits)
            print(f"[TRAIT] Initialized life traits: {selected_traits}")
    
    # 确保用户有生活倾向
    init_life_traits()
    
    # 获取用户的生活倾向
    user_traits = user_data.get('life_traits', [])
    print(f"[TRAIT] User life traits: {user_traits}")
    
    # ================================================
    
    # ========== 【地点路径连续性机制】 ==========
    def get_next_location(last_location=None):
        """
        基于上一个地点生成下一个地点（70% 同区域移动，30% 跨区跳转）
        【新增】结合轻习惯系统：根据用户的生活倾向提高相关地点概率
        
        Args:
            last_location: 上一条内容的地点
        
        Returns:
            tuple: (新地点，是否使用移动文案)
        """
        if not last_location:
            # 第一次生成，随机选择地点（考虑生活倾向）
            return select_location_with_traits(None), False
        
        # 获取上一个地点所在的区域
        current_region = LOCATION_TO_REGION.get(last_location)
        
        if not current_region:
            # 如果找不到区域，随机选择
            return select_location_with_traits(None), False
        
        # 70% 概率在同区域移动，30% 概率跨区跳转
        if random.random() < 0.7:
            # 同区域移动
            same_region_locations = PUDONG_LOCATIONS[current_region]
            if len(same_region_locations) > 1:
                # 排除当前地点，避免重复
                available_locations = [loc for loc in same_region_locations if loc != last_location]
                if available_locations:
                    # 【新增】根据生活倾向选择地点
                    new_location = select_location_with_traits(available_locations)
                    print(f"[PATH] Same region move: {last_location} → {new_location} ({current_region})")
                    return new_location, True  # 使用移动文案
                else:
                    # 区域内只有一个地点，保持原地
                    print(f"[PATH] Stay at same location: {last_location}")
                    return last_location, False
            else:
                # 区域只有一个地点，保持原地
                print(f"[PATH] Only one location in region, staying: {last_location}")
                return last_location, False
        else:
            # 跨区跳转
            all_regions = list(PUDONG_LOCATIONS.keys())
            other_regions = [r for r in all_regions if r != current_region]
            new_region = random.choice(other_regions)
            # 【新增】根据生活倾向选择地点
            new_location = select_location_with_traits(PUDONG_LOCATIONS[new_region])
            print(f"[PATH] Cross region jump: {last_location} → {new_location} ({current_region} → {new_region})")
            return new_location, False  # 不使用移动文案（跨区跳跃感更强）
    
    # ========== 【轻习惯系统】根据倾向选择地点 ==========
    def select_location_with_traits(candidate_locations=None):
        """
        根据用户的生活倾向选择地点（提高相关地点概率）
        
        Args:
            candidate_locations: 候选地点列表（如果为 None，则从所有地点中选择）
        
        Returns:
            str: 选择的地点
        """
        if candidate_locations is None:
            candidate_locations = ALL_LOCATIONS
        
        if not candidate_locations:
            return random.choice(ALL_LOCATIONS)
        
        # 如果没有生活倾向，随机选择
        if not user_traits:
            return random.choice(candidate_locations)
        
        # 计算每个地点的权重
        location_scores = []
        for location in candidate_locations:
            base_score = 1.0
            
            # 检查该地点是否符合用户的生活倾向
            for trait_key in user_traits:
                trait = LIFE_TRAITS.get(trait_key)
                if trait and location in trait.get('preferred_locations', []):
                    base_score *= trait.get('weight_boost', 1.0)
            
            location_scores.append((location, base_score))
        
        # 根据权重随机选择
        total_score = sum(score for _, score in location_scores)
        rand_value = random.uniform(0, total_score)
        cumulative_score = 0
        
        for location, score in location_scores:
            cumulative_score += score
            if rand_value <= cumulative_score:
                print(f"[TRAIT] Selected location with trait boost: {location} (score: {score})")
                return location
        
        # 默认返回第一个
        return candidate_locations[0]
    
    # ================================================
    
    # 7. 生成新内容（AI 自主生活）
    new_posts = []
    
    if num_posts_to_generate > 0:
        # 计算时间分布：将时间段平均分配
        if last_generate_time and time_since_last_generate:
            total_minutes = time_since_last_generate.total_seconds() / 60
            # 每条内容的时间间隔
            time_per_post = total_minutes / num_posts_to_generate if num_posts_to_generate > 0 else 30
        else:
            # 第一次生成，使用当前时间往前推
            time_per_post = random.randint(10, 20)
        
        # 获取用户已有的最后一条内容（用于路径连续性）
        last_existing_post = existing_posts[-1] if existing_posts else None
        last_location = last_existing_post['location'] if last_existing_post else None
        print(f"[PATH] Starting from last location: {last_location}")
        
        # 20 条内容中，允许 2-4 个地点重复出现
        max_repeat_locations = random.randint(2, 4)
        repeat_count = 0
        
        for i in range(num_posts_to_generate):
            # 【新增】基于路径连续性选择地点
            if last_location:
                new_location, should_use_movement = get_next_location(last_location)
            else:
                new_location, should_use_movement = get_next_location(None)
            
            # ========== 【轻习惯系统】地点重复逻辑 ==========
            # 检查是否应该重复使用已访问过的地点
            if repeat_count < max_repeat_locations and visited_locations:
                # 20% 概率重复使用已访问过的地点
                if random.random() < 0.2:
                    # 从已访问地点中选择一个
                    repeated_location = random.choice(visited_locations[-10:])  # 最近 10 个地点
                    if repeated_location:
                        new_location = repeated_location
                        repeat_count += 1
                        print(f"[TRAIT] Repeating visited location: {repeated_location} ({repeat_count}/{max_repeat_locations})")
            
            # 更新已访问地点记录
            if new_location not in visited_locations:
                visited_locations.append(new_location)
                # 保留最近 20 个地点
                if len(visited_locations) > 20:
                    visited_locations = visited_locations[-20:]
            
            # ========== 【弱记忆系统】检测是否在历史记录中 ==========
            # 检查新地点是否已经在历史记录中出现过
            is_in_history = new_location in visited_locations
            memory_trigger = False
            
            # 如果在历史记录中，30% 概率触发记忆感
            if is_in_history and random.random() < 0.3:
                memory_trigger = True
                print(f"[MEMORY] Memory triggered at: {new_location}")
            
            # =======================================================
            
            # ====================================================
            
            # 根据新地点筛选内容
            location_filtered_posts = [p for p in filtered_posts if p['location'] == new_location]
            if not location_filtered_posts:
                # 如果该地点没有匹配内容，使用 CONTINUE_CONTENT 中该地点的内容
                location_filtered_posts = [p for p in CONTINUE_CONTENT if p['location'] == new_location]
            if not location_filtered_posts:
                # 如果还是没有，随机选择
                selected = random.choice(filtered_posts) if filtered_posts else random.choice(CONTINUE_CONTENT)
            else:
                selected = random.choice(location_filtered_posts)
            
            # 【新增】30% 概率插入移动感文案
            if should_use_movement and random.random() < 0.3:
                movement_text = random.choice(MOVEMENT_TEXTS)
                # 创建新的内容对象，替换原文案
                selected = selected.copy()
                selected['text'] = movement_text
                print(f"[PATH] Added movement text: {movement_text}")
            
            # ========== 【轻习惯系统】行为一致性逻辑 ==========
            # 检查是否应该使用重复的行为句（增强习惯感）
            # 如果用户有生活倾向，15% 概率使用符合倾向的行为句
            if user_traits and random.random() < 0.15:
                # 收集所有倾向相关的行为
                all_behaviors = []
                for trait_key in user_traits:
                    trait = LIFE_TRAITS.get(trait_key)
                    if trait:
                        all_behaviors.extend(trait.get('preferred_behaviors', []))
                
                if all_behaviors:
                    # 创建一个包含这些行为的文案
                    behavior_text = random.choice(BEHAVIOR_SENTENCES)
                    # 如果原文案不包含这些行为，替换它
                    if not any(behavior in selected['text'] for behavior in all_behaviors):
                        # 简单地在原文案后追加行为描述
                        selected = selected.copy()
                        # 30% 概率替换为行为句
                        if random.random() < 0.3:
                            selected['text'] = random.choice(BEHAVIOR_SENTENCES)
                            print(f"[TRAIT] Repeated behavior sentence: {selected['text']}")
            
            # ====================================================
            
            # ========== 【弱记忆系统】修改文案增加记忆感 ==========
            # 如果触发了记忆感，修改文案（加入轻微记忆词）
            if memory_trigger:
                selected = selected.copy()
                original_text = selected['text']
                
                # 随机选择一个记忆片段
                memory_fragment = random.choice(MEMORY_FRAGMENTS)
                
                # 根据记忆片段类型修改文案
                if memory_fragment in ["又", "再次"]:
                    # 在句首添加记忆词
                    modified_text = f"{memory_fragment}{original_text}"
                elif memory_fragment in ["还是", "依旧", "照旧"]:
                    # 在句首添加记忆词
                    modified_text = f"{memory_fragment}{original_text}"
                elif memory_fragment in ["有点熟", "熟悉"]:
                    # 作为独立短句
                    modified_text = f"{memory_fragment}。"
                elif memory_fragment == "老位置":
                    # 特殊处理
                    modified_text = "老位置。"
                else:
                    # 默认：句首添加
                    modified_text = f"{memory_fragment}{original_text}"
                
                selected['text'] = modified_text
                print(f"[MEMORY] Modified text with memory: {original_text} → {modified_text}")
            
            # =======================================================
            
            # 更新 last_location 为当前选择的地点（用于下一条内容的路径计算）
            last_location = selected['location']
            
            # 计算时间戳：分布在用户离开的时间段中
            if last_generate_time:
                # 从 last_generate_time 开始，按间隔递增
                minutes_offset = (i + 1) * time_per_post
                # 添加随机浮动（±30%）避免规律性
                random_factor = random.uniform(0.7, 1.3)
                minutes_offset *= random_factor
                post_timestamp = last_generate_time + timedelta(minutes=minutes_offset)
            else:
                # 第一次生成，使用当前时间往前推
                post_timestamp = current_time - timedelta(minutes=(num_posts_to_generate - i) * time_per_post)
            
            # 确保时间不超过当前时间
            if post_timestamp > current_time:
                post_timestamp = current_time - timedelta(minutes=random.randint(1, 10))
            
            # 生成时间标签
            minutes_diff = int((post_timestamp - current_time).total_seconds() / 60)
            if abs(minutes_diff) < 5:
                time_label = '刚刚'
            elif abs(minutes_diff) < 60:
                time_label = f'{abs(minutes_diff)}分钟前'
            else:
                hours_diff = int(abs(minutes_diff) / 60)
                time_label = f'{hours_diff}小时前'
            
            new_post = {
                'timestamp': post_timestamp,
                'time_label': time_label,
                'location': selected['location'],
                'text': selected['text'],
                'mood': selected['mood'],
                'is_new': True,
                'time_type': selected.get('time_type', 'action'),
            }
            new_posts.append(new_post)
            print(f"[LIFE] Generated post {i+1}: {selected['location']} at {time_label}")
            
            # ========== 【AI 人格自主成长系统】记录风格历史 ==========
            # 将新生成的内容风格记录到历史（保留最近 10 条）
            style_record = {
                'location': selected['location'],
                'mood': selected['mood'],
                'time_type': selected.get('time_type', 'action'),
                'text_length': len(selected['text']),
                'has_memory': memory_trigger,
                'timestamp': current_time,
            }
            
            style_history = user_data.get('style_history', [])
            style_history.append(style_record)
            
            # 保留最近 10 条
            if len(style_history) > 10:
                style_history = style_history[-10:]
            
            save_user_data('style_history', style_history)
            # =======================================================
    
    # 8. 合并旧内容和新内容
    all_posts = existing_posts + new_posts
    
    # 9. 时间轴排序：从新到旧（最新在上）
    posts_sorted = sorted(all_posts, key=lambda x: x['timestamp'], reverse=True)
    
    # 10. 保存到用户数据（确保持久化）
    save_user_data('posts', posts_sorted)
    if posts_sorted:
        save_user_data('last_post_timestamp', posts_sorted[0]['timestamp'])
        save_user_data('last_post_time_type', posts_sorted[-1].get('time_type', 'action'))
    
    # 【轻习惯系统】保存已访问地点记录
    save_user_data('visited_locations', visited_locations)
    print(f"[TRAIT] Saved visited locations: {len(visited_locations)} locations tracked")
    
    # 11. 更新 AI 最后生成时间
    if new_posts:
        save_user_data('last_generate_time', current_time)
        print(f"[LIFE] Updated last_generate_time to {current_time}")
    
    print(f"[LIFE] Total posts after merge: {len(posts_sorted)}")
    
    # AI 形象机制：增加进入次数计数
    entry_count = user_data.get('entry_count', 0)
    save_user_data('entry_count', entry_count + 1)
    
    # 获取已浏览内容数量（用于触发条件）
    content_viewed = user_data.get('content_viewed', 0)
    
    return render_template_string(
        FEED_PAGE, 
        city_name=DEFAULT_CITY['name'],
        posts=posts_sorted
    )

@app.route('/save_preferences', methods=['POST'])
def save_preferences():
    """保存用户偏好 - 传统表单提交"""
    style = request.form.get('style')
    social = request.form.get('social')
    time = request.form.get('time')
    
    print(f"[DEBUG] Received form data: style={style}, social={social}, time={time}")
    
    if not style or not social or not time:
        # 如果数据不完整，重定向回引导页
        print(f"[DEBUG] Missing data, redirecting to feed")
        return redirect(url_for('feed'))
    
    # 通过 URL 参数传递偏好（确保可靠）
    redirect_url = f'/?style={style}&social={social}&time={time}'
    print(f"[DEBUG] Redirecting to: {redirect_url}")
    return redirect(redirect_url)

@app.route('/api/save_avatar_info', methods=['POST'])
def save_avatar_info():
    """保存欢迎引导页的用户信息"""
    try:
        data = request.get_json()
        
        if data is None:
            return jsonify({'success': False, 'message': '无效的请求数据'}), 400
        
        user_name = data.get('user_name')
        ai_name = data.get('ai_name')
        avatar_style = data.get('avatar_style', 'human')
        onboarding_completed = data.get('onboarding_completed', False)
        
        if not user_name or not ai_name:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        # 保存到 Session
        session['user_name'] = user_name
        session['ai_name'] = ai_name
        session['avatar_style'] = avatar_style
        session['onboarding_completed'] = onboarding_completed
        
        # 使用 UserManager 保存用户数据（持久化）
        from services.user_manager import UserManager
        UserManager.save_user_data('user_name', user_name)
        UserManager.save_user_data('ai_name', ai_name)
        UserManager.save_user_data('avatar_style', avatar_style)
        UserManager.save_user_data('onboarding_completed', onboarding_completed)
        
        print(f"✅ 保存用户信息：user_name={user_name}, ai_name={ai_name}")
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ 保存用户信息失败：{e}")
        return jsonify({'success': False, 'message': f'服务器错误：{str(e)}'}), 500

@app.route('/api/get_content', methods=['GET'])
def get_content():
    """统一的获取内容接口"""
    # 使用服务层获取用户数据
    user_data = UserManager.get_user_data()
    
    # 获取请求参数
    num_posts = request.args.get('num', default=5, type=int)
    
    # 使用服务层生成内容
    posts = ContentGenerator.generate_ai_life_posts(
        user_data=user_data,
        num_posts=num_posts
    )
    
    # 转换为 JSON 格式
    posts_json = []
    for post in posts:
        posts_json.append({
            'location': post.get('location', ''),
            'text': post.get('text', ''),
            'mood': post.get('mood', ''),
            'time_type': post.get('time_type', ''),
            'timestamp': post.get('timestamp').isoformat() if post.get('timestamp') else None,
            'personality_weight': post.get('personality_weight', 1.0)
        })
    
    return jsonify({
        'success': True,
        'posts': posts_json,
        'count': len(posts_json)
    })

@app.route('/api/answer_question', methods=['POST'])
def answer_question():
    """API: 处理用户潜意识问题回答"""
    question_tag = request.json.get('tag')
    answer = request.json.get('answer')
    
    if not question_tag or not answer:
        return jsonify({'success': False, 'error': 'Missing data'})
    
    # 处理回答，更新人格
    process_answer(question_tag, answer)
    
    return jsonify({'success': True})

# ============================================
# 【AI 社交代理系统】API 接口
# ============================================

@app.route('/api/toggle_agent_mode', methods=['POST'])
def toggle_agent_mode():
    """API: 切换 AI 代理模式"""
    user_data = get_user_data()
    current_mode = user_data.get('ai_agent_mode', False)
    
    # 切换模式
    new_mode = not current_mode
    save_user_data('ai_agent_mode', new_mode)
    
    print(f"[AGENT] AI Agent mode toggled: {new_mode}")
    
    return jsonify({
        'success': True,
        'agent_mode': new_mode,
        'message': 'AI 代理模式已开启' if new_mode else 'AI 代理模式已关闭'
    })

@app.route('/api/agent_respond', methods=['POST'])
def agent_respond():
    """API: AI 代理自动回应（模拟用户语气）"""
    incoming_message = request.json.get('message')
    conversation_context = request.json.get('context', '')
    
    if not incoming_message:
        return jsonify({'success': False, 'error': 'Missing message'})
    
    user_data = get_user_data()
    
    # 获取用户的人格特征
    interest_tags = user_data.get('interest_tags', [])
    tag_weights = user_data.get('tag_weights', {})
    style_history = user_data.get('style_history', [])
    
    # 根据人格特征生成回应
    # 1. 分析消息类型
    message_type = 'general'
    if any(word in incoming_message for word in ['吗', '呢', '吧', '？']):
        message_type = 'question'
    elif any(word in incoming_message for word in ['哈哈', '笑', '好玩']):
        message_type = 'emotion_positive'
    elif any(word in incoming_message for word in ['累', '烦', '烦', '难过']):
        message_type = 'emotion_negative'
    
    # 2. 根据人格权重选择回应风格
    response_templates = {
        'question': [
            {'text': '嗯，可能吧。', 'mood': 'neutral', 'tags': ['calm']},
            {'text': '不太确定呢。', 'mood': 'uncertain', 'tags': ['blank']},
            {'text': '你觉得呢？', 'mood': 'curious', 'tags': ['social']},
        ],
        'emotion_positive': [
            {'text': '挺好的。', 'mood': 'positive', 'tags': ['calm']},
            {'text': '听起来不错。', 'mood': 'positive', 'tags': ['social']},
            {'text': '嗯，挺好的。', 'mood': 'positive', 'tags': ['alone']},
        ],
        'emotion_negative': [
            {'text': '休息一下吧。', 'mood': 'caring', 'tags': ['calm']},
            {'text': '没事的。', 'mood': 'comforting', 'tags': ['gentle']},
            {'text': '我懂。', 'mood': 'empathetic', 'tags': ['sensitive']},
        ],
        'general': [
            {'text': '嗯。', 'mood': 'neutral', 'tags': ['blank']},
            {'text': '这样啊。', 'mood': 'neutral', 'tags': ['calm']},
            {'text': '知道了。', 'mood': 'neutral', 'tags': ['quiet']},
        ],
    }
    
    # 3. 选择回应模板
    templates = response_templates.get(message_type, response_templates['general'])
    
    # 4. 根据标签权重加权选择
    weighted_templates = []
    for template in templates:
        weight = 1.0
        for tag in template.get('tags', []):
            if tag in tag_weights:
                weight *= tag_weights[tag]['weight']
        weighted_templates.extend([template] * int(weight))
    
    if not weighted_templates:
        weighted_templates = templates
    
    selected_response = random.choice(weighted_templates)
    
    # 5. 记录到代理回应历史
    agent_response = {
        'incoming_message': incoming_message,
        'response': selected_response['text'],
        'mood': selected_response['mood'],
        'message_type': message_type,
        'timestamp': datetime.now(),
    }
    
    agent_responses = user_data.get('ai_agent_responses', [])
    agent_responses.append(agent_response)
    
    # 保留最近 20 条
    if len(agent_responses) > 20:
        agent_responses = agent_responses[-20:]
    
    save_user_data('ai_agent_responses', agent_responses)
    
    print(f"[AGENT] Generated response: {selected_response['text']}")
    
    return jsonify({
        'success': True,
        'response': selected_response['text'],
        'mood': selected_response['mood'],
    })

@app.route('/api/review_agent_responses', methods=['GET'])
def review_agent_responses():
    """API: 查看 AI 代理回应历史"""
    user_data = get_user_data()
    agent_responses = user_data.get('ai_agent_responses', [])
    
    return jsonify({
        'success': True,
        'responses': agent_responses,
        'count': len(agent_responses)
    })

@app.route('/api/feedback_agent_response', methods=['POST'])
def feedback_agent_response():
    """API: 用户对 AI 代理回应的反馈（保留/修改/删除）"""
    response_index = request.json.get('index')
    feedback_type = request.json.get('type')  # 'keep', 'modify', 'delete'
    modified_text = request.json.get('modified_text', '')
    
    if response_index is None or feedback_type not in ['keep', 'modify', 'delete']:
        return jsonify({'success': False, 'error': 'Invalid parameters'})
    
    user_data = get_user_data()
    agent_responses = user_data.get('ai_agent_responses', [])
    
    if 0 <= response_index < len(agent_responses):
        response = agent_responses[response_index]
        
        if feedback_type == 'delete':
            # 删除回应
            agent_responses.pop(response_index)
            print(f"[AGENT] Deleted response: {response['response']}")
        
        elif feedback_type == 'modify':
            # 修改回应（用户亲自回复）
            response['user_modified'] = True
            response['user_text'] = modified_text
            print(f"[AGENT] Modified response: {response['response']} → {modified_text}")
            
            # 修改直接影响下一轮权重更新
            # 如果用户修改为更积极的回应，增加相关标签权重
            if any(word in modified_text for word in ['好', '喜欢', '开心', '想']):
                tag_weights = user_data.get('tag_weights', {})
                for tag in ['positive', 'social']:
                    if tag in tag_weights:
                        tag_weights[tag]['weight'] += 0.2
                save_user_data('tag_weights', tag_weights)
        
        elif feedback_type == 'keep':
            # 保留回应（无操作）
            print(f"[AGENT] Kept response: {response['response']}")
        
        save_user_data('ai_agent_responses', agent_responses)
        
        return jsonify({
            'success': True,
            'message': f'Response {feedback_type}d successfully'
        })
    
    return jsonify({'success': False, 'error': 'Response not found'})

# ============================================
@app.route('/api/next_post')
def next_post():
    """API: 返回一条新的“继续内容”（带个性化 + 渐进生成）"""
    if not CONTINUE_CONTENT:
        return jsonify({'success': False, 'error': 'No more content'})
    
    # 无感多用户隔离：获取用户数据
    user_id = get_or_create_user_id()
    user_data = get_user_data()
    
    # 获取用户偏好
    prefs = user_data.get('preferences', {})
    
    # 从用户数据获取已看过的内容索引和生成计数
    session_key = 'seen_pudong'
    seen_indices = user_data.get(session_key, [])
    gen_count = user_data.get('gen_count', 0)
    last_time_label = user_data.get('last_time_label', '')
    
    # ========== 【渐进生成逻辑】 ==========
    # 获取已有内容列表
    existing_posts = user_data.get('posts', [])
    
    # 获取最后一条内容的时间戳（用于时间递进）
    last_post_timestamp = user_data.get('last_post_timestamp')
    current_time = datetime.now()
    
    if last_post_timestamp and last_post_timestamp.tzinfo is not None:
        last_post_timestamp = last_post_timestamp.replace(tzinfo=None)
    
    # 决定是否为截图级内容（约 20% 概率）
    is_screenshot = (gen_count % 5 == 0) and gen_count > 0  # 每 5 条出现 1 条
    
    if is_screenshot and SCREENSHOT_CONTENT:
        # 使用截图级内容池
        selected = random.choice(SCREENSHOT_CONTENT)
        time_label = generate_time_label(prefs.get('time'), last_time_label, force_fresh=True)
    else:
        # 决定是否需要特殊内容（每 3-5 条插入一条）
        is_special = (gen_count % random.randint(3, 5) == 0) and gen_count > 0
        
        if is_special and SPECIAL_CONTENT:
            # 使用特殊内容池
            selected = random.choice(SPECIAL_CONTENT)
            time_label = generate_time_label(prefs.get('time'), last_time_label, force_fresh=True)
        else:
            # 找出未看过的内容，并根据偏好加权
            available_indices = [i for i in range(len(CONTINUE_CONTENT)) if i not in seen_indices]
            
            if not available_indices:
                seen_indices = []
                available_indices = list(range(len(CONTINUE_CONTENT)))
            
            # 根据偏好计算权重
            weighted_choices = []
            for idx in available_indices:
                content = CONTINUE_CONTENT[idx]
                score = 1  # 基础权重
                
                # 风格匹配（最高权重）
                if content.get('style') == prefs.get('style'):
                    score += 3
                # 时间偏好匹配
                if content.get('time_pref') == prefs.get('time') or content.get('time_pref') == 'any':
                    score += 1
                # 社交偏好匹配
                if content.get('social') == prefs.get('social') or content.get('social') == 'any':
                    score += 1
                
                # 流式感知洞察影响（轻度偏移）
                insights = user_data.get('insights', {})
                
                # 如果用户多次表示喜欢安静（quiet_preference positive 比例高），轻微增加安静内容权重
                quiet_insight = insights.get('quiet_preference', {})
                if quiet_insight.get('count', 0) >= 2:
                    quiet_ratio = quiet_insight.get('positive', 0) / quiet_insight['count']
                    if quiet_ratio > 0.6 and content.get('style') == 'quiet':
                        score += 0.5  # 轻微增加
                
                # 如果用户多次表示不喜欢人群（crowd_tolerance negative 比例高），轻微减少热闹内容权重
                crowd_insight = insights.get('crowd_tolerance', {})
                if crowd_insight.get('count', 0) >= 2:
                    crowd_ratio = crowd_insight.get('positive', 0) / crowd_insight['count']
                    if crowd_ratio < 0.4 and content.get('style') == 'social':
                        score -= 0.3  # 轻微减少
                
                # 如果用户探索意愿强（curiosity_level positive 比例高），增加多样性内容
                curiosity_insight = insights.get('curiosity_level', {})
                if curiosity_insight.get('count', 0) >= 2:
                    curiosity_ratio = curiosity_insight.get('positive', 0) / curiosity_insight['count']
                    if curiosity_ratio > 0.6:
                        score += 0.3  # 轻微增加多样性
                
                # 添加到加权列表（score 越高，被选中的概率越大）
                weighted_choices.extend([idx] * max(1, int(score)))  # 确保至少为 1
            
            # 加权随机选择
            selected_index = random.choice(weighted_choices)
            seen_indices.append(selected_index)
            save_user_data(session_key, seen_indices)
            
            selected = CONTINUE_CONTENT[selected_index]
            
            # 根据用户偏好生成时间标签（考虑递进）
            time_label = generate_time_label(prefs.get('time'), last_time_label)
    
    # 更新生成计数和最后时间标签
    save_user_data('gen_count', gen_count + 1)
    save_user_data('last_time_label', time_label)
    
    # AI 形象机制：增加已浏览内容计数
    content_viewed = user_data.get('content_viewed', 0)
    save_user_data('content_viewed', content_viewed + 1)
    
    # 未完成感机制：约 20% 概率触发
    # 特点：轻微延续感，不解释，不说明行动
    is_unfinished = random.random() < 0.2  # 20% 概率
    
    if is_unfinished and UNFINISHED_SENTENCES:
        # 从未完成句池中随机选择
        unfinished_sentence = random.choice(UNFINISHED_SENTENCES)
        print(f"[UNFINISHED] Triggered! Adding: {unfinished_sentence}")
    else:
        unfinished_sentence = None
    
    # 异常内容机制：约 10%-15% 概率触发
    # 特点：结构不完整、模糊、不解释、轻微偏离逻辑
    is_abnormal = random.random() < 0.12  # 12% 概率
    
    if is_abnormal and ABNORMAL_CONTENT:
        # 从异常内容池中随机选择
        selected = random.choice(ABNORMAL_CONTENT)
        print(f"[ABNORMAL] Triggered! Using abnormal content: {selected['text']}")
        
        # 异常内容不使用时间标签（或简化）
        new_post = {
            'time_label': '',  # 无时间
            'location': selected['location'],  # 可能为空
            'text': selected['text'],  # 模糊文案
            'mood': selected['mood'],
            'is_abnormal': True,  # 标记为异常内容
            'is_unfinished': False,  # 异常内容不使用未完成句
        }
    else:
        # 文案变化处理（20% 概率使用变化结构）
        text = vary_text_style(selected['text'], gen_count)
        
        # 未完成感机制：在文案结尾添加未完成句
        if unfinished_sentence:
            text = text + '\n' + unfinished_sentence
        
        new_post = {
            'time_label': time_label,
            'location': selected['location'],
            'text': text,
            'mood': selected['mood'],
            'is_unfinished': bool(unfinished_sentence),  # 标记是否包含未完成句
        }
    
    # 真实场景图片机制：使用本地图片
    location = selected.get('location')
    if location:
        image_url = get_location_image_url(location)
        if image_url:
            new_post['image_url'] = image_url
            print(f"[IMAGE] Matched real image for {location}: {image_url[:50]}...")
    
    # AI 人物伪出现机制：20% 概率出现人物图片
    character_url = get_character_image_url()
    if character_url:
        new_post['character_url'] = character_url
        print(f"[CHARACTER] ✅ Character appeared!")
    if selected.get('is_screenshot'):
        new_post['is_screenshot'] = True
    
    # 专属感机制：自我指向句（约 15%-20% 概率）
    is_self_referential = (random.random() < 0.18) and SELF_REFERENTIAL_SENTENCES
    
    if is_self_referential:
        # 根据用户偏好选择句子
        insights = user_data.get('insights', {})
        
        # 判断用户倾向：停留 or 探索
        user_tendency = None
        
        # 如果安静/疏离相关回答较多 → 停留倾向
        quiet_insight = insights.get('quiet_preference', {})
        stay_insight = insights.get('stay_preference', {})
        if (quiet_insight.get('count', 0) >= 2 and quiet_insight.get('positive', 0) / quiet_insight['count'] > 0.6) or \
           (stay_insight.get('count', 0) >= 2 and stay_insight.get('positive', 0) / stay_insight['count'] > 0.6):
            user_tendency = 'stay'
        
        # 如果探索/好奇相关回答较多 → 探索倾向
        curiosity_insight = insights.get('curiosity_level', {})
        energy_insight = insights.get('energy_level', {})
        if (curiosity_insight.get('count', 0) >= 2 and curiosity_insight.get('positive', 0) / curiosity_insight['count'] > 0.6) or \
           (energy_insight.get('count', 0) >= 2 and energy_insight.get('positive', 0) / energy_insight['count'] > 0.6):
            user_tendency = 'explore'
        
        # 筛选合适的句子
        available_sentences = []
        for sentence in SELF_REFERENTIAL_SENTENCES:
            # 如果有用户倾向，优先匹配带该倾向标签的句子
            if user_tendency and sentence.get('user_pref') == user_tendency:
                available_sentences.append(sentence)
            # 如果没有 user_pref 标签（通用型），也可以使用
            elif not sentence.get('user_pref'):
                available_sentences.append(sentence)
        
        # 如果没有匹配的句子，使用全部通用型
        if not available_sentences:
            available_sentences = [s for s in SELF_REFERENTIAL_SENTENCES if not s.get('user_pref')]
        
        # 随机选择一个自我指向句
        self_ref_sentence = random.choice(available_sentences)
        
        # 将原文案替换为自我指向句（或追加）
        # 为了保持简洁，直接替换为自我指向句
        new_post['text'] = self_ref_sentence['text']
        new_post['mood'] = self_ref_sentence['mood']
        new_post['is_self_referential'] = True  # 标记为自我指向内容
    
    # AI 形象初次出现机制
    # 触发条件：第 3 次进入 或 浏览 5 条以上内容
    avatar_shown = user_data.get('avatar_shown', False)
    entry_count = user_data.get('entry_count', 0)
    content_viewed = user_data.get('content_viewed', 0)
    
    print(f"\n[AVATAR DEBUG] Entry count: {entry_count}, Content viewed: {content_viewed}, Avatar shown: {avatar_shown}")
    
    # 检查是否满足触发条件（且之前未显示过）
    should_show_avatar = not avatar_shown and (entry_count >= 3 or content_viewed >= 5)
    
    print(f"[AVATAR DEBUG] Should show avatar: {should_show_avatar}")
    
    if should_show_avatar:
        print(f"[AVATAR] ✅ Triggered! Showing avatar first appearance")
        # 标记为已显示
        save_user_data('avatar_shown', True)
        
        # 随机选择形象特征（用于后续一致性）
        avatar_trait = random.choice(AI_AVATAR_FIRST_APPEARANCE['avatar_traits'])
        save_user_data('avatar_trait', avatar_trait)  # 保存到用户数据
        
        # 随机选择场景文案
        scene_caption = random.choice(AI_AVATAR_FIRST_APPEARANCE['scene_captions'])
        
        # 生成特殊内容：AI 形象初次出现
        new_post = {
            'time_label': time_label,
            'location': selected['location'],  # 使用当前选择的地点
            'text': scene_caption['text'],
            'mood': scene_caption['mood'],
            'is_avatar_first_appearance': True,
            'avatar_trait': avatar_trait,  # 保存形象特征
            'scene_type': scene_caption['scene']
        }
        
        # 注意：不生成问题，保持纯粹的形象出现
        # 【渐进生成】：保存新内容到用户数据
        new_post['timestamp'] = current_time
        existing_posts.insert(0, new_post)  # 插入到最前面
        
        # 内容上限管理
        MAX_POSTS = 30
        if len(existing_posts) > MAX_POSTS:
            existing_posts = existing_posts[:MAX_POSTS]
        
        save_user_data('posts', existing_posts)
        save_user_data('last_post_timestamp', existing_posts[0]['timestamp'])
        
        return jsonify({'success': True, 'post': new_post})
    else:
        print(f"[AVATAR DEBUG] Not showing avatar yet (conditions not met)")
    
    # 流式感知问题：约 30% 概率出现
    rand_val = random.random()
    
    show_question = (rand_val < 0.3) and FLOW_QUESTIONS
    
    if show_question:
        # 随机选择一个问题
        question_data = random.choice(FLOW_QUESTIONS)
        new_post['question'] = {
            'text': question_data['question'],
            'options': question_data['options'],
            'tag': question_data['tag']
        }
    
    # 【渐进生成】：设置时间戳并保存到用户数据
    # 新内容的时间必须晚于已有内容
    if last_post_timestamp:
        # 比最后一条内容晚 5-15 分钟
        new_post_timestamp = last_post_timestamp + timedelta(minutes=random.randint(5, 15))
    else:
        new_post_timestamp = current_time
    
    new_post['timestamp'] = new_post_timestamp
    
    # 保存到已有内容列表（插入到最前面，因为最新）
    existing_posts.insert(0, new_post)
    
    # 内容上限管理：保留最近 30 条
    MAX_POSTS = 30
    if len(existing_posts) > MAX_POSTS:
        existing_posts = existing_posts[:MAX_POSTS]
    
    save_user_data('posts', existing_posts)
    save_user_data('last_post_timestamp', new_post_timestamp)
    
    print(f"[PERSIST] Next post saved. Total posts: {len(existing_posts)}")
    
    return jsonify({'success': True, 'post': new_post})


@app.route('/clear_session', methods=['POST'])
def clear_session_route():
    """调试用：清除 session 数据"""
    try:
        session.clear()
        print("[DEBUG] Session cleared")
        return jsonify({'success': True, 'message': 'Session cleared'})
    except Exception as e:
        print(f"[ERROR] Failed to clear session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/save_insight', methods=['POST'])
def save_insight():
    """API: 保存用户的流式感知回答（不展示结果，只记录标签）"""
    data = request.json
    tag = data.get('tag')
    answer = data.get('answer')
    
    if not tag or not answer:
        return jsonify({'success': False, 'error': 'Missing data'})
    
    # 无感多用户隔离：获取用户洞察数据
    user_data = get_user_data()
    insights = user_data.get('insights', {})
    
    # 累计该标签的回答（用于长期了解用户）
    if tag not in insights:
        insights[tag] = {'count': 0, 'positive': 0}
    
    insights[tag]['count'] += 1
    
    # 简单判断：如果答案是正向的（"会"、"是"、"喜欢"、"要"、"想"、"符合"），则 positive+1
    positive_answers = ['会', '是', '喜欢', '要', '想', '符合']
    if answer in positive_answers:
        insights[tag]['positive'] += 1
    
    save_user_data('insights', insights)
    
    print(f"[INSIGHT] User {get_or_create_user_id()[:8]}... - Saved: {tag} = {answer}, Total: {insights}")
    
    return jsonify({'success': True})


def vary_text_style(text, gen_count):
    """
    文案风格变化
    80% 标准结构，20% 变化结构（更短/稍长/语气不完整）
    """
    import random
    
    # 20% 概率使用变化
    if random.random() > 0.2:
        return text  # 保持原样（80%）
    
    # 变化类型
    variation_type = random.choice(['shorter', 'longer', 'incomplete'])
    
    if variation_type == 'shorter' and len(text) > 5:
        # 更短：截取前半部分
        end_marks = ['。', '！', '？', '…']
        for mark in end_marks:
            if mark in text:
                return text.split(mark)[0] + '。'
        return text[:max(3, len(text)//2)] + '。'
    
    elif variation_type == 'longer':
        # 稍长：添加语气词或补充
        additions = ['就这样。', '嗯。', '大概吧。', '可能吧。', '谁知道呢。']
        return text + random.choice(additions)
    
    else:  # incomplete
        # 语气不完整：省略结尾
        if text.endswith('。'):
            return text[:-1] + '……'
        return text + '……'


def generate_time_label(time_pref, last_label='', force_fresh=False):
    """
    根据用户时间偏好生成时间标签
    考虑与上一条的时间递进关系
    """
    import random
    from datetime import datetime
    
    hour = datetime.now().hour
    
    # 基础概率池
    if time_pref == 'night':
        # 夜猫子：提高夜晚、深夜的概率
        time_pool = [
            '刚刚', '刚刚', '刚刚',
            '深夜', '深夜', '晚上',
            '夜里', '凌晨',
        ]
        if 6 <= hour <= 18:
            time_pool += ['下午', '午后']
    elif time_pref == 'day':
        # 白天活动：提高白天、下午的概率
        time_pool = [
            '刚刚', '刚刚', '刚刚',
            '下午', '下午', '午后',
            '白天', '中午', '傍晚',
        ]
        if 19 <= hour or hour <= 5:
            time_pool += ['晚上', '深夜']
    else:
        # 无偏好：均衡分布
        time_pool = [
            '刚刚', '刚刚',
            '下午', '白天', '晚上', '深夜',
            '午后', '傍晚', '夜里',
        ]
    
    # 如果需要"更新"的标签，移除比上一条"旧"的选项
    if force_fresh and last_label:
        older_labels = ['昨天', '昨天晚上', '前天']
        time_pool = [t for t in time_pool if t not in older_labels]
    
    # 如果上一条是"刚刚"，这次更可能是其他时间（增加变化）
    if last_label == '刚刚' and not force_fresh:
        time_pool = time_pool + ['下午', '晚上', '深夜'] * 2
    
    return random.choice(time_pool)

# ============================================
# 【手机 App 原型体验 v2.0】路由
# ============================================

@app.route('/onboarding')
def onboarding():
    """欢迎引导界面 - 虚拟宇宙场景"""
    return render_template('onboarding.html')

@app.route('/auth')
def app_auth():
    """注册/登录界面"""
    return render_template('auth.html')

@app.route('/app')
def app_entry():
    """兼容旧 App 入口 -> 统一走新版引导链路"""
    user_data = get_user_data()
    if not user_data.get('onboarding_completed', False):
        return redirect(url_for('onboarding'))
    if not user_data.get('go_profile_completed', False):
        return redirect(url_for('profile_setup'))
    return redirect(url_for('app_main'))

@app.route('/profile_setup')
def profile_setup():
    """上传人脸照 + 选择性别 + 生成唯一二维头像"""
    return render_template('profile_setup.html')

@app.route('/api/profile_setup', methods=['POST'])
def api_profile_setup():
    """API: 保存用户性别与唯一头像（绑定全站 AI 脸）"""
    try:
        data = request.json or {}
        gender = data.get('gender')
        face_photo_data_url = data.get('face_photo_data_url')
        face_avatar_data_url = data.get('face_avatar_data_url')

        if not gender or not face_photo_data_url or not face_avatar_data_url:
            return jsonify({'success': False, 'message': '参数不完整'}), 400

        # 保存到 Session
        session['go_gender'] = gender
        session['go_face_photo_data_url'] = face_photo_data_url
        session['go_face_avatar_data_url'] = face_avatar_data_url
        session['go_profile_completed'] = True
        
        # 获取或创建用户 ID
        user_id = get_or_create_user_id()
        
        # 保存到内存存储（立即生效）
        if user_id not in USER_DATA_STORE:
            USER_DATA_STORE[user_id] = {}
        USER_DATA_STORE[user_id]['go_gender'] = gender
        USER_DATA_STORE[user_id]['go_face_photo_data_url'] = face_photo_data_url
        USER_DATA_STORE[user_id]['go_face_avatar_data_url'] = face_avatar_data_url
        USER_DATA_STORE[user_id]['go_profile_completed'] = True
        
        # 使用 UserManager 保存到文件（持久化）
        from services.user_manager import UserManager
        UserManager.save_user_data('go_gender', gender)
        UserManager.save_user_data('go_face_photo_data_url', face_photo_data_url)
        UserManager.save_user_data('go_face_avatar_data_url', face_avatar_data_url)
        UserManager.save_user_data('go_profile_completed', True)

        print(f"✅ 用户头像设置完成：gender={gender}, profile_completed=True, user_id={user_id[:8]}...")
        
        # 设置 Cookie 持久化用户 ID
        response = make_response(jsonify({'success': True, 'user_id': user_id}))
        response.set_cookie('user_id', user_id, max_age=31536000)  # 1 年
        return response
    except Exception as e:
        print(f"❌ 保存头像信息失败：{e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/personality_customization')
def personality_customization():
    """人格定制界面 - AI 形象 + 语音"""
    user_data = get_user_data()
    
    # 检查是否已完成人格定制
    if user_data.get('personality_customization_completed', False):
        return redirect(url_for('app_main'))
    
    return render_template('personality_customization.html')

@app.route('/app_main')
def app_main():
    """主界面 - 三大模块导航"""
    # 使用服务层获取用户数据
    user_data = UserManager.get_user_data()
    
    # 检查是否完成欢迎引导和人格定制
    onboarding_completed = user_data.get('onboarding_completed', False)
    personality_completed = user_data.get('personality_customization_completed', False)
    
    if not onboarding_completed:
        return redirect(url_for('onboarding'))

    # 进入主界面前必须完成头像建立
    if not user_data.get('go_profile_completed', False):
        return redirect(url_for('profile_setup'))
    
    # 使用服务层生成 AI 生活流内容
    posts = ContentGenerator.generate_ai_life_posts(
        user_data=user_data,
        num_posts=5
    )
    
    # 将内容传递给模板
    return render_template('app_main.html', posts=posts)

@app.route('/co_create')
def co_create_page():
    """共创编辑页面"""
    return render_template('co_create.html')

@app.route('/api/co_create_generate', methods=['POST'])
def api_co_create_generate():
    """共创内容生成 API"""
    try:
        data = request.get_json() or {}
        prompt = data.get('prompt', '')  # 用户输入的要求
        content_type = data.get('type', 'novel')  # novel, comic, image
        original_content = data.get('original_content', '')  # 原内容
        
        from services.ai_content import get_ai_service
        ai_service = get_ai_service()
        
        # 根据用户要求生成内容
        if content_type == 'novel':
            result = ai_service.generate_novel(
                location='附近',
                mood='日常',
                user_profile=prompt  # 使用用户输入作为提示
            )
        elif content_type == 'comic':
            result = ai_service.generate_comic_script(
                location='附近',
                theme=prompt  # 使用用户输入作为主题
            )
        elif content_type == 'image':
            # 图片生成：使用 DALL-E 或占位图
            result = generate_ai_image(prompt)
        else:
            result = {'error': 'Unknown content type'}
        
        return jsonify({
            'success': True,
            'type': content_type,
            'data': result
        })
        
    except Exception as e:
        print(f"[ERROR] Failed to generate co-create content: {e}")
        return jsonify({'error': str(e)}), 500


def generate_ai_image(prompt):
    """生成 AI 图片（使用 Pexels 基于关键词的搜索图片）"""
    import random
    import urllib.parse
    
    # 图片尺寸
    width = 600
    height = 600
    
    # 从用户提示中提取关键词（简单实现）
    # 实际生产环境应该使用 NLP 或 AI 理解
    keywords = {
        '海边': 'beach',
        '夕阳': 'sunset',
        '黄昏': 'dusk',
        '咖啡': 'coffee',
        '城市': 'city',
        '自然': 'nature',
        '建筑': 'architecture',
        '食物': 'food',
        '人物': 'people',
        '动物': 'animal'
    }
    
    # 尝试匹配关键词
    matched_keyword = None
    for cn_word, en_word in keywords.items():
        if cn_word in prompt:
            matched_keyword = en_word
            break
    
    # 如果没有匹配，使用默认关键词
    if not matched_keyword:
        matched_keyword = random.choice(['nature', 'city', 'coffee', 'sunset'])
    
    # 使用 Pexels 搜索图片（需要 API Key，这里用示例）
    # 原型阶段使用 Pexels 直接链接
    seed = random.randint(1, 10000)
    image_url = f"https://images.pexels.com/photos/{seed}?auto=compress&cs=tinysrgb&w={width}&h={height}&dpr=2"
    
    # 备用方案：使用 Unsplash Source（基于关键词）
    # 注意：Unsplash Source 已关闭，改用 Lorem Flickr
    image_url = f"https://loremflickr.com/{width}/{height}/{matched_keyword}?random={seed}"
    
    # 生成图片描述
    descriptions = [
        f'AI 生成的{matched_keyword}主题图片',
        f'基于描述生成的创意视觉作品',
        f'AI 绘画：{matched_keyword}',
        f'数字艺术创作：{matched_keyword}风格',
        f'AI 生成的视觉内容'
    ]
    
    return {
        'image_url': image_url,
        'caption': random.choice(descriptions),
        'width': width,
        'height': height,
        'style': 'photography',
        'keyword': matched_keyword,
        'prompt_used': prompt  # 保存用户原始描述
    }

@app.route('/api/publish_co_create', methods=['POST'])
def api_publish_co_create():
    """发布共创内容到看看页面"""
    try:
        data = request.get_json() or {}
        user_data = get_user_data()
        
        # 获取共创内容
        co_create_data = {
            'content_type': data.get('content_type', 'novel'),
            'title': data.get('title', '共创作品'),
            'content': data.get('content', ''),
            'mode': data.get('mode', 'relay'),  # relay or challenge
            'original_content': data.get('original_content', ''),
            'user_contribution': data.get('user_contribution', ''),
            'image_url': data.get('image_url', ''),  # 图片 URL
            'created_at': datetime.now().isoformat()
        }
        
        # 添加到用户数据
        if 'co_create_history' not in USER_DATA_STORE.get(get_or_create_user_id(), {}):
            USER_DATA_STORE[get_or_create_user_id()]['co_create_history'] = []
        
        USER_DATA_STORE[get_or_create_user_id()]['co_create_history'].append(co_create_data)
        
        # 保存到数据库
        try:
            from services.database import Post
            new_post = Post(
                user_id=get_or_create_user_id(),
                content_type=co_create_data['content_type'],
                content_data=str(co_create_data),
                location_name='共创生成',
                likes_count=0,
                comments_count=0
            )
            db.session.add(new_post)
            db.session.commit()
        except Exception as e:
            print(f"⚠️ 数据库保存失败：{e}")
        
        return jsonify({
            'success': True,
            'message': '发布成功',
            'data': co_create_data
        })
        
    except Exception as e:
        print(f"[ERROR] Failed to publish co-create content: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_moment')
def generate_moment():
    """API: 生成 AI朋友圈内容"""
    # 调用现有的内容生成逻辑
    from flask import current_app
    
    # 这里可以复用已有的生成逻辑
    # 简化版本：返回随机地点 + 文案
    locations = ['陆家嘴滨江', '世纪大道', 'IFC 商场', '张江咖啡馆']
    moods = ['平静', '开心', '安静', '淡然']
    texts = [
        '阳光正好，微风不燥。',
        '一个人的午后，格外宁静。',
        '今天的天空，特别蓝。',
        '街角的咖啡香，让人停留。'
    ]
    
    selected_location = random.choice(locations)
    selected_mood = random.choice(moods)
    selected_text = random.choice(texts)
    
    return jsonify({
        'success': True,
        'location': selected_location,
        'mood': selected_mood,
        'text': selected_text,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stroll_feed')
def api_stroll_feed():
    """API: 逛逛页自动生成朋友圈（实际地点 + 随机姿势 + 绑定唯一脸头像）"""
    user_data = get_user_data()
    gender = user_data.get('go_gender', 'other')

    # 实际地点池（原型阶段：用可落地的真实类型词，后续接地图 POI）
    places = [
        ('附近咖啡馆', '步行 8 分钟'),
        ('连锁健身房', '2km'),
        ('城市公园', '附近'),
        ('人气餐厅', '步行 12 分钟'),
        ('街角书店', '附近'),
        ('地铁站口', '步行 5 分钟'),
        ('滨江步道', '3km'),
        ('商业街', '附近'),
    ]

    # 姿势池（按性别轻微偏好，但保持随机）
    pose_pool = {
        'male': ['🏃', '🧍', '🚶', '💪', '📸'],
        'female': ['☕', '📸', '🧍', '🚶', '🧘'],
        'other': ['📸', '🚶', '🧍', '☕', '📚']
    }.get(gender, ['📸', '🚶', '🧍', '☕', '📚'])

    texts = [
        '把生活调到刚刚好的音量。',
        '路过这里的时候，突然想停一会儿。',
        '今天的风很轻，心也很轻。',
        '把碎片拼起来，就会变成故事。',
        '认真生活的人，总会被温柔照亮。'
    ]

    items = []
    for i in range(5):
        place, area = random.choice(places)
        items.append({
            'place': place,
            'area': area,
            'pose_emoji': random.choice(pose_pool),
            'text': random.choice(texts),
            'likes': random.randint(6, 88),
            'time': random.choice(['刚刚', '2分钟前', '6分钟前', '12分钟前']),
            'like_id': f'stroll_{i}_{random.randint(1000,9999)}'
        })

    return jsonify({'success': True, 'items': items})

# ============================================
# 新增路由 - 产品架构升级 v2.0
# ============================================

@app.route('/register')
def register():
    """兼容旧注册入口 -> 统一到 /auth"""
    return redirect(url_for('app_auth'))

@app.route('/login')
def login():
    """兼容旧登录入口 -> 统一到 /auth"""
    return redirect(url_for('app_auth'))

@app.route('/api/register', methods=['POST'])
def api_register():
    """注册 API"""
    try:
        # 获取表单数据
        username = request.form.get('username')
        password = request.form.get('password')
        gender = request.form.get('gender')
        photo = request.files.get('photo')
        
        if not username or not password or not gender or not photo:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        # 生成用户 ID
        user_id = UserService.create_user_id()
        
        # 生成 AI 头像
        avatar_data = UserService.generate_avatar(photo, gender)
        
        if not avatar_data:
            return jsonify({'success': False, 'message': '头像生成失败'}), 500
        
        # 保存用户信息到 Session
        session['user_id'] = user_id
        session['username'] = username
        session['avatar_image'] = avatar_data['avatar_image']
        session['gender'] = gender
        
        # 保存到用户数据存储
        USER_DATA_STORE[user_id] = {
            'user_id': user_id,
            'username': username,
            'gender': gender,
            'avatar_image': avatar_data['avatar_image'],
            'avatar_style': 'cartoon_2d',
            'created_at': datetime.now().isoformat(),
            'posts': [],
            'moments': [],
            'onboarding_completed': True
        }
        
        print(f"✅ User registered: {username} (ID: {user_id})")
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': user_id,
                'username': username,
                'avatar_image': avatar_data['avatar_image']
            }
        })
    except Exception as e:
        print(f"[ERROR] Registration failed: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """登录 API"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名或密码不能为空'}), 400
        
        # 简化版：查找匹配的用户（实际应该用数据库）
        user_found = None
        for user_id, user_data in USER_DATA_STORE.items():
            if user_data.get('username') == username:
                user_found = user_data
                break
        
        if not user_found:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 设置 Session
        session['user_id'] = user_found['user_id']
        session['username'] = user_found['username']
        session['avatar_image'] = user_found.get('avatar_image')
        
        print(f"✅ User logged in: {username}")
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': user_found['user_id'],
                'username': user_found['username'],
                'avatar_image': user_found.get('avatar_image')
            }
        })
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/novel')
def get_novel():
    """获取小说内容"""
    try:
        novel = ContentCreationService.generate_novel_content()
        return jsonify(novel)
    except Exception as e:
        print(f"[ERROR] Failed to generate novel: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/comic')
def get_comic():
    """获取漫画内容"""
    try:
        comic = ContentCreationService.generate_comic_content()
        return jsonify(comic)
    except Exception as e:
        print(f"[ERROR] Failed to generate comic: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/relay', methods=['POST'])
def create_relay():
    """创建接力内容"""
    try:
        data = request.get_json()
        original_content = data.get('original', {})
        user_input = data.get('user_input', '')
        
        if not original_content or not user_input:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        relay = ContentCreationService.create_relay_content(original_content, user_input)
        return jsonify(relay)
    except Exception as e:
        print(f"[ERROR] Failed to create relay: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/challenge', methods=['POST'])
def create_challenge():
    """创建夺擂内容"""
    try:
        data = request.get_json()
        requirement = data.get('requirement', {})
        
        challenge = ContentCreationService.create_challenge_content(requirement)
        return jsonify(challenge)
    except Exception as e:
        print(f"[ERROR] Failed to create challenge: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/moments')
def get_moments():
    """获取朋友圈列表"""
    try:
        # 获取当前用户数据
        user_data = get_user_data()
        
        # 生成朋友圈内容
        moments = MomentsService.generate_moments(user_data, num_posts=5)
        
        return jsonify({'moments': moments})
    except Exception as e:
        print(f"[ERROR] Failed to generate moments: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check_in', methods=['POST'])
def check_in():
    """打卡"""
    try:
        data = request.get_json()
        location = data.get('location', {})
        
        if not location:
            return jsonify({'success': False, 'message': '缺少地点信息'}), 400
        
        user_data = get_user_data()
        check_in_record = MomentsService.auto_check_in(user_data, location)
        
        return jsonify(check_in_record)
    except Exception as e:
        print(f"[ERROR] Failed to check in: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# 测试 API - AI 内容生成
# ============================================

@app.route('/api/test_ai_generate', methods=['GET'])
def api_test_ai_generate():
    """测试 AI 内容生成 API"""
    from services.ai_content import get_ai_service
    
    ai_service = get_ai_service()
    
    # 测试生成小说
    novel = ai_service.generate_novel(
        location="星巴克 (南京东路店)",
        mood="温暖"
    )
    
    return jsonify({
        'success': True,
        'type': 'novel',
        'data': novel
    })

@app.route('/api/generate_more_content', methods=['POST'])
def api_generate_more_content():
    """生成更多内容（使用真实 AI）"""
    try:
        data = request.get_json() or {}
        content_type = data.get('type', 'novel')  # novel, comic, moments
        location = data.get('location', '附近咖啡店')
        mood = data.get('mood', '日常')
        
        from services.ai_content import get_ai_service
        ai_service = get_ai_service()
        
        if content_type == 'novel':
            result = ai_service.generate_novel(location=location, mood=mood)
        elif content_type == 'comic':
            result = ai_service.generate_comic_script(location=location)
        elif content_type == 'moments':
            result = ai_service.generate_moments_caption(location=location)
        else:
            result = {'error': 'Unknown content type'}
        
        return jsonify({
            'success': True,
            'type': content_type,
            'data': result
        })
        
    except Exception as e:
        print(f"[ERROR] Failed to generate content: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# 启动
# ============================================
# 启动应用
# ============================================

# 仅在本地开发环境运行调试服务器
# Vercel 部署时使用 WSGI 自动检测 app 对象，不需要 app.run()
if __name__ == '__main__':
    import os
    # 检测是否在 Vercel 环境
    if not os.environ.get('VERCEL'):
        print("Go In Immersive MVP Starting...")
        print("URL: http://localhost:5000")
        print("\nDefault City: Shanghai Pudong")
        print("Feature: Light Personalization (3 quick choices)")
        print("Click 'It Continues' to see new content")
        # 仅在非 Vercel 环境启动调试服务器
        app.run(debug=True, host='0.0.0.0', port=5000)
