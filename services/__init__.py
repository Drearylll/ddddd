"""
Go In Services Package

服务层包含核心业务逻辑
"""

# 延迟导入，避免 Vercel 部署时因缺少依赖而失败
__all__ = [
    'ContentGenerator',
    'UserManager',
    'UserService',
    'ContentCreationService',
    'MomentsService'
]

def __getattr__(name):
    """延迟导入服务类"""
    if name == 'ContentGenerator':
        from .content_generator import ContentGenerator
        return ContentGenerator
    elif name == 'UserManager':
        from .user_manager import UserManager
        return UserManager
    elif name == 'UserService':
        from .user_service import UserService
        return UserService
    elif name == 'ContentCreationService':
        from .content_creation_service import ContentCreationService
        return ContentCreationService
    elif name == 'MomentsService':
        from .moments_service import MomentsService
        return MomentsService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
