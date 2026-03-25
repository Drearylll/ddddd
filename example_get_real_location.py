"""
get_real_location 快速使用示例
"""

from services.location import LocationService

# 创建服务实例
location_service = LocationService()

print("=" * 60)
print("get_real_location 快速使用示例")
print("=" * 60)

# 示例 1：获取随机地点
print("\n【示例 1】获取随机地点（默认上海人民广场）")
print("-" * 60)

location = location_service.get_real_location()

print(f"📍 名称：{location['name']}")
print(f"🏷️ 类型：{location['type']}")
print(f"📮 地址：{location['address']}")
print(f"🖼️ 图片：{location['image_url'][:50]}..." if location['image_url'] else "🖼️ 图片：无")
print(f"📝 描述：{location['description']}")
print(f" 坐标：{location['lat']}, {location['lng']}")

# 示例 2：指定位置
print("\n" + "=" * 60)
print("\n【示例 2】指定位置（外滩）")
print("-" * 60)

location_waitan = location_service.get_real_location(
    lat=31.239493,
    lng=121.490686
)

print(f"📍 名称：{location_waitan['name']}")
print(f"🏷️ 类型：{location_waitan['type']}")
print(f"📮 地址：{location_waitan['address']}")
print(f"📝 描述：{location_waitan['description']}")

# 示例 3：指定类型
print("\n" + "=" * 60)
print("\n【示例 3】指定类型（仅餐饮服务）")
print("-" * 60)

location_food = location_service.get_real_location(
    lat=31.230416,
    lng=121.473701,
    types=["餐饮服务"]
)

print(f"📍 名称：{location_food['name']}")
print(f"🏷️ 类型：{location_food['type']}")
print(f"📮 地址：{location_food['address']}")
print(f"📝 描述：{location_food['description']}")

# 示例 4：多个类型
print("\n" + "=" * 60)
print("\n【示例 4】多个类型（景点 + 购物）")
print("-" * 60)

location_mix = location_service.get_real_location(
    lat=31.230416,
    lng=121.473701,
    types=["风景名胜", "购物服务"]
)

print(f"📍 名称：{location_mix['name']}")
print(f"🏷️ 类型：{location_mix['type']}")
print(f"📮 地址：{location_mix['address']}")
print(f"📝 描述：{location_mix['description']}")
print(f"🖼️ 图片：{location_mix['image_url'][:50]}..." if location_mix['image_url'] else "🖼️ 图片：无")

print("\n" + "=" * 60)
print("示例完成！")
print("=" * 60)

# 使用建议
print("\n💡 使用建议：")
print("-" * 60)
print("1. 在逛逛功能中调用 get_real_location()")
print("2. 使用返回的地点信息生成内容")
print("3. 将地点与 AI 生成的文案结合")
print("4. 展示真实的地点图片增强可信度")
print("\n示例代码：")
print("""
# 在 AI 内容生成服务中使用
def generate_content():
    # 获取真实地点
    location = location_service.get_real_location()
    
    # 使用地点信息生成 AI 内容
    content = {
        "location_name": location['name'],
        "location_address": location['address'],
        "location_image": location['image_url'],
        "ai_text": generate_ai_text(location)
    }
    
    return content
""")
