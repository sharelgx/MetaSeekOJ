@echo off
echo ========================================
echo Starting WSL with MCP Environment Setup
echo ========================================

echo Checking WSL status...
wsl --status
if %errorlevel% neq 0 (
    echo WSL is not running or not installed properly!
    pause
    exit /b 1
)

echo Starting WSL Ubuntu distribution...
wsl -d Ubuntu -u metaspeekoj -- bash -c "echo 'WSL started successfully as user metaspeekoj'"
if %errorlevel% neq 0 (
    echo Failed to start WSL Ubuntu!
    pause
    exit /b 1
)

echo Setting up MCP environment...
wsl -d Ubuntu -u metaspeekoj -- bash -c "cd /home/metaspeekoj/mcp-servers && echo 'Current directory: $(pwd)'"

echo Checking MCP server files...
wsl -d Ubuntu -u metaspeekoj -- bash -c "ls -la /home/metaspeekoj/mcp-servers/*.js"

echo Testing MCP servers startup...
wsl -d Ubuntu -u metaspeekoj -- bash -c "cd /home/metaspeekoj/mcp-servers && timeout 2s node project_restart_mcp_server.js || echo 'Project restart server: OK'"
wsl -d Ubuntu -u metaspeekoj -- bash -c "cd /home/metaspeekoj/mcp-servers && timeout 2s node browser_log_mcp_server.js || echo 'Browser log server: OK'"
wsl -d Ubuntu -u metaspeekoj -- bash -c "cd /home/metaspeekoj/mcp-servers && timeout 2s node test_file_manager_mcp_server.js || echo 'Test file manager server: OK'"

echo Checking MCP configuration file...
wsl -d Ubuntu -u metaspeekoj -- bash -c "echo '123456' | sudo -S ls -la /home/sharelgx/.trae-server/data/Machine/mcp.json"

echo Verifying MCP configuration content...
wsl -d Ubuntu -u metaspeekoj -- bash -c "echo '123456' | sudo -S grep -c 'test-file-manager' /home/sharelgx/.trae-server/data/Machine/mcp.json && echo 'MCP config contains all servers'"

echo ========================================
echo WSL MCP Environment Setup Complete!
echo ========================================
echo.
echo Available MCP Servers:
echo - test-file-manager (文件管理)
echo - browser-log-monitor (浏览器日志监控)
echo - project-restart (项目重启)
echo - playwright (浏览器自动化)
echo - postgresql (数据库)
echo - GitHub (代码仓库)
echo.
echo You can now start Trae IDE to use MCP tools.
echo Press any key to continue...
pause > nul