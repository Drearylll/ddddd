"""
AI 文案策划服务
Go In App - 智能文案生成

功能：
1. 分析图片中的人物动作和表情
2. 结合地点氛围生成文案
3. 生成多种风格的文案（短句、长文）
4. 返回 JSON 格式的文案和建议标签

使用模型：
- 豆包 Pro（文本生成）
- 豆包 Vision Pro（图像理解）
- 阿里云百炼（备用）
"""

import requests
import json
from typing import Dict, List, Optional
from services.doubao_ai import get_doubao_ai, DoubaoAI


class CaptionGenerator:
    """文案生成器"""
    
    def __init__(self, use_backup=False):
        """
        初始化文案生成器
        
        Args:
            use_backup: 是否使用备用配置
        """
        self.ai = get_doubao_ai(use_backup=use_backup)
        
        # 文案风格模板
        self.style_templates = {
            "short": {
                "prompt": """请为这张照片写一个简短的朋友圈文案（20 字以内）。
要求：
- 简洁有感染力
- 像日常说话一样自然
- 带一点情绪或感悟
- 避免陈词滥调

参考风格：
- "把碎片拼起来，就是故事。"
- "今天的阳光刚刚好。"
- "这一刻，值得记录。"

地点氛围：{atmosphere}
风格标签：{style_tags}""",
                "max_tokens": 100,
                "temperature": 0.8
            },
            
            "long": {
                "prompt": """请为这张照片写一段朋友圈长文案（50-100 字）。
要求：
- 有场景感和画面感
- 带有情感共鸣
- 像是在讲述一个小故事
- 语言优美但不矫情

参考风格：
- "在这个喧嚣的城市里，总有一个角落属于你。也许是街角的咖啡店，也许是黄昏的江边，也许就是此刻脚下的路。"
- "生活就是这样吧，在忙碌中寻找片刻的宁静。看着人来人往，想着自己的心事。"

地点氛围：{atmosphere}
风格标签：{style_tags}""",
                "max_tokens": 300,
                "temperature": 0.7
            },
            
            "poetic": {
                "prompt": """请为这张照片写一首短诗或诗意文案（30-60 字）。
要求：
- 有意境和韵律感
- 使用意象和隐喻
- 表达细腻的情感
- 给人想象空间

参考风格：
- "黄昏把影子拉长/思念在风中飘荡/你站在城市的这头/望着那头的月光"
- "时光匆匆/我们在人海中相遇/又在风中告别/只留下/这一刻的微笑"

地点氛围：{atmosphere}
风格标签：{style_tags}""",
                "max_tokens": 200,
                "temperature": 0.9
            }
        }
    
    def generate_caption(
        self,
        image_url: str,
        style_tags: List[str],
        location_name: str = "",
        location_atmosphere: str = ""
    ) -> Dict:
        """
        生成文案
        
        Args:
            image_url: 融合后的图片 URL
            style_tags: 风格标签列表（如 ["慵懒", "午后", "文艺"]）
            location_name: 地点名称
            location_atmosphere: 地点氛围描述
            
        Returns:
            Dict: 生成的文案和标签
            {
                "success": True,
                "captions": {
                    "short": "短句文案",
                    "long": "长句文案",
                    "poetic": "诗意文案"
                },
                "hashtags": ["#生活碎片", "#AI 日记"],
                "analysis": "人物动作和表情分析"
            }
        """
        print("\n📝 开始生成文案...")
        
        # 步骤 1：分析图片中的人物动作和表情
        print("  【1】分析图片中的人物动作和表情...")
        analysis = self._analyze_image_content(image_url)
        
        # 步骤 2：结合地点氛围生成文案
        print("  【2】结合地点氛围生成文案...")
        
        # 准备提示词参数
        style_tags_str = ", ".join(style_tags) if style_tags else "日常"
        atmosphere = location_atmosphere or "日常生活场景"
        
        captions = {}
        
        # 生成短句文案
        print("    - 生成短句文案...")
        short_result = self._generate_with_style(
            "short", 
            image_url, 
            analysis,
            atmosphere, 
            style_tags_str
        )
        captions["short"] = short_result.get("content", "")
        
        # 生成长句文案
        print("    - 生成长句文案...")
        long_result = self._generate_with_style(
            "long", 
            image_url, 
            analysis,
            atmosphere, 
            style_tags_str
        )
        captions["long"] = long_result.get("content", "")
        
        # 生成诗意文案（可选）
        print("    - 生成诗意文案...")
        poetic_result = self._generate_with_style(
            "poetic", 
            image_url, 
            analysis,
            atmosphere, 
            style_tags_str
        )
        captions["poetic"] = poetic_result.get("content", "")
        
        # 步骤 3：生成建议的标签
        print("  【3】生成建议的标签...")
        hashtags = self._generate_hashtags(style_tags, location_name)
        
        # 组装结果
        result = {
            "success": True,
            "captions": captions,
            "hashtags": hashtags,
            "analysis": analysis.get("analysis", ""),
            "location": location_name,
            "atmosphere": atmosphere
        }
        
        print("✅ 文案生成完成！")
        return result
    
    def _analyze_image_content(self, image_url: str) -> Dict:
        """
        分析图片内容（人物动作、表情、场景）
        
        Args:
            image_url: 图片 URL
            
        Returns:
            Dict: 分析结果
        """
        prompt = """请详细分析这张图片：

【分析要点】
1. 人物信息：
   - 有几个人？
   - 他们的动作是什么？（站立、坐着、行走等）
   - 表情如何？（开心、沉思、放松等）
   - 穿着打扮有什么特点？

2. 场景信息：
   - 这是什么地方？（室内/室外、城市/自然等）
   - 光线如何？（明亮、黄昏、夜晚等）
   - 周围有什么显著的元素？

3. 氛围感受：
   - 整体给人的感觉？（温馨、孤独、热闹、宁静等）
   - 适合什么样的情绪表达？

请用简洁的语言描述，200 字左右。"""

        # 调用 AI 分析
        result = self.ai.analyze_image(image_url, prompt)
        
        if result.get("success"):
            return {
                "success": True,
                "analysis": result.get("analysis", ""),
                "model": result.get("model", "")
            }
        else:
            # 降级到模拟数据
            return self._mock_analyze_image_content()
    
    def _generate_with_style(
        self,
        style: str,
        image_url: str,
        analysis: Dict,
        atmosphere: str,
        style_tags_str: str
    ) -> Dict:
        """
        根据指定风格生成文案
        
        Args:
            style: 文案风格 ("short", "long", "poetic")
            image_url: 图片 URL
            analysis: 图片分析结果
            atmosphere: 地点氛围
            style_tags_str: 风格标签字符串
            
        Returns:
            Dict: 生成的文案
        """
        # 获取风格模板
        template = self.style_templates.get(style, self.style_templates["short"])
        
        # 构建完整的提示词
        full_prompt = f"""【图片分析】
{analysis.get('analysis', '日常生活场景')}

【文案创作】
{template['prompt'].format(
            atmosphere=atmosphere,
            style_tags=style_tags_str
        )}

请直接创作文案，不需要解释说明。"""

        # 调用 AI 生成
        result = self.ai.generate_text(
            prompt=full_prompt,
            system_prompt="你是一个专业的社交媒体文案创作者，擅长写打动人心的短文案。你的文字简洁有力，富有感染力，像是朋友间的分享，而不是广告语。",
            max_tokens=template["max_tokens"],
            temperature=template["temperature"]
        )
        
        if result.get("success"):
            content = result.get("content", "").strip()
            # 清理可能的多余内容
            content = self._clean_caption(content)
            return {
                "success": True,
                "content": content,
                "model": result.get("model", "")
            }
        else:
            # 降级到模拟数据
            return self._mock_generate_caption(style)
    
    def _generate_hashtags(
        self,
        style_tags: List[str],
        location_name: str
    ) -> List[str]:
        """
        生成建议的标签
        
        Args:
            style_tags: 风格标签
            location_name: 地点名称
            
        Returns:
            List[str]: 标签列表
        """
        # 基础标签
        base_tags = ["#生活碎片", "#AI 日记"]
        
        # 根据风格标签生成
        style_hashtags = []
        for tag in style_tags[:3]:  # 最多取前 3 个
            # 将标签转换为 hashtag 格式
            hashtag = f"#{tag}"
            style_hashtags.append(hashtag)
        
        # 如果有地点名称，添加地点标签
        if location_name:
            location_tag = f"#{location_name.replace(' ', '')}"
            style_hashtags.append(location_tag)
        
        # 合并标签（去重）
        all_tags = list(dict.fromkeys(base_tags + style_hashtags))
        
        # 限制标签数量（最多 6 个）
        return all_tags[:6]
    
    def _clean_caption(self, text: str) -> str:
        """
        清理文案中的多余内容
        
        Args:
            text: 原始文案
            
        Returns:
            str: 清理后的文案
        """
        # 移除可能的前缀
        prefixes_to_remove = [
            "文案：",
            "短句：",
            "长句：",
            "诗意：",
            "以下是文案：",
            "生成的文案："
        ]
        
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # 移除引号（如果是成对的）
        if (text.startswith('"') and text.endswith('"')) or \
           (text.startswith("'") and text.endswith("'")):
            text = text[1:-1]
        
        # 移除换行符（替换为空格）
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # 压缩多余的空格
        while '  ' in text:
            text = text.replace('  ', ' ')
        
        return text.strip()
    
    def _mock_analyze_image_content(self) -> Dict:
        """模拟图片分析（用于降级）"""
        return {
            "success": True,
            "analysis": "图片中有一个人站在城市场景中，姿态放松自然，表情平静带着淡淡的微笑。背景是现代都市街景，光线柔和，可能是午后时分。整体氛围轻松惬意，展现了日常生活中的美好瞬间。",
            "model": "mock-vision"
        }
    
    def _mock_generate_caption(self, style: str) -> Dict:
        """模拟文案生成（用于降级）"""
        mock_captions = {
            "short": {
                "content": "把平凡的日子，过成喜欢的样子。",
                "model": "mock-text"
            },
            "long": {
                "content": "在这个快节奏的城市里，我们都在寻找属于自己的节奏。也许是路边的一朵花，也许是天边的一片云，又或许，就是此刻脚下走过的路。生活的美好，往往藏在这些不经意的瞬间里。",
                "model": "mock-text"
            },
            "poetic": {
                "content": "阳光透过树叶的缝隙/洒在肩头/这一刻的温暖/足够抵御整个冬天的寒",
                "model": "mock-text"
            }
        }
        
        return mock_captions.get(style, mock_captions["short"])


# 全局实例
_caption_generator = None


def get_caption_generator(use_backup=False):
    """获取文案生成器实例"""
    global _caption_generator
    if _caption_generator is None:
        _caption_generator = CaptionGenerator(use_backup=use_backup)
    return _caption_generator


# 便捷函数
def generate_caption(
    image_url: str,
    style_tags: List[str],
    location_name: str = "",
    location_atmosphere: str = ""
) -> Dict:
    """
    生成文案（便捷函数）
    
    Args:
        image_url: 融合后的图片 URL
        style_tags: 风格标签列表
        location_name: 地点名称
        location_atmosphere: 地点氛围描述
        
    Returns:
        Dict: 生成的文案和标签
    """
    generator = get_caption_generator(use_backup=False)
    return generator.generate_caption(
        image_url,
        style_tags,
        location_name,
        location_atmosphere
    )
