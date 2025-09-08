#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetaSeekOJ 项目重启脚本 (Python版本)
提供更好的错误处理和状态检查
"""

import os
import sys
import time
import subprocess
import signal
import psutil
import requests
from pathlib import Path

class ProjectManager:
    def __init__(self):
        self.base_dir = Path("/home/metaspeekoj")
        self.backend_dir = self.base_dir / "OnlineJudge"
        self.frontend_dir = self.base_dir / "OnlineJudgeFE"
        self.log_dir = Path("/tmp")
        
    def kill_processes(self, patterns):
        """根据进程名模式杀死进程"""
        killed = []
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
        time.sleep(3)
        
        # 强制杀死仍在运行的进程
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.pid in killed and proc.is_running():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return len(killed)
    
    def check_port(self, port):
        """检查端口是否被占用"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return True
        return False
    
    def start_redis(self):
        """启动Redis服务"""
        print("启动Redis服务...")
        try:
            # 检查Redis是否已经运行
            result = subprocess.run(['redis-cli', 'ping'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and 'PONG' in result.stdout:
                print("✓ Redis服务已在运行")
                return True
        except:
            pass
            
        # 启动Redis
        log_file = self.log_dir / "redis.log"
        cmd = f"nohup redis-server > {log_file} 2>&1 &"
        subprocess.run(cmd, shell=True)
        
        # 等待启动
        for i in range(10):
            time.sleep(1)
            try:
                result = subprocess.run(['redis-cli', 'ping'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    print("✓ Redis服务启动成功")
                    return True
            except:
                continue
                
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
            
        log_file = self.log_dir / "backend.log"
        cmd = f"cd {self.backend_dir} && nohup {venv_python} manage.py runserver 0.0.0.0:8086 > {log_file} 2>&1 &"
        subprocess.run(cmd, shell=True)
        
        # 等待启动
        for i in range(15):
            time.sleep(1)
            if self.check_port(8086):
                try:
                    response = requests.get('http://localhost:8086', timeout=5)
                    if response.status_code in [200, 404]:  # 404也表示服务在运行
                        print("✓ 后端服务启动成功")
                        return True
                except:
                    continue
                    
        print("✗ 后端服务启动失败")
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
        
        cmd = f"cd {self.frontend_dir} && nohup npm run dev -- --port 8080 > {log_file} 2>&1 &"
        subprocess.run(cmd, shell=True, env=env)
        
        # 等待启动
        for i in range(30):
            time.sleep(1)
            if self.check_port(8080):
                try:
                    response = requests.get('http://localhost:8080', timeout=5)
                    if response.status_code == 200:
                        print("✓ 前端服务启动成功")
                        return True
                except:
                    continue
                    
        print("✗ 前端服务启动失败")
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
        except:
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
            'redis-server'
        ]
        killed_count = self.kill_processes(patterns)
        print(f"已停止 {killed_count} 个进程")
        
        time.sleep(2)
        
        # 启动服务
        success = True
        
        if not self.start_redis():
            success = False
            
        if not self.start_backend():
            success = False
            
        if not self.start_frontend():
            success = False
            
        # 检查状态
        self.check_status()
        
        if success:
            print("\n🎉 项目重启成功!")
        else:
            print("\n❌ 项目重启过程中出现错误，请检查日志")
            print("日志文件:")
            print(f"  Redis: {self.log_dir}/redis.log")
            print(f"  后端: {self.log_dir}/backend.log")
            print(f"  前端: {self.log_dir}/frontend.log")
            
        return success

def main():
    try:
        manager = ProjectManager()
        manager.restart_project()
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()