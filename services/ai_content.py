"""
AI 内容生成服务
Go In App - 大模型 API 对接

支持内容类型：
1. 短篇小说（200-500 字）
2. 四格漫画脚本
3. 朋友圈文案（50-100 字）

技术方案：
- 通义千问 / GPT-4 / Claude
- 系统提示词工程
- 结构化输出（JSON）
"""

import json
import random
import requests
from datetime import datetime

# API 配置（可配置环境变量）
LLM_API_KEY = "sk-87930805570a46c38f5eefa1c03cd2e6"  # 通义千问 API Key
LLM_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"  # 通义千问


class ContentAIService:
    """AI 内容生成服务"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or LLM_API_KEY
        self.use_mock = not self.api_key  # 没有 API Key 时使用模拟数据
    
    # ========== 公开方法 ==========
    
    def generate_novel(self, location, user_profile=None, mood=None):
        """
        生成短篇小说
        
        Args:
            location: 地点名称（如"星巴克 (南京东路店)"）
            user_profile: 用户画像（性别、年龄等）
            mood: 情绪基调（如"温暖"、"孤独"、"期待"）
            
        Returns:
            dict: {
                "title": "标题",
                "content": "正文内容",
                "word_count": 字数，
                "location": 地点，
                "mood": 情绪
            }
        """
        if self.use_mock:
            return self._mock_novel(location, mood)
        
        # 调用真实 API
        return self._call_llm_api(self._build_novel_prompt(location, user_profile, mood))
    
    def generate_comic_script(self, location, user_profile=None, theme=None):
        """
        生成四格漫画脚本
        
        Args:
            location: 地点名称
            user_profile: 用户画像
            theme: 主题（如"日常"、"惊喜"、"巧合"）
            
        Returns:
            dict: {
                "title": "漫画标题",
                "panels": [
                    {"panel": 1, "scene": "场景描述", "dialogue": "台词/心理活动"},
                    {"panel": 2, "scene": "场景描述", "dialogue": "台词/心理活动"},
                    {"panel": 3, "scene": "场景描述", "dialogue": "台词/心理活动"},
                    {"panel": 4, "scene": "场景描述", "dialogue": "台词/心理活动"}
                ],
                "location": 地点，
                "theme": 主题
            }
        """
        if self.use_mock:
            return self._mock_comic(location, theme)
        
        return self._call_llm_api(self._build_comic_prompt(location, user_profile, theme))
    
    def generate_moments_caption(self, location, user_profile=None, photo_desc=None):
        """
        生成朋友圈文案
        
        Args:
            location: 地点名称
            user_profile: 用户画像
            photo_desc: 照片描述（可选）
            
        Returns:
            dict: {
                "content": "文案内容",
                "emoji": "推荐 emoji",
                "location": 地点，
                "mood": 情绪标签
            }
        """
        if self.use_mock:
            return self._mock_moments(location, photo_desc)
        
        return self._call_llm_api(self._build_moments_prompt(location, user_profile, photo_desc))
    
    # ========== 内部方法 ==========
    
    def _call_llm_api(self, prompt):
        """调用大模型 API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "qwen-plus",  # 通义千问模型
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个 AI 社交 App 的内容生成器。请生成符合现实逻辑、有情感共鸣的内容。输出必须是 JSON 格式。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "result_format": "text"
            }
        }
        
        try:
            response = requests.post(LLM_API_URL, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            # 解析返回的 JSON
            if result.get('output') and result['output'].get('text'):
                content = result['output']['text']
                print(f"✅ API 调用成功，返回内容：{content[:100]}...")
                return json.loads(content)
            else:
                print(f"❌ API 返回格式异常：{result}")
                return self._mock_fallback(prompt)
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP 错误：{e}")
            print(f"响应内容：{response.text}")
            return self._mock_fallback(prompt)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败：{e}")
            return self._mock_fallback(prompt)
        except Exception as e:
            print(f"❌ AI 内容生成失败：{e}")
            # 降级到模拟数据
            return self._mock_fallback(prompt)
    
    def _build_novel_prompt(self, location, user_profile, mood):
        """构建小说生成 Prompt"""
        return f"""
请生成一个发生在【{location}】的短篇故事。

要求：
1. 200-500 字
2. 情绪基调：{mood or '温暖/治愈'}
3. 符合现实逻辑，有具体细节
4. 有情感共鸣，像真实发生的事
5. 不要虚构夸张的情节

用户画像：{user_profile or '普通年轻人'}

请输出 JSON 格式：
{{
    "title": "标题（10 字以内）",
    "content": "正文内容",
    "word_count": 字数（数字）,
    "location": "{location}",
    "mood": "{mood or '温暖'}"
}}
"""
    
    def _build_comic_prompt(self, location, user_profile, theme):
        """构建漫画脚本 Prompt"""
        return f"""
请生成一个发生在【{location}】的四格漫画脚本。

主题：{theme or '日常小确幸'}

要求：
1. 4 格场景，每格有场景描述和台词/心理活动
2. 符合现实逻辑
3. 轻松有趣或有共鸣
4. 场景要具体可视觉化

用户画像：{user_profile or '普通年轻人'}

请输出 JSON 格式：
{{
    "title": "漫画标题（10 字以内）",
    "panels": [
        {{"panel": 1, "scene": "第一格场景描述", "dialogue": "台词/心理活动"}},
        {{"panel": 2, "scene": "第二格场景描述", "dialogue": "台词/心理活动"}},
        {{"panel": 3, "scene": "第三格场景描述", "dialogue": "台词/心理活动"}},
        {{"panel": 4, "scene": "第四格场景描述", "dialogue": "台词/心理活动"}}
    ],
    "location": "{location}",
    "theme": "{theme or '日常'}"
}}
"""
    
    def _build_moments_prompt(self, location, user_profile, photo_desc):
        """构建朋友圈文案 Prompt"""
        return f"""
请为【{location}】生成一条朋友圈文案。

照片描述：{photo_desc or '日常场景'}

要求：
1. 50-100 字
2. 有情绪表达，不要太平淡
3. 符合年轻人说话方式
4. 可以带点小感慨或小幽默

用户画像：{user_profile or '普通年轻人'}

请输出 JSON 格式：
{{
    "content": "文案内容",
    "emoji": "推荐 emoji（1-2 个）",
    "location": "{location}",
    "mood": "情绪标签（如'惬意'、'小确幸'、'日常'）"
}}
"""
    
    # ========== 模拟数据（用于开发测试） ==========
    
    def _mock_novel(self, location, mood):
        """模拟小说数据"""
        templates = [
            {
                "title": "午后的偶遇",
                "content": f"在{location}的角落里，阳光透过玻璃窗洒在木桌上。她低头搅拌着咖啡，勺子碰到杯壁发出清脆的声响。对面的座位空着，像是在等待什么，又像是在告别什么。手机屏幕亮起，是一条迟到的消息：「抱歉，今天不能来了。」她笑了笑，把手机扣在桌上。有些等待，本就不需要结果。",
                "word_count": 128,
                "location": location,
                "mood": mood or "温暖"
            },
            {
                "title": "深夜食堂",
                "content": f"{location}的灯光在夜色中格外温暖。他推门进来，风铃轻响。老板抬头看了一眼，什么也没问，开始热一份便当。这是他们之间的默契——不需要寒暄，只需要一份刚好的温度。在这个城市，总有一个地方，会让你觉得，被世界温柔以待。",
                "word_count": 115,
                "location": location,
                "mood": "治愈"
            }
        ]
        return random.choice(templates)
    
    def _mock_comic(self, location, theme):
        """模拟漫画脚本"""
        return {
            "title": "咖啡店的日常",
            "panels": [
                {"panel": 1, "scene": f"{location}，早上 9 点，店内刚开门", "dialogue": "「今天也要加油啊」"},
                {"panel": 2, "scene": "点单时发现钱包忘带了", "dialogue": "「啊...糟糕...」"},
                {"panel": 3, "scene": "后面的女生递过一张卡", "dialogue": "「我请你吧」"},
                {"panel": 4, "scene": "两人相视一笑，阳光正好", "dialogue": "「谢谢」「下次我请你」"}
            ],
            "location": location,
            "theme": theme or "日常"
        }
    
    def _mock_moments(self, location, photo_desc):
        """模拟朋友圈文案"""
        templates = [
            {
                "content": f"在{location}发呆的下午，时间好像变慢了。生活不一定要很赶，偶尔停下来，才能看见风景。",
                "emoji": "☕️",
                "location": location,
                "mood": "惬意"
            },
            {
                "content": f"路过{location}，突然想起某个人。有些记忆，总是在不经意间浮现。",
                "emoji": "🌆",
                "location": location,
                "mood": "怀念"
            },
            {
                "content": f"{location}的这家店，藏着我整个青春的回忆。",
                "emoji": "📸",
                "location": location,
                "mood": "回忆"
            }
        ]
        return random.choice(templates)
    
    def _mock_fallback(self, prompt):
        """降级模拟数据"""
        if "小说" in prompt or "故事" in prompt:
            return self._mock_novel("某地", "温暖")
        elif "漫画" in prompt:
            return self._mock_comic("某地", "日常")
        else:
            return self._mock_moments("某地", "日常")


# 全局实例
_ai_service = None

def get_ai_service():
    """获取 AI 服务实例"""
    global _ai_service
    if _ai_service is None:
        _ai_service = ContentAIService()
    return _ai_service
