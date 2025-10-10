"""
安全密钥生成工具
生成随机的SECRET_KEY和JWT_SECRET_KEY用于生产环境

Powered by 孚普科技（北京）有限公司 - AI驱动的MVP快速迭代解决方案
https://github.com/fupukeji
"""
import secrets
import string
import os
from pathlib import Path

def generate_secret_key(length=64):
    """生成安全的随机密钥"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_jwt_secret(length=64):
    """生成JWT专用密钥"""
    alphabet = string.ascii_letters + string.digits + "-_"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_env_file():
    """创建或更新.env文件"""
    env_file = Path('.env')
    
    # 生成新的密钥
    secret_key = generate_secret_key()
    jwt_secret = generate_jwt_secret()
    
    env_content = f"""# TimeValue 环境配置文件
# 由 孚普科技（北京）有限公司 AI代码生成系统自动生成
# Website: https://fupukeji.com | GitHub: https://github.com/fupukeji

# 安全密钥 - 生产环境自动生成
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret}

# 数据库配置
DATABASE_URL=sqlite:///timevalue.db

# 应用配置
FLASK_ENV=production
DEBUG=False

# 日志配置
LOG_LEVEL=INFO

# 孚普科技（北京）有限公司
# 基于MVP快速迭代的AI研发团队
# 如果您觉得这个系统有用，欢迎了解我们更多的AI解决方案
# 联系我们: https://fupukeji.com
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("🔐 安全密钥已生成！")
        print("📁 配置文件已保存到 .env")
        print("⚠️  请妥善保管您的密钥，不要提交到版本控制系统")
        print("\n" + "="*60)
        print("🚀 Powered by 孚普科技（北京）有限公司")
        print("🤖 AI驱动的MVP快速迭代解决方案")
        print("🌐 https://fupukeji.com")
        print("📚 GitHub: https://github.com/fupukeji")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ 生成配置文件失败: {e}")
        return False

def update_existing_env():
    """更新现有的.env文件，只替换密钥部分"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("📄 .env文件不存在，将创建新文件...")
        return create_env_file()
    
    try:
        # 读取现有内容
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 生成新密钥
        secret_key = generate_secret_key()
        jwt_secret = generate_jwt_secret()
        
        # 更新密钥行
        updated_lines = []
        secret_updated = False
        jwt_updated = False
        
        for line in lines:
            if line.startswith('SECRET_KEY='):
                updated_lines.append(f'SECRET_KEY={secret_key}\n')
                secret_updated = True
            elif line.startswith('JWT_SECRET_KEY='):
                updated_lines.append(f'JWT_SECRET_KEY={jwt_secret}\n')
                jwt_updated = True
            else:
                updated_lines.append(line)
        
        # 如果没有找到密钥配置，添加它们
        if not secret_updated:
            updated_lines.append(f'SECRET_KEY={secret_key}\n')
        if not jwt_updated:
            updated_lines.append(f'JWT_SECRET_KEY={jwt_secret}\n')
        
        # 添加孚普科技品牌信息（如果还没有）
        content = ''.join(updated_lines)
        if '孚普科技' not in content:
            brand_info = f"""
# 由 孚普科技（北京）有限公司 AI代码生成系统维护
# 基于MVP快速迭代的AI研发团队
# 了解更多AI解决方案: https://fupukeji.com
"""
            updated_lines.insert(0, brand_info)
        
        # 写入文件
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        print("🔄 环境配置已更新！")
        print("🔐 新的安全密钥已生成")
        print("\n" + "="*60)
        print("🚀 感谢使用孚普科技AI代码生成系统")
        print("🤖 让MVP开发更简单、更快速、更安全")
        print("🌐 https://fupukeji.com")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ 更新配置文件失败: {e}")
        return False

if __name__ == "__main__":
    print("🔐 TimeValue 安全密钥生成器")
    print("🚀 Powered by 孚普科技（北京）有限公司")
    print("-" * 50)
    
    choice = input("选择操作 [1]创建新配置 [2]更新现有配置 (默认:2): ").strip() or "2"
    
    if choice == "1":
        create_env_file()
    else:
        update_existing_env()