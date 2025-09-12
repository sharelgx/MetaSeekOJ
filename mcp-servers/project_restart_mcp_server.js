#!/usr/bin/env node

/**
 * MetaSeekOJ项目重启MCP服务器
 * 提供全面的项目重启功能，包含Redis、前端、后端等所有服务
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { spawn, exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const fsPromises = fs.promises;

const execAsync = promisify(exec);

class ProjectRestartServer {
  constructor() {
    this.server = new Server(
      {
        name: 'project-restart-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'restart_full_project',
            description: '全面重启项目 - 包含Redis、前端、后端等所有服务',
            inputSchema: {
              type: 'object',
              properties: {
                verbose: {
                  type: 'boolean',
                  description: '是否显示详细输出',
                  default: true
                },
                check_status: {
                  type: 'boolean',
                  description: '启动后是否检查服务状态',
                  default: true
                }
              }
            }
          },
          {
            name: 'solo_mode_restart',
            description: 'SOLO模式启动 - 提供命令而不是自动启动服务',
            inputSchema: {
              type: 'object',
              properties: {
                verbose: {
                  type: 'boolean',
                  description: '是否显示详细输出',
                  default: true
                }
              }
            }
          },
          {
            name: 'quick_restart',
            description: '快速重启 - 使用现有的restart.sh脚本',
            inputSchema: {
              type: 'object',
              properties: {}
            }
          },
          {
            name: 'python_restart',
            description: 'Python版本重启 - 使用restart_project.py脚本',
            inputSchema: {
              type: 'object',
              properties: {}
            }
          },
          {
            name: 'check_project_status',
            description: '检查项目状态 - 查看所有服务运行状态',
            inputSchema: {
              type: 'object',
              properties: {}
            }
          },
          {
            name: 'stop_all_services',
            description: '停止所有服务 - 停止前端、后端、Redis等所有服务',
            inputSchema: {
              type: 'object',
              properties: {}
            }
          },
          {
            name: 'start_redis_only',
            description: '仅启动Redis服务',
            inputSchema: {
              type: 'object',
              properties: {}
            }
          },
          {
            name: 'start_backend_only',
            description: '仅启动后端服务（Django）',
            inputSchema: {
              type: 'object',
              properties: {}
            }
          },
          {
            name: 'start_frontend_only',
            description: '仅启动前端服务（Vue.js）',
            inputSchema: {
              type: 'object',
              properties: {}
            }
          },
          {
            name: 'troubleshoot_gateway_timeout',
            description: '故障排除 - 诊断和解决504网关超时问题',
            inputSchema: {
              type: 'object',
              properties: {
                auto_fix: {
                  type: 'boolean',
                  description: '是否自动尝试修复问题',
                  default: true
                },
                check_config: {
                  type: 'boolean',
                  description: '是否检查前端代理配置',
                  default: true
                }
              }
            }
          }
        ]
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'restart_full_project':
            return await this.restartFullProject(args);
          case 'solo_mode_restart':
            return await this.soloModeRestart(args);
          case 'quick_restart':
            return await this.quickRestart();
          case 'python_restart':
            return await this.pythonRestart();
          case 'check_project_status':
            return await this.checkProjectStatus();
          case 'stop_all_services':
            return await this.stopAllServices();
          case 'start_redis_only':
            return await this.startRedisOnly();
          case 'start_backend_only':
            return await this.startBackendOnly();
          case 'start_frontend_only':
            return await this.startFrontendOnly();
          case 'troubleshoot_gateway_timeout':
            return await this.troubleshootGatewayTimeout(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error executing ${name}: ${error.message}`
            }
          ],
          isError: true
        };
      }
    });
  }

  async executeCommand(command, options = {}) {
    try {
      const { stdout, stderr } = await execAsync(command, options);
      return { success: true, stdout, stderr };
    } catch (error) {
      return { success: false, error: error.message, stdout: error.stdout, stderr: error.stderr };
    }
  }

  async restartFullProject(args = {}) {
    const { verbose = true, check_status = true } = args;
    let output = [];

    output.push('=== MetaSeekOJ 项目全面重启开始 ===\n');

    // 1. 停止现有服务
    output.push('1. 停止现有服务...');
    const stopResult = await this.executeCommand(
      "pkill -f 'python.*manage.py.*runserver' || true && pkill -f 'node.*dev-server' || true && pkill -f 'redis-server' || true"
    );
    if (verbose) {
      output.push(`停止服务结果: ${stopResult.success ? '成功' : '部分成功'}`);
    }

    // 等待进程停止
    await new Promise(resolve => setTimeout(resolve, 3000));

    // 2. 启动Redis服务
    output.push('\n2. 启动Redis服务...');
    const redisResult = await this.executeCommand('redis-server --daemonize yes');
    if (verbose) {
      output.push(`Redis启动: ${redisResult.success ? '成功' : '失败'}`);
    }

    // 等待Redis启动
    await new Promise(resolve => setTimeout(resolve, 2000));

    // 3. 启动后端服务
    output.push('\n3. 启动后端Django服务...');
    const backendResult = await this.executeCommand(
      'cd /home/metaspeekoj/OnlineJudge && nohup python3 manage.py runserver 0.0.0.0:8086 > /tmp/backend.log 2>&1 &'
    );
    if (verbose) {
      output.push(`后端启动: ${backendResult.success ? '成功' : '失败'}`);
    }

    // 等待后端启动
    await new Promise(resolve => setTimeout(resolve, 5000));

    // 4. 启动前端服务
    output.push('\n4. 启动前端Vue.js服务...');
    const frontendResult = await this.executeCommand(
      'cd /home/metaspeekoj/OnlineJudgeFE && export NODE_OPTIONS="--openssl-legacy-provider" && nohup npm run dev -- --port 8080 > /tmp/frontend.log 2>&1 &'
    );
    if (verbose) {
      output.push(`前端启动: ${frontendResult.success ? '成功' : '失败'}`);
    }

    // 等待前端启动
    await new Promise(resolve => setTimeout(resolve, 5000));

    // 5. 检查服务状态
    if (check_status) {
      output.push('\n5. 检查服务状态...');
      const statusResult = await this.checkServicesStatus();
      output.push(statusResult);
    }

    output.push('\n=== 项目重启完成 ===');
    output.push('前端访问地址: http://localhost:8080');
    output.push('后端API地址: http://localhost:8086');
    output.push('查看日志: tail -f /tmp/backend.log 或 tail -f /tmp/frontend.log');

    return {
      content: [
        {
          type: 'text',
          text: output.join('\n')
        }
      ]
    };
  }

  async quickRestart() {
    const result = await this.executeCommand('bash /home/metaspeekoj/restart.sh');
    
    return {
      content: [
        {
          type: 'text',
          text: `快速重启结果:\n${result.stdout || ''}${result.stderr || ''}${result.error || ''}`
        }
      ]
    };
  }

  async pythonRestart() {
    const result = await this.executeCommand('python3 /home/metaspeekoj/mcp-servers/restart_project.py');
    
    return {
      content: [
        {
          type: 'text',
          text: `Python重启结果:\n${result.stdout || ''}${result.stderr || ''}${result.error || ''}`
        }
      ]
    };
  }

  async checkProjectStatus() {
    const statusResult = await this.checkServicesStatus();
    
    return {
      content: [
        {
          type: 'text',
          text: `=== MetaSeekOJ 项目状态 ===\n${statusResult}\n\n=== 访问地址 ===\n前端: http://localhost:8080\n后端API: http://localhost:8086`
        }
      ]
    };
  }

  async checkServicesStatus() {
    let status = [];

    // 检查前端服务 (8080)
    const frontendCheck = await this.executeCommand("netstat -tuln | grep ':8080 '");
    status.push(`前端服务 (8080): ${frontendCheck.success ? '✓ 运行中' : '✗ 未运行'}`);

    // 检查后端服务 (8086)
    const backendCheck = await this.executeCommand("netstat -tuln | grep ':8086 '");
    status.push(`后端服务 (8086): ${backendCheck.success ? '✓ 运行中' : '✗ 未运行'}`);

    // 检查Redis服务
    const redisCheck = await this.executeCommand('redis-cli ping 2>/dev/null');
    status.push(`Redis服务: ${redisCheck.success && redisCheck.stdout.includes('PONG') ? '✓ 运行中' : '✗ 未运行'}`);

    return status.join('\n');
  }

  async stopAllServices() {
    let output = [];
    output.push('=== 停止所有服务 ===');

    // 停止前端服务
    const stopFrontend = await this.executeCommand("pkill -f 'node.*dev-server' || pkill -f 'npm.*dev'");
    output.push(`停止前端服务: ${stopFrontend.success ? '成功' : '部分成功'}`);

    // 停止后端服务
    const stopBackend = await this.executeCommand("pkill -f 'python.*manage.py.*runserver'");
    output.push(`停止后端服务: ${stopBackend.success ? '成功' : '部分成功'}`);

    // 停止Redis服务
    const stopRedis = await this.executeCommand("pkill -f 'redis-server'");
    output.push(`停止Redis服务: ${stopRedis.success ? '成功' : '部分成功'}`);

    output.push('所有服务已停止');

    return {
      content: [
        {
          type: 'text',
          text: output.join('\n')
        }
      ]
    };
  }

  async startRedisOnly() {
    const result = await this.executeCommand('redis-server --daemonize yes');
    
    // 等待启动
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 检查状态
    const checkResult = await this.executeCommand('redis-cli ping 2>/dev/null');
    const isRunning = checkResult.success && checkResult.stdout.includes('PONG');
    
    return {
      content: [
        {
          type: 'text',
          text: `Redis服务启动: ${result.success ? '命令执行成功' : '命令执行失败'}\nRedis状态: ${isRunning ? '✓ 运行中' : '✗ 未运行'}`
        }
      ]
    };
  }

  async startBackendOnly() {
    const result = await this.executeCommand(
      'cd /home/metaspeekoj/OnlineJudge && nohup python3 manage.py runserver 0.0.0.0:8086 > /tmp/backend.log 2>&1 &'
    );
    
    // 等待启动
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // 检查状态
    const checkResult = await this.executeCommand("netstat -tuln | grep ':8086 '");
    
    return {
      content: [
        {
          type: 'text',
          text: `后端服务启动: ${result.success ? '命令执行成功' : '命令执行失败'}\n后端状态: ${checkResult.success ? '✓ 运行中 (端口8086)' : '✗ 未运行'}\n访问地址: http://localhost:8086\n查看日志: tail -f /tmp/backend.log`
        }
      ]
    };
  }

  async startFrontendOnly() {
    const result = await this.executeCommand(
      'cd /home/metaspeekoj/OnlineJudgeFE && export NODE_OPTIONS="--openssl-legacy-provider" && nohup npm run dev -- --port 8080 > /tmp/frontend.log 2>&1 &'
    );
    
    // 等待启动
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // 检查状态
    const checkResult = await this.executeCommand("netstat -tuln | grep ':8080 '");
    
    return {
      content: [
        {
          type: 'text',
          text: `前端服务启动: ${result.success ? '命令执行成功' : '命令执行失败'}\n前端状态: ${checkResult.success ? '✓ 运行中 (端口8080)' : '✗ 未运行'}\n访问地址: http://localhost:8080\n查看日志: tail -f /tmp/frontend.log`
        }
      ]
    };
  }

  async soloModeRestart(args = {}) {
    const { verbose = true } = args;
    let output = [];

    output.push('=== MetaSeekOJ 项目 SOLO 模式启动 ===\n');

    // 1. 停止现有服务
    output.push('1. 停止现有服务...');
    const stopResult = await this.executeCommand(
      "pkill -f 'python.*manage.py.*runserver' || true && pkill -f 'node.*dev-server' || true && pkill -f 'npm.*dev' || true"
    );
    if (verbose) {
      output.push(`停止服务结果: ${stopResult.success ? '成功' : '部分成功'}\n`);
    }

    // 2. 提供启动命令而不是自动启动服务
    output.push('2. SOLO 模式启动说明');
    output.push('在 SOLO 模式下，您需要手动启动各个服务。以下是启动命令：\n');

    // Redis 启动命令
    output.push('=== Redis 服务启动命令 ===');
    output.push('redis-server --daemonize yes');
    output.push('# 或者在后台运行：');
    output.push('nohup redis-server > /tmp/redis.log 2>&1 &\n');

    // 后端启动命令
    output.push('=== 后端服务启动命令 ===');
    output.push('cd /home/metaspeekoj/OnlineJudge');
    output.push('source django_env/bin/activate  # 或 source venv/bin/activate');
    output.push('python manage.py runserver 0.0.0.0:8086\n');

    // 前端启动命令
    output.push('=== 前端服务启动命令 ===');
    output.push('cd /home/metaspeekoj/OnlineJudgeFE');
    output.push('export NODE_OPTIONS="--openssl-legacy-provider"');
    output.push('npm run dev -- --port 8080\n');

    // 3. 提供检查状态命令
    output.push('=== 检查服务状态命令 ===');
    output.push('# 检查Redis服务');
    output.push('redis-cli ping');
    output.push('# 检查后端服务');
    output.push('netstat -tuln | grep ":8086 "');
    output.push('# 检查前端服务');
    output.push('netstat -tuln | grep ":8080 "\n');

    output.push('=== 访问地址 ===');
    output.push('前端: http://localhost:8080');
    output.push('后端API: http://localhost:8086');
    output.push('\n🎉 SOLO 模式准备就绪! 请按照上述说明在终端中启动服务');

    return {
      content: [
        {
          type: 'text',
          text: output.join('\n')
        }
      ]
    };
  }

  async troubleshootGatewayTimeout(args = {}) {
    const { auto_fix = true, check_config = true } = args;
    let output = [];
    let diagnostics = [];
    let fixes = [];

    output.push('=== 504网关超时问题诊断开始 ===\n');

    // 1. 检查后端服务状态
    output.push('1. 检查后端服务状态...');
    const backendCheck = await this.executeCommand('curl -I http://localhost:8086/api/website');
    const backendStatus = backendCheck.success && backendCheck.stdout.includes('200 OK');
    
    diagnostics.push(`后端服务 (8086): ${backendStatus ? '✓ 正常' : '✗ 异常'}`);
    if (!backendStatus) {
      diagnostics.push('  - 后端服务可能未启动或无响应');
      if (auto_fix) {
        fixes.push('尝试重启后端服务');
      }
    }

    // 2. 检查前端代理状态
    output.push('\n2. 检查前端代理状态...');
    const proxyCheck = await this.executeCommand('curl -I http://localhost:8080/api/website');
    const proxyStatus = proxyCheck.success && proxyCheck.stdout.includes('200 OK');
    const has504Error = proxyCheck.stderr && proxyCheck.stderr.includes('504');
    
    diagnostics.push(`前端代理 (8080): ${proxyStatus ? '✓ 正常' : '✗ 异常'}`);
    if (has504Error || !proxyStatus) {
      diagnostics.push('  - 前端代理出现504超时错误');
      diagnostics.push('  - 可能是代理配置错误或服务未完全启动');
    }

    // 3. 检查前端配置文件
    if (check_config) {
      output.push('\n3. 检查前端代理配置...');
      try {
        const configPath = '/home/metaspeekoj/OnlineJudgeFE/config/index.js';
        const configContent = await fs.readFile(configPath, 'utf8');
        const hasCorrectPort = configContent.includes('localhost:8086');
        const hasWrongPort = configContent.includes('localhost:8000');
        
        diagnostics.push(`代理配置: ${hasCorrectPort ? '✓ 正确 (8086)' : '✗ 需要检查'}`);
        
        if (hasWrongPort) {
          diagnostics.push('  - 发现错误的端口配置 (8000)');
          diagnostics.push('  - 需要修改为正确的后端端口 (8086)');
          if (auto_fix) {
            fixes.push('修正前端代理配置');
          }
        }
      } catch (error) {
        diagnostics.push('代理配置: ✗ 无法读取配置文件');
      }
    }

    // 4. 检查服务进程状态
    output.push('\n4. 检查服务进程状态...');
    const processCheck = await this.executeCommand("ps aux | grep -E '(manage.py.*runserver|node.*dev-server)' | grep -v grep");
    const hasBackendProcess = processCheck.stdout && processCheck.stdout.includes('manage.py');
    const hasFrontendProcess = processCheck.stdout && processCheck.stdout.includes('dev-server');
    
    diagnostics.push(`后端进程: ${hasBackendProcess ? '✓ 运行中' : '✗ 未运行'}`);
    diagnostics.push(`前端进程: ${hasFrontendProcess ? '✓ 运行中' : '✗ 未运行'}`);

    // 执行自动修复
    if (auto_fix && fixes.length > 0) {
      output.push('\n=== 自动修复开始 ===');
      
      for (const fix of fixes) {
        output.push(`执行修复: ${fix}`);
        
        if (fix.includes('修正前端代理配置')) {
          const fixResult = await this.fixProxyConfig();
          output.push(`配置修复: ${fixResult.success ? '成功' : '失败'}`);
        }
        
        if (fix.includes('重启后端服务')) {
          const restartResult = await this.startBackendOnly();
          output.push('后端服务重启完成');
        }
      }
      
      // 重启前端服务以应用配置
      if (fixes.some(f => f.includes('配置'))) {
        output.push('\n重启前端服务以应用配置...');
        await this.startFrontendOnly();
        
        // 等待服务启动后重新测试
        await new Promise(resolve => setTimeout(resolve, 8000));
        
        output.push('\n=== 修复后验证 ===');
        const verifyResult = await this.executeCommand('curl -I http://localhost:8080/api/website');
        const isFixed = verifyResult.success && verifyResult.stdout.includes('200 OK');
        output.push(`验证结果: ${isFixed ? '✓ 问题已解决' : '✗ 问题仍存在'}`);
      }
    }

    // 生成报告
    const report = [
      ...output,
      '\n=== 诊断结果 ===',
      ...diagnostics,
      '\n=== 建议解决方案 ==='
    ];

    if (fixes.length === 0) {
      if (!backendStatus) {
        report.push('1. 重启后端服务: 使用 start_backend_only 工具');
      }
      if (!proxyStatus) {
        report.push('2. 检查前端代理配置，确保指向正确端口 (8086)');
        report.push('3. 重启前端服务: 使用 start_frontend_only 工具');
      }
      report.push('4. 如问题持续，使用 restart_full_project 进行完整重启');
    }

    report.push('\n参考文档: /home/metaspeekoj/mcp-servers/GATEWAY_TIMEOUT_TROUBLESHOOTING.md');

    return {
      content: [
        {
          type: 'text',
          text: report.join('\n')
        }
      ]
    };
  }

  async fixProxyConfig() {
    try {
      const configPath = '/home/metaspeekoj/OnlineJudgeFE/config/index.js';
      let configContent = await fs.readFile(configPath, 'utf8');
      
      // 修复代理配置
      configContent = configContent.replace(
        /target:\s*['"]http:\/\/localhost:8000['"]/g,
        "target: 'http://localhost:8086'"
      );
      
      await fs.writeFile(configPath, configContent, 'utf8');
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('MetaSeekOJ项目重启MCP服务器已启动');
  }
}

const server = new ProjectRestartServer();
server.run().catch(console.error);