#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import django

# 设置Django环境
sys.path.append('/home/metaspeekoj/OnlineJudge')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oj.settings')
django.setup()

from choice_question.models import ExamPaper, ChoiceQuestion, ExamPaperQuestion

def check_imported_data():
    try:
        # 查找最新的试卷（按ID降序）
        latest_papers = ExamPaper.objects.all().order_by('-id')[:3]
        print(f"最新的3个试卷:")
        for paper in latest_papers:
            paper_questions = ExamPaperQuestion.objects.filter(paper=paper)
            print(f"试卷ID: {paper.id}, 标题: {paper.title}, 题目数量: {paper_questions.count()}")
            
        # 查找最新的试卷详情
        if latest_papers:
            paper = latest_papers[0]
            print(f"\n最新试卷详情 - ID: {paper.id}, 标题: {paper.title}")
            print(f"试卷描述: {paper.description}")
            
            # 查找关联的题目
            paper_questions = ExamPaperQuestion.objects.filter(paper=paper)
            print(f"\n📝 试卷包含题目数量: {paper_questions.count()}")
        else:
            print("❌ 没有找到任何试卷")
            return
        
        # 检查所有选择题
        all_questions = ChoiceQuestion.objects.all().order_by('-id')[:3]
        print(f"\n🔍 最近创建的3个选择题详情:")
        for q in all_questions:
            print(f"\n--- 题目ID: {q.id} ---")
            print(f"标题: {q.title}")
            print(f"题目类型: {q.question_type}")
            print(f"选项原始数据: {repr(q.options)}")
            print(f"正确答案: {q.correct_answer}")
            print(f"创建时间: {q.create_time}")
            
            # 尝试解析选项
            if isinstance(q.options, str):
                import json
                try:
                    options = json.loads(q.options)
                    print(f"解析后的选项: {options}")
                    if isinstance(options, list):
                        for i, opt in enumerate(options):
                            print(f"  选项{i+1}: {opt}")
                except Exception as e:
                    print(f"选项解析失败: {e}")
            else:
                print(f"选项类型: {type(q.options)}")
        
        if paper_questions.exists():
            for i, pq in enumerate(paper_questions, 1):
                question = pq.question
                print(f"\n--- 题目 {i} ---")
                print(f"题目标题: {question.title}")
                print(f"题目类型: {question.question_type}")
                print(f"选项数据: {question.options}")
                print(f"正确答案: {question.correct_answer}")
                
                # 检查选项格式
                if isinstance(question.options, str):
                    import json
                    try:
                        options = json.loads(question.options)
                        print(f"解析后的选项: {options}")
                    except:
                        print(f"选项解析失败: {question.options}")
                else:
                    print(f"选项类型: {type(question.options)}")
        else:
            print("❌ 试卷中没有找到题目")
            # 检查是否有孤立的题目（没有关联到试卷）
            test_questions = ChoiceQuestion.objects.filter(title="测试选择题").order_by('-id')[:3]
            if test_questions.exists():
                print("\n🔍 找到测试选择题:")
                for q in test_questions:
                    print(f"\n--- 测试题目ID: {q.id} ---")
                    print(f"标题: {q.title}")
                    print(f"题目类型: {q.question_type}")
                    print(f"选项原始数据: {repr(q.options)}")
                    print(f"正确答案: {q.correct_answer}")
                    
                    # 解析选项
                    if isinstance(q.options, str):
                        import json
                        try:
                            options = json.loads(q.options)
                            print(f"解析后的选项: {options}")
                            if isinstance(options, list):
                                for i, opt in enumerate(options):
                                    if isinstance(opt, dict):
                                        print(f"  选项{opt.get('key', i+1)}: {opt.get('text', opt)}")
                                    else:
                                        print(f"  选项{i+1}: {opt}")
                        except Exception as e:
                            print(f"选项解析失败: {e}")
                    else:
                        print(f"选项类型: {type(q.options)}")
            else:
                print("\n❌ 没有找到标题为'测试选择题'的题目")
            
    except ExamPaper.DoesNotExist:
        print("❌ 未找到ID为131的试卷")
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")

if __name__ == "__main__":
    check_imported_data()