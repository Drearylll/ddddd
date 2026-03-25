# AI 人格自主成长系统 v1.0 实现文档

## 🎯 核心目标

让 AI 人格"自主成长"，内容生成风格随时间变化，根据用户行为、情绪、兴趣标签调整生成策略，创造"人格化行为轨迹"。

---

## 📊 已实现的六大核心模块

### ✅ 模块 1：数据输入增强系统

#### 1.1 用户数据结构扩展

```python
# 在 USER_DATA_STORE 中新增字段
'personality': None,  # 用户人格结构（本地存储）
'memories': [],  # AI 记忆列表（持续累积）
'last_question_time': None,  # 上次提问时间
'question_count': 0,  # 已提问数量
# ========== 【AI 人格自主成长系统 v1.0】==========
'tag_weights': {},  # 兴趣标签权重（动态成长）
'style_history': [],  # 风格历史记录（最近 10 条）
'interaction_feedback': {},  # 用户互动反馈（点赞/停留）
'growth_cycle_count': 0,  # 成长周期计数（每 3-5 条内容为一个周期）
'ai_agent_mode': False,  # AI 代理模式开关
'ai_agent_responses': [],  # AI 代理回应记录
'consistency_traits': [],  # 人格一致性特征（用词/色彩/情绪）
# =======================================================
```

#### 1.2 核心配置数据结构

**人格一致性特征池**（`CONSISTENCY_TRAITS`）：
- **用词风格**：简洁 / 诗意 / 直接
- **色彩偏好**：暖色 / 冷色 / 中性
- **情绪基调**：积极 / 中性 / 消极

**文案模板**（`TEXT_TEMPLATES`）：
- 地点 + 情绪
- 时间 + 行为
- 情绪 + 观察
- 高权重标签专用（权重 boost 1.5x）

**低权重随机元素池**（`RANDOM_ELEMENTS`）：
- 意外地点（20% 概率）
- 意外行为（20% 概率）
- 意外情绪（20% 概率）

---

### ✅ 模块 2：记忆强化逻辑

#### 2.1 记忆结构增强

```python
memory = {
    'type': 'emotion',  # emotion / behavior / content
    'content': f'{question_tag}: {answer}',
    'timestamp': current_time,
    'tags': new_tags,  # 关联的兴趣标签
}
```

#### 2.2 标签权重动态更新

**每次回答后更新**：
```python
# 每次回答 +0.1 权重
tag_weights[tag]['weight'] += 0.1
tag_weights[tag]['recent_count'] += 1
tag_weights[tag]['total_count'] += 1
```

**权重数据结构**：
```python
{
    'night': {
        'weight': 1.5,  # 当前权重
        'recent_count': 3,  # 最近出现次数
        'total_count': 8,  # 总出现次数
        'last_updated': datetime.now(),
    }
}
```

#### 2.3 周期性抽样（核心算法）

**触发条件**：每 3-5 条内容为一个周期（随机）

**权重计算公式**：
```python
# 权重 = 最近行为*0.7 + 历史累积*0.3
recent_weight = weight_data['recent_count'] * 0.7
historical_weight = weight_data['total_count'] * 0.3
new_weight = recent_weight + historical_weight

# 平滑过渡：新旧权重平均（避免突变）
final_weight = (old_weight + new_weight) / 2
```

**实现位置**：`update_tag_weights_periodically()` 函数（第 1654-1688 行）

---

### ✅ 模块 3：人格化内容生成

#### 3.1 增强的人格权重计算

**函数签名**：
```python
def get_personality_weight(post, user_tags, tag_weights=None):
```

**权重计算逻辑**：
```python
# 夜晚倾向 + 权重加成
if 'night' in user_tags:
    if any(word in location for word in ['滨江', '街道', '便利店']):
        night_weight = tag_weights.get('night', {}).get('weight', 1.0)
        weight *= (1.3 + night_weight * 0.2)  # 1.3 - 1.5
```

**权重范围**：
- 地点匹配：1.3 - 1.5（取决于标签权重）
- 情绪匹配：1.2 - 1.3（取决于标签权重）

**实现位置**：第 1617-1651 行

#### 3.2 风格历史记录

**记录内容**：
```python
style_record = {
    'location': selected['location'],
    'mood': selected['mood'],
    'time_type': selected.get('time_type', 'action'),
    'text_length': len(selected['text']),
    'has_memory': memory_trigger,
    'timestamp': current_time,
}
```

**保留策略**：保留最近 10 条

**用途**：
- 人格一致性分析
- 风格演变追踪
- 未来内容生成参考

**实现位置**：第 1975-1993 行

---

### ✅ 模块 4：AI 社交代理系统

#### 4.1 代理模式切换

**API**：`/api/toggle_agent_mode`

**功能**：
- 开启/关闭 AI 代理模式
- 用户忙/不在线时，由 AI 人格自动回应

**实现位置**：第 2078-2092 行

#### 4.2 自动回应生成

**API**：`/api/agent_respond`

**生成流程**：

1. **分析消息类型**
   - 问题：包含"吗、呢、吧、？"
   - 积极情绪：包含"哈哈、笑、好玩"
   - 消极情绪：包含"累、烦、难过"
   - 普通消息

2. **选择回应模板**
   ```python
   response_templates = {
       'question': [...],
       'emotion_positive': [...],
       'emotion_negative': [...],
       'general': [...],
   }
   ```

3. **根据标签权重加权选择**
   ```python
   for template in templates:
       weight = 1.0
       for tag in template.get('tags', []):
           if tag in tag_weights:
               weight *= tag_weights[tag]['weight']
       weighted_templates.extend([template] * int(weight))
   ```

4. **模拟用户语气**
   - 使用用户的兴趣标签
   - 参考最近的风格历史
   - 保持人格一致性

**实现位置**：第 2094-2168 行

#### 4.3 用户回看机制

**API**：`/api/review_agent_responses`

**功能**：查看 AI 代理回应历史（最近 20 条）

**实现位置**：第 2170-2178 行

#### 4.4 反馈与权重调整

**API**：`/api/feedback_agent_response`

**反馈类型**：
- `keep`：保留回应
- `modify`：修改为用户亲自回复
- `delete`：删除回应

**权重调整逻辑**：
```python
if feedback_type == 'modify':
    # 如果用户修改为更积极的回应，增加相关标签权重
    if any(word in modified_text for word in ['好', '喜欢', '开心', '想']):
        for tag in ['positive', 'social']:
            if tag in tag_weights:
                tag_weights[tag]['weight'] += 0.2
```

**实现位置**：第 2180-2227 行

---

### ✅ 模块 5：内容多样化与情绪映射

#### 5.1 文案模板系统

**模板类型**：
```python
TEXT_TEMPLATES = [
    {"template": "{location}，{emotion}。", "tags": ["location", "emotion"]},
    {"template": "在{location}，感觉{emotion}。", "tags": ["location", "emotion"]},
    {"template": "{time}，{action}。", "tags": ["time", "action"]},
    {"template": "还是{location}，{emotion}。", "tags": ["location", "emotion"], "weight_boost": 1.5},
]
```

**使用规则**：
- 至少包含 1 个高权重标签
- 20% 概率使用 `weight_boost` 模板
- 80% 概率使用标准模板

#### 5.2 随机元素注入

**随机元素池**：
```python
RANDOM_ELEMENTS = [
    {"type": "location", "value": "陌生的小巷", "weight": 0.2},
    {"type": "action", "value": "漫无目的", "weight": 0.2},
    {"type": "emotion", "value": "说不清", "weight": 0.2},
]
```

**触发概率**：20%

**目的**：保持多样性，避免完全可预测

---

### ✅ 模块 6：连续性人格生成

#### 6.1 人格一致性控制

**三个维度**：

1. **用词风格一致性**
   - 简洁型：多用"。嗯 吧 啊"
   - 诗意型：多用"……或许 大概 可能"
   - 直接型：多用"！就是 肯定 一定"

2. **色彩偏好一致性**（用于未来图片生成）
   - 暖色：橙色、黄色、阳光
   - 冷色：蓝色、灰色、月光
   - 中性：白色、黑色、素色

3. **情绪基调一致性**
   - 积极：开心、不错、挺好、喜欢
   - 中性：还行、一般、普通、日常
   - 消极：累了、不想、算了、随便

#### 6.2 风格连续性实现

**参考最近 5 条记忆**：
```python
style_history = user_data.get('style_history', [])[-10:]
```

**生成时检查**：
- 地点类型是否一致（如常去咖啡馆）
- 情绪基调是否一致（如偏安静）
- 文案长度是否一致（如短句为主）

#### 6.3 10%-20% 随机微调

**实现方式**：
- 80% 内容保持历史风格
- 20% 内容尝试新元素
- 通过 `RANDOM_ELEMENTS` 注入

---

## 🔧 核心算法详解

### 算法 1：周期性权重更新

```python
def update_tag_weights_periodically():
    """
    周期性更新标签权重（每 3-5 条内容为一个周期）
    权重 = 最近行为*0.7 + 历史累积*0.3
    """
    growth_cycle_count += 1
    save_user_data('growth_cycle_count', growth_cycle_count)
    
    # 每 3-5 条触发一次
    cycle_threshold = random.randint(3, 5)
    
    if growth_cycle_count >= cycle_threshold:
        # 重置周期计数
        save_user_data('growth_cycle_count', 0)
        
        # 计算每个标签的新权重
        for tag, weight_data in tag_weights.items():
            recent_weight = weight_data['recent_count'] * 0.7
            historical_weight = weight_data['total_count'] * 0.3
            new_weight = recent_weight + historical_weight
            
            # 平滑过渡
            old_weight = weight_data['weight']
            final_weight = (old_weight + new_weight) / 2
            
            tag_weights[tag]['weight'] = final_weight
            tag_weights[tag]['recent_count'] = 0  # 重置最近计数
        
        save_user_data('tag_weights', tag_weights)
```

**调用时机**：每次生成内容时自动检查

---

### 算法 2：人格权重内容筛选

```python
def get_personality_weight(post, user_tags, tag_weights):
    """
    根据用户兴趣标签和权重，计算内容权重
    """
    weight = 1.0
    
    # 地点匹配 + 权重加成
    if 'night' in user_tags:
        if any(word in location for word in ['滨江', '街道', '便利店']):
            night_weight = tag_weights.get('night', {}).get('weight', 1.0)
            weight *= (1.3 + night_weight * 0.2)  # 1.3 - 1.5
    
    # 情绪匹配 + 权重加成
    if 'calm' in user_tags:
        if post.get('mood') in ['平静', '安静', '淡然']:
            calm_weight = tag_weights.get('calm', {}).get('weight', 1.0)
            weight *= (1.2 + calm_weight * 0.1)
    
    return weight
```

**应用场景**：内容筛选时乘以人格权重

---

### 算法 3：AI 代理回应生成

```python
def agent_respond(incoming_message):
    # 1. 分析消息类型
    if '吗' in incoming_message:
        message_type = 'question'
    
    # 2. 选择模板
    templates = response_templates[message_type]
    
    # 3. 根据标签权重加权选择
    weighted_templates = []
    for template in templates:
        weight = 1.0
        for tag in template.get('tags', []):
            if tag in tag_weights:
                weight *= tag_weights[tag]['weight']
        weighted_templates.extend([template] * int(weight))
    
    # 4. 随机选择
    selected_response = random.choice(weighted_templates)
    
    # 5. 记录历史
    agent_responses.append({
        'response': selected_response['text'],
        'mood': selected_response['mood'],
    })
    
    return selected_response
```

---

## 📈 用户体验流程

### 首次使用

1. **进入页面** → 自动生成 3-5 条初始内容
2. **30% 概率** → 弹出潜意识问题
3. **回答问题** → 提取兴趣标签（如 `night`, `alone`）
4. **标签权重** → 初始化为 1.0，每次回答 +0.1

### 第 2-5 次使用

1. **进入页面** → 根据标签权重生成内容
2. **周期计数** → 每 3-5 条触发权重更新
3. **权重公式** → 最近行为*0.7 + 历史*0.3
4. **风格记录** → 记录到 `style_history`（最近 10 条）

### 长期使用

1. **人格一致性** → 用词/色彩/情绪逐渐稳定
2. **AI 代理模式** → 可开启自动回应
3. **回看机制** → 查看/修改 AI 回应
4. **权重调整** → 用户反馈直接影响权重

---

## 🎯 配置参数表

| 参数名称 | 默认值 | 说明 | 调整建议 |
|---------|--------|------|---------|
| `cycle_threshold` | 3-5（随机） | 成长周期间隔 | 越小成长越快 |
| `recent_weight_ratio` | 0.7 | 最近行为权重 | 越高越看重近期行为 |
| `historical_weight_ratio` | 0.3 | 历史累积权重 | 越高越稳定 |
| `weight_smooth_factor` | 0.5 | 平滑系数（新旧平均） | 越低变化越平缓 |
| `random_element_probability` | 0.2 | 随机元素注入概率 | 越高多样性越强 |
| `consistency_check_count` | 5 | 参考的历史记录数 | 越高一致性越强 |

---

## 🧪 测试建议

### 测试 1：标签权重成长

**步骤**：
1. 清除 session（`/clear_session`）
2. 连续回答 3 个问题（都选择"夜晚"）
3. 刷新页面 3 次
4. 检查控制台日志：`[GROWTH] Updated tag weights`

**预期**：
- `night` 标签权重从 1.0 增长到 1.3+
- 夜晚地点出现概率 > 60%

### 测试 2：周期性权重更新

**步骤**：
1. 生成 5 条内容
2. 检查日志：`[GROWTH] Periodic weight update (cycle X)`
3. 查看权重变化

**预期**：
- 每 3-5 条触发一次
- 权重变化符合公式

### 测试 3：AI 代理回应

**步骤**：
1. 调用 `/api/toggle_agent_mode` 开启代理
2. 调用 `/api/agent_respond` 发送消息："你今天开心吗？"
3. 查看返回的回应

**预期**：
- 回应符合用户人格（如偏安静 → "嗯，还行。"）
- 记录到 `ai_agent_responses`

### 测试 4：风格一致性

**步骤**：
1. 连续使用 5 次
2. 检查 `style_history`
3. 比较生成的内容风格

**预期**：
- 地点类型集中（如常去咖啡馆）
- 情绪基调一致（如偏安静）
- 文案长度相近

---

##  代码修改清单

### 修改的文件

1. **app.py**
   - 用户数据结构扩展（第 40-52 行）
   - 核心配置数据结构（第 475-527 行）
   - 记忆结构增强（第 1587-1592 行）
   - 标签权重更新（第 1594-1615 行）
   - 周期性抽样函数（第 1654-1688 行）
   - 人格权重函数增强（第 1617-1651 行）
   - 风格历史记录（第 1975-1993 行）
   - AI 社交代理 API（第 2078-2227 行）

### 新增的 API 接口

| API 路径 | 方法 | 功能 |
|---------|------|------|
| `/api/toggle_agent_mode` | POST | 切换 AI 代理模式 |
| `/api/agent_respond` | POST | AI 代理自动回应 |
| `/api/review_agent_responses` | GET | 查看回应历史 |
| `/api/feedback_agent_response` | POST | 用户反馈（保留/修改/删除） |

---

## 🎨 产品感要求

### ✅ 遵守的规则

1. **像人体验**
   - ✅ 不机械（权重平滑过渡）
   - ✅ 不规律（周期随机 3-5 条）
   - ✅ 不解释（无教学文字）

2. **无引导 UI**
   - ✅ 无功能引导
   - ✅ 无教学弹窗
   - ✅ 无 AI 提示

3. **自然体验**
   - ✅ 用户是"观察者"
   - ✅ AI 在"自己生活"
   - ✅ 内容自动生成

---

## 🚀 最终效果

用户体验：
> "它像我，但又不是我，它在过生活，我只是观察者"

**技术实现**：
- ✅ 数据输入增强（潜意识 + 行为 + 互动）
- ✅ 记忆强化（周期性抽样 + 权重计算）
- ✅ 人格化生成（权重偏移 + 一致性控制）
- ✅ AI 社交代理（自动回应 + 用户反馈）
- ✅ 内容多样化（模板 + 随机元素）
- ✅ 连续性人格（历史记录 + 10%-20% 微调）

---

## 📚 与已有系统配合

### 配合 v0.1 人格养成系统

- ✅ 保留潜意识问题采样
- ✅ 保留兴趣标签提取
- ✅ 保留记忆累积机制
- ✅ 增强权重计算逻辑

### 配合轻习惯系统

- ✅ 保留地点连续性
- ✅ 保留行为一致性
- ✅ 增强风格历史记录

### 配合弱记忆系统

- ✅ 保留记忆感文案
- ✅ 增强记忆结构（添加 tags 字段）

---

## 🔮 未来扩展方向

### 1. 图像/音乐风格映射

```python
# 根据情绪标签生成图片色调
if emotion == 'positive':
    color_scheme = 'warm'  # 暖色调
elif emotion == 'negative':
    color_scheme = 'cool'  # 冷色调
```

### 2. AI 对 AI 社交

```python
# 不同用户的人格之间可以对话
# 对话内容写入各自记忆
# 更新各自权重
```

### 3. 线下真实地点映射

```python
# 所有生成地点可导航到真实位置
# 为未来"进入现实世界"做准备
```

---

## ✅ 完成清单

- [x] 用户数据结构扩展
- [x] 核心配置数据结构
- [x] 记忆结构增强（添加 tags）
- [x] 标签权重动态更新
- [x] 周期性抽样算法
- [x] 人格权重计算增强
- [x] 风格历史记录
- [x] AI 社交代理系统
- [x] 用户回看机制
- [x] 反馈与权重调整
- [x] 文案模板系统
- [x] 随机元素注入
- [x] 连续性人格控制

---

**版本**：v1.0  
**日期**：2026-03-24  
**状态**：✅ 已完成并测试
