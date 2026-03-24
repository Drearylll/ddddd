"""
Go In 内容共创服务

负责 AI 内容生成、接力创作、夺擂创作等功能
"""

import random
from datetime import datetime


class ContentCreationService:
    """内容共创服务类"""
    
    # 短篇小说模板
    NOVEL_TEMPLATES = [
        {
            'title': '城市夜归人',
            'genre': '都市情感',
            'opening': '深夜的地铁站，最后一班列车刚刚驶离。她站在空荡荡的站台上，看着手中已经熄灭的手机屏幕...',
            'tags': ['都市', '情感', '治愈']
        },
        {
            'title': '咖啡馆的偶遇',
            'genre': '浪漫邂逅',
            'opening': '这是一家藏在老弄堂里的咖啡馆，木质门楣上挂着的风铃在风中轻摆。他推门而入，目光恰好对上窗边那个熟悉的身影...',
            'tags': ['浪漫', '邂逅', '温馨']
        },
        {
            'title': '雨夜的便利店',
            'genre': '生活小品',
            'opening': '暴雨突至，他躲进街角的 24 小时便利店。收银台的姑娘微笑着递来一杯热咖啡："外面雨大，坐会儿吧。"...',
            'tags': ['生活', '温暖', '小确幸']
        }
    ]
    
    # 四格漫画创意库
    COMIC_IDEAS = [
        {
            'title': '打工人的日常',
            'panels': [
                {'scene': '早上 7 点，闹钟响起', 'dialogue': '再睡 5 分钟...'},
                {'scene': '8 点半，狂奔赶地铁', 'dialogue': '要迟到了要迟到了！'},
                {'scene': '9 点整，打卡成功', 'dialogue': '呼...还好赶上了'},
                {'scene': '下班后，疲惫但满足', 'dialogue': '今天也辛苦了！'}
            ],
            'style': '轻松幽默'
        },
        {
            'title': '恋爱日记',
            'panels': [
                {'scene': '第一次约会前', 'dialogue': '穿什么好呢？'},
                {'scene': '见面时的紧张', 'dialogue': '你...你来啦'},
                {'scene': '牵手瞬间', 'dialogue': '手心好温暖'},
                {'scene': '分别时的不舍', 'dialogue': '明天还能见吗？'}
            ],
            'style': '甜蜜浪漫'
        }
    ]
    
    @staticmethod
    def generate_novel_content(theme=None):
        """
        生成短篇小说内容
        
        Args:
            theme: 主题（可选）
        
        Returns:
            dict: 小说内容
        """
        # 随机选择一个模板
        template = random.choice(ContentCreationService.NOVEL_TEMPLATES)
        
        # 生成后续情节（简化版，实际应该调用 AI）
        plot_developments = [
            '突然，一个陌生人走了过来，递给她一张纸条："有人在等你。"',
            '手机震动，是一条陌生号码发来的消息："别回头，跟我走。"',
            '她深吸一口气，做出了一个改变人生的决定...',
            '就在这时，灯光骤灭，周围陷入一片黑暗...'
        ]
        
        content = {
            'type': 'novel',
            'title': template['title'],
            'genre': template['genre'],
            'tags': template['tags'],
            'opening': template['opening'],
            'development': random.choice(plot_developments),
            'word_count': len(template['opening']) + len(random.choice(plot_developments)),
            'created_at': datetime.now().isoformat(),
            'author': 'AI 创作者',
            'likes': random.randint(10, 500),
            'comments': random.randint(5, 100),
            'co_create_available': True
        }
        
        return content
    
    @staticmethod
    def generate_comic_content(theme=None):
        """
        生成四格漫画内容
        
        Args:
            theme: 主题（可选）
        
        Returns:
            dict: 漫画内容
        """
        idea = random.choice(ContentCreationService.COMIC_IDEAS)
        
        content = {
            'type': 'comic',
            'title': idea['title'],
            'style': idea['style'],
            'panels': idea['panels'],
            'panel_count': len(idea['panels']),
            'created_at': datetime.now().isoformat(),
            'author': 'AI 画师',
            'likes': random.randint(50, 1000),
            'comments': random.randint(10, 200),
            'co_create_available': True
        }
        
        return content
    
    @staticmethod
    def create_relay_content(original_content, user_input):
        """
        创建接力内容（续写/续画）
        
        Args:
            original_content: 原始内容
            user_input: 用户输入（续写内容）
        
        Returns:
            dict: 接力后的新内容
        """
        relay_content = {
            'type': 'relay',
            'original_id': original_content.get('id'),
            'original_title': original_content.get('title'),
            'user_contribution': user_input,
            'ai_continuation': ContentCreationService._generate_ai_continuation(user_input),
            'created_at': datetime.now().isoformat(),
            'relay_count': original_content.get('relay_count', 0) + 1
        }
        
        return relay_content
    
    @staticmethod
    def _generate_ai_continuation(user_input):
        """
        根据用户输入生成 AI 续写（简化版）
        
        Args:
            user_input: 用户输入
        
        Returns:
            str: AI 续写内容
        """
        continuations = [
            '故事还在继续，下一个转角会发生什么呢？',
            '命运的齿轮开始转动，一切都变得不同...',
            '阳光透过云层洒下，新的旅程即将开始。',
            '她微微一笑，心中已经有了答案。'
        ]
        
        return random.choice(continuations)
    
    @staticmethod
    def create_challenge_content(requirement):
        """
        创建夺擂内容（根据要求创作）
        
        Args:
            requirement: 创作要求
        
        Returns:
            dict: 创作的内容
        """
        # 根据要求生成内容（简化版）
        if 'theme' in requirement:
            theme = requirement['theme']
        else:
            theme = random.choice(['爱情', '友情', '梦想', '成长'])
        
        content_type = requirement.get('type', 'novel')
        
        if content_type == 'novel':
            content = ContentCreationService.generate_novel_content(theme)
        elif content_type == 'comic':
            content = ContentCreationService.generate_comic_content(theme)
        else:
            content = ContentCreationService.generate_novel_content(theme)
        
        content['challenge_mode'] = True
        content['requirement'] = requirement
        content['created_at'] = datetime.now().isoformat()
        
        return content
    
    @staticmethod
    def get_co_create_options(content):
        """
        获取共创选项
        
        Args:
            content: 原始内容
        
        Returns:
            list: 共创选项列表
        """
        options = []
        
        if content['type'] == 'novel':
            options = [
                {
                    'type': 'relay',
                    'name': '接力续写',
                    'description': '延续这个故事，写下你的版本',
                    'available': True
                },
                {
                    'type': 'challenge',
                    'name': '夺擂创作',
                    'description': '根据新要求重新创作',
                    'available': True
                }
            ]
        elif content['type'] == 'comic':
            options = [
                {
                    'type': 'relay',
                    'name': '接力续画',
                    'description': '为漫画添加新的分镜',
                    'available': True
                },
                {
                    'type': 'challenge',
                    'name': '夺擂创作',
                    'description': '用不同风格重新演绎',
                    'available': True
                }
            ]
        
        return options
