"""
多模态 AI 分析服务
Go In App - 地点图片风格分析

功能：
1. 分析地点图片的色调（冷色/暖色）
2. 分析地点图片的风格（文艺/繁华/宁静）
3. 判断场景类型（适合约会/发呆/打卡）
4. 输出 JSON 格式的风格标签和氛围描述

使用模型：
- Qwen-VL（阿里云百炼）
- GPT-4o（可选）
"""

import requests
import json
from typing import Dict, Optional

# API 配置
DASHSCOPE_API_KEY = ""  # 阿里云百炼 API Key（需配置）
DASHSCOPE_VL_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

# 备用配置
GPT4O_API_KEY = ""  # OpenAI API Key（可选）
GPT4O_URL = "https://api.openai.com/v1/chat/completions"


class LocationStyleAnalyzer:
    """地点风格分析器"""
    
    def __init__(self, api_key=None, model="qwen-vl"):
        """
        初始化分析器
        
        Args:
            api_key: API Key
            model: 使用的模型 ("qwen-vl" 或 "gpt-4o")
        """
        self.api_key = api_key or DASHSCOPE_API_KEY
        self.model = model
        self.use_mock = not self.api_key  # 没有 API Key 时使用模拟数据
        
        # 分析提示词模板
        self.prompt_template = """
你是一个专业的地点场景分析师。请分析这张图片并提取以下信息：

【图片信息】
- 地点名称：{name}
- 地址：{address}

【分析要求】
1. 色调分析：判断主色调是冷色还是暖色
2. 风格分析：判断是文艺、繁华、宁静、复古、现代等风格
3. 场景类型：判断适合约会、发呆、打卡、拍照、休闲等场景
4. 氛围描述：用一段优美的文字描述这个地点的氛围

【输出格式】
请严格按照以下 JSON 格式输出（不要包含其他内容）：
{{
    "color_tone": "暖色/冷色/中性",
    "style_tags": ["标签 1", "标签 2", "标签 3"],
    "scene_type": ["适合场景 1", "适合场景 2"],
    "atmosphere_description": "一段优美的氛围描述（100 字以内）",
    "keywords": ["关键词 1", "关键词 2", "关键词 3"]
}}

【示例输出】
{{
    "color_tone": "暖色",
    "style_tags": ["文艺", "复古", "宁静"],
    "scene_type": ["适合发呆", "适合拍照"],
    "atmosphere_description": "阳光透过梧桐树叶洒在石板路上，斑驳的光影中透着老上海的风情。这里时间仿佛慢了下来，适合一个人静静发呆，或与好友轻声聊天。",
    "keywords": ["老上海", "梧桐树", "石板路", "慢生活"]
}}
"""
    
    def analyze_location_style(self, image_url: str, name: str, address: str = "") -> Dict:
        """
        分析地点图片风格
        
        Args:
            image_url: 图片 URL
            name: 地点名称
            address: 地点地址（可选）
            
        Returns:
            Dict: 分析结果
            {
                "color_tone": "暖色",
                "style_tags": ["文艺", "复古", "宁静"],
                "scene_type": ["适合发呆", "适合拍照"],
                "atmosphere_description": "阳光透过梧桐树叶...",
                "keywords": ["老上海", "梧桐树", "石板路"]
            }
        """
        if self.use_mock:
            return self._mock_analyze(image_url, name, address)
        
        if self.model == "qwen-vl":
            return self._analyze_with_qwen(image_url, name, address)
        elif self.model == "gpt-4o":
            return self._analyze_with_gpt4o(image_url, name, address)
        else:
            return self._mock_analyze(image_url, name, address)
    
    def _analyze_with_qwen(self, image_url: str, name: str, address: str) -> Dict:
        """使用 Qwen-VL 分析"""
        prompt = self.prompt_template.format(name=name, address=address)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "qwen-vl-max",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"image": image_url},
                            {"text": prompt}
                        ]
                    }
                ]
            },
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 500,
                "result_format": "message"
            }
        }
        
        try:
            response = requests.post(DASHSCOPE_VL_URL, headers=headers, json=payload, timeout=15)
            result = response.json()
            
            if response.status_code == 200 and 'choices' in result:
                content = result['choices'][0]['message']['content']
                return self._parse_json_response(content)
            else:
                print(f"❌ Qwen-VL API 调用失败：{result.get('message', 'Unknown error')}")
                return self._mock_analyze(image_url, name, address)
                
        except Exception as e:
            print(f"❌ Qwen-VL 分析异常：{e}")
            return self._mock_analyze(image_url, name, address)
    
    def _analyze_with_gpt4o(self, image_url: str, name: str, address: str) -> Dict:
        """使用 GPT-4o 分析"""
        prompt = self.prompt_template.format(name=name, address=address)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(GPT4O_URL, headers=headers, json=payload, timeout=15)
            result = response.json()
            
            if response.status_code == 200 and 'choices' in result:
                content = result['choices'][0]['message']['content']
                return self._parse_json_response(content)
            else:
                print(f"❌ GPT-4o API 调用失败：{result.get('error', {}).get('message', 'Unknown error')}")
                return self._mock_analyze(image_url, name, address)
                
        except Exception as e:
            print(f"❌ GPT-4o 分析异常：{e}")
            return self._mock_analyze(image_url, name, address)
    
    def _parse_json_response(self, content: str) -> Dict:
        """解析 JSON 响应"""
        try:
            # 尝试直接解析
            return json.loads(content)
        except:
            # 尝试提取 JSON 内容
            import re
            json_match = re.search(r'\{.*?\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            # 解析失败返回模拟数据
            print("⚠️ JSON 解析失败，使用模拟数据")
            return self._mock_analyze("", "", "")
    
    def _mock_analyze(self, image_url: str, name: str, address: str) -> Dict:
        """模拟分析（用于开发测试）"""
        # 根据地点类型生成模拟数据
        mock_data = self._get_mock_data_by_name(name)
        
        return {
            "color_tone": mock_data["color_tone"],
            "style_tags": mock_data["style_tags"],
            "scene_type": mock_data["scene_type"],
            "atmosphere_description": mock_data["atmosphere_description"],
            "keywords": mock_data["keywords"]
        }
    
    def _get_mock_data_by_name(self, name: str) -> Dict:
        """根据地点名称生成模拟数据"""
        name_lower = name.lower()
        
        # 咖啡厅
        if "咖啡" in name or "starbucks" in name_lower or "manner" in name_lower:
            return {
                "color_tone": "暖色",
                "style_tags": ["文艺", "小资", "舒适"],
                "scene_type": ["适合发呆", "适合聊天", "适合办公"],
                "atmosphere_description": "温暖的灯光下，咖啡香气弥漫。这里是一个可以放慢脚步的角落，适合一个人静静发呆，或与好友分享时光。",
                "keywords": ["咖啡香", "慢生活", "温暖"]
            }
        
        # 景点/公园
        elif "公园" in name or "外滩" in name or "豫园" in name:
            return {
                "color_tone": "自然色",
                "style_tags": ["宁静", "自然", "开阔"],
                "scene_type": ["适合散步", "适合拍照", "适合放松"],
                "atmosphere_description": "绿意盎然中透着城市的活力，这里是喧嚣都市中的一片净土。清晨或黄昏时分，最适合来这里感受自然与城市的交融。",
                "keywords": ["自然", "城市绿洲", "放松"]
            }
        
        # 商场
        elif "商场" in name or "购物" in name or "新世界" in name or "来福士" in name:
            return {
                "color_tone": "冷色",
                "style_tags": ["现代", "繁华", "时尚"],
                "scene_type": ["适合购物", "适合打卡", "适合约会"],
                "atmosphere_description": "时尚与现代感交织，这里是潮流的聚集地。明亮的灯光、精致的橱窗，每一个角落都值得驻足。",
                "keywords": ["时尚", "潮流", "繁华"]
            }
        
        # 餐厅
        elif "酒楼" in name or "餐厅" in name or "老半斋" in name:
            return {
                "color_tone": "暖色",
                "style_tags": ["传统", "温馨", "烟火气"],
                "scene_type": ["适合聚餐", "适合品尝美食"],
                "atmosphere_description": "传统的中式装饰，温暖的色调，这里充满了人间烟火气。与亲朋好友围坐一桌，分享美食与欢笑。",
                "keywords": ["美食", "传统", "温馨"]
            }
        
        # 步行街
        elif "步行街" in name or "南京路" in name:
            return {
                "color_tone": "多彩",
                "style_tags": ["热闹", "繁华", "历史"],
                "scene_type": ["适合逛街", "适合打卡", "适合拍照"],
                "atmosphere_description": "百年老街见证着城市的变迁，霓虹闪烁中透着历史的厚重。这里是游客必到之地，也是本地人的生活记忆。",
                "keywords": ["百年老街", "霓虹", "历史"]
            }
        
        # 默认
        else:
            return {
                "color_tone": "中性",
                "style_tags": ["独特", "城市"],
                "scene_type": ["适合探索", "适合拍照"],
                "atmosphere_description": "这个地点有着独特的魅力，等待着你的发现和探索。每一个角落都有故事，每一刻都有不同的风景。",
                "keywords": ["独特", "探索", "城市"]
            }


# 全局实例
_analyzer = None

def get_location_analyzer(api_key=None, model="qwen-vl"):
    """获取地点风格分析器实例"""
    global _analyzer
    if _analyzer is None:
        _analyzer = LocationStyleAnalyzer(api_key, model)
    return _analyzer


# 便捷函数
def analyze_location_style(image_url: str, name: str, address: str = "") -> Dict:
    """
    分析地点图片风格（便捷函数）
    
    Args:
        image_url: 图片 URL
        name: 地点名称
        address: 地点地址（可选）
        
    Returns:
        Dict: 分析结果
    """
    analyzer = get_location_analyzer()
    return analyzer.analyze_location_style(image_url, name, address)
