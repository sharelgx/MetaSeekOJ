# -*- coding: utf-8 -*-
"""
MCP监控视图
提供简单的监控面板功能
"""

import json
import psutil
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render


class MCPMonitoringDashboardView(View):
    """MCP监控仪表盘视图"""
    
    def get(self, request):
        """返回监控仪表盘页面"""
        # 使用模板文件渲染页面
        return render(request, 'mcp_monitoring/dashboard.html')


@method_decorator(csrf_exempt, name='dispatch')
class MCPMonitoringAPIView(View):
    """MCP监控API视图"""
    
    def get(self, request):
        """返回监控指标数据"""
        try:
            # 系统指标
            system_metrics = {
                'cpu_percent': round(psutil.cpu_percent(interval=1), 1),
                'memory_percent': round(psutil.virtual_memory().percent, 1),
                'disk_percent': round(psutil.disk_usage('/').percent, 1)
            }
            
            # 服务状态检查
            services = {
                'Redis': {'port': 6379, 'running': self.check_port(6379), 'pid': self.get_pid_by_port(6379)},
                'Django': {'port': 8000, 'running': self.check_port(8000), 'pid': self.get_pid_by_port(8000)},
                'MCP监控': {'port': 8001, 'running': self.check_port(8001), 'pid': self.get_pid_by_port(8001)},
                '前端服务': {'port': 8080, 'running': self.check_port(8080), 'pid': self.get_pid_by_port(8080)}
            }
            
            metrics = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'system': system_metrics,
                'services': services
            }
            
            return JsonResponse(metrics, json_dumps_params={'ensure_ascii': False})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def check_port(self, port):
        """检查端口是否被占用"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
            return False
        except:
            return False
    
    def get_pid_by_port(self, port):
        """根据端口获取进程ID"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return conn.pid
            return None
        except:
            return None