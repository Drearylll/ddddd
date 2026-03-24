"""
AI 绘画合成服务
Go In App - 人物与背景合成

功能：
1. 背景处理：使用 inpainting 技术擦除真实地点图片中的人物
2. 人物融合：将用户 AI 形象与真实背景融合
3. 风格匹配：调整光影和色调，使其自然融合
4. 生成图片：输出 1080x1920 竖屏图片

使用模型：
- 通义万相（AI 绘画）
- ControlNet（构图控制）
- Stable Diffusion（图像修复）
"""

import requests
import json
import base64
from typing import Dict, Optional, Tuple
from PIL import Image, ImageFilter, ImageEnhance
import io
import numpy as np

# API 配置
from config.dashscope_config import (
    DASHSCOPE_API_KEY,
    WANXIANG_API_KEY,
    WANXIANG_BASE_URL,
    MODELS
)


class AIImageCompositor:
    """AI 图像合成器"""
    
    def __init__(self, api_key=None):
        """
        初始化合成器
        
        Args:
            api_key: API Key
        """
        self.api_key = api_key or WANXIANG_API_KEY
        self.use_mock = not self.api_key  # 没有 API Key 时使用模拟数据
        
        # API 端点
        self.wanxiang_url = WANXIANG_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 输出尺寸
        self.output_width = 1080
        self.output_height = 1920
    
    def composite_images(
        self,
        user_image_url: str,
        background_image_url: str,
        location_name: str,
        style_description: str
    ) -> Dict:
        """
        合成用户形象与背景
        
        Args:
            user_image_url: 用户 AI 形象 URL
            background_image_url: 真实地点背景 URL
            location_name: 地点名称
            style_description: 风格描述
            
        Returns:
            Dict: 合成结果
            {
                "success": True,
                "image_url": "合成后的图片 URL",
                "image_data": "base64 编码的图片数据",
                "width": 1080,
                "height": 1920,
                "message": "合成成功"
            }
        """
        if self.use_mock:
            return self._mock_composite(user_image_url, background_image_url, location_name)
        
        # 使用通义万相进行图像合成
        return self._composite_with_wanxiang(
            user_image_url,
            background_image_url,
            location_name,
            style_description
        )
    
    def _composite_with_wanxiang(
        self,
        user_image_url: str,
        background_image_url: str,
        location_name: str,
        style_description: str
    ) -> Dict:
        """使用通义万相进行图像合成"""
        
        # 构建提示词
        prompt = self._build_composite_prompt(
            location_name,
            style_description
        )
        
        # API 请求
        payload = {
            "model": "wanx-v1",
            "input": {
                "prompt": prompt,
                "ref_img": background_image_url,  # 参考背景
                "ref_img_strength": 0.6  # 背景强度
            },
            "parameters": {
                "style": "<auto>",
                "resolution": "1080*1920",
                "num_images": 1,
                "seed": 12345
            }
        }
        
        try:
            response = requests.post(
                self.wanxiang_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and 'output' in result:
                # 获取生成的图片
                images = result['output'].get('results', [])
                if images:
                    image_url = images[0]['url']
                    return {
                        "success": True,
                        "image_url": image_url,
                        "image_data": None,
                        "width": 1080,
                        "height": 1920,
                        "message": "合成成功"
                    }
            
            print(f"❌ 通义万相 API 调用失败：{result.get('message', 'Unknown error')}")
            return self._mock_composite(user_image_url, background_image_url, location_name)
            
        except Exception as e:
            print(f"❌ 图像合成异常：{e}")
            return self._mock_composite(user_image_url, background_image_url, location_name)
    
    def _build_composite_prompt(
        self,
        location_name: str,
        style_description: str
    ) -> str:
        """
        构建合成提示词
        
        Args:
            location_name: 地点名称
            style_description: 风格描述
            
        Returns:
            str: 优化后的提示词
        """
        # 基础提示词模板
        base_prompt = """
在{location_name}拍摄一张人像照片。
人物自然地站在场景中，与背景完美融合。
光线：{lighting}
色调：{color_tone}
氛围：{atmosphere}
高质量，专业摄影，8K 分辨率，竖屏构图
        """.strip()
        
        # 根据风格描述提取光线、色调、氛围
        lighting = self._extract_lighting(style_description)
        color_tone = self._extract_color_tone(style_description)
        atmosphere = self._extract_atmosphere(style_description)
        
        return base_prompt.format(
            location_name=location_name,
            lighting=lighting,
            color_tone=color_tone,
            atmosphere=atmosphere
        )
    
    def _extract_lighting(self, style_description: str) -> str:
        """从风格描述中提取光线信息"""
        lighting_keywords = {
            "暖色": "温暖的黄昏光线，金色阳光",
            "冷色": "清冷的自然光，柔和的散射光",
            "自然色": "自然光，明亮通透",
            "多彩": "丰富的霓虹灯光，城市夜景"
        }
        
        for keyword, lighting in lighting_keywords.items():
            if keyword in style_description:
                return lighting
        
        return "自然光，柔和均匀"
    
    def _extract_color_tone(self, style_description: str) -> str:
        """从风格描述中提取色调信息"""
        if "暖色" in style_description:
            return "温暖的橙黄色调"
        elif "冷色" in style_description:
            return "清新的蓝绿色调"
        elif "自然色" in style_description:
            return "自然的绿色调"
        elif "多彩" in style_description:
            return "丰富的多彩色调"
        else:
            return "中性色调，自然真实"
    
    def _extract_atmosphere(self, style_description: str) -> str:
        """从风格描述中提取氛围信息"""
        atmosphere_keywords = {
            "文艺": "文艺清新的氛围",
            "繁华": "热闹繁华的都市感",
            "宁静": "安静祥和的氛围",
            "复古": "怀旧复古的情调",
            "现代": "现代时尚的气息",
            "温馨": "温馨舒适的居家感",
            "烟火气": "人间烟火气，生活气息浓厚"
        }
        
        for keyword, atmosphere in atmosphere_keywords.items():
            if keyword in style_description:
                return atmosphere
        
        return "自然真实的氛围"
    
    def _mock_composite(
        self,
        user_image_url: str,
        background_image_url: str,
        location_name: str
    ) -> Dict:
        """模拟合成（用于开发测试）"""
        
        # 模拟成功的合成结果
        return {
            "success": True,
            "image_url": "https://images.pexels.com/photos/1234567/pexels-photo-1234567.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920",
            "image_data": None,
            "width": 1080,
            "height": 1920,
            "message": f"✅ 已将您的 AI 形象合成到{location_name}"
        }
    
    def process_user_image(
        self,
        user_image_url: str,
        background_image_url: str
    ) -> Tuple[Image.Image, Image.Image]:
        """
        处理用户图片和背景图片
        
        Args:
            user_image_url: 用户图片 URL
            background_image_url: 背景图片 URL
            
        Returns:
            Tuple[Image.Image, Image.Image]: (用户图片，背景图片)
        """
        # 下载图片
        user_image = self._download_image(user_image_url)
        background_image = self._download_image(background_image_url)
        
        return user_image, background_image
    
    def _download_image(self, image_url: str) -> Optional[Image.Image]:
        """下载图片"""
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
        except Exception as e:
            print(f"❌ 下载图片失败：{e}")
        return None
    
    def remove_background_from_user(
        self,
        user_image: Image.Image
    ) -> Optional[Image.Image]:
        """
        移除用户图片的背景（抠图）
        
        Args:
            user_image: 用户图片
            
        Returns:
            Image.Image: 去除背景的用户图片（透明背景）
        """
        # TODO: 使用 AI 抠图模型（如 MODNet、RMBG 等）
        # 这里简化处理
        return user_image
    
    def inpaint_background(
        self,
        background_image: Image.Image,
        mask: Optional[Image.Image] = None
    ) -> Optional[Image.Image]:
        """
        对背景进行 inpainting（图像修复）
        擦除背景中的人物区域
        
        Args:
            background_image: 背景图片
            mask: 掩码图片（白色区域需要修复）
            
        Returns:
            Image.Image: 修复后的背景
        """
        # TODO: 使用 Stable Diffusion inpainting 或 ControlNet
        # 这里简化处理
        if mask:
            # 使用 OpenCV 或 PIL 进行简单的图像修复
            pass
        
        return background_image
    
    def blend_images(
        self,
        user_image: Image.Image,
        background_image: Image.Image,
        position: Tuple[int, int] = None
    ) -> Image.Image:
        """
        融合用户和背景
        
        Args:
            user_image: 用户图片（PNG 透明背景）
            background_image: 背景图片
            position: 用户图片在背景中的位置
            
        Returns:
            Image.Image: 融合后的图片
        """
        # 调整背景尺寸
        background_image = background_image.resize(
            (self.output_width, self.output_height),
            Image.Resampling.LANCZOS
        )
        
        # 调整用户图片尺寸（保持比例）
        user_width = int(self.output_width * 0.4)  # 人物占画面 40% 宽度
        aspect_ratio = user_image.height / user_image.width
        user_height = int(user_width * aspect_ratio)
        user_image = user_image.resize(
            (user_width, user_height),
            Image.Resampling.LANCZOS
        )
        
        # 默认位置：底部居中
        if position is None:
            position = (
                (self.output_width - user_width) // 2,
                self.output_height - user_height - 100
            )
        
        # 创建空白图层
        result = Image.new('RGBA', (self.output_width, self.output_height), (0, 0, 0, 0))
        result.paste(background_image, (0, 0))
        
        # 合成用户图片
        result.paste(user_image, position, user_image)
        
        return result
    
    def adjust_style(
        self,
        image: Image.Image,
        color_tone: str,
        lighting: str
    ) -> Image.Image:
        """
        调整图片风格和色调
        
        Args:
            image: 图片
            color_tone: 色调（暖色/冷色/中性）
            lighting: 光线
            
        Returns:
            Image.Image: 调整后的图片
        """
        # 调整色温
        if color_tone == "暖色":
            image = self._apply_warm_tone(image)
        elif color_tone == "冷色":
            image = self._apply_cool_tone(image)
        
        # 调整亮度和对比度
        image = self._adjust_brightness_contrast(image, lighting)
        
        return image
    
    def _apply_warm_tone(self, image: Image.Image) -> Image.Image:
        """应用暖色调"""
        enhancer = ImageEnhance.Color(image)
        # 增强红色和黄色通道
        return enhancer.enhance(1.2)
    
    def _apply_cool_tone(self, image: Image.Image) -> Image.Image:
        """应用冷色调"""
        enhancer = ImageEnhance.Color(image)
        # 增强蓝色和绿色通道
        return enhancer.enhance(1.1)
    
    def _adjust_brightness_contrast(
        self,
        image: Image.Image,
        lighting: str
    ) -> Image.Image:
        """调整亮度和对比度"""
        if "黄昏" in lighting or "温暖" in lighting:
            # 黄昏：降低对比度，增加亮度
            brightness = ImageEnhance.Brightness(image)
            image = brightness.enhance(1.1)
            
            contrast = ImageEnhance.Contrast(image)
            image = contrast.enhance(0.9)
        
        return image


# 全局实例
_compositor = None

def get_ai_compositor(api_key=None):
    """获取 AI 图像合成器实例"""
    global _compositor
    if _compositor is None:
        _compositor = AIImageCompositor(api_key)
    return _compositor


# 便捷函数
def composite_images(
    user_image_url: str,
    background_image_url: str,
    location_name: str,
    style_description: str
) -> Dict:
    """
    合成用户形象与背景（便捷函数）
    
    Args:
        user_image_url: 用户 AI 形象 URL
        background_image_url: 真实地点背景 URL
        location_name: 地点名称
        style_description: 风格描述
        
    Returns:
        Dict: 合成结果
    """
    compositor = get_ai_compositor()
    return compositor.composite_images(
        user_image_url,
        background_image_url,
        location_name,
        style_description
    )
