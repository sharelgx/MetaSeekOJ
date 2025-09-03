# MetaSeekOJ 项目重启指南

## 概述

本项目提供了多种方式来快速重启MetaSeekOJ的前端和后端服务，适用于开发环境中的日常使用。

## 可用的重启方式

### 1. Python脚本版本（推荐）

**文件**: `restart_project.py`

**特点**:
- 智能进程管理，使用psutil库精确控制进程
- 详细的状态检查和错误处理
- 自动验证服务启动状态
- 支持强制停止和优雅重启

**使用方法**:
```bash
# 直接运行
python3 /home/metaspeekoj/restart_project.py

# 或者使用可执行权限
/home/metaspeekoj/restart_project.py
```

### 2. Shell脚本版本（快速）

**文件**: `restart.sh`

**特点**:
- 轻量级，启动速度快
- 使用nohup后台运行服务
- 自动生成日志文件
- 简单的状态检查

**使用方法**:
```bash
# 直接运行
bash /home/metaspeekoj/restart.sh

# 或者使用可执行权限
/home/metaspeekoj/restart.sh
```

### 3. MCP集成版本（智能）

**文件**: `.codebuddy/mcp_restart_project.json`

**特点**:
- 与Trae AI深度集成
- 支持语音和文本命令
- 提供多种快捷方式
- 参数化配置

**使用方法**:
在Trae AI中直接说：
- "重启项目"
- "快速重启"
- "检查项目状态"

## 服务信息

### 后端服务 (Django)
- **端口**: 8086
- **启动命令**: `python3 manage.py runserver 0.0.0.0:8086`
- **工作目录**: `/home/metaspeekoj/OnlineJudge`
- **访问地址**: http://localhost:8086

### 前端服务 (Vue.js)
- **端口**: 8080
- **启动命令**: `npm run dev -- --port 8080`
- **工作目录**: `/home/metaspeekoj/OnlineJudgeFE`
- **访问地址**: http://localhost:8080
- **环境变量**: `NODE_OPTIONS="--openssl-legacy-provider"`

## 日志文件

使用shell脚本版本时，日志文件位置：
- 后端日志: `/tmp/backend.log`
- 前端日志: `/tmp/frontend.log`

查看实时日志：
```bash
# 查看后端日志
tail -f /tmp/backend.log

# 查看前端日志
tail -f /tmp/frontend.log
```

## 故障排除

### 端口被占用
如果遇到端口被占用的问题：
```bash
# 查看端口占用情况
netstat -tuln | grep -E ':(8080|8086)'

# 手动杀死进程
pkill -f "manage.py runserver"
pkill -f "npm run dev"
```

### 权限问题
确保脚本有执行权限：
```bash
chmod +x /home/metaspeekoj/restart_project.py
chmod +x /home/metaspeekoj/restart.sh
```

### 依赖问题
Python脚本需要psutil库：
```bash
pip3 install psutil
```

## 自定义配置

你可以修改脚本中的以下参数：
- 端口号（默认8080和8086）
- 等待时间（默认3-5秒）
- 日志文件路径
- 环境变量设置

## 开机自启动

如果需要开机自动启动项目，可以将重启脚本添加到系统启动项中：

```bash
# 添加到用户的.bashrc或.profile
echo '/home/metaspeekoj/restart.sh' >> ~/.bashrc
```

## 注意事项

1. 重启脚本会强制停止现有的服务进程
2. 确保在重启前保存所有未保存的工作
3. 重启过程大约需要10-15秒完成
4. 如果服务启动失败，请检查相应的日志文件
5. 建议在开发环境中使用，生产环境请使用专门的部署脚本

---

**最后更新**: $(date)
**维护者**: MetaSeekOJ Team