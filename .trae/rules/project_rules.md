# MetaSeekOJ 项目问题记录和解决方案

## 判题服务器连接问题

### 问题描述
判题服务器容器IP地址变化导致后端无法连接到判题服务器，提交状态一直为PENDING。

### 根本原因
1. **数据库不同步**: 本地Django应用和Docker容器中的dramatiq worker使用不同的数据库实例
   - 本地Django: 连接到本地数据库
   - Docker容器: 连接到容器内数据库
   - 结果: 本地创建的提交记录在容器数据库中不存在

2. **判题服务器配置**: 数据库中JudgeServer记录的service_url需要指向正确的判题容器IP
   - 正确的判题服务器: onlinejudgedeploy-oj-judge-1 (IP: 172.20.0.3:8080)
   - 错误配置会导致连接失败或协议不匹配

### 解决方案

#### 方案1: 使用Docker环境进行完整测试
```bash
# 进入后端容器
docker exec -it oj-backend bash

# 在容器内创建提交和发送判题任务
python manage.py shell
```

#### 方案2: 确保数据库同步
- 确认本地Django和Docker容器使用相同的数据库连接
- 检查数据库配置文件中的连接参数

#### 方案3: 更新判题服务器配置
```python
# 更新JudgeServer配置指向正确的判题容器
from conf.models import JudgeServer
server = JudgeServer.objects.get(id=1)
server.service_url = 'http://172.20.0.3:8080'  # 正确的判题服务器IP
server.save()
```

### 验证步骤
1. 检查判题容器状态: `docker ps | grep judge`
2. 确认容器IP: `docker inspect onlinejudgedeploy-oj-judge-1 | grep IPAddress`
3. 测试连接: `curl -X POST http://172.20.0.3:8080/judge -H "Content-Type: application/json" -d '{}'`
4. 检查dramatiq日志: `docker exec oj-backend tail -f /data/log/dramatiq.log`

### 注意事项
- onlinejudgedeploy-oj-judge-1 使用REST API (HTTP POST)
- oj-judge-new 使用XML-RPC协议，不兼容当前系统
- 判题服务器需要token验证，直接API调用会返回"invalid token"错误

### 最后更新
2025-01-19 - 识别数据库不同步问题，需要在Docker环境中进行完整测试