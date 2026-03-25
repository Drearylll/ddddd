# AI 文案策划功能 - 快速开始指南

## 🎯 一句话介绍

**输入**：融合图片 + 风格标签  
**输出**：3 种风格的文案 + 建议标签（JSON 格式）

---

## 📝 快速使用

### 最简单的调用

```python
from services.caption_generator import generate_caption

result = generate_caption(
    image_url="https://example.com/image.jpg",  # 融合后的图片
    style_tags=["文艺", "午后", "咖啡"],        # 风格标签
    location_name="Manner Coffee",              # 地点名称
    location_atmosphere="慵懒的午后时光"         # 地点氛围
)

print(result["captions"]["short"])  # 短句文案
print(result["hashtags"])           # 建议标签
```

### 返回结果示例

```json
{
  "success": true,
  "captions": {
    "short": "把平凡的日子，过成喜欢的样子。",
    "long": "在这个快节奏的城市里，我们都在寻找属于自己的节奏...",
    "poetic": "阳光透过树叶的缝隙/洒在肩头/这一刻的温暖..."
  },
  "hashtags": ["#生活碎片", "#AI 日记", "#文艺", "#午后", "#咖啡"]
}
```

---

## 🎨 三种文案风格

### 1. 短句（20 字以内）

**特点**：简洁有力，适合快速阅读

**示例**：
- "把碎片拼起来，就是故事。"
- "今天的阳光刚刚好。"
- "这一刻，值得记录。"

**使用场景**：朋友圈、微博等短内容平台

### 2. 长文（50-100 字）

**特点**：有场景感和情感共鸣

**示例**：
```
"在这个喧嚣的城市里，总有一个角落属于你。也许是街角的咖啡店，
也许是黄昏的江边，也许就是此刻脚下的路。生活的美好，往往藏在
这些不经意的瞬间里。"
```

**使用场景**：公众号、小红书等需要深度内容的平台

### 3. 诗意（30-60 字）

**特点**：有意境和韵律感

**示例**：
```
"黄昏把影子拉长/思念在风中飘荡/你站在城市的这头/望着那头的月光"
```

**使用场景**：文艺类内容、情感表达

---

## 💡 参数说明

### image_url（必填）

融合后的图片 URL

```python
image_url = composite_result["image_url"]  # 从图像合成结果获取
```

### style_tags（推荐）

风格标签列表，影响文案调性

```python
# 好的例子
style_tags = ["文艺", "午后", "咖啡", "悠闲"]

# 不好的例子
style_tags = ["好", "美"]  # 太笼统
```

**建议**：提供 3-5 个具体的形容词或名词

### location_name（可选）

地点名称，用于生成地点标签

```python
location_name = "Manner Coffee"
# 自动生成标签：#MannerCoffee
```

### location_atmosphere（强烈推荐）

地点氛围描述，让文案更贴切

```python
# 好的描述
location_atmosphere = "慵懒的午后，阳光透过玻璃窗洒在木质桌面上，空气中弥漫着咖啡香气"

# 简单的描述
location_atmosphere = "咖啡厅的午后"
```

**效果对比**：
- ✅ 详细描述 → 文案质量高，更有意境
- ❌ 简单描述 → 文案较普通

---

## 🔧 完整工作流

### 逛逛功能完整流程

```python
# 步骤 1：获取真实地点
from services.location import get_real_location

location = get_real_location(
    lat=31.230416,
    lng=121.473701,
    types=["风景名胜", "餐饮服务", "购物服务"]
)

# 步骤 2：分析地点风格
from services.location_analyzer import analyze_location_style

style = analyze_location_style(
    image_url=location["image_url"],
    name=location["name"],
    address=location["address"]
)

# 步骤 3：合成用户形象
from services.ai_compositor import composite_images

composite = composite_images(
    user_image_url=user_url,
    background_image_url=location["image_url"],
    location_name=location["name"],
    style_description=style["atmosphere_description"]
)

# 步骤 4：生成文案
from services.caption_generator import generate_caption

caption = generate_caption(
    image_url=composite["image_url"],
    style_tags=style["style_tags"],
    location_name=location["name"],
    location_atmosphere=style["atmosphere_description"]
)

# 最终输出
print(f"📍 地点：{location['name']}")
print(f"🖼️ 图片：{composite['image_url']}")
print(f"✍️ 文案：{caption['captions']['short']}")
print(f"🏷️ 标签：{' '.join(caption['hashtags'])}")
```

---

## ⚠️ 常见问题

### Q1: API 调用失败怎么办？

**现象**：
```
❌ 豆包 API 调用失败：The model or endpoint xxx does not exist
```

**解决**：
1. 检查火山引擎 API Key 配置
2. 验证模型名称是否正确
3. 或者使用降级模式（会自动切换到阿里云）

**临时方案**：
```python
# 强制使用降级模式
result = generate_caption(..., use_backup=True)
```

### Q2: 文案质量不够好？

**原因**：
- 地点氛围描述太简单
- 风格标签不够具体

**改进**：
```python
# ❌ 不好的描述
location_atmosphere = "咖啡厅"

# ✅ 好的描述
location_atmosphere = "慵懒的午后，阳光透过玻璃窗洒在木质桌面上，
                      空气中弥漫着咖啡香气，轻柔的音乐在耳边流淌"
```

### Q3: 如何自定义文案风格？

**方法**：修改 `services/caption_generator.py` 中的模板

```python
self.style_templates = {
    "short": {
        "prompt": """你的自定义提示词...""",
        "max_tokens": 100,
        "temperature": 0.8
    },
    # ... 其他风格
}
```

---

## 🎯 最佳实践

### 1. 提供详细的氛围描述

```python
# ✅ 推荐
location_atmosphere = "黄昏时分，金色的阳光洒在黄浦江上，
                      对岸的东方明珠清晰可见，微风拂过，
                      游客们在江边散步，享受着这难得的悠闲时光"

# ❌ 不推荐
location_atmosphere = "外滩"
```

### 2. 使用具体的风格标签

```python
# ✅ 推荐
style_tags = ["慵懒", "午后", "咖啡香", "慢生活", "小资情调"]

# ❌ 不推荐
style_tags = ["好", "美", "开心"]
```

### 3. 根据场景选择合适的文案

```python
# 日常分享 → 短句
daily_caption = caption["captions"]["short"]

# 旅行记录 → 长文
travel_caption = caption["captions"]["long"]

# 文艺表达 → 诗意
artistic_caption = caption["captions"]["poetic"]
```

### 4. 标签不要太多

```python
# ✅ 推荐（4-6 个）
hashtags = caption["hashtags"][:6]

# ❌ 不推荐（太多会显得 spam）
hashtags = caption["hashtags"]  # 可能有 10+ 个
```

---

## 📊 性能指标

### 响应时间

| 阶段 | 预计耗时 |
|------|----------|
| 图片分析 | 2-5 秒 |
| 短句生成 | 1-3 秒 |
| 长文生成 | 2-4 秒 |
| 诗意生成 | 2-4 秒 |
| **总计** | **7-16 秒** |

### 文案质量

**评估维度**：
- ✅ 简洁性：短句 20 字以内
- ✅ 感染力：有情感共鸣
- ✅ 场景感：符合地点氛围
- ✅ 自然度：像日常说话

**目标**：80% 以上的文案可直接使用

---

## 🚀 进阶用法

### 批量生成

```python
# 为多张图片生成文案
images = [url1, url2, url3]
for image_url in images:
    result = generate_caption(image_url=image_url, ...)
    print(result["captions"]["short"])
```

### 自定义温度参数

```python
generator = get_caption_generator()

# 调整温度参数获得不同风格
generator.style_templates["short"]["temperature"] = 0.9  # 更有创意
# 或
generator.style_templates["short"]["temperature"] = 0.5  # 更保守
```

### 添加新的文案风格

```python
generator.style_templates["humorous"] = {
    "prompt": """请写一个幽默风趣的文案...""",
    "max_tokens": 100,
    "temperature": 0.9
}

result = generator.generate_caption(...)
print(result["captions"]["humorous"])
```

---

## ✅ 检查清单

使用前确认：
- [ ] 已安装所需依赖
- [ ] 配置文件已更新
- [ ] API Key 已验证（或使用降级模式）

使用时注意：
- [ ] 提供详细的地点氛围描述
- [ ] 使用具体的风格标签
- [ ] 根据需要选择合适的文案风格

使用后检查：
- [ ] 文案是否自然流畅
- [ ] 标签是否合理相关
- [ ] JSON 格式是否正确解析

---

## 📞 技术支持

**遇到问题？**

1. 查看《AI 文案策划功能实现报告.md》了解详细技术说明
2. 检查 API Key 配置是否正确
3. 确认火山引擎模型名称

**文档位置**：
- 实现报告：`AI 文案策划功能实现报告.md`
- 测试脚本：`test_caption_generator.py`
- 源代码：`services/caption_generator.py`

---

*最后更新：2026 年 3 月 20 日*
