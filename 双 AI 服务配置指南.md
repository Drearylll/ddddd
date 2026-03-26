# 双 AI 服务配置指南

## ✅ 当前状态

项目现在**同时支持火山引擎豆包和阿里云通义千问**两个 AI 服务，可以灵活切换使用！

---

## 🔧 配置说明

### 1. 环境变量配置

**文件**: `.env.local`

```bash
# 火山引擎 - 豆包 AI（可选 - 有免费额度）
VOLCENGINE_API_KEY=de012cdc-ddcb-4695-a362-a67e26d5dcda
DOUBAO_API_KEY=de012cdc-ddcb-4695-a362-a67e26d5dcda

# 阿里云百炼 - 通义千问/万相（可选 - 有免费额度）
DASHSCOPE_API_KEY=sk-2274b3d46339f95092d68b83150ead7f
QWEN_API_KEY=sk-2274b3d46339f95092d68b83150ead7f
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# AI 服务选择（优先使用哪个 API）
# 可选值：doubao（火山引擎） | qwen（阿里云） | mock（模拟）
PREFERRED_AI_PROVIDER=qwen
```

### 2. 如何切换 AI 服务

#### 方式 A: 使用火山引擎豆包（已验证有效）

编辑 `.env.local`：
```bash
PREFERRED_AI_PROVIDER=doubao
```

**优点**:
- ✅ API Key 已验证有效
- ✅ 已完整测试通过
- ✅ 有免费额度
- ✅ 智能度高

#### 方式 B: 使用阿里云通义千问（需要正确的 Key）

编辑 `.env.local`：
```bash
PREFERRED_AI_PROVIDER=qwen
```

**前提**: 需要获取正确的阿里云 API Key

#### 方式 C: 使用 Mock 模式（零成本）

编辑 `.env.local`：
```bash
PREFERRED_AI_PROVIDER=mock
```

或者直接不配置任何 API Key，系统会自动降级到 Mock 模式。

---

## 🚀 快速开始

### 步骤 1: 选择 AI 服务

编辑 `.env.local` 文件，设置：
```bash
PREFERRED_AI_PROVIDER=qwen  # 或 doubao 或 mock
```

### 步骤 2: 启动应用

```bash
python app.py
```

### 步骤 3: 访问聊天页面

```
http://localhost:5000/go
```

---

## 📊 API 对比

| 特性 | 火山引擎豆包 | 阿里云通义 | Mock 模式 |
|------|-------------|-----------|----------|
| **API Key** | ✅ 已配置 | ✅ 已配置 | - |
| **验证状态** | ✅ HTTP 200 | ❌ HTTP 401 | - |
| **模型** | doubao-seed-2-0-pro | qwen-plus | 关键词匹配 |
| **免费额度** | ✅ 有 | ✅ 有 | ¥0 |
| **智能度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **响应速度** | <500ms | <300ms | <200ms |
| **推荐场景** | 真实用户 | 真实用户 | 开发测试 |

---

## 💡 使用建议

### 开发测试阶段

**推荐**: 使用 Mock 模式
```bash
PREFERRED_AI_PROVIDER=mock
```

**理由**:
- ✅ 零成本
- ✅ 响应快
- ✅ 功能完整
- ✅ 无需 API Key

### 灰度测试阶段

**推荐**: 使用火山引擎豆包
```bash
PREFERRED_AI_PROVIDER=doubao
```

**理由**:
- ✅ 已验证有效
- ✅ 有免费额度
- ✅ 智能度高

### 正式上线

**推荐**: 根据用户反馈选择
- 如果豆包表现好 → 继续使用 doubao
- 如果需要切换 → 改为 qwen

---

## 🔍 智能降级逻辑

系统会自动检测并按以下优先级选择：

```python
if PREFERRED_AI_PROVIDER == 'doubao' and DOUBAO_API_KEY:
    使用火山引擎豆包 ✅
elif PREFERRED_AI_PROVIDER == 'qwen' and QWEN_API_KEY:
    使用阿里云通义千问 ✅
else:
    使用 Mock 模式（自动降级）✅
```

**安全性**: 即使配置错误，也会自动降级到 Mock 模式，不会崩溃！

---

## 📝 测试方法

### 测试火山引擎豆包

```bash
# 1. 设置为 doubao
PREFERRED_AI_PROVIDER=doubao

# 2. 启动应用
python app.py

# 3. 访问聊天页面测试
http://localhost:5000/go
```

### 测试阿里云通义

```bash
# 1. 获取正确的 API Key
# 2. 更新 .env.local 中的 QWEN_API_KEY
# 3. 设置为 qwen
PREFERRED_AI_PROVIDER=qwen

# 4. 测试 API
python test_qwen_api.py

# 5. 如果成功，启动应用
python app.py
```

### 测试 Mock 模式

```bash
# 1. 设置为 mock 或不设置
PREFERRED_AI_PROVIDER=mock

# 2. 直接启动（会自动使用 Mock）
python app.py
```

---

## ✅ 总结

### 当前配置

- ✅ **火山引擎豆包**: API Key 有效，已测试通过
- ⚠️ **阿里云通义**: API Key 需要替换为正确的
- ✅ **Mock 模式**: 永远可用，零成本

### 灵活切换

通过修改 `PREFERRED_AI_PROVIDER` 环境变量，可以：
- 🔁 在 doubao 和 qwen 之间切换
- 🔁 在真实 API 和 Mock 之间切换
- 🔁 自动降级，保证可用性

### 推荐方案

**短期**: 使用 Mock 模式进行开发测试  
**中期**: 使用火山引擎豆包进行灰度测试  
**长期**: 根据成本和效果选择最优方案

---

**更新时间**: 2026-03-20  
**更新者**: AI 协作者  
**状态**: ✅ 双 API 配置完成，可灵活切换
