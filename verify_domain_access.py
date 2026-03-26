"""
Vercel 域名配置验证工具

用于检查域名是否正确配置并可以访问
"""

import requests
import socket
import time
from datetime import datetime


def check_domain_access(domain):
    """检查域名是否可以访问"""
    print(f"\n{'='*60}")
    print(f"🔍 检查域名：{domain}")
    print(f"{'='*60}")
    
    try:
        # DNS 解析检查
        print("\n📡 DNS 解析检查...")
        ip_address = socket.gethostbyname(domain)
        print(f"✅ DNS 解析成功：{domain} → {ip_address}")
        
        # 检查是否是 Vercel 的 IP
        if ip_address.startswith('76.76.21.'):
            print(f"✅ IP 地址属于 Vercel")
        else:
            print(f"⚠️  IP 地址可能不属于 Vercel (76.76.21.x)")
        
        # HTTP 访问检查
        print(f"\n🌐 HTTP 访问检查...")
        url = f"https://{domain}"
        
        start_time = time.time()
        response = requests.get(url, timeout=10, allow_redirects=True)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        print(f"✅ HTTP 状态码：{response.status_code}")
        print(f"✅ 响应时间：{response_time:.2f}ms")
        print(f"✅ 最终 URL: {response.url}")
        
        # HTTPS 证书检查
        print(f"\n🔒 HTTPS 证书检查...")
        if response.url.startswith('https://'):
            print(f"✅ 使用 HTTPS 加密")
        else:
            print(f"⚠️  未使用 HTTPS")
        
        # 内容检查
        print(f"\n📄 页面内容检查...")
        if response.status_code == 200:
            print(f"✅ 页面正常加载")
            if 'Go In' in response.text or 'goin' in response.text.lower():
                print(f"✅ 页面内容包含 Go In 相关关键词")
        else:
            print(f"⚠️  页面可能有问题")
        
        return True
        
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败 - DNS 可能未生效")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求错误：{e}")
        return False
    except socket.gaierror as e:
        print(f"❌ DNS 解析失败：{e}")
        print(f"💡 提示：DNS 记录可能未生效，请等待或检查配置")
        return False
    except Exception as e:
        print(f"❌ 未知错误：{e}")
        return False


def check_vercel_deployment():
    """检查 Vercel 部署状态"""
    print(f"\n{'='*60}")
    print("🚀 检查 Vercel 部署状态")
    print(f"{'='*60}")
    
    # 检查 Vercel 默认域名
    default_domains = [
        'goin-git-master-drearylll.vercel.app',
    ]
    
    for domain in default_domains:
        print(f"\n📍 检查 Vercel 默认域名：{domain}")
        success = check_domain_access(domain)
        if success:
            print(f"✅ Vercel 部署正常")
        else:
            print(f"⚠️  Vercel 部署可能有问题")
    
    return True


def print_recommendations(success_count, total):
    """根据检查结果给出建议"""
    print(f"\n{'='*60}")
    print("💡 检查结果总结")
    print(f"{'='*60}")
    
    success_rate = (success_count / total * 100) if total > 0 else 0
    
    print(f"\n成功：{success_count}/{total}")
    print(f"成功率：{success_rate:.1f}%\n")
    
    if success_rate == 100:
        print("🎉 所有检查通过！域名配置成功！")
    elif success_rate >= 50:
        print("⚠️  部分检查未通过，可能原因：")
        print("   1. DNS 记录未完全生效")
        print("   2. HTTPS 证书正在申请中")
        print("   3. 需要等待几分钟再试")
    else:
        print("❌ 大部分检查未通过，建议：")
        print("   1. 检查 DNS 记录是否正确配置")
        print("   2. 等待 DNS 生效（5-30 分钟）")
        print("   3. 清除本地 DNS 缓存")
        print("   4. 联系域名注册商确认")
    
    print("\n📋 下一步建议:")
    print("   1. 访问 Vercel 控制台：https://vercel.com/dashboard/goin")
    print("   2. 检查 Settings → Domains 配置")
    print("   3. 查看 DNS 记录是否生效：https://dnschecker.org/")
    print("   4. 等待 10-30 分钟后重新测试")


def main():
    """主函数"""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         Vercel 域名配置验证工具                            ║")
    print("║         检查域名是否正确配置并可访问                        ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"\n检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 要检查的域名列表
    domains_to_check = [
        'www.goinia.com',
        'goinia.com',
    ]
    
    success_count = 0
    total = len(domains_to_check) + 1  # +1 for Vercel default domain check
    
    # 检查 Vercel 部署
    check_vercel_deployment()
    
    # 检查自定义域名
    for domain in domains_to_check:
        success = check_domain_access(domain)
        if success:
            success_count += 1
        time.sleep(1)  # 避免请求过快
    
    # 打印建议
    print_recommendations(success_count, total)
    
    print(f"\n{'='*60}")
    print("📞 相关链接")
    print(f"{'='*60}")
    print("Vercel 控制台：https://vercel.com/dashboard/goin")
    print("DNS 检查工具：https://dnschecker.org/")
    print("GitHub 仓库：https://github.com/Drearylll/ddddd")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
