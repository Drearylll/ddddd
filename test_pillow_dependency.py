"""
验证 Pillow 依赖是否正确安装

用于测试 PIL 模块是否可导入，确保 Vercel 部署不会失败
"""

def test_pil_import():
    """测试 PIL 导入"""
    try:
        from PIL import Image, ImageFilter, ImageEnhance
        print("✅ PIL 导入成功")
        
        # 测试基本功能
        img = Image.new('RGB', (100, 100), color='red')
        print(f"✅ 创建图像成功：{img.size}")
        
        # 测试滤镜
        img_filtered = img.filter(ImageFilter.GaussianBlur(radius=2))
        print("✅ 滤镜应用成功")
        
        # 测试增强器
        enhancer = ImageEnhance.Color(img)
        img_enhanced = enhancer.enhance(1.5)
        print("✅ 色彩增强成功")
        
        # 显示版本信息
        import PIL
        print(f"📦 Pillow 版本：{PIL.__version__}")
        
        return True
        
    except ModuleNotFoundError as e:
        print(f"❌ PIL 导入失败：{e}")
        print("\n解决方案:")
        print("1. 检查 requirements.txt 是否包含：Pillow==10.2.0")
        print("2. 运行：pip install -r requirements.txt")
        print("3. 重新部署到 Vercel")
        return False
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return False


def test_user_service_import():
    """测试 user_service.py 的导入"""
    try:
        from services.user_service import UserService
        print("✅ UserService 导入成功")
        return True
    except ImportError as e:
        print(f"❌ UserService 导入失败：{e}")
        return False


if __name__ == '__main__':
    print("=" * 50)
    print("🧪 Pillow 依赖验证测试")
    print("=" * 50)
    print()
    
    pil_ok = test_pil_import()
    print()
    
    service_ok = test_user_service_import()
    print()
    
    print("=" * 50)
    if pil_ok and service_ok:
        print("✅ 所有测试通过！Vercel 部署应该没问题")
    else:
        print("❌ 测试失败！请检查依赖安装")
    print("=" * 50)
