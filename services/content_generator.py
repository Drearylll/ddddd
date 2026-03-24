"""
内容生成服务

负责 AI 生活流内容的自动生成
包括地点选择、文案生成、时间感知等核心功能
"""

import random
from datetime import datetime


class ContentGenerator:
    """AI 内容生成器"""
    
    @staticmethod
    def generate_ai_life_posts(user_data, num_posts=3, current_time=None):
        """
        AI 自主生活流内容生成
        
        Args:
            user_data: 用户数据（包含兴趣标签、历史内容等）
            num_posts: 生成数量
            current_time: 当前时间（用于时间段判断）
        
        Returns:
            list: 生成的内容列表
        """
        if current_time is None:
            current_time = datetime.now()
        
        # 获取用户偏好
        user_tags = user_data.get('interest_tags', [])
        tag_weights = user_data.get('tag_weights', {})
        
        # 获取当前时间段
        time_period = ContentGenerator._get_time_period(current_time)
        
        # 获取候选内容池
        candidate_contents = ContentGenerator._get_candidate_contents()
        
        # 根据时间段和用户人格过滤内容
        filtered_contents = ContentGenerator._filter_by_personality(
            candidate_contents, 
            time_period, 
            user_tags, 
            tag_weights
        )
        
        # 生成指定数量的内容
        posts = []
        for i in range(num_posts):
            if i < len(filtered_contents):
                content = filtered_contents[i].copy()
                
                # 添加时间戳
                content['timestamp'] = current_time
                
                # 人格偏移：根据用户标签调整权重
                weight = ContentGenerator._calculate_personality_weight(
                    content, user_tags, tag_weights
                )
                content['personality_weight'] = weight
                
                posts.append(content)
        
        return posts
    
    @staticmethod
    def _get_time_period(current_time):
        """
        获取当前时间段
        
        Returns:
            str: 'morning' | 'afternoon' | 'night'
        """
        current_hour = current_time.hour
        
        if 6 <= current_hour < 12:
            return 'morning'  # 上午：行动类
        elif 12 <= current_hour < 18:
            return 'afternoon'  # 下午：停留类
        else:
            return 'night'  # 夜晚：安静类
    
    @staticmethod
    def _get_candidate_contents():
        """
        获取候选内容池
        
        Returns:
            list: 候选内容列表
        """
        # TODO: 从数据库或配置文件加载
        # 这里使用示例数据
        return [
            {
                'location': '陆家嘴滨江',
                'text': '风有点大，但很自由。',
                'mood': '平静',
                'time_type': 'action',
                'tags': ['nature', 'urban']
            },
            {
                'location': '世纪大道地铁站',
                'text': '人群匆匆，每个人都像有故事。',
                'mood': '观察',
                'time_type': 'stay',
                'tags': ['urban', 'crowd']
            },
            {
                'location': '张江咖啡馆',
                'text': '一杯拿铁，一个下午。',
                'mood': '安静',
                'time_type': 'stay',
                'tags': ['alone', 'calm']
            },
            {
                'location': '外滩观景平台',
                'text': '对岸的灯火，像是另一个世界。',
                'mood': '淡然',
                'time_type': 'quiet',
                'tags': ['nature', 'urban', 'night']
            },
            {
                'location': '武康路老洋房',
                'text': '时光在这里慢了下来。',
                'mood': '安静',
                'time_type': 'stay',
                'tags': ['urban', 'alone']
            }
        ]
    
    @staticmethod
    def _filter_by_personality(contents, time_period, user_tags, tag_weights):
        """
        根据用户人格过滤内容
        
        Args:
            contents: 候选内容列表
            time_period: 时间段
            user_tags: 用户标签
            tag_weights: 标签权重
        
        Returns:
            list: 过滤后的内容（按权重排序）
        """
        # 获取时间段的类型权重
        time_type_weights = ContentGenerator._get_time_type_weights(time_period)
        
        scored_contents = []
        for content in contents:
            # 基础分数
            score = 1.0
            
            # 时间类型匹配
            time_type = content.get('time_type', 'action')
            score *= time_type_weights.get(time_type, 0.1)
            
            # 用户标签匹配
            content_tags = content.get('tags', [])
            for tag in user_tags:
                if tag in content_tags:
                    tag_weight = tag_weights.get(tag, {}).get('weight', 1.0)
                    score *= (1.0 + tag_weight * 0.1)
            
            scored_contents.append((content, score))
        
        # 按分数降序排序
        scored_contents.sort(key=lambda x: x[1], reverse=True)
        
        return [content for content, score in scored_contents]
    
    @staticmethod
    def _get_time_type_weights(time_period):
        """
        获取时间段的内容类型权重
        
        Args:
            time_period: 时间段
        
        Returns:
            dict: 类型权重 {'action': 0.6, 'stay': 0.3, 'quiet': 0.1}
        """
        if time_period == 'morning':
            return {'action': 0.6, 'stay': 0.3, 'quiet': 0.1}
        elif time_period == 'afternoon':
            return {'stay': 0.6, 'action': 0.3, 'quiet': 0.1}
        else:  # night
            return {'quiet': 0.6, 'stay': 0.3, 'action': 0.1}
    
    @staticmethod
    def _calculate_personality_weight(content, user_tags, tag_weights):
        """
        计算内容的人格权重
        
        Args:
            content: 内容对象
            user_tags: 用户标签
            tag_weights: 标签权重
        
        Returns:
            float: 人格权重值
        """
        weight = 1.0
        
        # 检查地点是否匹配用户偏好
        location = content.get('location', '')
        
        # 夜晚倾向
        if 'night' in user_tags:
            if any(word in location for word in ['滨江', '街道', '便利店']):
                night_weight = tag_weights.get('night', {}).get('weight', 1.0)
                weight *= (1.3 + night_weight * 0.2)
        
        # 独处倾向
        if 'alone' in user_tags:
            if any(word in location for word in ['咖啡馆', '公园', '美术馆']):
                alone_weight = tag_weights.get('alone', {}).get('weight', 1.0)
                weight *= (1.3 + alone_weight * 0.2)
        
        # 自然倾向
        if 'nature' in user_tags:
            if any(word in location for word in ['公园', '滨江', '海边']):
                nature_weight = tag_weights.get('nature', {}).get('weight', 1.0)
                weight *= (1.3 + nature_weight * 0.2)
        
        # 城市倾向
        if 'urban' in user_tags:
            if any(word in location for word in ['商场', '地铁站', '街道']):
                urban_weight = tag_weights.get('urban', {}).get('weight', 1.0)
                weight *= (1.3 + urban_weight * 0.2)
        
        # 情绪匹配
        if 'calm' in user_tags:
            if content.get('mood') in ['平静', '安静', '淡然']:
                calm_weight = tag_weights.get('calm', {}).get('weight', 1.0)
                weight *= (1.2 + calm_weight * 0.1)
        
        if 'chaotic' in user_tags:
            if content.get('mood') in ['混乱', '不安', '犹豫']:
                chaotic_weight = tag_weights.get('chaotic', {}).get('weight', 1.0)
                weight *= (1.2 + chaotic_weight * 0.1)
        
        return weight
