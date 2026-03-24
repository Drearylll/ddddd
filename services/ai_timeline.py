"""
AI Timeline 主函数
Go In App - AI 自主生活流生成系统

功能流程：
1. 调用 get_real_location() 获取真实地点
2. 调用 analyze_location_style() 分析氛围
3. 调用图像融合脚本生成带 AI 形象的照片
4. 调用 generate_caption() 生成文案
5. 将结果存入数据库或本地 JSON 文件
6. 触发前端更新（WebSocket 消息或刷新信号）

使用示例：
    from services.ai_timeline import run_ai_timeline
    
    result = run_ai_timeline(user_id="xxx")
"""

from datetime import datetime
import json
import os
from typing import Dict, Optional

# 导入所有需要的服务
from services.location import get_real_location
from services.location_analyzer import analyze_location_style
from services.ai_compositor import composite_images
from services.caption_generator import generate_caption
from services.database import db, Post, User
from config.db_config import DB_CONFIG


def run_ai_timeline(
    user_id: str,
    lat: float = 31.230416,
    lng: float = 121.473701,
    location_types: list = None,
    save_to_db: bool = True,
    save_to_json: bool = True
) -> Dict:
    """
    AI Timeline 主函数 - 完整的 AI 自主生活流生成
    
    Args:
        user_id: 用户 ID
        lat: 纬度，默认上海人民广场
        lng: 经度，默认上海人民广场
        location_types: 地点类型列表，默认 ["风景名胜", "餐饮服务", "购物服务"]
        save_to_db: 是否保存到数据库
        save_to_json: 是否保存到本地 JSON 文件
        
    Returns:
        Dict: 生成结果
        {
            "success": True,
            "post_id": 123,
            "location": "地点名称",
            "image_url": "图片 URL",
            "caption": "文案",
            "hashtags": ["标签"],
            "timestamp": "时间戳"
        }
    """
    print("\n" + "=" * 60)
    print("🚀 开始 AI Timeline 生成...")
    print("=" * 60)
    
    timeline_result = {
        "success": False,
        "user_id": user_id,
        "post_id": None,
        "location": None,
        "image_url": None,
        "caption": None,
        "hashtags": [],
        "timestamp": datetime.now().isoformat(),
        "steps": {}
    }
    
    try:
        # ========== 步骤 1：获取真实地点 ==========
        print("\n【步骤 1】获取真实地点...")
        if location_types is None:
            location_types = ["风景名胜", "餐饮服务", "购物服务"]
        
        location = get_real_location(
            lat=lat,
            lng=lng,
            types=location_types
        )
        
        if not location or not location.get('name'):
            print("❌ 获取地点失败")
            timeline_result["steps"]["get_location"] = "failed"
            return timeline_result
        
        print(f"✅ 地点：{location['name']}")
        print(f"   地址：{location.get('address', '')}")
        print(f"   类型：{location.get('type', '')}")
        
        timeline_result["location"] = location['name']
        timeline_result["steps"]["get_location"] = "success"
        
        # ========== 步骤 2：分析地点风格 ==========
        print("\n【步骤 2】分析地点风格...")
        
        style_analysis = {}
        if location.get('image_url'):
            style = analyze_location_style(
                image_url=location['image_url'],
                name=location['name'],
                address=location.get('address', '')
            )
            
            if style and style.get('success'):
                style_analysis = style
                print(f"✅ 色调：{style.get('color_tone', '')}")
                print(f"   风格：{', '.join(style.get('style_tags', []))}")
                print(f"   场景：{', '.join(style.get('scene_type', []))}")
                timeline_result["steps"]["analyze_style"] = "success"
            else:
                print("⚠️ 风格分析失败，使用默认值")
                style_analysis = _get_default_style()
                timeline_result["steps"]["analyze_style"] = "fallback"
        else:
            print("⚠️ 无图片，使用默认风格")
            style_analysis = _get_default_style()
            timeline_result["steps"]["analyze_style"] = "fallback"
        
        # ========== 步骤 3：生成带 AI 形象的照片 ==========
        print("\n【步骤 3】生成带 AI 形象的融合照片...")
        
        # 获取用户的 AI 形象（从数据库或参数）
        user_avatar_url = _get_user_avatar_url(user_id)
        
        if not user_avatar_url:
            print("⚠️ 未找到用户 AI 形象，使用模拟图片")
            user_avatar_url = "https://images.pexels.com/photos/1234567/pexels-photo-1234567.jpeg?auto=compress&cs=tinysrgb&w=600"
        
        # 调用图像合成服务
        composite_result = composite_images(
            user_image_url=user_avatar_url,
            background_image_url=location.get('image_url'),
            location_name=location['name'],
            style_description=style_analysis.get('atmosphere_description', '')
        )
        
        if composite_result and composite_result.get('success'):
            print(f"✅ 图片合成成功")
            print(f"   尺寸：{composite_result.get('width', 0)}x{composite_result.get('height', 0)}")
            timeline_result["image_url"] = composite_result.get('image_url')
            timeline_result["steps"]["composite_image"] = "success"
        else:
            print("⚠️ 图片合成失败，使用背景图片")
            timeline_result["image_url"] = location.get('image_url')
            timeline_result["steps"]["composite_image"] = "fallback"
        
        # ========== 步骤 4：生成文案 ==========
        print("\n【步骤 4】生成文案...")
        
        caption_result = generate_caption(
            image_url=timeline_result["image_url"],
            style_tags=style_analysis.get('style_tags', []),
            location_name=location['name'],
            location_atmosphere=style_analysis.get('atmosphere_description', '')
        )
        
        if caption_result and caption_result.get('success'):
            captions = caption_result.get('captions', {})
            print(f"✅ 文案生成成功")
            print(f"   短句：{captions.get('short', '')[:30]}...")
            print(f"   长句：{captions.get('long', '')[:50]}...")
            
            # 使用短句作为默认文案
            timeline_result["caption"] = captions.get('short', '')
            timeline_result["hashtags"] = caption_result.get('hashtags', [])
            timeline_result["steps"]["generate_caption"] = "success"
        else:
            print("⚠️ 文案生成失败，使用默认文案")
            timeline_result["caption"] = _get_default_caption(location['name'])
            timeline_result["hashtags"] = ["#生活碎片", "#AI 日记"]
            timeline_result["steps"]["generate_caption"] = "fallback"
        
        # ========== 步骤 5：保存结果 ==========
        print("\n【步骤 5】保存结果...")
        
        post_data = {
            "user_id": user_id,
            "content_type": "moments",
            "content_data": {
                "image_url": timeline_result["image_url"],
                "caption": timeline_result["caption"],
                "hashtags": timeline_result["hashtags"],
                "location_name": location['name'],
                "location_data": {
                    "lat": lat,
                    "lng": lng,
                    "address": location.get('address', '')
                },
                "style_analysis": style_analysis,
                "pose_emoji": _get_pose_emoji(style_analysis)
            },
            "location_name": location['name'],
            "is_auto_generated": True
        }
        
        # 保存到数据库
        if save_to_db:
            post_id = _save_to_database(post_data)
            if post_id:
                print(f"✅ 已保存到数据库，Post ID: {post_id}")
                timeline_result["post_id"] = post_id
                timeline_result["steps"]["save_to_db"] = "success"
            else:
                print("❌ 数据库保存失败")
                timeline_result["steps"]["save_to_db"] = "failed"
        
        # 保存到本地 JSON 文件
        if save_to_json:
            json_file = _save_to_json_file(user_id, post_data)
            if json_file:
                print(f"✅ 已保存到 JSON 文件：{json_file}")
                timeline_result["steps"]["save_to_json"] = "success"
            else:
                print("❌ JSON 文件保存失败")
                timeline_result["steps"]["save_to_json"] = "failed"
        
        # ========== 步骤 6：触发前端更新 ==========
        print("\n【步骤 6】触发前端更新...")
        
        # 发送 WebSocket 消息或设置刷新标志
        _trigger_frontend_update(user_id, timeline_result)
        print("✅ 前端更新信号已发送")
        timeline_result["steps"]["trigger_update"] = "success"
        
        # ========== 完成 ==========
        timeline_result["success"] = True
        
        print("\n" + "=" * 60)
        print("🎉 AI Timeline 生成完成！")
        print("=" * 60)
        print(f"\n📍 地点：{timeline_result['location']}")
        print(f"🖼️ 图片：{timeline_result['image_url'][:50] if timeline_result['image_url'] else '无'}...")
        print(f"✍️ 文案：{timeline_result['caption']}")
        print(f"🏷️ 标签：{' '.join(timeline_result['hashtags'])}")
        
    except Exception as e:
        print(f"\n❌ AI Timeline 生成异常：{e}")
        timeline_result["error"] = str(e)
        import traceback
        traceback.print_exc()
    
    return timeline_result


def _get_default_style() -> Dict:
    """获取默认风格分析"""
    return {
        "color_tone": "自然色",
        "style_tags": ["现代", "日常"],
        "scene_type": ["适合打卡", "适合记录"],
        "atmosphere_description": "日常生活场景，自然真实的氛围"
    }


def _get_default_caption(location_name: str) -> str:
    """获取默认文案"""
    default_captions = [
        f"在{location_name}，遇见美好的自己。",
        "生活的美好，藏在每一个当下。",
        "把平凡的日子，过成喜欢的样子。",
        "这一刻，值得被记录。"
    ]
    import random
    return random.choice(default_captions)


def _get_user_avatar_url(user_id: str) -> Optional[str]:
    """获取用户 AI 形象 URL"""
    try:
        # 从数据库查询用户头像
        user = User.query.filter_by(user_id=user_id).first()
        if user and user.face_avatar_url:
            return user.face_avatar_url
        
        # 如果没有 AI 头像，尝试使用人脸照片
        if user and user.face_photo_url:
            return user.face_photo_url
        
    except Exception as e:
        print(f"⚠️ 获取用户头像失败：{e}")
    
    return None


def _get_pose_emoji(style_analysis: Dict) -> str:
    """根据风格分析获取姿势 emoji"""
    pose_mapping = {
        "文艺": "📚",
        "繁华": "🌃",
        "宁静": "🧘",
        "复古": "📷",
        "现代": "🏙️",
        "温馨": "☕",
        "烟火气": "🍜"
    }
    
    style_tags = style_analysis.get('style_tags', [])
    for tag in style_tags:
        if tag in pose_mapping:
            return pose_mapping[tag]
    
    return "✨"  # 默认 emoji


def _save_to_database(post_data: Dict) -> Optional[int]:
    """保存到数据库"""
    try:
        post = Post(
            user_id=post_data["user_id"],
            content_type=post_data["content_type"],
            content_data=json.dumps(post_data["content_data"]),
            location_name=post_data["location_name"],
            location_data=json.dumps(post_data["content_data"].get("location_data", {})),
            is_auto_generated=post_data["is_auto_generated"]
        )
        
        db.session.add(post)
        db.session.commit()
        
        return post.id
        
    except Exception as e:
        print(f"❌ 数据库保存失败：{e}")
        db.session.rollback()
        return None


def _save_to_json_file(user_id: str, post_data: Dict) -> Optional[str]:
    """保存到本地 JSON 文件"""
    try:
        # 创建用户目录
        user_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_data')
        os.makedirs(user_dir, exist_ok=True)
        
        # 用户文件
        user_file = os.path.join(user_dir, f"{user_id}.json")
        
        # 读取现有数据
        existing_data = {"posts": []}
        if os.path.exists(user_file):
            with open(user_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        
        # 添加新内容
        post_record = {
            "id": len(existing_data["posts"]) + 1,
            "timestamp": datetime.now().isoformat(),
            **post_data
        }
        existing_data["posts"].insert(0, post_record)
        
        # 保存
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        return user_file
        
    except Exception as e:
        print(f"❌ JSON 文件保存失败：{e}")
        return None


def _trigger_frontend_update(user_id: str, timeline_result: Dict):
    """触发前端更新"""
    try:
        # 方案 1：设置刷新标志（简单有效）
        from services.user_manager import UserManager
        user_data = UserManager.get_user_data(user_id)
        if user_data:
            user_data["last_refresh_time"] = datetime.now().isoformat()
            user_data["needs_refresh"] = True  # 设置刷新标志
            UserManager.save_user_data("last_refresh_time", user_data["last_refresh_time"], user_id)
            UserManager.save_user_data("needs_refresh", True, user_id)
        
        # 方案 2：发送 WebSocket 消息（如果有 WebSocket 支持）
        # TODO: 实现 WebSocket 广播
        print(f"ℹ️ 已为用户 {user_id[:8]}... 设置刷新标志")
        
    except Exception as e:
        print(f"⚠️ 触发前端更新失败：{e}")


# 便捷函数
def generate_single_moment(user_id: str) -> Dict:
    """生成单条瞬间（简化版）"""
    return run_ai_timeline(user_id=user_id)


def batch_generate_timeline(user_id: str, count: int = 3) -> list:
    """批量生成 Timeline"""
    results = []
    
    # 不同的地点（上海不同区域）
    locations = [
        {"lat": 31.230416, "lng": 121.473701, "types": ["风景名胜"]},  # 人民广场
        {"lat": 31.23956, "lng": 121.49137, "types": ["餐饮服务"]},  # 外滩
        {"lat": 31.22544, "lng": 121.44573, "types": ["购物服务"]},  # 静安寺
    ]
    
    for i in range(count):
        loc = locations[i % len(locations)]
        result = run_ai_timeline(
            user_id=user_id,
            lat=loc["lat"],
            lng=loc["lng"],
            location_types=loc["types"]
        )
        results.append(result)
    
    return results


if __name__ == "__main__":
    # 测试运行
    print("AI Timeline 测试运行")
    print("=" * 60)
    
    # 使用测试用户 ID
    test_user_id = "test_user_001"
    
    result = run_ai_timeline(
        user_id=test_user_id,
        save_to_db=False,  # 测试时不保存到数据库
        save_to_json=True
    )
    
    print("\n最终结果：")
    print(json.dumps(result, ensure_ascii=False, indent=2))
