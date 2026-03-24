"""
简化版自动抠图脚本
使用 remove.bg 在线 API（免费，每月 50 张额度）

使用方法：
1. 在 https://www.remove.bg/api 获取免费 API Key
2. 将 API Key 填入下方 REMOVEBG_API_KEY
3. 将 z1.jpg 到 z9.jpg 放入 static/images/characters/ 目录
4. 运行：python simple_remove_bg.py
"""

import os
import requests

# ========== 配置区域 ==========
# 在此处填入您的 remove.bg API Key
# 获取地址：https://www.remove.bg/api (免费注册，每月 50 张)
REMOVEBG_API_KEY = "GnwREEYxt35pgLS7zDmHsZnM"
# ===============================

def remove_background(input_path, output_path):
    """使用 remove.bg 移除背景"""
    
    if REMOVEBG_API_KEY == "YOUR_API_KEY_HERE":
        print("❌ 请先配置 API Key！")
        print("📝 获取地址：https://www.remove.bg/api")
        return False
    
    try:
        # 读取图片
        with open(input_path, 'rb') as f:
            image_data = f.read()
        
        # 调用 remove.bg API
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': (os.path.basename(input_path), image_data)},
            data={'size': 'auto'},
            headers={'X-Api-Key': REMOVEBG_API_KEY},
        )
        
        # 检查响应
        if response.status_code == 200:
            # 保存 PNG
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"❌ API 错误：{response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 处理失败：{str(e)}")
        return False

def process_images():
    """批量处理图片"""
    # 图片目录
    input_dir = "static/images/characters"
    
    # 确保目录存在
    if not os.path.exists(input_dir):
        print(f"❌ 目录不存在：{input_dir}")
        return
    
    # 获取所有 JPG 文件
    jpg_files = [f for f in os.listdir(input_dir) if f.startswith('z') and f.endswith('.jpg')]
    
    if not jpg_files:
        print(f"❌ 没有找到 JPG 文件（z1.jpg 到 z9.jpg）")
        return
    
    print(f"📸 找到 {len(jpg_files)} 个 JPG 文件")
    print("=" * 50)
    
    # 逐个处理
    for jpg_file in sorted(jpg_files):
        input_path = os.path.join(input_dir, jpg_file)
        output_file = jpg_file.replace('.jpg', '.png')
        output_path = os.path.join(input_dir, output_file)
        
        print(f"🔄 处理：{jpg_file} → {output_file}")
        
        if remove_background(input_path, output_path):
            print(f"✅ 成功：{output_file}")
        else:
            print(f"❌ 失败：{output_file}")
        
        print("-" * 50)
    
    print("🎉 批量处理完成！")
    print("=" * 50)
    print(f"📁 输出目录：{input_dir}")
    print("💡 提示：现在可以刷新浏览器查看效果")

if __name__ == "__main__":
    print("🤖 AI 自动抠图工具（remove.bg 版本）")
    print("=" * 50)
    
    if REMOVEBG_API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️  请先配置 API Key！")
        print("")
        print("📝 步骤：")
        print("1. 访问：https://www.remove.bg/api")
        print("2. 免费注册账号")
        print("3. 获取 API Key")
        print("4. 填入脚本中的 REMOVEBG_API_KEY")
        print("")
        print("💡 免费额度：每月 50 张图片")
        print("=" * 50)
    else:
        process_images()
