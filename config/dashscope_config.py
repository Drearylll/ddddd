"""
阿里云百炼 API 配置
Go In App - AI 绘画服务配置
"""

# 阿里云百炼 API 配置
DASHSCOPE_API_KEY = "sk-2274b3d46339f95092d68b83150ead7f"  # 阿里云百炼 API Key（已更新）
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"

# 通义万相 API（AI 绘画）
WANXIANG_API_KEY = "sk-2274b3d46339f95092d68b83150ead7f"  # 通义万相 API Key（已更新）
WANXIANG_BASE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image-generation"

# 通义千问 API（文案生成）
QWEN_API_KEY = "sk-2274b3d46339f95092d68b83150ead7f"  # 通义千问 API Key（已更新）
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation"

# 通义千问 VL API（多模态图像分析）
QWEN_VL_API_KEY = "sk-2274b3d46339f95092d68b83150ead7f"  # 通义千问 VL API Key（已更新）
QWEN_VL_BASE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation"

# 模型配置（已更新为真实可用的模型）
MODELS = {
    # 通义万相（AI 绘画）
    "wanxiang": {
        "model": "qwen-image-2.0-pro",  # 通义万相图像生成 2.0 Pro 版
        "api_key": WANXIANG_API_KEY,
        "base_url": WANXIANG_BASE_URL
    },
    
    # 通义千问（文案生成）
    "qwen": {
        "model": "tongyi-xiaomi-analysis-pro",  # 通义千问分析 Pro 版
        "api_key": QWEN_API_KEY,
        "base_url": QWEN_BASE_URL
    },
    
    # 通义千问 VL（多模态图像分析）
    "qwen-vl": {
        "model": "qwen3-vl-embedding",  # 通义千问 VL 嵌入模型
        "api_key": QWEN_VL_API_KEY,
        "base_url": QWEN_VL_BASE_URL
    },
    
    # 通义千问 TTS（语音合成）
    "qwen-tts": {
        "model": "qwen3-tts-vd-2026-01-26",  # 通义千问语音合成
        "api_key": QWEN_API_KEY,
        "base_url": QWEN_BASE_URL
    }
}

# 默认模型
DEFAULT_MODEL = "qwen"  # 默认使用通义千问分析 Pro 版
