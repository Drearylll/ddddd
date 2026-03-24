"""
火山引擎 API 配置
Go In App - 豆包/抖音/字节 AI 服务配置

火山引擎是字节跳动旗下的企业服务平台
提供豆包（Doubao）大模型、视频云、直播云等服务

API 文档：
https://www.volcengine.com/docs
"""

# 火山引擎 API 配置
VOLCENGINE_API_KEY = "de012cdc-ddcb-4695-a362-a67e26d5dcda"  # 火山引擎 API Key（已更新）
VOLCENGINE_API_SECRET = ""  # API Secret（如有需要请补充）
VOLCENGINE_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"  # 火山引擎方舟大模型 API

# 豆包大模型配置（Doubao）
# 豆包是字节推出的多功能大模型，支持文本、图像、语音等多模态任务
DOUBAO_API_KEY = "de012cdc-ddcb-4695-a362-a67e26d5dcda"  # 豆包 API Key
DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# 豆包模型版本（已更新为真实可用的模型）
DOUBAO_MODELS = {
    # 文本生成（使用 Doubao-Seed 系列）
    "text": {
        "model": "Doubao-Seed-2.0-pro",  # 豆包 Pro 版，高性能文本生成
        "api_key": DOUBAO_API_KEY,
        "base_url": DOUBAO_BASE_URL
    },
    
    # 轻量级文本生成（快速响应）
    "text_lite": {
        "model": "Doubao-Seed-2.0-lite",  # 豆包轻量版，快速低成本
        "api_key": DOUBAO_API_KEY,
        "base_url": DOUBAO_BASE_URL
    },
    
    # 迷你文本生成（极致性能）
    "text_mini": {
        "model": "Doubao-Seed-2.0-mini",  # 豆包迷你版，最快响应
        "api_key": DOUBAO_API_KEY,
        "base_url": DOUBAO_BASE_URL
    },
    
    # 代码生成
    "code": {
        "model": "Doubao-Seed-2.0-Code",  # 豆包代码专用
        "api_key": DOUBAO_API_KEY,
        "base_url": DOUBAO_BASE_URL
    },
    
    # 多模态理解（图像 + 文本）- 使用 Seedance 系列
    "vision": {
        "model": "Doubao-Seedance-1.5-pro",  # 豆包视觉理解，最强版本
        "api_key": DOUBAO_API_KEY,
        "base_url": DOUBAO_BASE_URL
    },
    
    # 视觉理解（轻量版）
    "vision_lite": {
        "model": "Doubao-Seedream-5.0-lite",  # 豆包视觉轻量版
        "api_key": DOUBAO_API_KEY,
        "base_url": DOUBAO_BASE_URL
    },
    
    # 视觉理解（快速版）
    "vision_fast": {
        "model": "Doubao-Seedance-1.0-pro-fast",  # 豆包视觉快速版
        "api_key": DOUBAO_API_KEY,
        "base_url": DOUBAO_BASE_URL
    },
    
    # 图像生成（文生图）- 使用 Seedream 系列
    "image_generation": {
        "model": "Doubao-Seedream-4.5",  # 豆包文生图 4.5 版本
        "api_key": DOUBAO_API_KEY,
        "base_url": DOUBAO_BASE_URL
    },
    
    # 向量嵌入（Embedding）
    "embedding": {
        "model": "Doubao-embedding",  # 标准版 Embedding
        "api_key": DOUBAO_API_KEY,
        "base_url": DOUBAO_BASE_URL
    },
    
    # 大型向量嵌入
    "embedding_large": {
        "model": "Doubao-embedding-large",  # 大型 Embedding
        "api_key": DOUBAO_API_KEY,
        "base_url": DOUBAO_BASE_URL
    },
    
    # 视觉向量嵌入
    "embedding_vision": {
        "model": "Doubao-embedding-vision",  # 视觉 Embedding
        "api_key": DOUBAO_API_KEY,
        "base_url": DOUBAO_BASE_URL
    },
    
    # 智能路由（自动选择最佳模型）
    "smart_router": {
        "model": "Doubao-Smart-Router",  # 智能路由
        "api_key": DOUBAO_API_KEY,
        "base_url": DOUBAO_BASE_URL
    }
}

# 默认使用的模型
DEFAULT_MODEL = "text"  # 默认使用 Doubao-Seed-2.0-pro

# 备用配置（阿里云百炼）
# 当火山引擎不可用时，可以降级到阿里云
ALIYUN_BACKUP = {
    "enabled": True,
    "api_key": "sk-2274b3d46339f95092d68b83150ead7f",
    "base_url": "https://dashscope.aliyuncs.com/api/v1"
}


def get_volcengine_config(service_type="text"):
    """
    获取火山引擎配置
    
    Args:
        service_type: 服务类型 ("text", "vision", "image_generation")
        
    Returns:
        dict: 配置信息
    """
    if service_type in DOUBAO_MODELS:
        return DOUBAO_MODELS[service_type]
    else:
        print(f"⚠️ 未知的服务类型：{service_type}，使用默认配置")
        return DOUBAO_MODELS["text"]


def get_backup_config():
    """
    获取备用配置（阿里云百炼）
    
    Returns:
        dict: 备用配置
    """
    return ALIYUN_BACKUP
