"""
验证 DeepSeek API 配置
"""

import os
from dotenv import load_dotenv

# 加载本地环境变量
load_dotenv('.env.local')

# 获取 API Key
deepseek_key = os.getenv("DEEPSEEK_API_KEY")

print("="*60)
print("DeepSeek API 配置验证")
print("="*60)

if deepseek_key:
    print(f"\n✅ DeepSeek API Key 已配置")
    print(f"   Key: {deepseek_key[:15]}...{deepseek_key[-10:]}")
    
    # 测试 API 调用
    print("\n正在测试 API 调用...")
    
    try:
        import requests
        
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {deepseek_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": "你好，请介绍一下你自己"}
            ],
            "max_tokens": 100
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            reply = result['choices'][0]['message']['content']
            
            print(f"\n✅ API 调用成功！")
            print(f"\n🤖 AI 回复:\n{reply}")
            
            # 测试 Function Calling
            print("\n" + "="*60)
            print("测试 Function Calling（意图识别）")
            print("="*60)
            
            functions_payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": "今天心情不太好，想去海边走走"}
                ],
                "functions": [{
                    "name": "extract_intent",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "intent_type": {
                                "type": "string",
                                "enum": ["want_to_visit", "want_to_do", "mood", "other"]
                            },
                            "location": {"type": "string"},
                            "activity": {"type": "string"},
                            "mood": {"type": "string"}
                        }
                    }
                }]
            }
            
            func_response = requests.post(url, json=functions_payload, headers=headers, timeout=30)
            
            if func_response.status_code == 200:
                func_result = func_response.json()
                ai_message = func_result['choices'][0]['message']
                
                print(f"\n✅ Function Calling 成功！")
                
                if ai_message.get('function_call'):
                    import json
                    intent = json.loads(ai_message['function_call']['arguments'])
                    print(f"\n🎯 识别到的意图:")
                    print(f"   类型：{intent.get('intent_type')}")
                    print(f"   地点：{intent.get('location')}")
                    print(f"   活动：{intent.get('activity')}")
                    print(f"   情绪：{intent.get('mood')}")
                else:
                    print(f"\n📝 AI 回复：{ai_message.get('content', '')}")
                
                print("\n" + "="*60)
                print("✅ 所有测试通过！DeepSeek API 配置正确")
                print("="*60)
                print("\n下一步:")
                print("1. 启动应用：python app.py")
                print("2. 访问聊天页面：http://localhost:5000/go")
                print("3. 体验真实的 AI 对话和意图识别功能")
                print()
            else:
                print(f"\n❌ Function Calling 测试失败：HTTP {func_response.status_code}")
                print(f"错误信息：{func_response.text}")
        else:
            print(f"\n❌ API 调用失败：HTTP {response.status_code}")
            print(f"错误信息：{response.text}")
            
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
else:
    print(f"\n❌ DeepSeek API Key 未配置")
    print("\n请按以下步骤操作:")
    print("1. 检查 .env.local 文件是否存在")
    print("2. 确认 DEEPSEEK_API_KEY 已正确配置")
    print("3. 重新启动应用")
    print()
