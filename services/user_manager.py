"""
用户数据管理服务

统一管理用户数据的读取和保存
"""

import json
import os
from datetime import datetime


class UserManager:
    """用户数据管理器"""
    
    @staticmethod
    def get_user_data(user_id=None):
        """
        获取用户数据
        
        Args:
            user_id: 用户 ID（可选，默认从 session 获取）
        
        Returns:
            dict: 用户数据
        """
        from flask import session
        
        if user_id is None:
            user_id = session.get('user_id')
        
        if not user_id:
            return {}
        
        # 从文件加载
        data_file = f'user_data/{user_id}.json'
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ERROR] Failed to load user data: {e}")
                return {}
        
        return {}
    
    @staticmethod
    def save_user_data(key, value, user_id=None):
        """
        保存用户数据
        
        Args:
            key: 数据键
            value: 数据值
            user_id: 用户 ID
        """
        from flask import session
        
        if user_id is None:
            user_id = session.get('user_id')
        
        if not user_id:
            print(f"[WARNING] No user_id found, cannot save data")
            return
        
        # 确保目录存在
        os.makedirs('user_data', exist_ok=True)
        
        # 加载现有数据
        data = UserManager.get_user_data(user_id)
        data[key] = value
        
        # 保存到文件
        data_file = f'user_data/{user_id}.json'
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[DEBUG] Saved user data: {key} = {value}")
        except Exception as e:
            print(f"[ERROR] Failed to save user data: {e}")
    
    @staticmethod
    def get_or_create_user_id():
        """
        获取或创建用户 ID
        
        Returns:
            str: 用户 ID
        """
        from flask import session
        import uuid
        
        user_id = session.get('user_id')
        
        if not user_id:
            # 尝试从客户端获取（如果之前保存过）
            # 这需要在请求头中传递
            # 暂时生成新的，但会在前端持久化
            user_id = str(uuid.uuid4())[:8]
            session['user_id'] = user_id
            
            # 初始化用户数据
            UserManager.save_user_data('created_at', datetime.now().isoformat(), user_id)
            UserManager.save_user_data('user_id', user_id, user_id)
            
            print(f"[INFO] Created new user: {user_id}")
        else:
            print(f"[INFO] Using existing user: {user_id}")
        
        return user_id
    
    @staticmethod
    def clear_user_data(user_id=None):
        """
        清除用户数据
        
        Args:
            user_id: 用户 ID
        """
        from flask import session
        
        if user_id is None:
            user_id = session.get('user_id')
        
        if not user_id:
            return
        
        data_file = f'user_data/{user_id}.json'
        if os.path.exists(data_file):
            try:
                os.remove(data_file)
                print(f"[INFO] Cleared user data for: {user_id}")
            except Exception as e:
                print(f"[ERROR] Failed to clear user data: {e}")
