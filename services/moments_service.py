"""
Go In AI 朋友圈服务

负责基于真实地点的 AI 朋友圈生成、打卡照片合成等功能
"""

import random
from datetime import datetime, timedelta


class MomentsService:
    """AI 朋友圈服务类"""
    
    # 真实地点数据库（以上海为例）
    REAL_LOCATIONS = {
        'restaurant': [
            {'name': '外滩十八号', 'address': '中山东一路 18 号', 'type': '高档餐厅', 'check_in_rate': 0.8},
            {'name': '南京大牌档', 'address': '南京东路 123 号', 'type': '本帮菜', 'check_in_rate': 0.7},
            {'name': '星巴克臻选上海烘焙工坊', 'address': '南京西路 789 号', 'type': '咖啡馆', 'check_in_rate': 0.9},
            {'name': '蓝蛙', 'address': '淮海中路 456 号', 'type': '西餐厅', 'check_in_rate': 0.6}
        ],
        'attraction': [
            {'name': '东方明珠', 'address': '陆家嘴世纪大道 1 号', 'type': '地标建筑', 'check_in_rate': 0.95},
            {'name': '上海中心大厦', 'address': '陆家嘴银城中路 501 号', 'type': '摩天大楼', 'check_in_rate': 0.9},
            {'name': '豫园', 'address': '福佑路 168 号', 'type': '古典园林', 'check_in_rate': 0.85},
            {'name': '田子坊', 'address': '泰康路 210 弄', 'type': '创意园区', 'check_in_rate': 0.75}
        ],
        'gym': [
            {'name': 'Pure Fitness', 'address': '兴业太古汇 L3', 'type': '高端健身房', 'check_in_rate': 0.6},
            {'name': 'Will\'s 威尔仕健身', 'address': '来福士广场 B2', 'type': '连锁健身房', 'check_in_rate': 0.5},
            {'name': '超级猩猩健身', 'address': '环贸 iapm', 'type': '按次付费', 'check_in_rate': 0.7}
        ],
        'street': [
            {'name': '武康路', 'address': '徐汇区武康路', 'type': '历史街道', 'check_in_rate': 0.8},
            {'name': '思南路', 'address': '黄浦区思南路', 'type': '花园洋房', 'check_in_rate': 0.7},
            {'name': '愚园路', 'address': '长宁区愚园路', 'type': '文艺街道', 'check_in_rate': 0.75}
        ]
    }
    
    # 打卡文案模板
    CHECK_IN_TEMPLATES = [
        '今天来到了{location}，感觉很棒！✨',
        '在{location}遇见美好的一天 🌟',
        '打卡{location}，推荐给大家！👍',
        '{location}的氛围感绝了～📸',
        '周末好去处：{location} 💕'
    ]
    
    # AI 形象姿势库
    AVATAR_POSES = [
        {'name': '自然站立', 'description': '轻松自然的站姿', 'suitable_for': ['street', 'attraction']},
        {'name': '坐姿优雅', 'description': '优雅的坐姿', 'suitable_for': ['restaurant', 'cafe']},
        {'name': '运动姿态', 'description': '活力四射的运动姿势', 'suitable_for': ['gym']},
        {'name': '比耶拍照', 'description': '经典的 V 字手势', 'suitable_for': ['all']},
        {'name': '侧身回眸', 'description': '文艺范的侧身回头', 'suitable_for': ['street', 'attraction']},
        {'name': '双手插兜', 'description': '酷酷的站姿', 'suitable_for': ['all']}
    ]
    
    @staticmethod
    def generate_moments(user_data, num_posts=5):
        """
        生成 AI 朋友圈内容
        
        Args:
            user_data: 用户数据
            num_posts: 生成数量
        
        Returns:
            list: 朋友圈列表
        """
        moments = []
        
        for i in range(num_posts):
            # 随机选择地点类型
            location_type = random.choice(list(MomentsService.REAL_LOCATIONS.keys()))
            
            # 随机选择一个具体地点
            location = random.choice(MomentsService.REAL_LOCATIONS[location_type])
            
            # 生成打卡时间（最近 24 小时内）
            check_in_time = datetime.now() - timedelta(hours=random.randint(1, 24))
            
            # 生成文案
            caption_template = random.choice(MomentsService.CHECK_IN_TEMPLATES)
            caption = caption_template.format(location=location['name'])
            
            # 选择合适的姿势
            suitable_poses = [p for p in MomentsService.AVATAR_POSES 
                             if location_type in p['suitable_for'] or 'all' in p['suitable_for']]
            pose = random.choice(suitable_poses)
            
            # 生成合成照片信息
            photo = MomentsService._generate_check_in_photo(
                user_data=user_data,
                location=location,
                pose=pose,
                time=check_in_time
            )
            
            moment = {
                'id': f'moment_{datetime.now().timestamp()}_{i}',
                'type': 'check_in',
                'user_id': user_data.get('user_id'),
                'avatar_image': user_data.get('avatar_image'),
                'location': location,
                'caption': caption,
                'photo': photo,
                'pose': pose,
                'timestamp': check_in_time,
                'likes': random.randint(0, 200),
                'comments': random.randint(0, 50),
                'is_ai_generated': True
            }
            
            moments.append(moment)
        
        return moments
    
    @staticmethod
    def _generate_check_in_photo(user_data, location, pose, time):
        """
        生成打卡合成照片（简化版，实际需要图像合成）
        
        Args:
            user_data: 用户数据
            location: 地点信息
            pose: 姿势信息
            time: 时间
        
        Returns:
            dict: 照片信息
        """
        # 实际应该：
        # 1. 获取用户的头像
        # 2. 获取地点的背景图
        # 3. 根据姿势合成照片
        # 这里先返回模拟数据
        
        photo_data = {
            'avatar_image': user_data.get('avatar_image'),
            'background': f'{location["name"]}_background.jpg',
            'pose': pose['name'],
            'time': time.strftime('%Y-%m-%d %H:%M'),
            'filter': random.choice(['清新', '复古', '胶片', '电影感']),
            'description': f'{user_data.get("username", "用户")}在{location["name"]}以{pose["name"]}的姿势打卡'
        }
        
        return photo_data
    
    @staticmethod
    def get_nearby_locations(latitude=None, longitude=None, radius=1000):
        """
        获取附近的地点
        
        Args:
            latitude: 纬度
            longitude: 经度
            radius: 半径（米）
        
        Returns:
            list: 地点列表
        """
        # 简化版：返回所有地点
        # 实际应该根据经纬度和半径过滤
        all_locations = []
        for loc_type, locations in MomentsService.REAL_LOCATIONS.items():
            for loc in locations:
                loc['category'] = loc_type
                all_locations.append(loc)
        
        return all_locations
    
    @staticmethod
    def auto_check_in(user_data, location):
        """
        AI 自动打卡
        
        Args:
            user_data: 用户数据
            location: 地点信息
        
        Returns:
            dict: 打卡记录
        """
        # 生成打卡时间
        check_in_time = datetime.now()
        
        # 选择合适的姿势
        suitable_poses = [p for p in MomentsService.AVATAR_POSES 
                         if location.get('category') in p['suitable_for'] or 'all' in p['suitable_for']]
        pose = random.choice(suitable_poses)
        
        # 生成文案
        caption_template = random.choice(MomentsService.CHECK_IN_TEMPLATES)
        caption = caption_template.format(location=location['name'])
        
        # 生成照片
        photo = MomentsService._generate_check_in_photo(
            user_data=user_data,
            location=location,
            pose=pose,
            time=check_in_time
        )
        
        check_in_record = {
            'id': f'checkin_{datetime.now().timestamp()}',
            'user_id': user_data.get('user_id'),
            'avatar_image': user_data.get('avatar_image'),
            'location': location,
            'caption': caption,
            'photo': photo,
            'pose': pose,
            'timestamp': check_in_time,
            'is_auto_generated': True
        }
        
        return check_in_record
    
    @staticmethod
    def validate_location(location):
        """验证地点信息"""
        required_fields = ['name', 'address', 'type']
        return all(field in location for field in required_fields)
