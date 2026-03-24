"""
Go In - 沉浸式 MVP
一个会自己发生的 AI 世界
"""

from flask import Flask, render_template_string, session, redirect, url_for, jsonify, request, make_response
from datetime import datetime, timedelta
import random
import uuid

app = Flask(__name__)
app.secret_key = 'goin_immersive_mvp_2026'

# 无感多用户隔离：服务器端数据存储
# 使用字典存储所有用户数据，key 为 user_id
USER_DATA_STORE = {}

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
        }
        print(f"[USER] New user created: {user_id[:8]}...")
    
    return user_id

def get_user_data():
    """获取当前用户的数据"""
    user_id = get_or_create_user_id()
    return USER_DATA_STORE.get(user_id, {})

def save_user_data(key, value):
    """保存用户数据"""
    user_id = get_or_create_user_id()
    if user_id not in USER_DATA_STORE:
        USER_DATA_STORE[user_id] = {}
    USER_DATA_STORE[user_id][key] = value

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
# 地点库 - 上海浦东具体真实地点（约 15 个）
# 目标：让用户产生"我知道这个地方"的真实感
# ============================================
PUDONG_LOCATIONS = [
    # 陆家嘴区域
    "世纪大道地铁站口",
    "陆家嘴滨江步道",
    "IFC 商场外",
    "正大广场门口",
    "东方明珠下",
    # 张江区域
    "张江咖啡馆",
    "张江地铁站",
    "金科路商业街",
    # 前滩区域
    "前滩太古里",
    "前滩友城公园",
    # 金桥区域
    "金桥路街边",
    "金桥国际广场",
    # 其他浦东地标
    "浦东美术馆",
    "世纪公园",
    "龙阳路地铁站",
]

# 截图级内容池 - 高共鸣、抽象、短句（约 20% 概率出现）
# 升级：使用具体真实地点，增强"我知道这个地方"的真实感
SCREENSHOT_CONTENT = [
    {"location": random.choice(PUDONG_LOCATIONS), "text": "也不是非要来。", "mood": "疏离", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "好像不是这里的问题。", "mood": "疑惑", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "只是刚好走到这。", "mood": "淡然", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "也没有人在等我。", "mood": "平静", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "偶尔也会想，如果当时选了另一条路。", "mood": "思索", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "就这样吧。", "mood": "释然", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "总要去一个地方的。", "mood": "随意", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "今天不太一样。", "mood": "微妙", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "下次再说。", "mood": "留白", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "已经不重要了。", "mood": "平静", "style": "quiet", "time_pref": "any", "social": "alone", "is_screenshot": True},
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

# 未完成感机制 - 约 20% 概率
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
    {"location": random.choice(PUDONG_LOCATIONS), "text": "好像不是这里的问题。", "mood": "疑惑", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "只是刚好走到这。", "mood": "淡然", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "也不是第一次这样。", "mood": "平静", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "有点说不清。", "mood": "思索", "style": "quiet", "time_pref": "any", "social": "alone"},
    
    # 模糊、不解释（升级为具体地点）
    {"location": random.choice(PUDONG_LOCATIONS), "text": "不应该在这里。", "mood": "疏离", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "又错过了。", "mood": "遗憾", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "其实也没什么。", "mood": "克制", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "就这样吧。", "mood": "释然", "style": "quiet", "time_pref": "any", "social": "alone"},
    
    # 轻微偏离逻辑（保留时间性模糊，但地点具体）
    {"location": random.choice(PUDONG_LOCATIONS), "text": "昨天路过的，今天应该不在了。", "mood": "思索", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "下次也不会来。", "mood": "疏离", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "记不太清了。", "mood": "模糊", "style": "quiet", "time_pref": "any", "social": "alone"},
    {"location": random.choice(PUDONG_LOCATIONS), "text": "反正都一样。", "mood": "淡然", "style": "quiet", "time_pref": "any", "social": "alone"},
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
    
    # 获取用户上次浏览的最后一条内容类型
    last_post_type = user_data.get('last_post_time_type')
    
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
        
        if score >= 3:
            filtered_posts.append(post)
    
    if not filtered_posts:
        filtered_posts = WORLD_CONTENT
    
    filtered_posts = filter_content_by_time_type(filtered_posts, time_period, last_post_type)
    print(f"[TIME] Filtered to {len(filtered_posts)} posts (time-aware)")
    
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
        
        for i in range(num_posts_to_generate):
            # 选择内容
            selected = random.choice(filtered_posts) if filtered_posts else random.choice(CONTINUE_CONTENT)
            
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
    
    # 8. 合并旧内容和新内容
    all_posts = existing_posts + new_posts
    
    # 9. 时间轴排序：从新到旧（最新在上）
    posts_sorted = sorted(all_posts, key=lambda x: x['timestamp'], reverse=True)
    
    # 10. 保存到用户数据（确保持久化）
    save_user_data('posts', posts_sorted)
    if posts_sorted:
        save_user_data('last_post_timestamp', posts_sorted[0]['timestamp'])
        save_user_data('last_post_time_type', posts_sorted[-1].get('time_type', 'action'))
    
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
# 启动
# ============================================

if __name__ == '__main__':
    print("Go In Immersive MVP Starting...")
    print("URL: http://localhost:5000")
    print("\nDefault City: Shanghai Pudong")
    print("Feature: Light Personalization (3 quick choices)")
    print("Click 'It Continues' to see new content")
    # 关闭 debug 模式，避免热重启导致 session 丢失
    app.run(debug=False, host='0.0.0.0', port=5000)
