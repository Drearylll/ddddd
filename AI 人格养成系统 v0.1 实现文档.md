# AI 人格养成系统 v0.1 - 完整实现文档

## 一、核心目标

让 AI 生成的内容不再完全随机，而是逐渐"像用户"。

**重点：** 不是智能，而是"连续性人格"

---

## 二、已实现的四大核心模块

### ✅ 模块 1：用户潜意识采样系统

**目标：** 不使用复杂问卷，通过"偶发问题"逐渐了解用户

#### 实现细节：

**1. 问题弹出逻辑（30% 概率，不打扰）**

```python
def should_ask_question():
    """判断是否应该弹出问题"""
    # 第一次访问，不提问
    if not last_question_time:
        return False
    
    # 距离上次提问至少 10 分钟
    if time_since_last < 10:
        return False
    
    # 30% 概率弹出
    return random.random() < 0.3
```

**2. 内置题库（13 个轻量问题）**

```python
SUBCONSCIOUS_QUESTIONS = [
    # 时间/状态偏好
    {"question": "今天更像白天还是夜晚？", "tag": "time_preference"},
    {"question": "最近更接近哪种状态？", "options": ["平静", "空白", "混乱"], "tag": "emotion_state"},
    
    # 空间/场景偏好
    {"question": "现在更想去哪里？", "options": ["安静的地方", "热闹的地方"], "tag": "space_preference"},
    
    # 行为倾向
    {"question": "会更倾向于？", "options": ["待着不动", "出去走走"], "tag": "action_preference"},
    
    # 情绪表达
    {"question": "现在的情绪是？", "options": ["没什么情绪", "有点低落", "还行"], "tag": "current_emotion"},
]
```

**3. UI 设计（延迟 1.5 秒弹出，可跳过）**

- 弹窗样式：深色渐变背景，圆角卡片
- 弹出时机：页面加载后 1.5 秒
- 可跳过：点击"跳过"按钮关闭
- 自动记录：用户回答后自动更新人格

---

### ✅ 模块 2：本地人格数据结构

**目标：** 在前端或本地存储中建立用户人格结构

#### 数据结构：

```python
USER_DATA_STORE[user_id] = {
    # 基础数据
    'posts': [],  # 已浏览内容
    'preferences': {},  # 初始偏好设置
    
    # ========== 【AI 人格养成系统 v0.1】==========
    'personality': None,  # 用户人格结构
    'memories': [],  # AI 记忆列表（持续累积）
    'last_question_time': None,  # 上次提问时间
    'question_count': 0,  # 已提问数量
    'interest_tags': [],  # 兴趣标签（从回答中提取）
    # ============================================
}
```

#### 人格特征类型（6 种）：

```python
PERSONALITY_TRAITS = {
    "quiet": {"name": "安静", "keywords": ["独处", "安静", "内敛"]},
    "social": {"name": "社交", "keywords": ["人群", "热闹", "外向"]},
    "calm": {"name": "冷静", "keywords": ["平静", "理性", "克制"]},
    "sensitive": {"name": "敏感", "keywords": ["情绪", "细腻", "感知"]},
    "independent": {"name": "独立", "keywords": ["一个人", "自主", "自由"]},
    "gentle": {"name": "温柔", "keywords": ["温和", "柔软", "包容"]},
}
```

#### 兴趣标签映射（从回答中提取）：

```python
INTEREST_TAGS = {
    "day": ["白天", "阳光", "活动"],
    "night": ["夜晚", "安静", "独处"],
    "nature": ["海边", "山里", "自然"],
    "urban": ["城市", "街道", "建筑"],
    "alone": ["一个人", "独处", "独立"],
    "crowd": ["人多", "热闹", "社交"],
    "calm": ["平静", "平和", "稳定"],
    "chaotic": ["混乱", "波动", "不安"],
    "blank": ["空白", "放空", "无感"],
}
```

---

### ✅ 模块 3：AI 记忆系统

**目标：** 让 AI"记住发生过的事情"，而不是每次重来

#### 记忆结构：

```python
memory = {
    'type': 'emotion',  # emotion / behavior / content
    'content': f'{question_tag}: {answer}',  # 文本内容
    'timestamp': current_time,  # 时间戳
}
```

#### 记忆记录内容：

1. **用户回答的问题**
   - 例：`time_preference: 夜晚`
   - 例：`social_preference: 一个人`

2. **生成的朋友圈内容**
   - 例：`content: 张江咖啡馆 - 坐了一个下午`

3. **用户浏览行为（简单记录）**
   - 例：`behavior: viewed_post_count: 5`

#### 记忆累积逻辑：

```python
memories = user_data.get('memories', [])
memories.append(memory)
save_user_data('memories', memories)
```

**特点：**
- ✅ 持续累积
- ✅ 不需要复杂算法
- ✅ 简单记录即可

---

### ✅ 模块 4：朋友圈生成逻辑升级

**目标：** 半随机 + 人格偏移（不再是完全随机）

#### 核心算法：人格权重计算

```python
def get_personality_weight(post, user_tags):
    """根据用户兴趣标签，计算内容权重"""
    weight = 1.0
    
    # 夜晚倾向：优先选择夜景相关地点
    if 'night' in user_tags:
        if any(word in location for word in ['滨江', '街道', '便利店']):
            weight *= 1.5
    
    # 独处倾向：优先选择安静地点
    if 'alone' in user_tags:
        if any(word in location for word in ['咖啡馆', '公园', '美术馆']):
            weight *= 1.5
    
    # 自然倾向：优先选择自然景点
    if 'nature' in user_tags:
        if any(word in location for word in ['公园', '滨江', '海边']):
            weight *= 1.5
    
    # 城市倾向：优先选择城市场景
    if 'urban' in user_tags:
        if any(word in location for word in ['商场', '地铁站', '街道']):
            weight *= 1.5
    
    # 检查文案是否匹配用户情绪
    if 'calm' in user_tags:
        if post.get('mood') in ['平静', '安静', '淡然']:
            weight *= 1.3
    
    if 'chaotic' in user_tags:
        if post.get('mood') in ['混乱', '不安', '犹豫']:
            weight *= 1.3
    
    return weight
```

#### 应用示例：

**用户 A 的兴趣标签：** `['night', 'alone', 'calm']`

**生成的内容倾向：**
- ✅ 地点：滨江步道、咖啡馆、公园（权重 × 1.5）
- ✅ 文案：平静、安静、淡然（权重 × 1.3）
- ✅ 时间：夜晚场景优先

**效果：**
```
📍 陆家嘴滨江步道
    夜晚很安静。
    
    刚刚

📍 张江咖啡馆
    一个人坐了一会儿。
    
    30 分钟前
```

---

## 三、修改内容汇总

### app.py 修改

#### 1. 用户数据结构增强（第 26-46 行）

```python
USER_DATA_STORE[user_id] = {
    ...
    'personality': None,  # 用户人格结构
    'memories': [],  # AI 记忆列表
    'last_question_time': None,
    'question_count': 0,
}
```

**行数变化：** +8 / -2

---

#### 2. 潜意识问题池定义（第 417-476 行）

```python
SUBCONSCIOUS_QUESTIONS = [...]  # 13 个问题
PERSONALITY_TRAITS = {...}  # 6 种性格类型
INTEREST_TAGS = {...}  # 兴趣标签映射
```

**行数变化：** +59

---

#### 3. 潜意识采样函数（第 1298-1399 行）

```python
def should_ask_question():
    """判断是否应该弹出问题（30% 概率）"""

def ask_subconscious_question():
    """随机选择一个潜意识问题"""

def process_answer(question_tag, answer):
    """处理回答，提取标签，更新人格"""
```

**行数变化：** +105

---

#### 4. 人格权重计算函数（第 1410-1450 行）

```python
def get_personality_weight(post, user_tags):
    """根据用户兴趣标签，计算内容权重"""
```

**行数变化：** +48

---

#### 5. 内容筛选逻辑增强（第 1458-1470 行）

```python
# 根据偏好过滤内容
for post in WORLD_CONTENT:
    score = 0
    ...
    
    # 【AI 人格养成系统】人格权重加成
    personality_weight = get_personality_weight(post, user_tags)
    score *= personality_weight
```

**行数变化：** +6

---

#### 6. API 路由新增（第 1793-1805 行）

```python
@app.route('/api/answer_question', methods=['POST'])
def answer_question():
    """处理用户潜意识问题回答"""
```

**行数变化：** +15

---

#### 7. FEED_PAGE 模板增强（第 1098-1217 行）

```html
<!-- 潜意识问题弹窗 -->
{% if current_question %}
<div id="subconscious-modal" class="modal-overlay">
    <div class="modal-content">
        <div class="modal-question">{{ current_question.question }}</div>
        <div class="modal-options">...</div>
        <button class="modal-skip">跳过</button>
    </div>
</div>
{% endif %}
```

**行数变化：** +119

---

## 四、用户体验流程

### 第一次访问

1. **进入首页**
   - 直接看到 3-5 条内容
   - 无欢迎页，无引导页

2. **1.5 秒后**
   - 弹出潜意识问题（30% 概率）
   - 例："今天更像白天还是夜晚？"
   - 选项：「白天」「夜晚」

3. **用户回答**
   - 点击选项
   - 弹窗关闭
   - 后台记录：`time_preference: 白天` → 提取标签 `day`

4. **后续内容生成**
   - 白天相关地点权重提升（× 1.5）
   - 阳光、活动相关文案权重提升

---

### 第 N 次访问（N > 3）

1. **用户画像逐渐清晰**
   - 兴趣标签：`['night', 'alone', 'calm']`
   - 记忆数量：10+ 条
   - 问题回答：5 次

2. **内容高度个性化**
   - 地点：滨江、咖啡馆、公园（占比 70%）
   - 文案：平静、安静、独处（占比 60%）
   - 时间：夜晚场景（占比 50%）

3. **用户感觉**
   > "这个人，好像一直都是这样生活的"
   > "这些地点和文案，很像我会去的地方"

---

## 五、配置参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 问题弹出概率 | 30% | 每次进入时的触发概率 |
| 问题间隔时间 | 10 分钟 | 两次提问的最小间隔 |
| 人格权重提升 | 1.3x - 1.5x | 匹配兴趣标签时的权重倍数 |
| 题库数量 | 13 个 | 内置潜意识问题数量 |
| 性格类型 | 6 种 | 安静、社交、冷静、敏感、独立、温柔 |
| 兴趣标签 | 9 类 | day/night/nature/urban/alone/crowd/calm/chaotic/blank |

---

## 六、测试建议

### 测试 1：首次访问体验

**步骤：**
1. 清除 session
2. 访问首页
3. 等待 1.5 秒

**预期：**
- ✅ 30% 概率弹出潜意识问题
- ✅ 问题简短、模糊、偏情绪
- ✅ 可跳过

---

### 测试 2：回答处理验证

**步骤：**
1. 回答问题："夜晚"
2. 刷新页面
3. 查看生成的内容

**预期：**
- ✅ 控制台输出 `[PERSONALITY] Processed answer: time_preference = 夜晚`
- ✅ 夜晚相关地点权重提升
- ✅ 出现更多夜景内容

---

### 测试 3：人格偏移验证

**步骤：**
1. 连续回答 5 个问题（都选择"夜晚"、"一个人"）
2. 刷新页面
3. 查看生成的内容

**预期：**
- ✅ 兴趣标签：`['night', 'alone']`
- ✅ 夜晚地点占比 > 50%
- ✅ 独处文案占比 > 40%

---

### 测试 4：记忆累积验证

**步骤：**
1. 访问 3 次
2. 检查用户数据

**预期：**
- ✅ `memories` 数组持续增长
- ✅ 每条记忆包含 type、content、timestamp
- ✅ 记忆数量 = 问题回答数 + 内容生成数

---

## 七、设计原则

### 1. 平行自我原则

内容表现为"一个可能的用户版本"在持续生活：
- ✅ 有稳定的兴趣偏好
- ✅ 有连续的记忆
- ✅ 有一致的行为模式

---

### 2. 真实世界映射

真实的人都有习惯和记忆：
- ✅ 会重复去喜欢的地方
- ✅ 有熟悉感
- ✅ 会记得经历过的事情

---

### 3. 克制表达

不过度渲染，保持自然：
- ✅ 问题轻量、模糊
- ✅ 可跳过，不强制
- ✅ 权重提升是概率性的，不是绝对的

---

### 4. 不可控体验

用户不能控制或选择：
- ✅ 问题是随机弹出的
- ✅ 人格是逐渐形成的
- ✅ 用户无法看到或修改

---

## 八、目标效果

### 用户打开 App 后的感受：

> "它在自己生活，而我只是看见"

### 具体表现：

1. **内容逐渐"像用户"**
   - 地点偏好匹配
   - 文案风格接近
   - 情绪倾向一致

2. **有连续性**
   - 记得去过哪里
   - 记得做过什么
   - 不是每次重来

3. **自然形成**
   - 不是一开始就设定好
   - 是通过互动逐渐形成
   - 用户感受不到被分析

---

## 九、与已有系统配合

### 三大系统协同工作：

1. **轻习惯系统** - 负责地点重复和行为一致性
2. **弱记忆系统** - 负责重复地点的记忆感
3. **人格养成系统** - 负责整体人格偏移

**独立但互补：**
```python
# 轻习惯：决定是否重复地点
if random.random() < 0.2:
    new_location = repeated_location

# 弱记忆：决定是否触发记忆感
if is_in_history and random.random() < 0.3:
    memory_trigger = True
    modify_text_with_memory()

# 人格养成：根据兴趣标签调整权重
weight = get_personality_weight(post, user_tags)
```

---

## 十、总结

### 核心改动

1. ✅ 创建潜意识问题池（13 个问题）
2. ✅ 定义人格数据结构（6 种性格类型，9 类兴趣标签）
3. ✅ 实现潜意识采样函数（30% 概率弹出）
4. ✅ 实现人格权重计算（1.3x - 1.5x 权重提升）
5. ✅ 实现记忆累积系统（持续记录）
6. ✅ 实现内容生成的人格偏移（半随机 + 人格权重）
7. ✅ 添加前端弹窗 UI（延迟 1.5 秒，可跳过）
8. ✅ 新增 API 路由（处理回答）

---

### 影响范围

- ✅ 仅影响内容生成模块
- ✅ 不影响其他系统
- ✅ 与轻习惯、弱记忆系统独立工作
- ✅ 保持向下兼容

---

### 文件修改

| 文件 | 修改内容 | 行数变化 |
|------|----------|----------|
| `app.py` | 用户数据结构增强 | +8 / -2 |
| `app.py` | 潜意识问题池定义 | +59 |
| `app.py` | 潜意识采样函数 | +105 |
| `app.py` | 人格权重计算函数 | +48 |
| `app.py` | 内容筛选逻辑增强 | +6 |
| `app.py` | API 路由新增 | +15 |
| `app.py` | FEED_PAGE 模板增强 | +119 |

---

### 最终目标实现

用户打开 App，不需要操作，

AI 已经在某个地方，
替他活了一段生活，
并留下了一句话。

🎉 AI 人格养成系统 v0.1 实现完成！
