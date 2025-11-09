from database import db
from datetime import datetime

class NginxConfig(db.Model):
    """Nginx配置模型"""
    __tablename__ = 'nginx_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 基础配置
    server_name = db.Column(db.String(255), default='_')  # 域名，_ 表示接受所有请求
    listen_port = db.Column(db.Integer, default=80)  # 监听端口
    
    # SSL配置
    ssl_enabled = db.Column(db.Boolean, default=False)  # 是否启用SSL
    ssl_port = db.Column(db.Integer, default=443)  # SSL端口
    ssl_certificate = db.Column(db.String(500))  # SSL证书路径
    ssl_certificate_key = db.Column(db.String(500))  # SSL私钥路径
    force_https = db.Column(db.Boolean, default=False)  # 强制HTTPS重定向
    
    # 代理配置
    frontend_proxy_enabled = db.Column(db.Boolean, default=True)  # 前端代理启用
    frontend_port = db.Column(db.Integer, default=3000)  # 前端端口
    backend_port = db.Column(db.Integer, default=5000)  # 后端API端口
    
    # 高级配置
    client_max_body_size = db.Column(db.String(20), default='20M')  # 最大上传大小
    gzip_enabled = db.Column(db.Boolean, default=True)  # Gzip压缩
    access_log_enabled = db.Column(db.Boolean, default=True)  # 访问日志
    
    # 自定义配置
    custom_config = db.Column(db.Text)  # 自定义Nginx配置片段
    
    # 状态
    is_active = db.Column(db.Boolean, default=False)  # 是否激活
    last_applied = db.Column(db.DateTime)  # 最后应用时间
    
    # 系统字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('nginx_configs', lazy=True))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'server_name': self.server_name,
            'listen_port': self.listen_port,
            'ssl_enabled': self.ssl_enabled,
            'ssl_port': self.ssl_port,
            'ssl_certificate': self.ssl_certificate,
            'ssl_certificate_key': self.ssl_certificate_key,
            'force_https': self.force_https,
            'frontend_proxy_enabled': self.frontend_proxy_enabled,
            'frontend_port': self.frontend_port,
            'backend_port': self.backend_port,
            'client_max_body_size': self.client_max_body_size,
            'gzip_enabled': self.gzip_enabled,
            'access_log_enabled': self.access_log_enabled,
            'custom_config': self.custom_config,
            'is_active': self.is_active,
            'last_applied': self.last_applied.isoformat() if self.last_applied else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def generate_nginx_config(self):
        """生成Nginx配置文件内容"""
        config_parts = []
        
        # HTTP服务器配置
        if self.force_https and self.ssl_enabled:
            # HTTP重定向到HTTPS
            config_parts.append(f"""# HTTP重定向到HTTPS
server {{
    listen {self.listen_port};
    server_name {self.server_name};
    return 301 https://$server_name$request_uri;
}}
""")
        else:
            # HTTP配置
            config_parts.append(self._generate_server_block(is_ssl=False))
        
        # HTTPS服务器配置
        if self.ssl_enabled:
            config_parts.append(self._generate_server_block(is_ssl=True))
        
        return '\n'.join(config_parts)
    
    def _generate_server_block(self, is_ssl=False):
        """生成服务器块配置"""
        lines = []
        
        # 服务器块开始
        lines.append("server {")
        
        # 监听端口
        if is_ssl:
            lines.append(f"    listen {self.ssl_port} ssl http2;")
            lines.append(f"    server_name {self.server_name};")
            lines.append("")
            # SSL证书
            if self.ssl_certificate:
                lines.append(f"    ssl_certificate {self.ssl_certificate};")
            if self.ssl_certificate_key:
                lines.append(f"    ssl_certificate_key {self.ssl_certificate_key};")
            lines.append("")
            # SSL优化
            lines.append("    ssl_protocols TLSv1.2 TLSv1.3;")
            lines.append("    ssl_ciphers HIGH:!aNULL:!MD5;")
            lines.append("    ssl_prefer_server_ciphers off;")
            lines.append("    ssl_session_cache shared:SSL:10m;")
            lines.append("    ssl_session_timeout 10m;")
        else:
            lines.append(f"    listen {self.listen_port};")
            lines.append(f"    server_name {self.server_name};")
        
        lines.append("")
        
        # 访问日志
        if self.access_log_enabled:
            lines.append("    access_log /var/log/nginx/timevalue_access.log;")
            lines.append("    error_log /var/log/nginx/timevalue_error.log;")
        else:
            lines.append("    access_log off;")
        
        lines.append("")
        
        # 客户端最大上传大小
        lines.append(f"    client_max_body_size {self.client_max_body_size};")
        lines.append("")
        
        # 前端代理
        if self.frontend_proxy_enabled:
            lines.append("    # 前端代理")
            lines.append("    location / {")
            lines.append(f"        proxy_pass http://127.0.0.1:{self.frontend_port};")
            lines.append("        proxy_set_header Host $host;")
            lines.append("        proxy_set_header X-Real-IP $remote_addr;")
            lines.append("        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;")
            lines.append("        proxy_set_header X-Forwarded-Proto $scheme;")
            lines.append("")
            lines.append("        # WebSocket支持")
            lines.append("        proxy_http_version 1.1;")
            lines.append("        proxy_set_header Upgrade $http_upgrade;")
            lines.append("        proxy_set_header Connection \"upgrade\";")
            lines.append("    }")
            lines.append("")
        
        # API代理
        lines.append("    # API代理")
        lines.append("    location /api/ {")
        lines.append(f"        proxy_pass http://127.0.0.1:{self.backend_port};")
        lines.append("        proxy_set_header Host $host;")
        lines.append("        proxy_set_header X-Real-IP $remote_addr;")
        lines.append("        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;")
        lines.append("        proxy_set_header X-Forwarded-Proto $scheme;")
        lines.append("")
        lines.append("        proxy_connect_timeout 60s;")
        lines.append("        proxy_send_timeout 60s;")
        lines.append("        proxy_read_timeout 60s;")
        lines.append("    }")
        lines.append("")
        
        # Gzip压缩
        if self.gzip_enabled:
            lines.append("    # Gzip压缩")
            lines.append("    gzip on;")
            lines.append("    gzip_vary on;")
            lines.append("    gzip_min_length 1024;")
            lines.append("    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json;")
            lines.append("")
        
        # 安全头
        lines.append("    # 安全头")
        lines.append("    add_header X-Frame-Options \"SAMEORIGIN\" always;")
        lines.append("    add_header X-Content-Type-Options \"nosniff\" always;")
        lines.append("    add_header X-XSS-Protection \"1; mode=block\" always;")
        lines.append("")
        
        # 自定义配置
        if self.custom_config:
            lines.append("    # 自定义配置")
            for line in self.custom_config.split('\n'):
                if line.strip():
                    lines.append(f"    {line}")
            lines.append("")
        
        # 服务器块结束
        lines.append("}")
        
        return '\n'.join(lines)
    
    def __repr__(self):
        return f'<NginxConfig {self.server_name}>'
