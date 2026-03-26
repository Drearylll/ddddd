"""
基于 LBS 的现实镜像与引导服务
Go In App - 1.0 核心功能

功能：
1. 基于用户定位，抓取附近真实地点的真实照片
2. 生成"模拟真实生活"的引导性文案（暗示健身/阅读/学习）
3. 语气自然、温暖，目的是潜意识引导用户去行动

技术方案：
- 高德地图 API 获取真实街景/店内照片
- LLM 生成引导性文案（Prompt 工程）
- 地点类型过滤：gym, library, cinema, cafe, park
"""

import os
import random
from typing import List, Dict, Optional
from datetime import datetime

# 导入已有的位置服务
from services.location import LocationService


class RealityMirrorService:
    """现实镜像与引导服务"""
    
    def __init__(self):
        """初始化服务"""
        self.location_service = LocationService()
        
        # LLM API 配置（优先从环境变量读取）
        self.llm_api_key = os.getenv("DOUBAO_API_KEY", "sk-87930805570a46c38f5eefa1c03cd2e6")
        self.llm_api_url = os.getenv("DOUBAO_API_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")
        
        # 目标地点类型（符合产品理念）
        self.TARGET_LOCATION_TYPES = [
            "健身房", "瑜伽馆", "运动中心",  # 健身类
            "图书馆", "书店", "自习室",  # 学习类
            "电影院", "剧院", "美术馆",  # 文化类
            "咖啡馆", "茶馆", "甜品店",  # 休闲类
            "公园", "绿地", "河边",  # 自然类
            "餐厅", "小吃店", "面包房"  # 餐饮类
        ]
        
        # 用户长期目标映射
        self.USER_GOALS = {
            'fitness': ['健身房', '瑜伽馆', '运动中心', '公园'],
            'learning': ['图书馆', '书店', '自习室', '咖啡馆'],
            'relaxation': ['咖啡馆', '茶馆', '公园', '河边'],
            'culture': ['电影院', '剧院', '美术馆', '博物馆'],
            'social': ['餐厅', '咖啡馆', '茶馆', '甜品店']
        }
    
    def get_nearby_real_places(
        self, 
        lat: float, 
        lon: float, 
        types: Optional[List[str]] = None,
        radius: int = 1000,
        limit: int = 5
    ) -> List[Dict]:
        """
        获取附近真实地点（带图片）
        
        Args:
            lat: 纬度
            lon: 经度
            types: 地点类型列表，默认使用 TARGET_LOCATION_TYPES
            radius: 搜索半径（米）
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 地点列表（包含真实照片 URL）
        """
        # 使用已有位置服务搜索
        search_types = types or self.TARGET_LOCATION_TYPES
        places = self.location_service.search_nearby(
            location={"lat": lat, "lon": lon},
            types=search_types,
            radius=radius,
            limit=limit * 2  # 多获取一些用于筛选
        )
        
        # 过滤并格式化结果
        result = []
        for place in places:
            if not place.get('image_url'):
                continue
                
            formatted_place = {
                "name": place.get('name', '未知地点'),
                "type": place.get('type', '其他'),
                "address": place.get('address', ''),
                "lat": place.get('lat', lat),
                "lng": place.get('lon', lon),
                "distance": place.get('distance', 0),
                "walk_time": place.get('walk_time', '未知'),
                "image_url": place.get('image_url', ''),
                "category": self._categorize_location(place.get('type', ''))
            }
            result.append(formatted_place)
            
            if len(result) >= limit:
                break
        
        return result
    
    def generate_nudge_caption(
        self, 
        place_type: str, 
        user_profile: Optional[Dict] = None,
        current_time: Optional[datetime] = None,
        place_name: Optional[str] = None
    ) -> Dict:
        """
        生成引导性文案（模拟真实生活）
        
        Args:
            place_type: 地点类型（如"健身房"、"图书馆"）
            user_profile: 用户画像（可选）
            current_time: 当前时间（可选）
            place_name: 地点名称（可选）
            
        Returns:
            Dict: {
                "caption": "文案内容",
                "mood": "情绪基调",
                "nudge_type": "引导类型",
                "prompt_level": "引导强度"
            }
        """
        if current_time is None:
            current_time = datetime.now()
        
        # 构建 Prompt
        prompt = self._build_nudge_prompt(place_type, user_profile, current_time, place_name)
        
        # 调用 LLM 或模拟生成
        if not self.llm_api_key:
            caption_data = self._mock_generate_caption(place_type, current_time, place_name)
        else:
            caption_data = self._call_llm_for_caption(prompt)
        
        return caption_data
    
    def _categorize_location(self, location_type: str) -> str:
        """
        将地点归类到目标类别
        
        Args:
            location_type: 原始地点类型
            
        Returns:
            str: 归类后的类别
        """
        type_lower = location_type.lower()
        
        # 健身类
        if any(kw in type_lower for kw in ['健身', '瑜伽', '运动', '体育']):
            return 'fitness'
        
        # 学习类
        if any(kw in type_lower for kw in ['图书', '书店', '自习', '教育']):
            return 'learning'
        
        # 文化类
        if any(kw in type_lower for kw in ['电影', '剧院', '美术', '博物', '展览']):
            return 'culture'
        
        # 休闲类
        if any(kw in type_lower for kw in ['咖啡', '茶', '甜品', '蛋糕']):
            return 'relaxation'
        
        # 自然类
        if any(kw in type_lower for kw in ['公园', '绿地', '河边', '湖', '山']):
            return 'nature'
        
        # 餐饮类
        if any(kw in type_lower for kw in ['餐', '酒', '吧', '烧烤', '火锅']):
            return 'dining'
        
        return 'other'
    
    def _build_nudge_prompt(
        self, 
        place_type: str, 
        user_profile: Optional[Dict],
        current_time: datetime,
        place_name: Optional[str]
    ) -> str:
        """
        构建 LLM Prompt
        
        Args:
            place_type: 地点类型
            user_profile: 用户画像
            current_time: 当前时间
            place_name: 地点名称
            
        Returns:
            str: LLM Prompt
        """
        time_str = current_time.strftime("%A %H:%M")
        hour = current_time.hour
        
        # 时间段描述
        if 5 <= hour < 9:
            time_period = "清晨"
        elif 9 <= hour < 12:
            time_period = "上午"
        elif 12 <= hour < 14:
            time_period = "中午"
        elif 14 <= hour < 18:
            time_period = "下午"
        elif 18 <= hour < 21:
            time_period = "傍晚"
        else:
            time_period = "夜晚"
        
        # 构建 Prompt
        prompt = f"""你是一个温暖的路人观察者。请模拟一个路人看到{place_type}时的内心独白。

【场景信息】
- 地点类型：{place_type}
- 地点名称：{place_name or '某个地方'}
- 时间：{time_str}（{time_period}）

【要求】
1. 语气自然、温暖，像朋友间的轻声建议
2. 目的是潜意识引导用户去行动（如看到健身房就想去运动，看到书店就想去阅读）
3. 禁止说教，不要使用"你应该"、"你要"等命令式语句
4. 用第一人称或第三人称描述一个美好的场景
5. 字数控制在 30-60 字之间
6. 可以加入 emoji 增强情感表达

【示例】
- 健身房："这家健身房的灯光好亮，感觉进去挥洒汗水会很爽。💪"
- 书店："这家书店的氛围好安静，感觉进去坐一下午，整个人都会静下来。📚"
- 咖啡馆："这家咖啡馆的香味飘出来了，好想进去点一杯，发会儿呆。☕"
- 公园："公园里好多人在散步，感觉现在去走走，心情会变好。🌳"

请根据以上场景，写一句路人的内心独白："""
        
        return prompt
    
    def _mock_generate_caption(
        self, 
        place_type: str, 
        current_time: datetime,
        place_name: Optional[str]
    ) -> Dict:
        """
        模拟生成文案（用于开发和测试）
        
        Args:
            place_type: 地点类型
            current_time: 当前时间
            place_name: 地点名称
            
        Returns:
            Dict: 文案数据
        """
        # 预设文案库（按地点类型分类）
        caption_templates = {
            'fitness': [
                "这个时间点，健身房应该人不多，好想进去动一动。💪",
                "看到有人刚从里面出来，满头大汗的样子，感觉好爽。🏃",
                "这里的器械看起来好专业，有点想试试。🔥",
                "运动完的感觉一定很好，要不要现在就进去？✨"
            ],
            'learning': [
                "这家书店的灯光好暖，感觉进去坐一下午，整个人都会静下来。📚",
                "图书馆好安静啊，好想找个角落，看一本喜欢的书。📖",
                "这里的氛围好适合学习，效率一定会很高。📝",
                "好久没静下心来读书了，今天是个好时机。🌟"
            ],
            'culture': [
                "这个展览看起来好有意思，好想进去看看。🎨",
                "电影院的预告片好吸引人，要不要现在就买票？🎬",
                "美术馆的光线好柔和，感觉能待一整天。🖼️",
                "剧场今天有演出，不知道会是什么样的故事。🎭"
            ],
            'relaxation': [
                "这家咖啡馆的香味飘出来了，好想进去点一杯，发会儿呆。☕",
                "坐在窗边晒太阳喝咖啡，应该会很舒服吧。☀️",
                "这里的甜品种类好多，好想尝尝看。🍰",
                "好久没放松了，今天要不要犒劳一下自己？💆"
            ],
            'nature': [
                "公园里好多人在散步，感觉现在去走走，心情会变好。🌳",
                "河边的风好凉爽，沿着河岸走走应该很舒服。🌊",
                "这片绿地看起来好舒服，好想躺上去晒太阳。☀️",
                "树上的鸟儿叫得好听，要不要去听听大自然的声音？🐦"
            ],
            'dining': [
                "这家店的招牌菜看起来好好吃，要不要试试看？😋",
                "闻起来好香啊，肚子都饿了。🍜",
                "这家餐厅的氛围好温馨，很适合和朋友聊天。🍷",
                "好久没吃美食了，今天要不要犒劳一下味蕾？🍽️"
            ]
        }
        
        # 根据地点类型选择文案
        category = self._categorize_location(place_type)
        templates = caption_templates.get(category, caption_templates['relaxation'])
        
        caption = random.choice(templates)
        
        # 确定情绪基调
        mood_map = {
            'fitness': '期待',
            'learning': '平静',
            'culture': '好奇',
            'relaxation': '惬意',
            'nature': '放松',
            'dining': '愉悦'
        }
        
        return {
            "caption": caption,
            "mood": mood_map.get(category, '平静'),
            "nudge_type": "subtle_suggestion",
            "prompt_level": "light"
        }
    
    def _call_llm_for_caption(self, prompt: str) -> Dict:
        """
        调用 LLM 生成文案
        
        Args:
            prompt: LLM Prompt
            
        Returns:
            Dict: 文案数据
        """
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.llm_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "doubao-pro-4k",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 100,
                "temperature": 0.8
            }
            
            response = requests.post(
                self.llm_api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                caption = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # 清理文案
                caption = caption.strip().strip('"\'')
                
                return {
                    "caption": caption,
                    "mood": "温暖",
                    "nudge_type": "subtle_suggestion",
                    "prompt_level": "light"
                }
            else:
                print(f"⚠️ LLM API 请求失败：HTTP {response.status_code}")
                return self._mock_generate_caption("咖啡馆", datetime.now(), "某地")
                
        except Exception as e:
            print(f"❌ LLM 调用失败：{e}")
            return self._mock_generate_caption("咖啡馆", datetime.now(), "某地")


# 全局实例
_reality_mirror = None


def get_reality_mirror() -> RealityMirrorService:
    """获取现实镜像服务实例"""
    global _reality_mirror
    if _reality_mirror is None:
        _reality_mirror = RealityMirrorService()
    return _reality_mirror


# 便捷函数
def get_nearby_real_places(lat: float, lon: float, types: Optional[List[str]] = None) -> List[Dict]:
    """获取附近真实地点"""
    service = get_reality_mirror()
    return service.get_nearby_real_places(lat, lon, types)


def generate_nudge_caption(place_type: str, user_profile: Optional[Dict] = None) -> Dict:
    """生成引导性文案"""
    service = get_reality_mirror()
    return service.generate_nudge_caption(place_type, user_profile)
