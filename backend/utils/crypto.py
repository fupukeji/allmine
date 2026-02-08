"""
凭据加密工具 - 使用 Fernet 对称加密
用于加密存储敏感信息（如账号密码、API密钥等）
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# 从环境变量获取加密密钥，若无则生成固定派生密钥
_ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

def _get_fernet():
    """获取 Fernet 实例"""
    global _ENCRYPTION_KEY
    
    if _ENCRYPTION_KEY:
        # 使用环境变量中的密钥
        key = _ENCRYPTION_KEY.encode() if isinstance(_ENCRYPTION_KEY, str) else _ENCRYPTION_KEY
        # 确保密钥是有效的 base64 编码的 32 字节
        try:
            return Fernet(key)
        except Exception:
            pass
    
    # 使用 SECRET_KEY 派生加密密钥
    secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-for-encryption')
    salt = b'timevalue_credential_salt_v1'
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
    return Fernet(key)

def encrypt_credential(plaintext: str) -> str:
    """
    加密凭据
    
    Args:
        plaintext: 明文字符串
        
    Returns:
        加密后的 base64 字符串
    """
    if not plaintext:
        return None
    
    fernet = _get_fernet()
    encrypted = fernet.encrypt(plaintext.encode('utf-8'))
    return encrypted.decode('utf-8')

def decrypt_credential(ciphertext: str) -> str:
    """
    解密凭据
    
    Args:
        ciphertext: 加密的 base64 字符串
        
    Returns:
        解密后的明文字符串
    """
    if not ciphertext:
        return None
    
    try:
        fernet = _get_fernet()
        decrypted = fernet.decrypt(ciphertext.encode('utf-8'))
        return decrypted.decode('utf-8')
    except Exception:
        # 解密失败时返回原文（兼容旧的明文数据）
        return ciphertext

def generate_encryption_key() -> str:
    """
    生成新的加密密钥（用于环境变量配置）
    
    Returns:
        可用于 ENCRYPTION_KEY 环境变量的密钥字符串
    """
    return Fernet.generate_key().decode('utf-8')


# 便捷别名
encrypt = encrypt_credential
decrypt = decrypt_credential
