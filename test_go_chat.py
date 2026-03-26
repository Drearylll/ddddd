"""
测试 Go 聊天功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量（如果没有配置）
if not os.getenv("DEEPSEEK_API_KEY"):
    print("⚠️ 未配置 DEEPSEEK_API_KEY，将使用模拟回复")
    print("如需使用真实 API，请设置环境变量:\n")
    print("export DEEPSEEK_API_KEY=your_api_key\n")

def test_mock_reply():
    """测试模拟回复功能"""
    from app import mock_go_reply
    
    print("\n" + "="*60)
    print("测试模拟回复功能")
    print("="*60)
    
    test_cases = [
        "今天心情不太好",
        "想去海边走走",
        "想找个安静的地方看书",
        "有什么好玩的地方推荐吗",
        "刚吃完火锅，好满足"
    ]
    
    for message in test_cases:
        print(f"\n📝 用户：{message}")
        reply, intent = mock_go_reply(message)
        print(f"🤖 Go: {reply}")
        if intent:
            print(f"🎯 意图：{intent}")
    
    print("\n✅ 测试完成")


def test_intent_extraction():
    """测试意图提取功能"""
    from app import extract_location, extract_activity, extract_mood
    
    print("\n" + "="*60)
    print("测试意图提取功能")
    print("="*60)
    
    # 测试地点提取
    print("\n【地点提取】")
    locations_test = [
        "我想去海边",
        "到图书馆看书",
        "公园散步怎么样"
    ]
    
    for text in locations_test:
        loc = extract_location(text.lower())
        print(f"  '{text}' -> {loc}")
    
    # 测试活动提取
    print("\n【活动提取】")
    activities_test = [
        "想去跑步",
        "打算看书",
        "想喝咖啡"
    ]
    
    for text in activities_test:
        act = extract_activity(text.lower())
        print(f"  '{text}' -> {act}")
    
    # 测试情绪提取
    print("\n【情绪提取】")
    moods_test = [
        "今天好开心",
        "心情很烦",
        "感觉好累"
    ]
    
    for text in moods_test:
        mood = extract_mood(text.lower())
        print(f"  '{text}' -> {mood}")
    
    print("\n✅ 测试完成")


def test_database_models():
    """测试数据库模型"""
    from services.database import db, init_db
    from models import UserIntent
    from flask import Flask
    
    print("\n" + "="*60)
    print("测试数据库模型")
    print("="*60)
    
    # 创建测试应用
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化数据库
    with app.app_context():
        db.init_app(app)
        db.create_all()
        
        # 创建测试数据
        intent = UserIntent(
            user_id="test_user",
            intent_type="want_to_visit",
            location="海边",
            activity="散步",
            mood="期待",
            keywords='["海边", "散步"]'
        )
        
        db.session.add(intent)
        db.session.commit()
        
        # 查询测试
        result = UserIntent.query.filter_by(user_id="test_user").first()
        
        print(f"\n✅ 成功创建并查询意图记录:")
        print(f"   ID: {result.id}")
        print(f"   类型：{result.intent_type}")
        print(f"   地点：{result.location}")
        print(f"   活动：{result.activity}")
        print(f"   情绪：{result.mood}")


if __name__ == "__main__":
    print("\n🚀 Go In - Go 聊天功能测试\n")
    
    # 运行所有测试
    test_mock_reply()
    test_intent_extraction()
    test_database_models()
    
    print("\n" + "="*60)
    print("✅ 所有测试通过！")
    print("="*60)
    print("\n下一步:")
    print("1. 启动应用：python app.py")
    print("2. 访问聊天页面：http://localhost:5000/go")
    print("3. 体验 AI 对话和意图识别功能")
    print()
