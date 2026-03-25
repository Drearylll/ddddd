"""
AI 绘画合成 - 快速使用示例
Go In App

这个脚本演示了如何使用 AI 绘画合成功能
"""

from services.location import get_real_location
from services.location_analyzer import analyze_location_style
from services.ai_compositor import composite_images

def main():
    """主函数"""
    print("=" * 60)
    print("AI 绘画合成 - 快速使用示例")
    print("=" * 60)
    
    # ========== 步骤 1：获取真实地点 ==========
    print("\n【1】获取真实地点...")
    location = get_real_location(
        lat=31.230416,  # 上海人民广场
        lng=121.473701,
        types=["风景名胜", "餐饮服务", "购物服务"]
    )
    
    print(f"📍 地点：{location['name']}")
    print(f"📮 地址：{location['address']}")
    print(f"🖼️ 图片：{'有' if location['image_url'] else '无'}")
    
    # ========== 步骤 2：分析地点风格 ==========
    print("\n【2】分析地点风格...")
    
    if location['image_url']:
        style = analyze_location_style(
            image_url=location['image_url'],
            name=location['name'],
            address=location['address']
        )
        
        print(f"🎨 色调：{style['color_tone']}")
        print(f"🏷️ 风格：{', '.join(style['style_tags'])}")
        print(f"📸 场景：{', '.join(style['scene_type'])}")
    else:
        style = {
            'color_tone': '自然色',
            'style_tags': ['现代', '时尚'],
            'scene_type': ['适合打卡', '适合拍照'],
            'atmosphere_description': '现代都市风格'
        }
        print("⚠️ 使用默认风格分析")
    
    # ========== 步骤 3：准备用户形象 ==========
    print("\n【3】准备用户形象...")
    
    # 这里使用模拟的用户图片 URL
    # 实际应用中，应该是用户上传的照片
    user_image_url = "https://images.pexels.com/photos/1234567/pexels-photo-1234567.jpeg?auto=compress&cs=tinysrgb&w=600"
    
    print(f"👤 用户形象：已准备")
    
    # ========== 步骤 4：合成图像 ==========
    print("\n【4】合成图像...")
    
    result = composite_images(
        user_image_url=user_image_url,
        background_image_url=location['image_url'] if location['image_url'] else None,
        location_name=location['name'],
        style_description=style['atmosphere_description']
    )
    
    print(f"\n✅ 合成结果：")
    print(f"  状态：{'成功' if result['success'] else '失败'}")
    print(f"  图片：{result['image_url'][:50] if result['image_url'] else '无'}...")
    print(f"  尺寸：{result.get('width', 0)}x{result.get('height', 0)}")
    print(f"  消息：{result.get('message', '')}")
    
    # ========== 总结 ==========
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print("\n💡 提示：")
    print("  - 实际使用时，user_image_url 应该是用户上传的照片")
    print("  - 确保阿里云百炼 API Key 配置正确")
    print("  - 输出图片尺寸为 1080x1920，适配朋友圈")
    
    return result


if __name__ == "__main__":
    main()
