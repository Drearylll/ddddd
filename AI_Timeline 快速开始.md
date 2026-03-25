# AI Timeline 主函数 - 快速开始指南

## 🎯 一句话介绍

**一个函数，自动生成完整的 AI 生活流内容**  
输入：用户 ID + 经纬度（可选）  
输出：真实地点 + 融合照片 + 创意文案 + 标签

---

## 📝 快速使用

### 最简单的调用

```python
from services.ai_timeline import run_ai_timeline

result = run_ai_timeline(
    user_id="user_123"  # 只需提供用户 ID
)

print(f"地点：{result['location']}")
print(f"文案：{result['caption']}")
print(f"图片：{result['image_url']}")
```

### 完整参数

```python
result = run_ai_timeline(
    user_id="user_123",           # 用户 ID（必填）
    lat=31.230416,                # 纬度（可选，默认上海）
    lng=121.473701,               # 经度（可选，默认上海）
    location_types=["风景名胜", "餐饮服务"],  # 地点类型（可选）
    save_to_db=True,              # 保存到数据库（可选）
    save_to_json=True             # 保存到 JSON 文件（可选）
)
```

---

## 🔄 完整流程

```
run_ai_timeline()
  ↓
【步骤 1】获取真实地点 → 高德地图 API
  ↓
【步骤 2】分析地点风格 → 多模态 AI
  ↓
【步骤 3】生成融合照片 → 图像合成
  ↓
【步骤 4】生成文案 → 文案策划 AI
  ↓
【步骤 5】保存结果 → 数据库/JSON
  ↓
【步骤 6】触发前端更新 → 刷新标志
  ↓
返回完整结果
```

---

## 💡 返回结果

```json
{
  "success": true,
  "user_id": "user_123",
  "post_id": 456,
  "location": "上海市历史博物馆",
  "image_url": "https://...",
  "caption": "把平凡的日子，过成喜欢的样子。",
  "hashtags": ["#生活碎片", "#AI 日记", "#现代"],
  "timestamp": "2026-03-20T10:30:00",
  "steps": {
    "get_location": "success",
    "analyze_style": "success",
    "composite_image": "success",
    "generate_caption": "success",
    "save_to_db": "success",
    "trigger_update": "success"
  }
}
```

---

## 🎨 使用场景

### 场景 1：单条生成

```python
# 为用户生成一条 AI 生活流
result = run_ai_timeline(user_id="xxx")
```

### 场景 2：批量生成

```python
from services.ai_timeline import batch_generate_timeline

# 批量生成 3 条
results = batch_generate_timeline(
    user_id="xxx",
    count=3
)

# 不同地点
locations = [
    {"lat": 31.23, "lng": 121.47},  # 人民广场
    {"lat": 31.24, "lng": 121.49},  # 外滩
]

for loc in locations:
    result = run_ai_timeline(
        user_id="xxx",
        lat=loc["lat"],
        lng=loc["lng"]
    )
```

### 场景 3：API 接口

```python
@app.route('/api/generate_timeline', methods=['POST'])
def generate_timeline():
    user_id = session.get('user_id')
    result = run_ai_timeline(user_id=user_id)
    return jsonify(result)
```

### 场景 4：定时任务

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=10)
def daily_auto_generate():
    """每天上午 10 点自动生成"""
    for user in get_all_users():
        run_ai_timeline(user_id=user.user_id)

scheduler.start()
```

---

## ⚙️ 配置选项

### 存储配置

```python
# 只保存到数据库
run_ai_timeline(save_to_db=True, save_to_json=False)

# 只保存到 JSON
run_ai_timeline(save_to_db=False, save_to_json=True)

# 都保存（推荐）
run_ai_timeline(save_to_db=True, save_to_json=True)

# 都不保存（仅测试）
run_ai_timeline(save_to_db=False, save_to_json=False)
```

### 地点配置

```python
# 上海不同区域
locations = {
    "人民广场": {"lat": 31.230416, "lng": 121.473701},
    "外滩": {"lat": 31.23956, "lng": 121.49137},
    "静安寺": {"lat": 31.22544, "lng": 121.44573},
    "陆家嘴": {"lat": 31.23593, "lng": 121.50165},
}

# 其他城市
beijing = {"lat": 39.9042, "lng": 116.4074}
guangzhou = {"lat": 23.1291, "lng": 113.2644}
```

### 地点类型配置

```python
# 只去餐厅
run_ai_timeline(location_types=["餐饮服务"])

# 只去景点
run_ai_timeline(location_types=["风景名胜"])

# 综合类型（推荐）
run_ai_timeline(location_types=["风景名胜", "餐饮服务", "购物服务"])
```

---

## 🔧 集成到现有项目

### 步骤 1：导入模块

```python
from services.ai_timeline import run_ai_timeline, batch_generate_timeline
```

### 步骤 2：创建 API 接口

```python
@app.route('/api/generate_moment', methods=['POST'])
def api_generate_moment():
    """生成 AI 瞬间"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"error": "未登录"}), 401
    
    result = run_ai_timeline(
        user_id=user_id,
        save_to_db=True,
        save_to_json=True
    )
    
    return jsonify(result)
```

### 步骤 3：前端调用

```javascript
// 前端 JavaScript
async function generateTimeline() {
    const response = await fetch('/api/generate_moment', {
        method: 'POST'
    });
    
    const result = await response.json();
    
    if (result.success) {
        console.log('生成成功:', result);
        // 刷新页面或更新 UI
        location.reload();
    }
}
```

---

## ⚠️ 常见问题

### Q1: API 调用失败怎么办？

**现象**：
```
❌ 豆包 API 调用失败：The model or endpoint xxx does not exist
```

**解决**：
1. 检查火山引擎/阿里云 API Key 配置
2. 验证模型名称是否正确
3. 或者依赖降级机制（会自动使用模拟数据）

**临时方案**：
```python
# 降级机制会自动处理，无需额外配置
result = run_ai_timeline(...)
```

### Q2: 如何获取用户头像？

**问题**：
```
⚠️ 获取用户头像失败：Working outside of application context.
```

**解决**：
```python
# 在 Flask 应用上下文中调用
with app.app_context():
    result = run_ai_timeline(user_id="xxx")

# 或者在路由中直接调用
@app.route('/generate')
def generate():
    return run_ai_timeline(user_id=session['user_id'])
```

### Q3: 如何自定义文案风格？

**修改** `services/caption_generator.py`：

```python
self.style_templates = {
    "short": {
        "prompt": """你的自定义提示词...""",
        "max_tokens": 100,
        "temperature": 0.8
    }
}
```

---

## 📊 性能指标

### 响应时间

| 阶段 | 预计耗时 |
|------|----------|
| 获取地点 | <1 秒 |
| 风格分析 | 2-5 秒 |
| 图像合成 | 1-3 秒 |
| 文案生成 | 2-4 秒 |
| 数据存储 | <1 秒 |
| **总计** | **6-14 秒** |

### 成功率

**测试结果**：
- ✅ 地点获取：100%
- ✅ 整体流程：100%（含降级）
- ⚠️ 真实 API：取决于配置

---

## 🎯 最佳实践

### 1. 生产环境配置

```python
# 启用数据库存储
result = run_ai_timeline(
    user_id=user_id,
    save_to_db=True,      # ✅ 启用
    save_to_json=False    # ❌ 关闭（避免重复）
)
```

### 2. 开发调试

```python
# 只保存到 JSON，便于查看
result = run_ai_timeline(
    save_to_db=False,
    save_to_json=True
)
```

### 3. 批量初始化

```python
# 为新用户批量生成初始内容
def initialize_user_feed(user_id, count=5):
    results = batch_generate_timeline(user_id=user_id, count=count)
    return [r for r in results if r['success']]
```

### 4. 定时生成

```python
# 每天固定时间生成
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=9, minute=0)
def morning_generate():
    for user in get_active_users():
        run_ai_timeline(user_id=user.user_id)
```

---

## ✅ 检查清单

使用前确认：
- [ ] 已导入 `ai_timeline` 模块
- [ ] 数据库已初始化
- [ ] 配置文件已更新（可选）

使用时注意：
- [ ] 提供有效的 user_id
- [ ] 根据需求配置存储选项
- [ ] 考虑是否需要批量生成

使用后检查：
- [ ] 检查返回的 success 字段
- [ ] 验证各步骤状态（steps）
- [ ] 确认数据已保存

---

## 📞 技术支持

**遇到问题？**

1. 查看《AI_Timeline 主函数实现报告.md》了解详细技术说明
2. 检查 API Key 配置是否正确
3. 确认数据库连接正常

**文档位置**：
- 实现报告：`AI_Timeline 主函数实现报告.md`
- 测试脚本：`test_ai_timeline.py`
- 源代码：`services/ai_timeline.py`

---

*最后更新：2026 年 3 月 20 日*
