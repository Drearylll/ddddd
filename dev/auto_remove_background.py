"""
自动抠图脚本 - 批量处理人物素材
使用 rembg AI 模型自动去除背景

使用方法：
1. 将 z1.jpg 到 z9.jpg 放入 static/images/characters/ 目录
2. 运行：python auto_remove_background.py
3. 等待处理完成
4. 生成的 PNG 文件会在同一目录下
"""

import os
from rembg import remove
from PIL import Image

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
        
        try:
            print(f"🔄 处理：{jpg_file} → {output_file}")
            
            # 打开图片
            with Image.open(input_path) as input_image:
                # 转换为 RGB（处理 RGBA 图片）
                if input_image.mode in ('RGBA', 'LA', 'P'):
                    input_image = input_image.convert('RGB')
                
                # 移除背景
                output_image = remove(input_image)
                
                # 保存 PNG
                output_image.save(output_path, 'PNG')
                
            print(f"✅ 成功：{output_file}")
            
        except Exception as e:
            print(f"❌ 失败：{jpg_file} - {str(e)}")
        
        print("-" * 50)
    
    print("🎉 批量处理完成！")
    print("=" * 50)
    print(f"📁 输出目录：{input_dir}")
    print("💡 提示：现在可以刷新浏览器查看效果")

if __name__ == "__main__":
    print("🤖 AI 自动抠图工具")
    print("=" * 50)
    process_images()
