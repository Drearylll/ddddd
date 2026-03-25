# Go In App API 配置说明

## ✅ 已配置的 API

### 1. 通义千问（AI 内容生成）

**状态**: ⚠️ 已配置但账户欠费  
**API Key**: `sk-87930805570a46c38f5eefa1c03cd2e6`  
**配置文件**: `services/ai_content.py`  
**当前模式**: 模拟数据（优雅降级）

**欠费提示**:
```json
{
  "code": "Arrearage",
  "message": "Access denied, please make sure your account is in good standing"
}
```

**解决方案**:
1. 访问阿里云控制台：https://dashscope.console.aliyun.com/
2. 充值账户
3. 开通通义千问服务
4. 确保有可用的免费额度或付费额度

**当前功能**:
- ✅ 短篇小说生成（模拟）
- ✅ 四格漫画脚本生成（模拟）
- ✅ 朋友圈文案生成（模拟）

---

## 🔧 待配置的 API

### 2. 高德地图（地理位置）

**状态**: ❌ 未配置  
**配置文件**: `services/location.py`  
**当前模式**: 模拟数据

**申请步骤**:
1. 访问高德开放平台：https://lbs.amap.com/
2. 注册/登录账号
3. 创建应用，获取 API Key
4. 开通 Web 服务 API
5. 配置 `services/location.py`:
   ```python
   GAODE_API_KEY = "你的高德 API Key"
   ```

**功能**:
- 周边搜索（咖啡厅、餐厅、景点等）
- 距离计算
- 步行时间估算
- 地理编码

---

### 3. AI 图像生成（预留）

**状态**: ⏸️ 预留接口  
**推荐服务**:
- Stable Diffusion API
- DALL-E 3 (OpenAI)
- 通义万相（阿里）

**后续配置**:
1. 选择图像生成服务商
2. 申请 API Key
3. 创建 `services/image_synthesis.py`
4. 实现头像 + 场景融合

---

## 📊 当前系统状态

### ✅ 正常工作的功能
- 数据库持久化（SQLite + SQLAlchemy）
- 用户数据双重存储（内存 + 数据库）
- 评论功能（前端组件）
- 分享功能（前端组件）
- 共创功能（前端组件）
- AI 内容生成（模拟模式）
- 地理位置（模拟模式）

### ⚠️ 使用模拟数据的功能
- AI 内容生成（真实 API 欠费）
- 地理位置服务（未配置 API Key）

### 🎯 下一步行动

**优先级 1: 充值通义千问账户**
1. 访问：https://dashscope.console.aliyun.com/
2. 充值账户（新用户有免费额度）
3. 测试真实 API 调用

**优先级 2: 配置高德地图**
1. 申请 API Key
2. 更新 `services/location.py`
3. 测试周边搜索

**优先级 3: 图像合成**
1. 选择服务商
2. 申请 API Key
3. 实现图像合成功能

---

## 🔍 如何检查 API 状态

### 测试 AI 内容生成
```bash
python test_ai_api.py
```

**预期输出**:
- ✅ 如果成功：显示生成的内容
- ⚠️ 如果欠费：显示 HTTP 错误，但使用模拟数据

### 测试数据库
访问 http://localhost:5000/app_main，刷新页面数据不丢失即成功。

---

## 💡 降级机制说明

系统设计了完善的降级机制：

1. **API 调用失败** → 自动使用模拟数据
2. **无 API Key** → 自动使用模拟数据
3. **网络异常** → 自动使用模拟数据

**模拟数据特点**:
- 内容质量良好
- 符合现实逻辑
- 可用于开发和测试
- 不影响用户体验

---

## 📞 获取帮助

**阿里云百炼（通义千问）**:
- 控制台：https://dashscope.console.aliyun.com/
- 文档：https://help.aliyun.com/zh/model-studio/
- 错误码：https://help.aliyun.com/zh/model-studio/error-code

**高德地图**:
- 控制台：https://lbs.amap.com/
- 文档：https://lbs.amap.com/api/webservice/guide/

---

**当前系统可以正常使用，所有功能都有降级方案！** ✅
