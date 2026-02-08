"""
数据库配置模块
提供MySQL和SQLite的统一配置管理
"""
import os
from urllib.parse import quote_plus


class DatabaseConfig:
    """数据库配置类"""
    
    @staticmethod
    def get_mysql_uri(host, port, database, username, password, charset='utf8mb4'):
        """
        生成MySQL连接URI
        
        Args:
            host: 数据库主机地址
            port: 端口号
            database: 数据库名
            username: 用户名
            password: 密码
            charset: 字符集，默认utf8mb4
            
        Returns:
            MySQL连接URI字符串
        """
        encoded_password = quote_plus(password)
        return f'mysql+pymysql://{username}:{encoded_password}@{host}:{port}/{database}?charset={charset}'
    
    @staticmethod
    def get_sqlite_uri(db_name='timevalue.db', data_dir=None):
        """
        生成SQLite连接URI
        
        Args:
            db_name: 数据库文件名
            data_dir: 数据目录路径，默认为项目根目录下的data文件夹
            
        Returns:
            SQLite连接URI字符串
        """
        if data_dir is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(project_root, 'data')
        
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, db_name)
        return f'sqlite:///{db_path}'
    
    @staticmethod
    def get_database_uri_from_env():
        """
        从环境变量读取数据库配置
        支持两套环境变量格式：
        - DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD (自定义)
        - MYSQL_ADDRESS/MYSQL_USERNAME/MYSQL_PASSWORD (微信云托管默认)
        """
        db_type = os.getenv('DB_TYPE', 'mysql').lower()
        
        if db_type == 'mysql':
            # 优先使用 DB_* 变量
            host = os.getenv('DB_HOST')
            port = os.getenv('DB_PORT')
            
            # 如果没有 DB_HOST，尝试从 MYSQL_ADDRESS 解析
            if not host:
                mysql_addr = os.getenv('MYSQL_ADDRESS', 'localhost:3306')
                if ':' in mysql_addr:
                    host, port = mysql_addr.rsplit(':', 1)
                else:
                    host = mysql_addr
                    port = port or '3306'
            
            return DatabaseConfig.get_mysql_uri(
                host=host or 'localhost',
                port=int(port or 3306),
                database=os.getenv('DB_NAME', 'allmine'),
                username=os.getenv('DB_USER') or os.getenv('MYSQL_USERNAME', 'root'),
                password=os.getenv('DB_PASSWORD') or os.getenv('MYSQL_PASSWORD', '')
            )
        else:
            return DatabaseConfig.get_sqlite_uri()


class DatabaseSettings:
    """数据库通用设置"""
    
    # 连接池配置
    POOL_SIZE = 5  # 减少连接池大小
    POOL_RECYCLE = 1800  # 30分钟回收连接（避免超时）
    POOL_PRE_PING = True  # 连接前ping测试
    POOL_TIMEOUT = 30  # 连接超时时间
    
    # 查询配置
    MAX_OVERFLOW = 10  # 减少溢出连接数
    ECHO = False  # 是否打印SQL语句（开发环境可访为True）
    
    @staticmethod
    def get_engine_options():
        """获取数据库引擎配置选项"""
        return {
            'pool_size': DatabaseSettings.POOL_SIZE,
            'pool_recycle': DatabaseSettings.POOL_RECYCLE,
            'pool_pre_ping': DatabaseSettings.POOL_PRE_PING,
            'pool_timeout': DatabaseSettings.POOL_TIMEOUT,
            'max_overflow': DatabaseSettings.MAX_OVERFLOW,
            'connect_args': {
                'connect_timeout': 10,
                'read_timeout': 30,
                'write_timeout': 30
            }
        }
