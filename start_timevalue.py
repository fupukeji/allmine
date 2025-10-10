#!/usr/bin/env python3
"""
TimeValue 个人资产管理系统启动脚本

🚀 Powered by 孚普科技（北京）有限公司
🤖 AI驱动的MVP快速迭代解决方案
🌐 https://fupukeji.com
📚 GitHub: https://github.com/fupukeji

让个人资产管理变得简单高效！
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """显示启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                            TimeValue 资产管理系统                              ║
║                                                                              ║
║  🚀 Powered by 孚普科技（北京）有限公司                                         ║
║  🤖 AI驱动的MVP快速迭代解决方案                                                 ║
║  🌐 https://fupukeji.com                                                     ║
║  📚 GitHub: https://github.com/fupukeji                                     ║
║                                                                              ║
║  💡 让个人资产管理变得简单高效！                                                ║
║  💰 恒产生金 - 让每一份资产都创造价值                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_environment():
    """检查运行环境"""
    print("🔍 正在检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8+")
        return False
    
    print(f"✅ Python版本: {sys.version}")
    
    # 检查必要的目录
    required_dirs = ['backend', 'frontend']
    for directory in required_dirs:
        if not Path(directory).exists():
            print(f"❌ 缺少必要目录: {directory}")
            return False
    
    print("✅ 目录结构检查通过")
    return True

def setup_security():
    """设置安全密钥"""
    print("\n🔐 正在设置安全密钥...")
    
    env_file = Path('.env')
    if not env_file.exists() or check_keys_need_update():
        print("🔑 生成安全密钥...")
        try:
            # 运行密钥生成脚本
            os.chdir('backend')
            result = subprocess.run([sys.executable, 'generate_keys.py'], 
                                  input="2\n", text=True, capture_output=True)
            os.chdir('..')
            
            if result.returncode == 0:
                print("✅ 安全密钥设置完成")
            else:
                print(f"⚠️ 密钥生成警告: {result.stderr}")
        except Exception as e:
            print(f"❌ 密钥设置失败: {e}")
    else:
        print("✅ 安全密钥已存在")

def check_keys_need_update():
    """检查是否需要更新密钥"""
    env_file = Path('.env')
    if not env_file.exists():
        return True
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            # 检查是否包含默认的开发密钥
            if 'dev-secret-key' in content or 'jwt-secret-key' in content:
                return True
    except:
        return True
    
    return False

def install_backend_dependencies():
    """安装后端依赖"""
    print("\n📦 正在安装后端依赖...")
    os.chdir('backend')
    
    try:
        # 检查是否有requirements.txt
        if Path('requirements.txt').exists():
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                         check=True)
            print("✅ 后端依赖安装完成")
        else:
            print("⚠️ 未找到requirements.txt")
    except subprocess.CalledProcessError as e:
        print(f"❌ 后端依赖安装失败: {e}")
    finally:
        os.chdir('..')

def install_frontend_dependencies():
    """安装前端依赖"""
    print("\n📦 正在安装前端依赖...")
    os.chdir('frontend')
    
    try:
        # 检查npm是否可用
        subprocess.run(['npm', '--version'], check=True, capture_output=True)
        
        # 安装依赖
        subprocess.run(['npm', 'install'], check=True)
        print("✅ 前端依赖安装完成")
    except subprocess.CalledProcessError:
        print("❌ npm不可用或前端依赖安装失败")
    except FileNotFoundError:
        print("❌ 未找到npm，请先安装Node.js")
    finally:
        os.chdir('..')

def start_backend():
    """启动后端服务"""
    print("\n🚀 正在启动后端服务...")
    os.chdir('backend')
    
    try:
        # 启动Flask应用
        process = subprocess.Popen([sys.executable, 'app.py'])
        print("✅ 后端服务已启动 (端口: 5000)")
        return process
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        return None
    finally:
        os.chdir('..')

def start_frontend():
    """启动前端服务"""
    print("\n🚀 正在启动前端服务...")
    os.chdir('frontend')
    
    try:
        # 启动Vite开发服务器
        process = subprocess.Popen(['npm', 'run', 'dev'])
        print("✅ 前端服务已启动 (端口: 3000/3001)")
        return process
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")
        return None
    finally:
        os.chdir('..')

def show_success_info():
    """显示成功启动信息"""
    success_info = """
🎉 TimeValue 系统启动成功！

🌐 访问地址: http://localhost:3000 或 http://localhost:3001
📊 后端API: http://localhost:5000

📖 使用说明:
  • 首次访问请注册账户
  • 默认管理员: admin/admin123
  • 开始管理您的个人资产，让财富增值！

💡 提示: 按 Ctrl+C 可以停止所有服务

═══════════════════════════════════════════════════════════════
🚀 感谢使用孚普科技（北京）有限公司的AI代码生成系统
🤖 让MVP开发更简单、更快速、更安全
🌐 了解更多AI解决方案: https://fupukeji.com
📧 商务合作: contact@fupukeji.com
═══════════════════════════════════════════════════════════════
"""
    print(success_info)

def main():
    """主启动流程"""
    print_banner()
    
    try:
        # 1. 检查环境
        if not check_environment():
            sys.exit(1)
        
        # 2. 设置安全密钥
        setup_security()
        
        # 3. 安装依赖
        install_backend_dependencies()
        install_frontend_dependencies()
        
        # 4. 启动服务
        backend_process = start_backend()
        if not backend_process:
            print("❌ 无法启动后端服务")
            sys.exit(1)
        
        # 等待后端启动
        time.sleep(3)
        
        frontend_process = start_frontend()
        if not frontend_process:
            print("❌ 无法启动前端服务")
            backend_process.terminate()
            sys.exit(1)
        
        # 5. 显示成功信息
        show_success_info()
        
        # 6. 等待用户中断
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 正在停止服务...")
            
            if backend_process:
                backend_process.terminate()
            if frontend_process:
                frontend_process.terminate()
            
            print("✅ 所有服务已停止")
            print("👋 感谢使用TimeValue系统！")
            print("🚀 Powered by 孚普科技（北京）有限公司")
    
    except Exception as e:
        print(f"❌ 启动过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()