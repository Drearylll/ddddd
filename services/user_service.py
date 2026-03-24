"""
Go In 用户服务

负责用户注册、登录、头像处理等核心功能
"""

import uuid
import os
import json
from datetime import datetime
from PIL import Image, ImageFilter, ImageEnhance
import io
import base64


class UserService:
    """用户服务类"""
    
    @staticmethod
    def create_user_id():
        """创建唯一用户 ID"""
        return str(uuid.uuid4())[:8]
    
    @staticmethod
    def generate_avatar(user_photo, gender):
        """
        根据用户上传的照片生成二维手绘彩色头像
        
        Args:
            user_photo: 用户照片（文件对象或路径）
            gender: 性别 ('male' / 'female')
        
        Returns:
            dict: 生成的头像信息
        """
        try:
            # 打开图片
            if isinstance(user_photo, str):
                img = Image.open(user_photo)
            else:
                img = Image.open(io.BytesIO(user_photo.read()))
            
            # 调整大小为 512x512
            img = img.resize((512, 512), Image.Resampling.LANCZOS)
            
            # 转换为卡通风格
            avatar = UserService._apply_cartoon_style(img, gender)
            
            # 保存为 base64
            buffered = io.BytesIO()
            avatar.save(buffered, format="PNG")
            avatar_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # 生成头像元数据
            avatar_data = {
                'original_photo': user_photo if isinstance(user_photo, str) else None,
                'avatar_image': f'data:image/png;base64,{avatar_base64}',
                'gender': gender,
                'style': 'cartoon_2d',
                'created_at': datetime.now().isoformat(),
                'unique_id': str(uuid.uuid4())[:12]
            }
            
            return avatar_data
            
        except Exception as e:
            print(f"[ERROR] Failed to generate avatar: {e}")
            return None
    
    @staticmethod
    def _apply_cartoon_style(img, gender):
        """
        应用二维手绘卡通风格
        
        Args:
            img: PIL Image 对象
            gender: 性别
        
        Returns:
            PIL Image 对象（处理后的头像）
        """
        # 1. 边缘增强
        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        # 2. 色彩量化（减少颜色数量，形成卡通感）
        img = img.quantize(colors=64, method=Image.Quantize.MEDIANCUT)
        img = img.convert('RGB')
        
        # 3. 增强色彩饱和度
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.5)  # 增加 50% 饱和度
        
        # 4. 增强亮度
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.1)  # 增加 10% 亮度
        
        # 5. 根据性别调整色调
        if gender == 'female':
            # 女性：偏暖色调
            img = UserService._adjust_color_temperature(img, warm=True)
        else:
            # 男性：偏冷色调
            img = UserService._adjust_color_temperature(img, cool=True)
        
        # 6. 添加手绘效果（轻微模糊）
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # 7. 锐化边缘
        img = img.filter(ImageFilter.SHARPEN)
        
        return img
    
    @staticmethod
    def _adjust_color_temperature(img, warm=False, cool=False):
        """
        调整色温
        
        Args:
            img: PIL Image 对象
            warm: 是否调整为暖色调
            cool: 是否调整为冷色调
        
        Returns:
            PIL Image 对象
        """
        # 转换为 RGBA 以便处理
        img = img.convert('RGBA')
        pixels = img.load()
        
        for i in range(img.width):
            for j in range(img.height):
                r, g, b, a = pixels[i, j]
                
                if warm:
                    # 暖色调：增加红色和黄色
                    r = min(255, int(r * 1.1))
                    g = min(255, int(g * 1.05))
                elif cool:
                    # 冷色调：增加蓝色
                    b = min(255, int(b * 1.1))
                
                pixels[i, j] = (r, g, b, a)
        
        return img
    
    @staticmethod
    def validate_user_data(user_data):
        """
        验证用户数据完整性
        
        Args:
            user_data: 用户数据字典
        
        Returns:
            bool: 是否有效
        """
        required_fields = [
            'user_id',
            'username',
            'gender',
            'avatar_image'
        ]
        
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                return False
        
        return True
    
    @staticmethod
    def save_avatar_to_file(avatar_base64, user_id, output_dir='static/avatars'):
        """
        将头像保存到文件
        
        Args:
            avatar_base64: base64 编码的头像数据
            user_id: 用户 ID
            output_dir: 输出目录
        
        Returns:
            str: 保存的文件路径
        """
        try:
            # 确保目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 解码 base64
            if ',' in avatar_base64:
                avatar_base64 = avatar_base64.split(',')[1]
            
            image_data = base64.b64decode(avatar_base64)
            
            # 生成文件名
            filename = f'avatar_{user_id}_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join(output_dir, filename)
            
            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            # 返回相对路径
            return f'/{filepath}'
            
        except Exception as e:
            print(f"[ERROR] Failed to save avatar: {e}")
            return None
