@echo off
echo Starting WSL MCP Environment...

REM 启动WSL并设置环境
wsl -d Ubuntu -u metaspeekoj -- bash -c "source ~/.bashrc && echo 'WSL MCP environment ready'"

REM 检查MCP服务器状态
wsl -d Ubuntu -u metaspeekoj -- bash -c "cd /home/metaspeekoj/mcp-servers && echo 'MCP servers directory ready'"

REM 验证配置文件
wsl -d Ubuntu -u metaspeekoj -- bash -c "echo '123456' | sudo -S test -f /home/sharelgx/.trae-server/data/Machine/mcp.json && echo 'MCP config file exists'"

echo MCP Environment Ready! You can now start Trae IDE.
pause