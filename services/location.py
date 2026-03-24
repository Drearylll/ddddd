"""
地理位置服务
Go In App - 高德地图 API 对接

功能：
1. 周边搜索（POI）- 获取真实地点
2. 距离计算 - 计算步行时间
3. 地理编码 - 地址转坐标
4. 获取真实地点图片

API 文档：
https://lbs.amap.com/api/webservice/guide/api/search
https://lbs.amap.com/api/webservice/guide/api/placeinfo
"""

import requests
import random
import re
from typing import List, Dict, Optional

# API 配置（可配置环境变量）
GAODE_API_KEY = "2274b3d46339f95092d68b83150ead7f"  # 高德地图 Web 服务 API Key（已更新）
GAODE_API_SECRET = ""  # 安全密钥（可选）
GAODE_API_URL = "https://restapi.amap.com/v3/place/around"  # 周边搜索
GAODE_GEO_URL = "https://restapi.amap.com/v3/geocode/geo"  # 地理编码
GAODE_PLACE_INFO_URL = "https://restapi.amap.com/v3/place/info"  # 地点详情


class LocationService:
    """地理位置服务"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or GAODE_API_KEY
        self.use_mock = not self.api_key  # 没有 API Key 时使用模拟数据
        
        # 默认城市中心（上海人民广场）
        self.default_location = {
            "name": "上海",
            "lat": 31.230416,
            "lon": 121.473701
        }
    
    # ========== 公开方法 ==========
    
    def search_nearby(
        self,
        location: Optional[Dict] = None,
        types: Optional[List[str]] = None,
        radius: int = 1000,
        limit: int = 10
    ) -> List[Dict]:
        """
        搜索周边地点
        
        Args:
            location: 位置 {"lat": 纬度，"lon": 经度}，默认使用城市中心
            types: 地点类型列表，如 ["咖啡厅", "餐厅", "景点"]
            radius: 搜索半径（米），默认 1000 米
            limit: 返回数量限制，默认 10 个
            
        Returns:
            List[Dict]: 地点列表
            [
                {
                    "name": "星巴克 (南京东路店)",
                    "type": "咖啡厅",
                    "address": "黄浦区南京东路 XXX 号",
                    "distance": 350,  # 距离（米）
                    "walk_time": "5 分钟",  # 步行时间
                    "lat": 31.23456,
                    "lon": 121.45678
                }
            ]
        """
        if self.use_mock:
            return self._mock_search_nearby(location, types, radius, limit)
        
        # 调用真实 API
        return self._call_gaode_api(location, types, radius, limit)
    
    def get_walk_time(self, from_loc: Dict, to_loc: Dict) -> str:
        """
        计算步行时间
        
        Args:
            from_loc: 起点 {"lat": 纬度，"lon": 经度}
            to_loc: 终点 {"lat": 纬度，"lon": 经度}
            
        Returns:
            str: 步行时间（如"5 分钟"）
        """
        # 简单估算：步行速度 5km/h
        lat_diff = abs(from_loc['lat'] - to_loc['lat'])
        lon_diff = abs(from_loc['lon'] - to_loc['lon'])
        
        # 近似距离（米）
        distance = ((lat_diff * 111000) ** 2 + (lon_diff * 85000) ** 2) ** 0.5
        
        # 步行时间（分钟）
        walk_minutes = int(distance / 83)  # 5km/h ≈ 83m/min
        
        if walk_minutes < 1:
            return "1 分钟"
        elif walk_minutes > 60:
            hours = walk_minutes // 60
            mins = walk_minutes % 60
            return f"{hours}小时{mins}分钟" if mins > 0 else f"{hours}小时"
        else:
            return f"{walk_minutes}分钟"
    
    def get_real_location(
        self,
        lat: float = 31.230416,
        lng: float = 121.473701,
        types: Optional[List[str]] = None
    ) -> Dict:
        """
        获取一个真实的地点（包含图片）
        
        Args:
            lat: 纬度，默认上海人民广场
            lng: 经度，默认上海人民广场
            types: 地点类型列表，默认 ["风景名胜", "餐饮服务", "购物服务"]
            
        Returns:
            Dict: 真实地点信息
            {
                "name": "外滩",
                "address": "上海市黄浦区中山东一路",
                "image_url": "https://example.com/image.jpg",  # 如果有
                "description": "外滩位于上海市黄浦区，是上海最具代表性的地标之一...",
                "lat": 31.239493,
                "lng": 121.490686,
                "type": "风景名胜"
            }
        """
        if types is None:
            types = ["风景名胜", "餐饮服务", "购物服务"]
        
        # 1. 搜索周边地点
        location = {"lat": lat, "lon": lng}
        pois = self.search_nearby(location, types=types, radius=2000, limit=20)
        
        if not pois:
            return {
                "name": "未知地点",
                "address": "未知地址",
                "image_url": None,
                "description": "暂无可用地点信息",
                "lat": lat,
                "lng": lng,
                "type": "其他"
            }
        
        # 2. 随机选择一个地点
        poi = random.choice(pois)
        
        # 3. 获取地点详情（包括图片）
        poi_info = self._get_poi_details(poi)
        
        return poi_info
    
    def _get_poi_details(self, poi: Dict) -> Dict:
        """
        获取地点详细信息（包括图片）
        
        Args:
            poi: 地点信息
            
        Returns:
            Dict: 包含图片的完整地点信息
        """
        # 首先尝试从现有数据中获取图片
        image_url = poi.get('image_url')
        
        # 如果没有图片，调用高德地图 API 获取
        if not image_url and self.api_key:
            image_url = self._fetch_poi_image(poi)
        
        # 生成描述
        description = self._generate_description(poi)
        
        return {
            "name": poi.get('name', '未知地点'),
            "address": poi.get('address', '未知地址'),
            "image_url": image_url,
            "description": description,
            "lat": poi.get('lat'),
            "lng": poi.get('lon'),
            "type": poi.get('type', '其他')
        }
    
    def _fetch_poi_image(self, poi: Dict) -> Optional[str]:
        """
        从高德地图 API 获取地点图片
        
        Args:
            poi: 地点信息
            
        Returns:
            Optional[str]: 图片 URL，如果没有则返回 None
        """
        poi_id = poi.get('id')
        
        if not poi_id:
            return None
        
        params = {
            "id": poi_id,
            "key": self.api_key,
            "output": "json"
        }
        
        try:
            response = requests.get(GAODE_PLACE_INFO_URL, params=params, timeout=5)
            result = response.json()
            
            if result.get('status') == '1' and result.get('pois'):
                poi_detail = result['pois'][0]
                
                # 尝试获取图片
                if 'photos' in poi_detail:
                    photos = poi_detail.get('photos', [])
                    if photos:
                        # 返回第一张图片
                        return photos[0].get('url')
                
                # 尝试获取缩略图
                if 'thumbnail' in poi_detail:
                    return poi_detail.get('thumbnail')
                    
        except Exception as e:
            print(f"❌ 获取地点图片失败：{e}")
        
        return None
    
    def _generate_description(self, poi: Dict) -> str:
        """
        生成地点描述
        
        Args:
            poi: 地点信息
            
        Returns:
            str: 地点描述
        """
        name = poi.get('name', '这个地点')
        address = poi.get('address', '')
        poi_type = poi.get('type', '地点')
        distance = poi.get('distance', 0)
        walk_time = poi.get('walk_time', '')
        
        # 根据类型生成描述
        type_descriptions = {
            "景点": f"{name}是一个值得一游的地方",
            "咖啡厅": f"{name}提供香浓的咖啡和舒适的环境",
            "餐厅": f"{name}提供美味的当地特色菜肴",
            "商场": f"{name}是购物和休闲的好去处",
            "交通": f"{name}提供便捷的交通服务"
        }
        
        base_desc = type_descriptions.get(poi_type, f"{name}是一个受欢迎的地点")
        
        # 添加距离信息
        desc = f"{base_desc}。这里距离你约{distance}米，步行{walk_time}。"
        
        # 添加地址信息
        if address:
            # 简化地址（只显示区 + 路名）
            simple_address = self._simplify_address(address)
            desc += f"位于{simple_address}。"
        
        return desc
    
    def _simplify_address(self, address: str) -> str:
        """
        简化地址（提取区和路名）
        
        Args:
            address: 完整地址
            
        Returns:
            str: 简化后的地址
        """
        # 匹配区名
        district_pattern = r'([黄浦 | 徐汇 | 长宁 | 静安 | 普陀 | 虹口 | 杨浦 | 闵行 | 宝山 | 嘉定 | 浦东 | 金山 | 松江 | 青浦 | 奉贤 | 崇明] 区)'
        match = re.search(district_pattern, address)
        
        if match:
            district = match.group(1)
            # 提取路名
            road_match = re.search(r'([\u4e00-\u9fa5]+ 路)', address)
            if road_match:
                road = road_match.group(1)
                return f"{district}{road}"
        
        # 如果无法简化，返回前 20 个字符
        return address[:20] + "..." if len(address) > 20 else address
    
    def geocode(self, address: str) -> Optional[Dict]:
        """
        地理编码：地址转坐标
        
        Args:
            address: 地址（如"上海市黄浦区南京东路"）
            
        Returns:
            Dict: {"lat": 纬度，"lon": 经度}
        """
        if not self.api_key:
            return self.default_location
        
        params = {
            "address": address,
            "key": self.api_key,
            "output": "json"
        }
        
        try:
            response = requests.get(GAODE_GEO_URL, params=params, timeout=5)
            result = response.json()
            
            if result.get('status') == '1' and result.get('geocodes'):
                geocode = result['geocodes'][0]
                location = geocode.get('location', '').split(',')
                return {
                    "lat": float(location[1]),
                    "lon": float(location[0])
                }
        except Exception as e:
            print(f"❌ 地理编码失败：{e}")
        
        return self.default_location
    
    # ========== 内部方法 ==========
    
    def _call_gaode_api(self, location, types, radius, limit):
        """调用高德 API"""
        loc = location or self.default_location
        
        params = {
            "key": self.api_key,
            "location": f"{loc['lon']},{loc['lat']}",
            "radius": radius,
            "output": "json"
        }
        
        # 地点类型过滤（支持更广泛的类型匹配）
        if types:
            # 扩展类型映射，支持多种叫法
            type_mapping = {
                "咖啡厅": ["餐饮服务;咖啡厅", "咖啡厅"],
                "餐厅": ["餐饮服务;中餐厅", "餐饮服务", "餐厅"],
                "景点": ["风景名胜", "景点"],
                "商场": ["购物服务;商场", "购物服务", "商场"],
                "地铁站": ["交通设施服务;地铁站", "交通"],
                "餐饮服务": ["餐饮服务"],
                "购物服务": ["购物服务"],
                "风景名胜": ["风景名胜"]
            }
            type_codes = []
            for t in types:
                if t in type_mapping:
                    type_codes.extend(type_mapping[t])
                else:
                    type_codes.append(t)
            params["types"] = "|".join(type_codes)
        
        try:
            response = requests.get(GAODE_API_URL, params=params, timeout=5)
            result = response.json()
            
            if result.get('status') != '1':
                print(f"❌ 高德 API 调用失败：{result.get('info', 'Unknown error')}")
                return self._mock_search_nearby(location, types, radius, limit)
            
            pois = result.get('pois', [])
            return self._parse_pois(pois, loc)
            
        except Exception as e:
            print(f"❌ 高德 API 异常：{e}")
            return self._mock_search_nearby(location, types, radius, limit)
    
    def _parse_pois(self, pois: List[Dict], center_loc: Dict) -> List[Dict]:
        """解析高德 POI 数据"""
        results = []
        
        for poi in pois[:10]:  # 最多 10 个
            try:
                location = poi.get('location', '').split(',')
                lat = float(location[1]) if len(location) > 1 else center_loc['lat']
                lon = float(location[0]) if len(location) > 0 else center_loc['lon']
                
                distance = int(poi.get('distance', 0))
                walk_time = self._calculate_walk_time(distance)
                
                results.append({
                    "name": poi.get('name', '未知地点'),
                    "type": self._simplify_type(poi.get('type', '')),
                    "address": poi.get('address', ''),
                    "distance": distance,
                    "walk_time": walk_time,
                    "lat": lat,
                    "lon": lon
                })
            except Exception as e:
                print(f"❌ 解析 POI 失败：{e}")
                continue
        
        return results
    
    def _simplify_type(self, type_str: str) -> str:
        """简化地点类型"""
        type_mapping = {
            "餐饮服务": "餐厅",
            "咖啡厅": "咖啡厅",
            "购物服务": "商场",
            "风景名胜": "景点",
            "交通设施服务": "交通"
        }
        
        for key, value in type_mapping.items():
            if key in type_str:
                return value
        
        return "其他"
    
    def _calculate_walk_time(self, distance: int) -> str:
        """计算步行时间"""
        walk_minutes = int(distance / 83)  # 5km/h ≈ 83m/min
        
        if walk_minutes < 1:
            return "1 分钟"
        elif walk_minutes > 60:
            hours = walk_minutes // 60
            mins = walk_minutes % 60
            return f"{hours}小时{mins}分钟" if mins > 0 else f"{hours}小时"
        else:
            return f"{walk_minutes}分钟"
    
    # ========== 模拟数据（用于开发测试） ==========
    
    def _mock_search_nearby(self, location, types, radius, limit):
        """模拟周边搜索数据"""
        mock_pois = [
            {
                "name": "星巴克 (南京东路店)",
                "type": "咖啡厅",
                "address": "黄浦区南京东路 123 号",
                "distance": 350,
                "walk_time": "5 分钟",
                "lat": 31.23456,
                "lon": 121.45678,
                "image_url": "https://images.pexels.com/photos/302899/pexels-photo-302899.jpeg?auto=compress&cs=tinysrgb&w=600"
            },
            {
                "name": "外滩观景平台",
                "type": "景点",
                "address": "黄浦区中山东一路",
                "distance": 680,
                "walk_time": "9 分钟",
                "lat": 31.23891,
                "lon": 121.49123,
                "image_url": "https://images.pexels.com/photos/1640772/pexels-photo-1640772.jpeg?auto=compress&cs=tinysrgb&w=600"
            },
            {
                "name": "新世界城",
                "type": "商场",
                "address": "黄浦区南京西路 100 号",
                "distance": 520,
                "walk_time": "7 分钟",
                "lat": 31.23234,
                "lon": 121.47456,
                "image_url": "https://images.pexels.com/photos/276518/pexels-photo-276518.jpeg?auto=compress&cs=tinysrgb&w=600"
            },
            {
                "name": "来福士广场",
                "type": "商场",
                "address": "黄浦区西藏中路 100 号",
                "distance": 450,
                "walk_time": "6 分钟",
                "lat": 31.23345,
                "lon": 121.47567,
                "image_url": "https://images.pexels.com/photos/1417058/pexels-photo-1417058.jpeg?auto=compress&cs=tinysrgb&w=600"
            },
            {
                "name": "人民公园",
                "type": "景点",
                "address": "黄浦区南京西路 200 号",
                "distance": 800,
                "walk_time": "11 分钟",
                "lat": 31.23567,
                "lon": 121.47234,
                "image_url": "https://images.pexels.com/photos/128707/pexels-photo-128707.jpeg?auto=compress&cs=tinysrgb&w=600"
            },
            {
                "name": "Manner Coffee",
                "type": "咖啡厅",
                "address": "黄浦区汉口路 50 号",
                "distance": 280,
                "walk_time": "4 分钟",
                "lat": 31.23123,
                "lon": 121.47890,
                "image_url": "https://images.pexels.com/photos/302899/pexels-photo-302899.jpeg?auto=compress&cs=tinysrgb&w=600"
            },
            {
                "name": "老半斋酒楼",
                "type": "餐厅",
                "address": "黄浦区福州路 200 号",
                "distance": 600,
                "walk_time": "8 分钟",
                "lat": 31.23678,
                "lon": 121.47345,
                "image_url": "https://images.pexels.com/photos/126707/pexels-photo-126707.jpeg?auto=compress&cs=tinysrgb&w=600"
            },
            {
                "name": "豫园",
                "type": "景点",
                "address": "黄浦区安仁街 137 号",
                "distance": 1200,
                "walk_time": "15 分钟",
                "lat": 31.22539,
                "lon": 121.49139,
                "image_url": "https://images.pexels.com/photos/2534523/pexels-photo-2534523.jpeg?auto=compress&cs=tinysrgb&w=600"
            },
            {
                "name": "南京路步行街",
                "type": "景点",
                "address": "黄浦区南京东路",
                "distance": 400,
                "walk_time": "5 分钟",
                "lat": 31.23416,
                "lon": 121.47694,
                "image_url": "https://images.pexels.com/photos/1406369/pexels-photo-1406369.jpeg?auto=compress&cs=tinysrgb&w=600"
            },
            {
                "name": "迪美购物中心",
                "type": "商场",
                "address": "黄浦区人民大道 221 号",
                "distance": 200,
                "walk_time": "3 分钟",
                "lat": 31.22956,
                "lon": 121.47512,
                "image_url": "https://images.pexels.com/photos/276518/pexels-photo-276518.jpeg?auto=compress&cs=tinysrgb&w=600"
            }
        ]
        
        # 类型过滤（支持大类类型）
        if types:
            # 扩展类型映射，支持大类
            type_mapping = {
                "餐饮服务": ["咖啡厅", "餐厅"],
                "购物服务": ["商场"],
                "风景名胜": ["景点"]
            }
            # 收集所有匹配的类型
            matched_types = set()
            for t in types:
                if t in type_mapping:
                    matched_types.update(type_mapping[t])
                else:
                    matched_types.add(t)
            
            # 过滤
            mock_pois = [p for p in mock_pois if p['type'] in matched_types]
        
        # 随机选择
        return random.sample(mock_pois, min(limit, len(mock_pois)))


# 全局实例
_location_service = None

def get_location_service():
    """获取地理位置服务实例"""
    global _location_service
    if _location_service is None:
        _location_service = LocationService()
    return _location_service


# ========== 便捷函数 ==========

def get_real_location(
    lat: float = 31.230416,
    lng: float = 121.473701,
    types: Optional[List[str]] = None
) -> Dict:
    """
    获取一个真实的地点（便捷函数）
    
    Args:
        lat: 纬度，默认上海人民广场
        lng: 经度，默认上海人民广场
        types: 地点类型列表，默认 ["风景名胜", "餐饮服务", "购物服务"]
        
    Returns:
        Dict: 真实地点信息
        {
            "name": "外滩",
            "address": "上海市黄浦区中山东一路",
            "image_url": "https://example.com/image.jpg",
            "description": "外滩位于上海市黄浦区...",
            "lat": 31.239493,
            "lng": 121.490686,
            "type": "风景名胜"
        }
    """
    service = get_location_service()
    return service.get_real_location(lat, lng, types)
