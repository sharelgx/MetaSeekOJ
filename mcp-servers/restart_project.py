#!/usr/bin/env python3
"""
MetaSeekOJ项目重启脚本
用于快速重启前端和后端服务
"""

import subprocess
import time
import os
import signal
import psutil

def kill_process_by_port(port):
    """根据端口号杀死进程"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.info['connections']:
                    if conn.laddr.port == port:
                        print(f"正在停止端口 {port} 上的进程 (PID: {proc.info['pid']})")
                        proc.kill()
                        proc.wait(timeout=3)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        print(f"停止端口 {port} 进程时出错: {e}")
    return False

def kill_process_by_name(name_pattern):
    """根据进程名模式杀死进程"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if name_pattern in cmdline:
                    print(f"正在停止进程: {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.kill()
                    proc.wait(timeout=3)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        print(f"停止进程时出错: {e}")

def restart_project():
    """重启整个项目"""
    print("=== MetaSeekOJ 项目重启开始 ===")
    
    # 1. 停止现有服务
    print("\n1. 停止现有服务...")
    
    # 停止Redis服务 (端口6379)
    kill_process_by_port(6379)
    
    # 停止前端服务 (端口8080)
    kill_process_by_port(8080)
    
    # 停止后端服务 (端口8086)
    kill_process_by_port(8086)
    
    # 停止可能的其他相关进程
    kill_process_by_name('redis-server')
    kill_process_by_name('manage.py runserver')
    kill_process_by_name('npm run dev')
    kill_process_by_name('node')
    
    print("等待进程完全停止...")
    time.sleep(3)
    
    # 2. 启动Redis服务
    print("\n2. 启动Redis服务...")
    redis_cmd = ["redis-server"]
    
    try:
        redis_process = subprocess.Popen(
            redis_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        print(f"Redis服务已启动 (PID: {redis_process.pid})")
        time.sleep(2)  # 等待Redis启动
    except Exception as e:
        print(f"启动Redis服务失败: {e}")
        return False
    
    # 3. 启动后端服务
    print("\n3. 启动后端Django服务...")
    backend_dir = "/home/metaspeekoj/OnlineJudge"
    backend_cmd = ["python3", "manage.py", "runserver", "0.0.0.0:8086"]
    
    try:
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        print(f"后端服务已启动 (PID: {backend_process.pid})")
        time.sleep(5)  # 等待后端启动
    except Exception as e:
        print(f"启动后端服务失败: {e}")
        return False
    
    # 4. 启动前端服务
    print("\n4. 启动前端开发服务...")
    frontend_dir = "/home/metaspeekoj/OnlineJudgeFE"
    frontend_cmd = ["npm", "run", "dev", "--", "--port", "8080"]
    
    # 设置Node.js环境变量
    env = os.environ.copy()
    env['NODE_OPTIONS'] = '--openssl-legacy-provider'
    
    try:
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            preexec_fn=os.setsid
        )
        print(f"前端服务已启动 (PID: {frontend_process.pid})")
        time.sleep(5)  # 等待前端启动
    except Exception as e:
        print(f"启动前端服务失败: {e}")
        return False
    
    # 5. 验证服务状态
    print("\n5. 验证服务状态...")
    
    # 检查端口是否被占用
    redis_running = False
    backend_running = False
    frontend_running = False
    
    for proc in psutil.process_iter(['pid', 'connections']):
        try:
            for conn in proc.info['connections']:
                if conn.laddr.port == 6379:
                    redis_running = True
                elif conn.laddr.port == 8086:
                    backend_running = True
                elif conn.laddr.port == 8080:
                    frontend_running = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    print(f"Redis服务 (端口6379): {'✓ 运行中' if redis_running else '✗ 未运行'}")
    print(f"后端服务 (端口8086): {'✓ 运行中' if backend_running else '✗ 未运行'}")
    print(f"前端服务 (端口8080): {'✓ 运行中' if frontend_running else '✗ 未运行'}")
    
    if redis_running and backend_running and frontend_running:
        print("\n=== 项目重启成功! ===")
        print("前端访问地址: http://localhost:8080")
        print("后端API地址: http://localhost:8086")
        return True
    else:
        print("\n=== 项目重启部分失败，请检查日志 ===")
        return False

if __name__ == "__main__":
    restart_project()