"""
完整集成示例：获取真实地点 + 分析风格
"""

from services.location import get_real_location
from services.location_analyzer import analyze_location_style

print("=" * 60)
print("完整集成示例：逛逛功能")
print("=" * 60)

# 步骤 1：获取真实地点
print("\n【步骤 1】获取真实地点...")
print("-" * 60)

location = get_real_location(
    lat=31.230416,
    lng=121.473701,
    types=["风景名胜", "餐饮服务", "购物服务"]
)

print(f"📍 地点：{location['name']}")
print(f"🏷️ 类型：{location['type']}")
print(f"📮 地址：{location['address']}")
print(f" 距离：{location.get('distance', 0)}米")
print(f"⏱️ 步行：{location.get('walk_time', '')}")
print(f"🖼️ 图片：{location['image_url'][:50]}..." if location['image_url'] else "🖼️ 图片：无")

# 步骤 2：分析地点风格
print("\n【步骤 2】分析地点风格...")
print("-" * 60)

style = analyze_location_style(
    image_url=location['image_url'],
    name=location['name'],
    address=location['address']
)

print(f"🎨 色调：{style['color_tone']}")
print(f"✨ 风格：{', '.join(style['style_tags'])}")
print(f"🎯 场景：{', '.join(style['scene_type'])}")
print(f"📝 描述：{style['atmosphere_description']}")
print(f"🔑 关键词：{', '.join(style['keywords'])}")

# 步骤 3：组合完整内容
print("\n【步骤 3】组合完整内容...")
print("-" * 60)

content = {
    # 地点信息
    "location_name": location['name'],
    "location_address": location['address'],
    "location_image": location['image_url'],
    "location_type": location['type'],
    "distance": location.get('distance', 0),
    "walk_time": location.get('walk_time', ''),
    "lat": location.get('lat'),
    "lng": location.get('lon'),
    
    # 风格分析
    "color_tone": style['color_tone'],
    "style_tags": style['style_tags'],
    "scene_type": style['scene_type'],
    "atmosphere_description": style['atmosphere_description'],
    "keywords": style['keywords']
}

print("完整内容 JSON：")
import json
print(json.dumps(content, ensure_ascii=False, indent=2))

# 步骤 4：前端展示示例
print("\n" + "=" * 60)
print("前端展示示例（HTML 结构）")
print("=" * 60)

html_example = f"""
<div class="location-card">
  <img src="{location['image_url']}" alt="{location['name']}">
  
  <div class="location-info">
    <h3>{location['name']}</h3>
    <p class="address">📍 {location['address']}</p>
    <p class="distance">🚶 {location.get('distance', 0)}米 | ⏱️ {location.get('walk_time', '')}</p>
    
    <!-- 风格标签 -->
    <div class="style-tags">
      {''.join([f'<span class="tag">{tag}</span>' for tag in style['style_tags']])}
    </div>
    
    <!-- 场景类型 -->
    <div class="scene-type">
      {''.join([f'<span class="scene">{scene}</span>' for scene in style['scene_type']])}
    </div>
    
    <!-- 氛围描述 -->
    <p class="atmosphere">
      {style['atmosphere_description']}
    </p>
    
    <!-- 关键词 -->
    <div class="keywords">
      {''.join([f'<span class="keyword">#{kw}</span>' for kw in style['keywords']])}
    </div>
  </div>
</div>
"""

print(html_example)

print("\n" + "=" * 60)
print("集成完成！")
print("=" * 60)

# 使用建议
print("\n💡 使用建议：")
print("-" * 60)
print("1. 在 Flask 路由中调用此集成逻辑")
print("2. 将 content 传递给前端模板")
print("3. 前端使用 CSS 美化卡片展示")
print("4. 可添加 AI 生成文案进一步增强内容")
print("\n示例代码：")
print("""
@app.route('/guangguang')
def guangguang():
    # 获取真实地点
    location = get_real_location()
    
    # 分析风格
    style = analyze_location_style(
        image_url=location['image_url'],
        name=location['name'],
        address=location['address']
    )
    
    # 组合内容
    content = {**location, **style}
    
    # 渲染模板
    return render_template('guangguang.html', content=content)
""")
