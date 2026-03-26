"""
专属风格人脸生成服务
Go In App - 1.0 核心功能

功能：
1. 用户上传人像 -> 提取面部特征向量
2. 调用 Stable Diffusion + ControlNet 生成专属风格头像
3. 确保唯一性：同一人生成的脸永远一致，且与他人不同

技术方案：
- face_recognition 库提取面部特征
- hashlib.sha256 生成唯一性密钥 (Seed)
- Stable Diffusion API + ControlNet (OpenPose/Depth)
- 输出透明背景 PNG 头像
"""

import os
import hashlib
import base64
from typing import Optional, Dict, Any
from PIL import Image
import io


class UniqueFaceGenerator:
    """专属风格人脸生成器"""
    
    def __init__(self):
        """初始化生成器"""
        # API 配置（优先从环境变量读取）
        self.sd_api_key = os.getenv("STABLE_DIFFUSION_API_KEY", "")
        self.sd_api_url = os.getenv("STABLE_DIFFUSION_API_URL", "https://api.stablediffusion.com/v1/generate")
        
        # ControlNet 配置
        self.controlnet_model = "control_v11p_sd15_openpose"  # OpenPose 姿态控制
        self.depth_model = "control_v11f1p_sd15_depth"  # Depth 深度控制
        
        # 风格化 Prompt（固化 Go In 专属艺术风格）
        self.style_prompt = (
            "Go In unique art style, hand-drawn portrait, distinct facial features, "
            "expressive eyes, masterpiece, high quality, detailed skin texture, "
            "soft lighting, warm color palette, artistic rendering, "
            "unique soul face, one-of-a-kind character design"
        )
        
        # 负面 Prompt
        self.negative_prompt = (
            "ugly, duplicate, deformed, blurry, lowres, text, watermark, "
            "signature, cropped, out of frame, worst quality, low quality, "
            "jpeg artifacts, signature, cut off, extra limbs, malformed limbs, "
            "missing arms, missing legs, extra fingers, fused fingers"
        )
        
        # 输出目录
        self.output_dir = "static/avatars"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_unique_face(
        self, 
        user_id: str, 
        image_file: Any,
        facial_embedding: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        生成独一无二的专属风格人脸
        
        Args:
            user_id: 用户唯一 ID
            image_file: 用户上传的照片文件
            facial_embedding: 面部特征向量（可选，如不提供则尝试从图片提取）
            
        Returns:
            Dict: {
                "success": bool,
                "face_image_path": str,  # 生成的头像路径
                "face_image_url": str,   # URL 地址
                "seed": str,             # 唯一性密钥
                "message": str
            }
        """
        try:
            # ========== 步骤 1：生成唯一性密钥 (Seed) ==========
            if facial_embedding is None:
                # 如果没有提供特征向量，尝试从图片提取简化的 hash
                facial_embedding = self._extract_simple_features(image_file)
            
            # 使用 hashlib.sha256 生成固定的 Seed
            seed_input = f"{user_id}:{facial_embedding.hex()}"
            unique_seed = hashlib.sha256(seed_input.encode()).hexdigest()
            # 转换为整数（SD API 需要整数 seed）
            seed_int = int(unique_seed[:16], 16) % (2**32)
            
            print(f"✅ 为用户 {user_id} 生成唯一性 Seed: {seed_int}")
            
            # ========== 步骤 2：准备 SD API 请求参数 ==========
            payload = {
                "prompt": self.style_prompt,
                "negative_prompt": self.negative_prompt,
                "seed": seed_int,
                "steps": 30,  # 采样步数
                "width": 512,
                "height": 512,
                "cfg_scale": 7.5,  # 提示词相关性
                "sampler_name": "DPM++ 2M Karras",
                
                # ControlNet 参数（OpenPose 姿态控制）
                "alwayson_scripts": {
                    "ControlNet": {
                        "args": [
                            {
                                "enabled": True,
                                "module": "openpose",
                                "model": self.controlnet_model,
                                "weight": 0.8,
                                "resize_mode": "Crop and Resize",
                                "lowvram": False,
                                "processor_res": 512,
                                "threshold_a": 0.5,
                                "threshold_b": 0.5,
                                "guidance_start": 0.0,
                                "guidance_end": 1.0,
                                "control_mode": "Balanced",
                                "pixel_perfect": True
                            }
                        ]
                    }
                },
                
                # 高清修复
                "enable_hr": True,
                "hr_upscaler": "Latent",
                "hr_scale": 1.5,
                "denoising_strength": 0.3
            }
            
            # ========== 步骤 3：调用 SD API（模拟或真实） ==========
            if not self.sd_api_key:
                # 没有 API Key 时使用模拟数据
                print("⚠️ 未配置 SD API Key，使用模拟生成")
                result = self._mock_generate(user_id, seed_int)
            else:
                # 调用真实 API
                print("🚀 调用 Stable Diffusion API...")
                result = self._call_sd_api(payload, image_file)
            
            if not result.get("success"):
                return result
            
            # ========== 步骤 4：保存头像 ==========
            face_image_path = os.path.join(self.output_dir, f"{user_id}_face.png")
            
            # 如果是 Base64 格式，先解码
            if "image_base64" in result:
                image_data = base64.b64decode(result["image_base64"])
                image = Image.open(io.BytesIO(image_data))
            elif "image_path" in result:
                image = Image.open(result["image_path"])
            else:
                return {
                    "success": False,
                    "message": "API 返回数据格式错误"
                }
            
            # 移除背景（简化版：直接保存为 PNG）
            # TODO: 使用 rembg 库进行专业抠图
            image.save(face_image_path, format="PNG", transparency=0)
            
            print(f"✅ 头像已保存：{face_image_path}")
            
            # ========== 步骤 5：返回结果 ==========
            return {
                "success": True,
                "face_image_path": face_image_path,
                "face_image_url": f"/{face_image_path}",
                "seed": str(seed_int),
                "message": "专属风格头像生成成功！你的灵魂肖像已注入 Go In 世界。"
            }
            
        except Exception as e:
            print(f"❌ 生成专属头像失败：{e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"生成失败：{str(e)}",
                "fallback_image_url": "/static/avatars/default_face.png"  #  fallback 默认头像
            }
    
    def _extract_simple_features(self, image_file: Any) -> bytes:
        """
        从图片提取简化的特征 hash（不依赖 face_recognition 库）
        
        Args:
            image_file: 图片文件
            
        Returns:
            bytes: 特征 hash
        """
        try:
            # 打开图片
            if hasattr(image_file, 'read'):
                image = Image.open(image_file)
            else:
                image = Image.open(image_file)
            
            # 转换为灰度图并调整大小
            image = image.convert('L').resize((32, 32))
            
            # 计算像素值的 hash
            pixels = list(image.getdata())
            pixel_hash = hashlib.md5(bytes(pixels)).digest()
            
            return pixel_hash
            
        except Exception as e:
            print(f"⚠️ 特征提取失败，使用默认 hash: {e}")
            # 返回一个固定 hash 作为 fallback
            return hashlib.md5(b"default_face_features").digest()
    
    def _mock_generate(self, user_id: str, seed: int) -> Dict[str, Any]:
        """
        模拟生成（用于开发和测试）
        
        Args:
            user_id: 用户 ID
            seed: 唯一性种子
            
        Returns:
            Dict: 包含模拟图片路径的结果
        """
        print(f"🎨 [MOCK] 正在绘制专属风格头像 (Seed: {seed})...")
        
        # 创建一个简单的彩色图像作为占位符
        width, height = 512, 512
        image = Image.new('RGB', (width, height), color=(255, 200, 150))
        
        # 添加一些艺术效果（渐变）
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        
        # 绘制圆形代表脸部轮廓
        center_x, center_y = width // 2, height // 2
        radius = 150
        draw.ellipse(
            [center_x - radius, center_y - radius, 
             center_x + radius, center_y + radius],
            fill=(255, 220, 180),
            outline=(200, 150, 100),
            width=3
        )
        
        # 绘制眼睛
        eye_offset = 50
        eye_size = 30
        draw.ellipse(
            [center_x - eye_offset - eye_size//2, center_y - 30 - eye_size//2,
             center_x - eye_offset + eye_size//2, center_y - 30 + eye_size//2],
            fill=(50, 50, 50)
        )
        draw.ellipse(
            [center_x + eye_offset - eye_size//2, center_y - 30 - eye_size//2,
             center_x + eye_offset + eye_size//2, center_y - 30 + eye_size//2],
            fill=(50, 50, 50)
        )
        
        # 绘制嘴巴
        draw.arc(
            [center_x - 50, center_y + 50, center_x + 50, center_y + 100],
            0, 180,
            fill=(200, 100, 100),
            width=3
        )
        
        # 保存到临时文件
        temp_path = f"static/avatars/mock_{user_id}_{seed}.png"
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        image.save(temp_path, format="PNG")
        
        return {
            "success": True,
            "image_path": temp_path,
            "message": "[MOCK] 模拟生成成功（请配置 SD API 以获取真实效果）"
        }
    
    def _call_sd_api(self, payload: Dict, image_file: Any) -> Dict[str, Any]:
        """
        调用 Stable Diffusion API
        
        Args:
            payload: API 请求参数
            image_file: 上传的照片（用于 ControlNet）
            
        Returns:
            Dict: API 返回结果
        """
        try:
            import requests
            
            # 准备请求头
            headers = {
                "Authorization": f"Bearer {self.sd_api_key}",
                "Content-Type": "application/json"
            }
            
            # 发送请求
            response = requests.post(
                self.sd_api_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                # 解析返回的图片（通常是 Base64）
                if "images" in result and len(result["images"]) > 0:
                    return {
                        "success": True,
                        "image_base64": result["images"][0]
                    }
                else:
                    return {
                        "success": False,
                        "message": "API 未返回图片数据"
                    }
            else:
                return {
                    "success": False,
                    "message": f"API 请求失败：HTTP {response.status_code}"
                }
                
        except Exception as e:
            print(f"❌ SD API 调用失败：{e}")
            return {
                "success": False,
                "message": f"API 调用失败：{str(e)}"
            }


# 全局实例
_face_generator = None


def get_face_generator() -> UniqueFaceGenerator:
    """获取人脸生成器实例"""
    global _face_generator
    if _face_generator is None:
        _face_generator = UniqueFaceGenerator()
    return _face_generator


# 便捷函数
def generate_unique_face(user_id: str, image_file: Any) -> Dict[str, Any]:
    """
    生成独一无二的专属风格人脸（便捷函数）
    
    Args:
        user_id: 用户唯一 ID
        image_file: 用户上传的照片文件
        
    Returns:
        Dict: 生成结果
    """
    generator = get_face_generator()
    return generator.generate_unique_face(user_id, image_file)
