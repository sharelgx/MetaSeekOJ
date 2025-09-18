# -*- coding: utf-8 -*-
"""
专题试做管理员API视图
"""

from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.http import HttpResponse
from utils.api import APIView
from account.decorators import super_admin_required
from .models import ExamSession, ChoiceQuestion, Category
from account.models import User
import json
import xlwt
from datetime import datetime, timedelta


class TopicPracticeRecordsAdminAPI(APIView):
    """
    专题练习记录管理API
    """
    
    @super_admin_required
    def get(self, request, record_id=None):
        """
        获取专题练习记录列表或详情
        """
        if record_id:
            # 获取单个记录详情
            try:
                session = ExamSession.objects.select_related('user', 'paper').get(
                    id=record_id,
                    paper__title__startswith='专题练习：'
                )
                
                # 获取答题详情
                question_details = []
                if session.answers:
                    paper_questions = json.loads(session.paper.questions)
                    for q_data in paper_questions:
                        question_id = q_data['id']
                        try:
                            question = ChoiceQuestion.objects.get(id=question_id)
                            user_answer = session.answers.get(str(question_id), '')
                            correct_answer = question.answer
                            is_correct = user_answer == correct_answer
                            
                            question_details.append({
                                'question_id': question_id,
                                'title': question.title,
                                'user_answer': user_answer,
                                'correct_answer': correct_answer,
                                'is_correct': is_correct
                            })
                        except ChoiceQuestion.DoesNotExist:
                            continue
                
                data = {
                    'id': session.id,
                    'username': session.user.username,
                    'user_id': session.user.id,
                    'topic_name': session.paper.title.replace('专题练习：', ''),
                    'topic_full_path': session.paper.title.replace('专题练习：', ''),
                    'status': session.status,
                    'score': session.score or 0,
                    'correct_count': session.correct_count or 0,
                    'total_count': session.total_count or 0,
                    'start_time': session.start_time,
                    'submit_time': session.submit_time,
                    'duration': self._calculate_duration(session),
                    'answers': session.answers,
                    'question_details': question_details
                }
                
                return self.success(data)
                
            except ExamSession.DoesNotExist:
                return self.error("练习记录不存在", status_code=404)
        
        # 获取记录列表
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        keyword = request.GET.get('keyword', '')
        
        # 基础查询：只获取专题练习记录
        sessions = ExamSession.objects.select_related('user', 'paper').filter(
            paper__title__startswith='专题练习：'
        )
        
        # 搜索过滤
        if keyword:
            sessions = sessions.filter(
                Q(user__username__icontains=keyword) |
                Q(paper__title__icontains=keyword)
            )
        
        # 排序
        sessions = sessions.order_by('-create_time')
        
        # 分页
        total = sessions.count()
        start = (page - 1) * page_size
        end = start + page_size
        sessions = sessions[start:end]
        
        # 构建返回数据
        records = []
        for session in sessions:
            records.append({
                'id': session.id,
                'username': session.user.username,
                'user_id': session.user.id,
                'topic_name': session.paper.title.replace('专题练习：', ''),
                'topic_full_path': session.paper.title.replace('专题练习：', ''),
                'status': session.status,
                'score': session.score or 0,
                'correct_count': session.correct_count or 0,
                'total_count': session.total_count or 0,
                'start_time': session.start_time,
                'submit_time': session.submit_time,
                'duration': self._calculate_duration(session)
            })
        
        return self.success({
            'results': records,
            'total': total,
            'page': page,
            'page_size': page_size
        })
    
    @super_admin_required
    def delete(self, request, record_id):
        """
        删除专题练习记录
        """
        try:
            session = ExamSession.objects.get(
                id=record_id,
                paper__title__startswith='专题练习：'
            )
            session.delete()
            return self.success("删除成功")
        except ExamSession.DoesNotExist:
            return self.error("练习记录不存在", status_code=404)
    
    def _calculate_duration(self, session):
        """
        计算练习用时（秒）
        """
        if session.start_time and session.submit_time:
            delta = session.submit_time - session.start_time
            return int(delta.total_seconds())
        return None


class TopicPracticeStatisticsAdminAPI(APIView):
    """
    专题练习统计API
    """
    
    @super_admin_required
    def get(self, request):
        """
        获取专题练习统计信息
        """
        # 获取所有专题练习记录
        sessions = ExamSession.objects.filter(
            paper__title__startswith='专题练习：'
        )
        
        # 总练习次数
        total_sessions = sessions.count()
        
        # 参与用户数
        total_users = sessions.values('user').distinct().count()
        
        # 平均得分
        avg_score = sessions.filter(status='completed').aggregate(
            avg_score=Avg('score')
        )['avg_score'] or 0
        avg_score = round(avg_score, 1)
        
        # 今日练习次数
        today = timezone.now().date()
        today_sessions = sessions.filter(
            create_time__date=today
        ).count()
        
        # 最近7天的练习趋势
        week_ago = timezone.now() - timedelta(days=7)
        daily_stats = []
        for i in range(7):
            date = (timezone.now() - timedelta(days=6-i)).date()
            count = sessions.filter(create_time__date=date).count()
            daily_stats.append({
                'date': date.strftime('%m-%d'),
                'count': count
            })
        
        # 热门专题排行
        popular_topics = sessions.values('paper__title').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        topic_stats = []
        for item in popular_topics:
            topic_name = item['paper__title'].replace('专题练习：', '')
            topic_stats.append({
                'name': topic_name,
                'count': item['count']
            })
        
        return self.success({
            'totalSessions': total_sessions,
            'totalUsers': total_users,
            'avgScore': avg_score,
            'todaySessions': today_sessions,
            'dailyStats': daily_stats,
            'topicStats': topic_stats
        })


class TopicPracticeExportAdminAPI(APIView):
    """
    专题练习记录导出API
    """
    
    @super_admin_required
    def get(self, request):
        """
        导出专题练习记录为Excel文件
        """
        keyword = request.GET.get('keyword', '')
        
        # 获取数据
        sessions = ExamSession.objects.select_related('user', 'paper').filter(
            paper__title__startswith='专题练习：'
        )
        
        if keyword:
            sessions = sessions.filter(
                Q(user__username__icontains=keyword) |
                Q(paper__title__icontains=keyword)
            )
        
        sessions = sessions.order_by('-create_time')
        
        # 创建Excel文件
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('专题练习记录')
        
        # 设置列标题
        headers = ['ID', '用户名', '专题名称', '状态', '得分(%)', '正确题数', '总题数', '用时(分钟)', '开始时间', '提交时间']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # 写入数据
        for row, session in enumerate(sessions, 1):
            duration_minutes = ''
            if session.start_time and session.submit_time:
                delta = session.submit_time - session.start_time
                duration_minutes = round(delta.total_seconds() / 60, 1)
            
            data = [
                session.id,
                session.user.username,
                session.paper.title.replace('专题练习：', ''),
                self._get_status_text(session.status),
                session.score or 0,
                session.correct_count or 0,
                session.total_count or 0,
                duration_minutes,
                session.start_time.strftime('%Y-%m-%d %H:%M:%S') if session.start_time else '',
                session.submit_time.strftime('%Y-%m-%d %H:%M:%S') if session.submit_time else ''
            ]
            
            for col, value in enumerate(data):
                worksheet.write(row, col, value)
        
        # 返回Excel文件
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="专题练习记录_{datetime.now().strftime("%Y%m%d")}.xls"'
        workbook.save(response)
        return response
    
    def _get_status_text(self, status):
        status_map = {
            'started': '进行中',
            'completed': '已完成',
            'timeout': '超时'
        }
        return status_map.get(status, status)