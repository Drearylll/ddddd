"""
Go In 1.0 核心功能集成服务
统一封装三大核心功能：
1. UniqueFace - 专属风格人脸生成
2. RealityMirror - LBS 现实镜像与引导
3. FusionComposer - 虚实融合合成
"""

from services.unique_face import UniqueFaceGenerator, get_face_generator, generate_unique_face
from services.reality_mirror import RealityMirrorService, get_reality_mirror, get_nearby_real_places, generate_nudge_caption
from services.fusion_composer import FusionComposer, get_fusion_composer, generate_fused_scene


class GoInCoreServices:
    """Go In 核心服务集成类"""
    
    def __init__(self):
        """初始化所有核心服务"""
        self.face_generator = get_face_generator()
        self.reality_mirror = get_reality_mirror()
        self.fusion_composer = get_fusion_composer()
    
    def create_parallel_world_moment(self, user_id: str, user_image_file, lat: float = None, lon: float = None, action_type: str = 'relaxation'):
        """
        一键创建平行世界影像（完整流程）
        
        Args:
            user_id: 用户 ID
            user_image_file: 用户上传的照片
            lat: 纬度（可选）
            lon: 经度（可选）
            action_type: 动作类型（fitness, learning, culture, relaxation, nature, dining）
            
        Returns:
            Dict: {
                "success": bool,
                "face_image_url": str,
                "moment": Dict (打卡内容),
                "message": str
            }
        """
        try:
            print(f"🚀 为用户 {user_id} 创建平行世界影像...")
            
            # ========== 步骤 1：生成专属人脸 ==========
            print("📸 步骤 1：生成专属风格人脸...")
            face_result = self.face_generator.generate_unique_face(user_id, user_image_file)
            
            if not face_result.get('success'):
                return {
                    "success": False,
                    "message": f"头像生成失败：{face_result.get('message')}"
                }
            
            face_image_path = face_result['face_image_path']
            print(f"✅ 头像生成成功：{face_image_path}")
            
            # ========== 步骤 2：获取附近真实地点 ==========
            print("🌍 步骤 2：获取附近真实地点...")
            if lat is None or lon is None:
                # 使用默认位置（上海人民广场）
                lat = 31.230416
                lon = 121.473701
            
            places = self.reality_mirror.get_nearby_real_places(lat, lon, limit=3)
            
            if not places:
                return {
                    "success": False,
                    "message": "附近暂无合适的地点"
                }
            
            selected_place = random.choice(places)
            print(f"📍 选择地点：{selected_place['name']}")
            
            # ========== 步骤 3：生成引导性文案 ==========
            print("💬 步骤 3：生成引导性文案...")
            caption_data = self.reality_mirror.generate_nudge_caption(
                place_type=selected_place['type'],
                place_name=selected_place['name']
            )
            print(f"✅ 文案生成：{caption_data['caption']}")
            
            # ========== 步骤 4：虚实融合 ==========
            print("🎨 步骤 4：虚实融合...")
            fused_result = self.fusion_composer.generate_fused_scene(
                face_image_path=face_image_path,
                location_photo_url=selected_place['image_url'],
                action_type=action_type
            )
            
            if not fused_result.get('success'):
                return {
                    "success": False,
                    "message": f"融合失败：{fused_result.get('message')}"
                }
            
            print(f"✅ 融合完成：{fused_result['fused_image_url']}")
            
            # ========== 步骤 5：组装最终结果 ==========
            moment = {
                'image_url': fused_result['fused_image_url'],
                'caption': caption_data['caption'],
                'mood': caption_data['mood'],
                'location_name': selected_place['name'],
                'location_type': selected_place['type'],
                'address': selected_place['address'],
                'lat': selected_place['lat'],
                'lng': selected_place['lng'],
                'distance': selected_place.get('distance', 0),
                'walk_time': selected_place.get('walk_time', '未知'),
                'action_type': action_type
            }
            
            return {
                "success": True,
                "face_image_url": face_result['face_image_url'],
                "moment": moment,
                "message": "平行世界影像已生成！你的另一个可能生活正在这里发生。"
            }
            
        except Exception as e:
            print(f"❌ 创建平行世界影像失败：{e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"服务器错误：{str(e)}"
            }


# 全局实例
_core_services = None


def get_core_services() -> GoInCoreServices:
    """获取核心服务实例"""
    global _core_services
    if _core_services is None:
        _core_services = GoInCoreServices()
    return _core_services


# 便捷导入
__all__ = [
    'UniqueFaceGenerator',
    'RealityMirrorService', 
    'FusionComposer',
    'GoInCoreServices',
    'get_face_generator',
    'get_reality_mirror',
    'get_fusion_composer',
    'get_core_services',
    'generate_unique_face',
    'get_nearby_real_places',
    'generate_nudge_caption',
    'generate_fused_scene'
]
