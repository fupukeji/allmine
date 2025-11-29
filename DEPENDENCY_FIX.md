# 依赖冲突修复说明

## 问题描述

在阿里云生产环境部署时遇到 Python 依赖包版本冲突：

```
ERROR: Cannot install -r requirements.txt (line 36) and langchain-core==0.3.0 
because these package versions have conflicting dependencies.

The conflict is caused by:
    The user requested langchain-core==0.3.0
    langgraph 0.2.0 depends on langchain-core<0.3 and >=0.2.27
```

## 问题原因

- `langgraph==0.2.0` 要求 `langchain-core<0.3` 且 `>=0.2.27`
- 但 `requirements.txt` 中指定了 `langchain-core==0.3.0`
- 两者版本要求冲突，导致 pip 无法解析依赖

## 解决方案

修改 `backend/requirements.txt` 第37行：

**修改前：**
```
langchain-core==0.3.0
```

**修改后：**
```
langchain-core>=0.2.27,<0.3.0
```

这样既满足 `langgraph 0.2.0` 的要求，又能使用兼容的最新版本。

## 部署步骤

### 方式一：重新部署（推荐）

```bash
# 在阿里云服务器上
cd /path/to/timevalue

# 拉取最新代码
git pull origin main

# 重新安装依赖
cd backend
source venv/bin/activate  # 如果使用虚拟环境
pip install --upgrade pip
pip install -r requirements.txt

# 重启服务
cd ..
./stop_production.sh
./start_production.sh
```

### 方式二：手动修复

如果无法拉取代码，手动修改服务器上的文件：

```bash
# 在服务器上编辑文件
nano backend/requirements.txt

# 找到第37行，修改为：
# langchain-core>=0.2.27,<0.3.0

# 保存后重新安装
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 重启服务
cd ..
./stop_production.sh
./start_production.sh
```

## 验证安装

安装成功后验证：

```bash
cd backend
source venv/bin/activate
pip list | grep langchain
```

应该看到类似输出：
```
langchain-core    0.2.38  # 版本号应该 >=0.2.27 且 <0.3.0
langgraph         0.2.0
```

## 预防措施

为避免未来类似问题，建议：

1. **使用兼容版本范围**
   ```
   # 推荐
   package>=1.0.0,<2.0.0
   
   # 避免
   package==1.0.0
   ```

2. **定期更新依赖**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

3. **使用依赖锁定文件**
   ```bash
   pip freeze > requirements-lock.txt
   ```

4. **测试依赖兼容性**
   ```bash
   pip install --dry-run -r requirements.txt
   ```

## 相关资源

- [Pip依赖解析文档](https://pip.pypa.io/en/latest/topics/dependency-resolution/)
- [LangGraph文档](https://github.com/langchain-ai/langgraph)
- [LangChain Core文档](https://github.com/langchain-ai/langchain)

---

**修复时间**: 2025-11-29  
**Powered by 孚普科技（北京）有限公司**
