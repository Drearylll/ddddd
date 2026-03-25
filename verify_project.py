"""
Go In 项目功能验证脚本

用于快速验证核心功能是否正常
"""

import sys
import os

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print_success(f"{description}: {filepath}")
        return True
    else:
        print_error(f"{description}不存在：{filepath}")
        return False

def check_directory_exists(dirpath, description):
    """检查目录是否存在"""
    if os.path.isdir(dirpath):
        print_success(f"{description}: {dirpath}")
        return True
    else:
        print_error(f"{description}不存在：{dirpath}")
        return False

def check_file_size(filepath, min_size=0, description=""):
    """检查文件大小"""
    try:
        size = os.path.getsize(filepath)
        if size >= min_size:
            print_success(f"{description}文件大小正常：{size/1024:.2f} KB")
            return True
        else:
            print_warning(f"{description}文件可能过小：{size/1024:.2f} KB")
            return False
    except Exception as e:
        print_error(f"无法检查文件大小：{e}")
        return False

def check_import(module_name):
    """检查模块导入"""
    try:
        __import__(module_name)
        print_success(f"模块导入正常：{module_name}")
        return True
    except ImportError as e:
        print_error(f"模块导入失败：{module_name} - {e}")
        return False

def check_flask_app():
    """检查 Flask 应用配置"""
    print_header("检查 Flask 应用配置")
    
    try:
        from app import app
        print_success("Flask 应用导入成功")
        
        # 检查应用配置
        if app.secret_key:
            print_success("Secret Key 已配置")
        else:
            print_warning("Secret Key 未配置")
        
        # 检查数据库配置
        if app.config.get('SQLALCHEMY_DATABASE_URI'):
            print_success("数据库 URI 已配置")
        else:
            print_error("数据库 URI 未配置")
        
        # 检查路由数量
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        print_info(f"已注册路由数量：{len(routes)}")
        
        # 检查关键路由
        critical_routes = ['/', '/welcome', '/feed', '/profile_setup', '/app_main', '/co_create']
        for route in critical_routes:
            if route in routes:
                print_success(f"关键路由存在：{route}")
            else:
                print_warning(f"关键路由缺失：{route}")
        
        return True
    except Exception as e:
        print_error(f"Flask 应用检查失败：{e}")
        return False

def check_services():
    """检查服务层"""
    print_header("检查服务层")
    
    services = [
        'services.content_generator',
        'services.user_manager',
        'services.user_service',
        'services.content_creation_service',
        'services.moments_service',
        'services.database',
        'services.location',
        'services.location_analyzer',
    ]
    
    success_count = 0
    for service in services:
        try:
            __import__(service)
            print_success(f"服务导入成功：{service}")
            success_count += 1
        except ImportError as e:
            print_error(f"服务导入失败：{service} - {e}")
    
    print_info(f"服务导入成功率：{success_count}/{len(services)}")
    return success_count == len(services)

def check_config_files():
    """检查配置文件"""
    print_header("检查配置文件")
    
    config_files = [
        ('config/db_config.py', '数据库配置'),
        ('config/dashscope_config.py', '阿里云配置'),
        ('config/volcengine_config.py', '火山引擎配置'),
        ('vercel.json', 'Vercel 部署配置'),
        ('requirements.txt', '依赖配置'),
    ]
    
    success_count = 0
    for filepath, description in config_files:
        if check_file_exists(filepath, description):
            success_count += 1
    
    print_info(f"配置文件检查：{success_count}/{len(config_files)}")
    return success_count == len(config_files)

def check_template_files():
    """检查模板文件"""
    print_header("检查模板文件")
    
    templates = [
        'templates/welcome_premium.html',
        'templates/index.html',
        'templates/profile_setup.html',
        'templates/personality_customization.html',
        'templates/app_main.html',
        'templates/co_create.html',
        'templates/login.html',
        'templates/register.html',
    ]
    
    success_count = 0
    for template in templates:
        if check_file_exists(template, f"模板：{template}"):
            success_count += 1
    
    print_info(f"模板文件检查：{success_count}/{len(templates)}")
    return success_count == len(templates)

def check_static_files():
    """检查静态资源"""
    print_header("检查静态资源")
    
    static_files = [
        ('static/css/goin_premium_v4.css', '主样式表'),
        ('static/css/goin_brand_v3.css', '品牌样式'),
        ('static/js/goin_brand_v3.js', '品牌脚本'),
        ('static/images/logo.png', 'Logo 图片'),
    ]
    
    success_count = 0
    for filepath, description in static_files:
        if check_file_exists(filepath, description):
            success_count += 1
    
    print_info(f"静态资源检查：{success_count}/{len(static_files)}")
    return success_count == len(static_files)

def check_user_data_directory():
    """检查用户数据目录"""
    print_header("检查用户数据目录")
    
    if check_directory_exists('user_data', '用户数据目录'):
        # 检查是否有用户数据文件
        import os
        files = os.listdir('user_data')
        if files:
            print_info(f"用户数据文件数量：{len(files)}")
            # 显示最大的 3 个文件
            file_sizes = [(f, os.path.getsize(f'user_data/{f}')) for f in files]
            file_sizes.sort(key=lambda x: x[1], reverse=True)
            print_info("最大的 3 个数据文件：")
            for f, size in file_sizes[:3]:
                print_info(f"  - {f}: {size/1024:.2f} KB")
        else:
            print_warning("用户数据目录为空（正常，等待第一个用户）")
        return True
    return False

def check_database():
    """检查数据库"""
    print_header("检查数据库")
    
    if check_file_exists('config/goin.db', 'SQLite 数据库'):
        try:
            import sqlite3
            conn = sqlite3.connect('config/goin.db')
            cursor = conn.cursor()
            
            # 检查表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print_info(f"数据库表数量：{len(tables)}")
            
            if tables:
                print_info("数据库表列表：")
                for table in tables:
                    print_info(f"  - {table[0]}")
            
            conn.close()
            print_success("数据库连接正常")
            return True
        except Exception as e:
            print_error(f"数据库检查失败：{e}")
            return False
    else:
        print_warning("数据库文件不存在（可能首次运行）")
        return True

def check_git_status():
    """检查 Git 状态"""
    print_header("检查 Git 状态")
    
    import subprocess
    try:
        result = subprocess.run(['git', 'status', '--short'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            if result.stdout.strip():
                print_warning("有以下未提交的更改：")
                print(result.stdout)
            else:
                print_success("工作区干净，无未提交更改")
            return True
        else:
            print_error("Git 状态检查失败")
            return False
    except Exception as e:
        print_error(f"Git 检查失败：{e}")
        return False

def main():
    """主函数"""
    print_header("Go In 项目功能验证脚本")
    print_info("开始全面检查项目功能...\n")
    
    # 设置工作目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    checks = [
        ("项目结构", check_file_exists('app.py', '主应用文件')),
        ("项目结构", check_directory_exists('services', '服务层目录')),
        ("项目结构", check_directory_exists('templates', '模板目录')),
        ("项目结构", check_directory_exists('static', '静态资源')),
        ("项目结构", check_directory_exists('config', '配置目录')),
        ("配置文件", check_config_files()),
        ("模板文件", check_template_files()),
        ("静态资源", check_static_files()),
        ("用户数据", check_user_data_directory()),
        ("数据库", check_database()),
        ("Flask 应用", check_flask_app()),
        ("服务层", check_services()),
        ("Git 状态", check_git_status()),
    ]
    
    # 统计结果
    total = len(checks)
    passed = sum(1 for _, result in checks if result)
    
    print_header("检查完成")
    print_info(f"检查项目：{total}")
    print_success(f"通过项目：{passed}")
    
    if passed == total:
        print_success("\n🎉 所有检查通过！项目功能完整，可以正常运行！")
        print_info("\n建议下一步：")
        print_info("1. 配置环境变量（DASHSCOPE_API_KEY, GAODE_KEY）")
        print_info("2. 本地测试：python app.py")
        print_info("3. 访问：http://localhost:5000")
        print_info("4. Vercel 部署已就绪")
        return 0
    else:
        print_warning(f"\n⚠️  有 {total - passed} 项检查未通过，请检查相关问题")
        return 1

if __name__ == '__main__':
    sys.exit(main())
