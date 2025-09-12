#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetaSeekOJ 项目优化重启脚本
提供更快速的启动、更好的错误处理和状态检查
支持SOLO模式和MCP模式
"""

import os
import sys
import time
import subprocess
import signal
import socket
import json
import argparse
from pathlib import Path

# 尝试导入psutil，如果不存在则提供备用方法
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# 不使用requests模块，避免依赖问题
HAS_REQUESTS = False

class ProjectManager:
    def __init__(self, solo_mode=False, skip_checks=False, parallel_start=True):
        self.base_dir = Path("/home/metaspeekoj")
        self.backend_dir = self.base_dir / "OnlineJudge"
        self.frontend_dir = self.base_dir / "OnlineJudgeFE"
        self.log_dir = Path("/tmp")
        self.solo_mode = solo_mode  # SOLO模式标志
        self.skip_checks = skip_checks  # 跳过检查标志
        self.parallel_start = parallel_start  # 并行启动标志
        self.processes = []  # 存储启动的进程
        
    def kill_processes(self, patterns):
        """根据进程名模式杀死进程"""
        killed = []
        
        if HAS_PSUTIL:
            # 使用psutil库（更准确）
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    for pattern in patterns:
                        if pattern in cmdline:
                            print(f"停止进程: {proc.info['pid']} - {cmdline[:80]}...")
                            proc.terminate()
                            killed.append(proc.info['pid'])
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 等待进程优雅退出
            time.sleep(2)
            
            # 强制杀死仍在运行的进程
            for proc in psutil.process_iter(['pid']):
                try:
                    if proc.pid in killed and proc.is_running():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        else:
            # 备用方法：使用pgrep和kill命令
            for pattern in patterns:
                try:
                    # 查找匹配的进程
                    result = subprocess.run(['pgrep', '-f', pattern], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        pids = result.stdout.strip().split('\n')
                        for pid in pids:
                            if pid:
                                print(f"停止进程: {pid} - {pattern}")
                                subprocess.run(['kill', pid])
                                killed.append(pid)
                except Exception as e:
                    print(f"停止进程时出错: {e}")
            
            # 等待进程优雅退出
            time.sleep(2)
            
            # 强制杀死仍在运行的进程
            for pid in killed:
                try:
                    # 检查进程是否仍在运行
                    if subprocess.run(['ps', '-p', pid], 
                                    capture_output=True).returncode == 0:
                        subprocess.run(['kill', '-9', pid])
                except Exception:
                    pass
                
        return len(killed)
    
    def check_port(self, port):
        """检查端口是否被占用"""
        if HAS_PSUTIL:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
            return False
        else:
            # 备用方法：使用netstat命令
            try:
                result = subprocess.run(
                    ['netstat', '-tuln'], 
                    capture_output=True, text=True
                )
                return f":{port} " in result.stdout
            except Exception:
                # 最后的备用方法：尝试连接到端口
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.connect(("localhost", port))
                    s.close()
                    return True
                except Exception:
                    return False
    
    def start_redis(self):
        """启动Redis服务"""
        print("启动Redis服务...")
        try:
            # 检查Redis是否已经运行
            result = subprocess.run(['redis-cli', 'ping'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and 'PONG' in result.stdout:
                print("✓ Redis服务已在运行")
                return True
        except Exception:
            pass
            
        # 启动Redis
        log_file = self.log_dir / "redis.log"
        cmd = f"redis-server --daemonize yes"
        try:
            subprocess.run(cmd, shell=True, check=True)
            
            # 快速检查
            time.sleep(1)
            result = subprocess.run(['redis-cli', 'ping'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                print("✓ Redis服务启动成功")
                return True
                
            # 如果快速检查失败，进行更多尝试
            if not self.skip_checks:
                for i in range(5):
                    time.sleep(1)
                    try:
                        result = subprocess.run(['redis-cli', 'ping'], 
                                              capture_output=True, text=True, timeout=2)
                        if result.returncode == 0:
                            print("✓ Redis服务启动成功")
                            return True
                    except Exception:
                        continue
        except Exception as e:
            print(f"启动Redis时出错: {e}")
                
        print("✗ Redis服务启动失败")
        return False
    
    def start_backend(self):
        """启动后端Django服务"""
        print("启动后端服务...")
        
        if not self.backend_dir.exists():
            print(f"✗ 后端目录不存在: {self.backend_dir}")
            return False
            
        venv_python = self.backend_dir / "venv" / "bin" / "python"
        if not venv_python.exists():
            print(f"✗ 虚拟环境不存在: {venv_python}")
            return False
        
        # 在启动前检查并杀死可能导致数据库锁定的多余Django进程
        print("检查并清理多余的Django进程以防止数据库锁定...")
        django_patterns = ['manage.py runserver']
        killed_count = self.kill_processes(django_patterns)
        if killed_count > 0:
            print(f"已停止 {killed_count} 个Django进程，防止数据库锁定")
            # 给进程完全终止的时间
            time.sleep(1)
            
        log_file = self.log_dir / "backend.log"
        
        if self.solo_mode:
            # SOLO模式：在前台运行，不使用nohup
            # 提供清理命令，方便用户在启动前清理多余进程
            clean_cmd = f"pkill -f \"manage.py runserver\""
            cmd = f"cd {self.backend_dir} && source venv/bin/activate && python manage.py runserver 0.0.0.0:8086"
            print("在SOLO模式下启动后端:")
            print(f"1. 首先清理多余Django进程: {clean_cmd}")
            print(f"2. 然后启动服务: {cmd}")
            print("注意：清理多余Django进程可以防止数据库锁定问题")
            return True
        else:
            # MCP模式：在后台运行
            cmd = f"cd {self.backend_dir} && source venv/bin/activate && python manage.py runserver 0.0.0.0:8086 > {log_file} 2>&1 &"
            subprocess.run(cmd, shell=True)
        
        # 快速检查端口
        time.sleep(1)
        if self.check_port(8086):
            print("✓ 后端服务端口已开启")
            return True
            
        # 如果快速检查失败且不跳过检查，进行更多尝试
        if not self.skip_checks:
            for i in range(10):
                time.sleep(1)
                if self.check_port(8086):
                    # 使用curl命令检查HTTP响应
                    try:
                        result = subprocess.run(
                            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:8086'],
                            capture_output=True, text=True, timeout=2
                        )
                        if result.returncode == 0:
                            status_code = int(result.stdout.strip())
                            if status_code in [200, 302, 404]:  # 这些状态码表示服务在运行
                                print(f"✓ 后端服务启动成功 (HTTP {status_code})")
                                return True
                    except Exception:
                        # 如果curl失败，仍然认为服务可能在运行
                        print("✓ 后端服务端口已开启")
                        return True
                    
        print("✗ 后端服务启动失败或正在启动中")
        return False
    
    def start_frontend(self):
        """启动前端Vue服务"""
        print("启动前端服务...")
        
        if not self.frontend_dir.exists():
            print(f"✗ 前端目录不存在: {self.frontend_dir}")
            return False
            
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            print(f"✗ package.json不存在: {package_json}")
            return False
            
        log_file = self.log_dir / "frontend.log"
        env = os.environ.copy()
        env['NODE_OPTIONS'] = '--openssl-legacy-provider'
        
        if self.solo_mode:
            # SOLO模式：在前台运行，不使用nohup
            cmd = f"cd {self.frontend_dir} && export NODE_OPTIONS='--openssl-legacy-provider' && npm run dev -- --port 8080"
            print(f"在SOLO模式下启动前端，请在终端中运行: {cmd}")
            return True
        else:
            # MCP模式：在后台运行
            cmd = f"cd {self.frontend_dir} && nohup npm run dev -- --port 8080 > {log_file} 2>&1 &"
            subprocess.run(cmd, shell=True, env=env)
        
        # 快速检查端口
        time.sleep(1)
        if self.check_port(8080):
            print("✓ 前端服务端口已开启")
            return True
            
        # 如果快速检查失败且不跳过检查，进行更多尝试
        if not self.skip_checks:
            for i in range(15):
                time.sleep(1)
                if self.check_port(8080):
                    # 使用curl命令检查HTTP响应
                    try:
                        result = subprocess.run(
                            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost:8080'],
                            capture_output=True, text=True, timeout=2
                        )
                        if result.returncode == 0:
                            status_code = int(result.stdout.strip())
                            if status_code == 200:
                                print(f"✓ 前端服务启动成功 (HTTP {status_code})")
                                return True
                    except Exception:
                        # 如果curl失败，仍然认为服务可能在运行
                        print("✓ 前端服务端口已开启")
                        return True
                    
        print("✗ 前端服务启动失败或正在启动中")
        return False
    
    def check_status(self):
        """检查所有服务状态"""
        print("\n=== 服务状态检查 ===")
        
        # Redis
        try:
            result = subprocess.run(['redis-cli', 'ping'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                print("✓ Redis服务: 运行中")
            else:
                print("✗ Redis服务: 未运行")
        except Exception:
            print("✗ Redis服务: 未运行")
            
        # 后端
        if self.check_port(8086):
            print("✓ 后端服务 (8086): 运行中")
        else:
            print("✗ 后端服务 (8086): 未运行")
            
        # 前端
        if self.check_port(8080):
            print("✓ 前端服务 (8080): 运行中")
        else:
            print("✗ 前端服务 (8080): 未运行")
            
        print("\n=== 访问地址 ===")
        print("前端: http://localhost:8080")
        print("后端API: http://localhost:8086")
    
    def restart_project(self):
        """重启整个项目"""
        print("=== MetaSeekOJ 项目重启 ===")
        
        # 停止现有服务
        print("\n停止现有服务...")
        patterns = [
            'manage.py runserver',
            'npm run dev',
            'node.*8080',
        ]
        
        # 在非SOLO模式下才停止Redis
        if not self.solo_mode:
            patterns.append('redis-server')
            
        killed_count = self.kill_processes(patterns)
        if killed_count > 0:
            print(f"已停止 {killed_count} 个进程")
            print("停止服务结果: 成功")
        else:
            print("没有找到需要停止的进程")
            print("停止服务结果: 无需操作")
        
        time.sleep(1)
        
        # 启动服务
        success = True
        
        # 启动Redis（在非SOLO模式下）
        if not self.solo_mode:
            if not self.start_redis():
                success = False
        else:
            print("SOLO模式: 跳过自动启动Redis")
        
        # 在并行模式下同时启动前端和后端
        if self.parallel_start and not self.solo_mode:
            import threading
            
            backend_success = [True]  # 使用列表以便在线程中修改
            frontend_success = [True]
            
            def start_backend_thread():
                if not self.start_backend():
                    backend_success[0] = False
                    
            def start_frontend_thread():
                if not self.start_frontend():
                    frontend_success[0] = False
            
            # 创建并启动线程
            backend_thread = threading.Thread(target=start_backend_thread)
            frontend_thread = threading.Thread(target=start_frontend_thread)
            
            backend_thread.start()
            frontend_thread.start()
            
            # 等待线程完成
            backend_thread.join()
            frontend_thread.join()
            
            if not backend_success[0] or not frontend_success[0]:
                success = False
        else:
            # 顺序启动
            if not self.start_backend():
                success = False
                
            if not self.start_frontend():
                success = False
        
        # 检查状态（在非SOLO模式下）
        if not self.solo_mode:
            self.check_status()
        
        if success:
            if self.solo_mode:
                print("\n🎉 项目准备就绪! 请按照上述说明在终端中启动服务")
            else:
                print("\n🎉 项目重启成功!")
        else:
            print("\n❌ 项目重启过程中出现错误，请检查日志")
            print("日志文件:")
            print(f"  Redis: {self.log_dir}/redis.log")
            print(f"  后端: {self.log_dir}/backend.log")
            print(f"  前端: {self.log_dir}/frontend.log")
            
        return success

def create_mcp_tool():
    """创建MCP工具配置文件"""
    mcp_config = {
        "server_name": "mcp.config.usrremotemcp.project-restart",
        "description": "",
        "tools": [
            {
                "name": "restart_full_project",
                "description": "全面重启项目 - 包含Redis、前端、后端等所有服务",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "verbose": {
                            "type": "boolean",
                            "description": "是否显示详细输出",
                            "default": True
                        },
                        "check_status": {
                            "type": "boolean",
                            "description": "启动后是否检查服务状态",
                            "default": True
                        }
                    }
                }
            },
            {
                "name": "quick_restart",
                "description": "快速重启 - 使用现有的restart.sh脚本",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "python_restart",
                "description": "Python版本重启 - 使用restart_project.py脚本",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "check_project_status",
                "description": "检查项目状态 - 查看所有服务运行状态",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "stop_all_services",
                "description": "停止所有服务 - 停止前端、后端、Redis等所有服务",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "start_redis_only",
                "description": "仅启动Redis服务",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "start_backend_only",
                "description": "仅启动后端服务（Django）",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "start_frontend_only",
                "description": "仅启动前端服务（Vue.js）",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    }
    
    # 将配置写入文件
    config_path = Path("/home/metaspeekoj/mcp-servers/project_restart_config.json")
    with open(config_path, 'w') as f:
        json.dump(mcp_config, f, indent=2)
    
    print(f"MCP工具配置已创建: {config_path}")

def main():
    parser = argparse.ArgumentParser(description='MetaSeekOJ项目启动工具')
    parser.add_argument('--solo', action='store_true', help='SOLO模式 - 提供命令而不是自动启动服务')
    parser.add_argument('--fast', action='store_true', help='快速模式 - 跳过大部分检查以加快启动速度')
    parser.add_argument('--sequential', action='store_true', help='顺序启动 - 不使用并行启动服务')
    parser.add_argument('--create-mcp', action='store_true', help='创建MCP工具配置文件')
    parser.add_argument('--redis-only', action='store_true', help='仅启动Redis服务')
    parser.add_argument('--backend-only', action='store_true', help='仅启动后端服务')
    parser.add_argument('--frontend-only', action='store_true', help='仅启动前端服务')
    parser.add_argument('--stop-all', action='store_true', help='停止所有服务')
    parser.add_argument('--check-status', action='store_true', help='检查服务状态')
    
    args = parser.parse_args()
    
    if args.create_mcp:
        create_mcp_tool()
        return
    
    try:
        manager = ProjectManager(
            solo_mode=args.solo,
            skip_checks=args.fast,
            parallel_start=not args.sequential
        )
        
        if args.redis_only:
            manager.start_redis()
        elif args.backend_only:
            manager.start_backend()
        elif args.frontend_only:
            manager.start_frontend()
        elif args.stop_all:
            patterns = ['manage.py runserver', 'npm run dev', 'node.*8080', 'redis-server']
            manager.kill_processes(patterns)
        elif args.check_status:
            manager.check_status()
        else:
            manager.restart_project()
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()