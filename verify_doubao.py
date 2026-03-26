"""
验证火山引擎豆包 API 配置
"""

import os
from dotenv import load_dotenv

# 加载本地环境变量
load_dotenv('.env.local')

# 获取 API Key
doubao_key = os.getenv("DOUBAO_API_KEY")

print("="*60)
print("火山引擎豆包 API 配置验证")
print("="*60)

if doubao_key:
    print(f"\n✅ 豆包 API Key 已配置")
    print(f"   Key: {doubao_key[:15]}...{doubao_key[-10:]}")
    
    # 测试 API 调用
    print("\n正在测试 API 调用...")
    
    try:
        import requests
        import json
        
        url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        headers = {
            "Authorization": f"Bearer {doubao_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "doubao-lite-4k",  # 使用免费额度模型
            "messages": [
                {"role": "user", "content": "你好，请介绍一下你自己"}
            ],
            "max_tokens": 200
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            reply = result['choices'][0]['message']['content']
            
            print(f"\n✅ API 调用成功！")
            print(f"\n🤖 AI 回复:\n{reply}")
            
            # 测试意图识别
            print("\n" + "="*60)
            print("测试意图识别（Prompt Engineering）")
            print("="*60)
            
            system_prompt = """你是一个温暖的 AI 朋友，名叫"Go"。
你的任务是倾听用户的心声，理解他们的想法和感受。

当用户表达想去某地、想做某事时，你要敏锐地捕捉这些意图，并在回复中自然地回应。

【重要】请在回复的最后，如果检测到用户有明确的意图（想去某地、想做某事、情绪状态），请用 JSON 格式标注：
<intent>{"intent_type": "want_to_visit|want_to_do|mood|other", "location": "地点", "activity": "活动", "mood": "情绪"}</intent>

如果没有明确意图，不需要添加此标注。"""
            
            test_message = "今天心情不太好，想去海边走走"
            
            intent_payload = {
                "model": "doubao-lite-4k",  # 使用免费额度模型
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": test_message}
                ],
                "max_tokens": 300
            }
            
            intent_response = requests.post(url, json=intent_payload, headers=headers, timeout=30)
            
            if intent_response.status_code == 200:
                intent_result = intent_response.json()
                ai_content = intent_result['choices'][0]['message']['content']
                
                print(f"\n测试消息：{test_message}")
                print(f"\n📝 AI 完整回复:\n{ai_content}")
                
                # 提取意图
                if '<intent>' in ai_content:
                    import re
                    intent_match = re.search(r'<intent>(.*?)</intent>', ai_content, re.DOTALL)
                    if intent_match:
                        intent_data = json.loads(intent_match.group(1))
                        
                        print(f"\n🎯 成功识别意图:")
                        print(f"   类型：{intent_data.get('intent_type')}")
                        if intent_data.get('location'):
                            print(f"   地点：{intent_data.get('location')}")
                        if intent_data.get('activity'):
                            print(f"   活动：{intent_data.get('activity')}")
                        if intent_data.get('mood'):
                            print(f"   情绪：{intent_data.get('mood')}")
                        
                        print("\n" + "="*60)
                        print("✅ 所有测试通过！豆包 API 配置正确")
                        print("="*60)
                        print("\n下一步:")
                        print("1. 启动应用：python app.py")
                        print("2. 访问聊天页面：http://localhost:5000/go")
                        print("3. 体验真实的 AI 对话和意图识别功能")
                        print()
                    else:
                        print(f"\n⚠️ 未找到有效的意图标注")
                else:
                    print(f"\n⚠️ AI 没有返回意图标注")
            else:
                print(f"\n❌ 意图识别测试失败：HTTP {intent_response.status_code}")
                print(f"错误信息：{intent_response.text}")
        else:
            print(f"\n❌ API 调用失败：HTTP {response.status_code}")
            print(f"错误信息：{response.text}")
            
            # 检查是否是免费额度用尽
            if response.status_code == 402:
                print("\n💡 提示：账户余额不足或免费额度已用尽")
                print("   请前往火山引擎控制台查看：https://console.volcengine.com")
            
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
else:
    print(f"\n❌ 豆包 API Key 未配置")
    print("\n请按以下步骤操作:")
    print("1. 检查 .env.local 文件是否存在")
    print("2. 确认 DOUBAO_API_KEY 已正确配置")
    print("3. 重新启动应用")
    print()
