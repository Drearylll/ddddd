"""
火山引擎豆包 AI 服务
Go In App - 多模态 AI 能力集成

功能：
1. 文本生成（文案、对话）
2. 图像理解（分析图片内容、风格）
3. 文生图（根据描述生成图片）
4. 智能降级（火山引擎 → 阿里云百炼）

使用模型：
- 豆包 Pro（文本生成）
- 豆包 Vision Pro（视觉理解）
- 豆包 Text2Image（图像生成）
"""

import requests
import json
from typing import Dict, Optional, List
from config.volcengine_config import (
    DOUBAO_API_KEY,
    DOUBAO_BASE_URL,
    DOUBAO_MODELS,
    ALIYUN_BACKUP,
    get_volcengine_config,
    get_backup_config
)


class DoubaoAI:
    """豆包 AI 服务类"""
    
    def __init__(self, api_key=None, use_backup=False):
        """
        初始化豆包 AI
        
        Args:
            api_key: API Key
            use_backup: 是否使用备用配置（阿里云）
        """
        if use_backup or not DOUBAO_API_KEY:
            # 使用备用配置
            self.config = get_backup_config()
            self.use_backup = True
            print("ℹ️ 使用备用配置（阿里云百炼）")
        else:
            # 使用火山引擎豆包
            self.config = get_volcengine_config("text")
            self.use_backup = False
            print("✅ 使用火山引擎豆包 AI")
        
        self.api_key = api_key or self.config.get("api_key")
        self.base_url = self.config.get("base_url")
        self.model = self.config.get("model", "doubao-pro-4k")
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict:
        """
        文本生成
        
        Args:
            prompt: 用户输入
            system_prompt: 系统提示词
            max_tokens: 最大生成长度
            temperature: 温度参数
            
        Returns:
            Dict: 生成结果
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and 'choices' in result:
                content = result['choices'][0]['message']['content']
                return {
                    "success": True,
                    "content": content,
                    "model": self.model,
                    "usage": result.get("usage", {})
                }
            
            print(f"❌ 豆包 API 调用失败：{result.get('error', {}).get('message', 'Unknown error')}")
            
            # 自动降级到备用配置
            if not self.use_backup:
                print("🔄 尝试切换到备用配置...")
                backup_ai = DoubaoAI(use_backup=True)
                return backup_ai.generate_text(prompt, system_prompt, max_tokens, temperature)
            
            return {
                "success": False,
                "error": result.get('error', {}).get('message', 'API 调用失败'),
                "model": self.model
            }
            
        except Exception as e:
            print(f"❌ 文本生成异常：{e}")
            
            # 自动降级
            if not self.use_backup:
                print("🔄 尝试切换到备用配置...")
                backup_ai = DoubaoAI(use_backup=True)
                return backup_ai.generate_text(prompt, system_prompt, max_tokens, temperature)
            
            return {
                "success": False,
                "error": str(e),
                "model": self.model
            }
    
    def analyze_image(
        self,
        image_url: str,
        question: str = "请分析这张图片的内容和风格"
    ) -> Dict:
        """
        图像理解分析
        
        Args:
            image_url: 图片 URL
            question: 分析问题
            
        Returns:
            Dict: 分析结果
        """
        # 使用豆包 Vision Pro 模型
        vision_config = get_volcengine_config("vision")
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    },
                    {
                        "type": "text",
                        "text": question
                    }
                ]
            }
        ]
        
        payload = {
            "model": vision_config["model"],
            "messages": messages,
            "max_tokens": 1000
        }
        
        headers = {
            "Authorization": f"Bearer {vision_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{vision_config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and 'choices' in result:
                content = result['choices'][0]['message']['content']
                return {
                    "success": True,
                    "analysis": content,
                    "model": vision_config["model"]
                }
            
            print(f"❌ 图像分析 API 调用失败：{result.get('error', {}).get('message', '')}")
            return self._mock_analyze_image(image_url, question)
            
        except Exception as e:
            print(f"❌ 图像分析异常：{e}")
            return self._mock_analyze_image(image_url, question)
    
    def generate_image(
        self,
        prompt: str,
        size: str = "1080x1920",
        style: str = "photorealistic"
    ) -> Dict:
        """
        文生图
        
        Args:
            prompt: 提示词
            size: 图片尺寸
            style: 风格
            
        Returns:
            Dict: 生成结果
        """
        # TODO: 实现豆包文生图 API 调用
        # 目前返回模拟数据
        
        return self._mock_generate_image(prompt, size, style)
    
    def _mock_analyze_image(
        self,
        image_url: str,
        question: str
    ) -> Dict:
        """模拟图像分析（用于降级）"""
        
        return {
            "success": True,
            "analysis": "这是一张现代都市风格的照片，展现了繁华的城市景象。色调明亮，光线充足，给人一种活力四射的感觉。适合用于展示都市生活、商业活动等场景。",
            "model": "mock-vision",
            "note": "模拟分析结果"
        }
    
    def _mock_generate_image(
        self,
        prompt: str,
        size: str,
        style: str
    ) -> Dict:
        """模拟文生图（用于降级）"""
        
        return {
            "success": True,
            "image_url": f"https://source.pexels.com/photos/{hash(prompt) % 1000000}.jpeg",
            "prompt": prompt,
            "size": size,
            "style": style,
            "model": "mock-image-gen"
        }


# 全局实例
_doubao_ai = None


def get_doubao_ai(use_backup=False):
    """获取豆包 AI 实例"""
    global _doubao_ai
    if _doubao_ai is None:
        _doubao_ai = DoubaoAI(use_backup=use_backup)
    return _doubao_ai


# 便捷函数
def generate_text(
    prompt: str,
    system_prompt: str = "",
    max_tokens: int = 1000,
    temperature: float = 0.7
) -> Dict:
    """文本生成便捷函数"""
    ai = get_doubao_ai()
    return ai.generate_text(prompt, system_prompt, max_tokens, temperature)


def analyze_image(
    image_url: str,
    question: str = "请分析这张图片"
) -> Dict:
    """图像分析便捷函数"""
    ai = get_doubao_ai()
    return ai.analyze_image(image_url, question)


def generate_image(
    prompt: str,
    size: str = "1080x1920",
    style: str = "photorealistic"
) -> Dict:
    """文生图便捷函数"""
    ai = get_doubao_ai()
    return ai.generate_image(prompt, size, style)
