#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考试分数计算调试脚本
用于捕捉和分析分数计算过程中的问题
"""

import os
import sys
import django
from datetime import datetime

# 设置Django环境
sys.path.append('/home/metaspeekoj/OnlineJudge')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.models import ExamSession, ChoiceQuestion
from django.contrib.auth.models import User
import json

class ScoreDebugger:
    """分数计算调试器"""
    
    def __init__(self):
        self.debug_info = []
        
    def log(self, message, level="INFO"):
        """记录调试信息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.debug_info.append(log_entry)
        print(log_entry)
        
    def debug_session_score(self, session_id=None, username=None):
        """调试指定会话的分数计算"""
        try:
            # 获取会话
            if session_id:
                session = ExamSession.objects.get(id=session_id)
            elif username:
                user = User.objects.get(username=username)
                session = ExamSession.objects.filter(user=user).order_by('-create_time').first()
                if not session:
                    self.log(f"用户 {username} 没有找到考试会话", "ERROR")
                    return
            else:
                session = ExamSession.objects.order_by('-create_time').first()
                if not session:
                    self.log("没有找到任何考试会话", "ERROR")
                    return
                    
            self.log(f"开始调试会话 ID: {session.id}")
            self.log(f"用户: {session.user.username}")
            self.log(f"试卷: {session.paper.title}")
            self.log(f"状态: {session.status}")
            self.log(f"当前分数: {session.score}")
            self.log(f"正确题数: {session.correct_count}")
            self.log(f"总题数: {session.total_count}")
            
            # 检查题目和答案数据
            self.log(f"题目列表: {session.questions}")
            self.log(f"答案记录: {session.answers}")
            
            if not session.questions:
                self.log("题目列表为空！", "ERROR")
                return
                
            if not session.answers:
                self.log("答案记录为空！", "WARNING")
                
            # 获取题目详情
            questions = ChoiceQuestion.objects.filter(id__in=session.questions)
            self.log(f"从数据库获取到 {questions.count()} 个题目")
            
            # 逐题分析
            correct_count = 0
            total_count = len(session.questions)
            
            for i, question in enumerate(questions):
                self.log(f"\n--- 题目 {i+1} (ID: {question.id}) ---")
                self.log(f"题目类型: {question.question_type}")
                self.log(f"题目内容: {question.content[:100]}...")
                
                # 检查选项格式
                try:
                    if question.options:
                        options = json.loads(question.options) if isinstance(question.options, str) else question.options
                        self.log(f"选项数量: {len(options)}")
                    else:
                        self.log("选项为空！", "ERROR")
                except Exception as e:
                    self.log(f"选项解析错误: {e}", "ERROR")
                    
                # 检查正确答案
                self.log(f"正确答案: {question.correct_answer} (类型: {type(question.correct_answer)})")
                
                # 检查用户答案
                question_id = str(question.id)
                user_answer = session.answers.get(question_id)
                self.log(f"用户答案: {user_answer} (类型: {type(user_answer)})")
                
                # 判断答案正确性
                is_correct = session.is_answer_correct(question, user_answer)
                self.log(f"答案正确性: {is_correct}")
                
                if is_correct:
                    correct_count += 1
                    
                # 详细分析答案匹配逻辑
                if question.question_type == 'single':
                    self.log(f"单选题比较: {user_answer} == {question.correct_answer} -> {user_answer == question.correct_answer}")
                elif question.question_type == 'multiple':
                    if isinstance(user_answer, list) and isinstance(question.correct_answer, list):
                        user_set = set(user_answer)
                        correct_set = set(question.correct_answer)
                        self.log(f"多选题比较: {user_set} == {correct_set} -> {user_set == correct_set}")
                    else:
                        self.log(f"多选题类型不匹配: 用户答案类型={type(user_answer)}, 正确答案类型={type(question.correct_answer)}", "ERROR")
                        
            # 计算分数
            self.log(f"\n--- 分数计算 ---")
            self.log(f"统计正确题数: {correct_count}")
            self.log(f"总题数: {total_count}")
            self.log(f"试卷总分: {session.paper.total_score}")
            
            if total_count > 0:
                calculated_score = int((correct_count / total_count) * session.paper.total_score)
                self.log(f"计算公式: ({correct_count} / {total_count}) * {session.paper.total_score} = {calculated_score}")
            else:
                calculated_score = 0
                self.log("总题数为0，分数设为0")
                
            self.log(f"计算得分: {calculated_score}")
            self.log(f"数据库中的分数: {session.score}")
            
            if calculated_score != session.score:
                self.log(f"分数不一致！计算值={calculated_score}, 数据库值={session.score}", "ERROR")
                
                # 尝试重新计算并保存
                self.log("尝试重新计算分数...")
                session.calculate_score()
                session.save()
                self.log(f"重新计算后的分数: {session.score}")
            else:
                self.log("分数计算正确")
                
        except Exception as e:
            self.log(f"调试过程中发生错误: {e}", "ERROR")
            import traceback
            self.log(f"错误详情: {traceback.format_exc()}", "ERROR")
            
    def debug_all_recent_sessions(self, limit=5):
        """调试最近的几个会话"""
        sessions = ExamSession.objects.order_by('-create_time')[:limit]
        self.log(f"开始调试最近的 {sessions.count()} 个会话")
        
        for session in sessions:
            self.log(f"\n{'='*50}")
            self.debug_session_score(session_id=session.id)
            
    def save_debug_log(self, filename=None):
        """保存调试日志到文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/home/metaspeekoj/OnlineJudge/choice_question/debug_score_{timestamp}.log"
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.debug_info))
            
        self.log(f"调试日志已保存到: {filename}")
        
def main():
    """主函数"""
    debugger = ScoreDebugger()
    
    print("考试分数计算调试脚本")
    print("=" * 30)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == '--session-id' and len(sys.argv) > 2:
            session_id = int(sys.argv[2])
            debugger.debug_session_score(session_id=session_id)
        elif sys.argv[1] == '--username' and len(sys.argv) > 2:
            username = sys.argv[2]
            debugger.debug_session_score(username=username)
        elif sys.argv[1] == '--all':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            debugger.debug_all_recent_sessions(limit=limit)
    else:
        # 默认调试最新的会话
        debugger.debug_session_score()
        
    # 保存日志
    debugger.save_debug_log()
    
if __name__ == '__main__':
    main()