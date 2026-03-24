# AI 自主生活流机制实现说明

**实现日期：** 2026 年 3 月 20 日  
**版本：** Go In v4.0 - AI Autonomous Life Flow

---

## 一、核心变革

### 从"按钮生成"到"AI 自主生活"

**旧机制（v3.x）：**
- 用户点击"它还在继续"按钮
- 触发 `/api/next_post` 路由
- 生成 1 条新内容
- 用户被动等待操作

**新机制（v4.0）：**
- 移除所有生成按钮
- AI 根据时间间隔自动生成内容
- 用户进入时看到"这段时间发生的事"
- 形成"这个人一直在生活"的感觉

---

## 二、核心机制

### 1. 初始化生活时间轴（per user）

每个用户拥有独立的"生活时间线"：

```python
USER_DATA_STORE[user_id] = {
    'posts': [],  # 已浏览内容（持久化）
    'last_post_timestamp': None,  # 最后一条内容的时间戳
    'last_generate_time': None,  # AI 最后生成时间
    'life_timeline': [],  # AI 生活时间轴
}
```

**关键字段：**
- `last_generate_time`: 记录 AI 上次生成的时间
- `life_timeline`: 预留未来扩展（记录 AI 生活轨迹）

---

### 2. 自动生成逻辑

**触发时机：** 用户进入 App 时

**计算逻辑：**

```python
# 计算当前时间与 last_generate_time 的差值
minutes_diff = (current_time - last_generate_time).total_seconds() / 60

# 根据时间间隔决定生成数量
if minutes_diff < 15:
    num_posts = 0  # 间隔太短，不生成
elif minutes_diff < 40:
    num_posts = 1 if random() < 0.7 else 0  # 30 分钟左右，70% 概率生成 1 条
elif minutes_diff < 90:
    num_posts = random.randint(1, 2)  # 1 小时左右，生成 1-2 条
elif minutes_diff < 180:
    num_posts = random.randint(2, 3)  # 2 小时左右，生成 2-3 条
else:
    num_posts = random.randint(3, 5)  # 更久，生成 3-5 条
```

**示例场景：**

| 用户离开时间 | 生成数量 | 说明 |
|-------------|---------|------|
| 10 分钟 | 0 条 | 间隔太短，不生成 |
| 30 分钟 | 1 条 | "刚刚发生了件事" |
| 1 小时 | 1-2 条 | "这段时间去了几个地方" |
| 2 小时 | 2-3 条 | "去了不少地方" |
| 5 小时+ | 3-5 条 | "这段时间的生活轨迹" |

---

### 3. 时间分布机制

**核心原则：** 内容平均分布在用户离开的时间段中

**实现逻辑：**

```python
# 计算每条内容的时间间隔
time_per_post = total_minutes / num_posts_to_generate

for i in range(num_posts_to_generate):
    # 添加随机浮动（±30%）避免规律性
    random_factor = random.uniform(0.7, 1.3)
    minutes_offset = (i + 1) * time_per_post * random_factor
    
    post_timestamp = last_generate_time + timedelta(minutes=minutes_offset)
```

**示例：**
- 用户离开了 60 分钟
- 生成 2 条内容
- 平均间隔 = 60 / 2 = 30 分钟
- 实际时间：
  - 第 1 条：last_generate_time + 30 分钟 × 0.8 = 24 分钟
  - 第 2 条：last_generate_time + 30 分钟 × 1.2 = 36 分钟

**效果：** 内容时间自然分布，不会集中在某个时间点

---

### 4. 生活随机性

**随机浮动：±30%**

- 时间间隔不固定：避免"每小时一条"的规律感
- 生成数量不固定：2-3 条、3-5 条等随机变化
- 内容类型不固定：行动类、停留类、安静类混合

**概率控制：**

```python
# 30 分钟左右，70% 概率生成 1 条，30% 概率不生成
if minutes_diff < 40:
    num_posts = 1 if random.random() < 0.7 else 0
```

**目标：** 让用户感觉"这个人的生活是不稳定的、真实的"

---

### 5. 内容插入逻辑

**所有新内容加入已有内容流：**

```python
# 1. 读取已有内容
existing_posts = user_data.get('posts', [])

# 2. 生成新内容
new_posts = [...]  # 根据时间间隔生成

# 3. 合并
all_posts = existing_posts + new_posts

# 4. 时间轴排序（最新在上）
posts_sorted = sorted(all_posts, key=lambda x: x['timestamp'], reverse=True)
```

**效果：** 
- 内容持续积累
- 时间线连续
- 不会丢失历史内容

---

### 6. 首次进入机制

**触发条件：** 用户第一次访问（`last_generate_time is None`）

**生成逻辑：**
```python
if not last_generate_time:
    num_posts_to_generate = random.randint(2, 3)
    # 生成 2-3 条初始内容
```

**目标：** 模拟"已经发生过"的感觉，不是从零开始

---

## 三、删除内容

### 1. 移除生成按钮

**删除的 HTML：**
```html
<div class="footer-area">
    <button class="continue-btn" id="continueBtn" onclick="continueJourney()">
        它还在继续
    </button>
</div>
```

**删除的 CSS：**
- `.footer-area` 样式
- `.continue-btn` 及相关样式

**删除的 JavaScript：**
- `continueJourney()` 函数
- `addNewPost()` 函数

---

### 2. 删除 API 路由

**删除的路由：**
```python
@app.route('/api/next_post')
def next_post():
    """API: 返回一条新的"继续内容"（带个性化 + 渐进生成）"""
    # ... 删除整个函数（约 300 行代码）
```

**影响：**
- 用户无法主动触发生成
- 所有生成由 AI 自主决定

---

## 四、配置参数

### 生成间隔阈值

| 参数 | 值 | 说明 |
|------|-----|------|
| `MIN_INTERVAL` | 15 分钟 | 小于此值不生成 |
| `SHORT_INTERVAL` | 40 分钟 | 30 分钟左右 |
| `MEDIUM_INTERVAL` | 90 分钟 | 1 小时左右 |
| `LONG_INTERVAL` | 180 分钟 | 2 小时左右 |

### 生成数量

| 时间间隔 | 基础数量 | 随机浮动 |
|---------|---------|---------|
| < 15 分钟 | 0 | - |
| 15-40 分钟 | 1 | 70% 概率 |
| 40-90 分钟 | 1-2 | 随机 |
| 90-180 分钟 | 2-3 | 随机 |
| > 180 分钟 | 3-5 | 随机 |

### 时间分布随机性

```python
random_factor = random.uniform(0.7, 1.3)  # ±30% 浮动
```

---

## 五、日志输出

### 关键日志

```
[LIFE] Existing posts count: 15
[LIFE] Time since last generate: 45 minutes
[LIFE] Will generate 2 posts
[LIFE] Generated post 1: 陆家嘴滨江 at 32 分钟前
[LIFE] Generated post 2: IFC 商场 at 15 分钟前
[LIFE] Total posts after merge: 17
[LIFE] Updated last_generate_time to 2026-03-20 20:00:00
```

**日志含义：**
- `Existing posts count`: 已有内容数量
- `Time since last generate`: 距离上次生成的时间
- `Will generate`: 本次生成数量
- `Generated post X`: 每条内容的生成信息
- `Total posts after merge`: 合并后总数量

---

## 六、用户体验变化

### 旧体验（v3.x）

1. 用户进入 → 看到内容
2. 点击按钮 → 生成 1 条
3. 再点击 → 又生成 1 条
4. **感觉：** "我在控制这个 AI"

### 新体验（v4.0）

1. 用户进入 → 看到 2-3 条（初始内容）
2. 离开 1 小时后再次进入 → 看到 2 条新内容
3. 内容时间分布在过去的 1 小时中
4. **感觉：** "这个 AI 一直在生活，我只是偶尔看到"

---

## 七、目标效果

### 用户感知

**第一次进入：**
- "这里有几条内容，好像已经发生了一些事"

**第二次进入（间隔 1 小时）：**
- "这 1 小时里，他去了几个地方"
- "内容时间分布在过去 1 小时中"

**第三次进入（间隔 5 小时）：**
- "这 5 小时里，他经历了不少事"
- "内容时间自然分布，有远有近"

**多次进入后：**
- "这个人好像一直在生活"
- "而我只是偶尔看到"
- "这不是为我生成的，是真实发生的"

---

## 八、技术实现细节

### 1. 时间戳管理

```python
# 确保时间对象是 naive（无时区）
if current_time.tzinfo is not None:
    current_time = current_time.replace(tzinfo=None)

if last_generate_time and last_generate_time.tzinfo is not None:
    last_generate_time = last_generate_time.replace(tzinfo=None)
```

### 2. 时间标签生成

```python
minutes_diff = int((post_timestamp - current_time).total_seconds() / 60)

if abs(minutes_diff) < 5:
    time_label = '刚刚'
elif abs(minutes_diff) < 60:
    time_label = f'{abs(minutes_diff)}分钟前'
else:
    hours_diff = int(abs(minutes_diff) / 60)
    time_label = f'{hours_diff}小时前'
```

### 3. 内容上限管理

```python
MAX_POSTS = 30
if len(existing_posts) > MAX_POSTS:
    existing_posts = existing_posts[-MAX_POSTS:]  # 保留最近 30 条
```

---

## 九、测试建议

### 测试场景 1：首次进入

**步骤：**
1. 清除 session
2. 访问首页
3. 完成偏好设置

**预期结果：**
- 自动生成 2-3 条初始内容
- 内容时间：刚刚、10 分钟前、20 分钟前

---

### 测试场景 2：短时间后返回（15 分钟内）

**步骤：**
1. 首次访问后，等待 10 分钟
2. 刷新页面

**预期结果：**
- 不生成新内容
- 显示已有内容

---

### 测试场景 3：1 小时后返回

**步骤：**
1. 首次访问后，等待 1 小时
2. 刷新页面

**预期结果：**
- 生成 1-2 条新内容
- 内容时间分布在过去的 1 小时中

---

### 测试场景 4：长时间后返回（5 小时+）

**步骤：**
1. 首次访问后，等待 5 小时
2. 刷新页面

**预期结果：**
- 生成 3-5 条新内容
- 内容时间自然分布在过去 5 小时中

---

## 十、后续优化方向

### 1. 智能节奏调整

根据用户访问频率动态调整生成策略：
- 高频访问用户：减少每次生成数量
- 低频访问用户：增加每次生成数量

### 2. 生活事件聚类

将相关内容聚类为"事件"：
- 例如："在陆家嘴滨江散步" → 2-3 条相关内容
- 增强"生活轨迹"感

### 3. 季节性/节日影响

根据日期、天气、节日生成特殊内容：
- 雨天：生成室内活动
- 节日：生成节日相关内容

### 4. 用户状态感知

根据用户访问时间推断状态：
- 工作时间访问 → 生成简短内容
- 周末访问 → 生成丰富内容

---

## 十一、总结

### 核心变革

✅ **移除按钮**：用户无法主动控制  
✅ **AI 自主生成**：根据时间间隔自动生成  
✅ **时间分布**：内容平均分布在时间段中  
✅ **随机性**：避免规律性，像真实生活  

### 目标达成

用户在多次进入后产生感觉：
- ✅ "这个人好像一直在生活"
- ✅ "而我只是偶尔看到"
- ✅ "这不是为我生成的，是真实发生的"

---

**Go In v4.0 - AI Autonomous Life Flow**  
**一个会自己发生的世界**
