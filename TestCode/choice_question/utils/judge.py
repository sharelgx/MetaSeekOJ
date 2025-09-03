import json
from typing import List, Dict, Any, Union, Optional
from django.utils import timezone
from ..models import ChoiceQuestion, ChoiceQuestionSubmission
from .helpers import parse_answer


class ChoiceQuestionJudge:
    """
    选择题判题工具类
    负责选择题的自动判分逻辑
    """
    
    def __init__(self):
        self.judge_result = {
            'is_correct': False,
            'score': 0,
            'max_score': 0,
            'user_answer': [],
            'correct_answer': [],
            'explanation': '',
            'judge_time': None,
            'details': {}
        }
    
    def judge_submission(self, question: ChoiceQuestion, user_answer: Union[str, List], 
                        user=None, save_submission: bool = True) -> Dict[str, Any]:
        """
        判断用户提交的答案
        
        Args:
            question: 题目对象
            user_answer: 用户答案
            user: 用户对象
            save_submission: 是否保存提交记录
            
        Returns:
            判题结果
        """
        try:
            # 解析用户答案
            parsed_user_answer = self._parse_user_answer(user_answer, question.question_type)
            
            # 解析正确答案
            correct_answer = self._parse_correct_answer(question.correct_answer)
            
            # 执行判题
            is_correct = self._compare_answers(parsed_user_answer, correct_answer, question.question_type)
            
            # 计算得分
            score = self._calculate_score(is_correct, question.score, question.question_type, 
                                        parsed_user_answer, correct_answer)
            
            # 构建判题结果
            self.judge_result = {
                'is_correct': is_correct,
                'score': score,
                'max_score': question.score,
                'user_answer': parsed_user_answer,
                'correct_answer': correct_answer,
                'explanation': question.explanation or '',
                'judge_time': timezone.now(),
                'details': {
                    'question_type': question.question_type,
                    'question_id': question.id,
                    'difficulty': question.difficulty,
                    'options_count': len(question.options) if question.options else 0
                }
            }
            
            # 保存提交记录
            if save_submission and user:
                self._save_submission(question, user, parsed_user_answer, is_correct, score)
            
            return self.judge_result
            
        except Exception as e:
            return {
                'is_correct': False,
                'score': 0,
                'max_score': question.score,
                'user_answer': [],
                'correct_answer': [],
                'explanation': '',
                'judge_time': timezone.now(),
                'error': str(e),
                'details': {}
            }
    
    def batch_judge(self, submissions: List[Dict[str, Any]], save_submissions: bool = True) -> List[Dict[str, Any]]:
        """
        批量判题
        
        Args:
            submissions: 提交列表，每个元素包含question_id, user_answer, user等
            save_submissions: 是否保存提交记录
            
        Returns:
            判题结果列表
        """
        results = []
        
        for submission in submissions:
            try:
                question = ChoiceQuestion.objects.get(id=submission['question_id'])
                result = self.judge_submission(
                    question=question,
                    user_answer=submission['user_answer'],
                    user=submission.get('user'),
                    save_submission=save_submissions
                )
                result['question_id'] = submission['question_id']
                results.append(result)
                
            except ChoiceQuestion.DoesNotExist:
                results.append({
                    'question_id': submission['question_id'],
                    'is_correct': False,
                    'score': 0,
                    'max_score': 0,
                    'error': '题目不存在',
                    'judge_time': timezone.now()
                })
            except Exception as e:
                results.append({
                    'question_id': submission.get('question_id', 'unknown'),
                    'is_correct': False,
                    'score': 0,
                    'max_score': 0,
                    'error': str(e),
                    'judge_time': timezone.now()
                })
        
        return results
    
    def _parse_user_answer(self, user_answer: Union[str, List], question_type: str) -> List[int]:
        """
        解析用户答案
        
        Args:
            user_answer: 用户答案
            question_type: 题目类型
            
        Returns:
            解析后的答案索引列表
        """
        if isinstance(user_answer, list):
            # 如果已经是列表，直接处理
            if all(isinstance(x, int) for x in user_answer):
                return sorted(user_answer)
            else:
                # 转换为索引
                return self._convert_to_indices(user_answer)
        
        if isinstance(user_answer, str):
            # 字符串格式处理
            user_answer = user_answer.strip()
            
            # JSON格式
            if user_answer.startswith('[') and user_answer.endswith(']'):
                try:
                    parsed = json.loads(user_answer)
                    return self._convert_to_indices(parsed)
                except json.JSONDecodeError:
                    pass
            
            # 逗号分隔格式 "A,C" 或 "0,2"
            if ',' in user_answer:
                parts = [part.strip() for part in user_answer.split(',')]
                return self._convert_to_indices(parts)
            
            # 单个答案
            return self._convert_to_indices([user_answer])
        
        return []
    
    def _convert_to_indices(self, answers: List[Union[str, int]]) -> List[int]:
        """
        将答案转换为索引列表
        
        Args:
            answers: 答案列表
            
        Returns:
            索引列表
        """
        indices = []
        
        for answer in answers:
            if isinstance(answer, int):
                indices.append(answer)
            elif isinstance(answer, str):
                answer = answer.strip().upper()
                
                # 字母格式 A, B, C...
                if len(answer) == 1 and answer.isalpha():
                    index = ord(answer) - ord('A')
                    if 0 <= index < 26:
                        indices.append(index)
                
                # 数字格式
                elif answer.isdigit():
                    index = int(answer)
                    # 支持1-based索引，转换为0-based
                    if index > 0:
                        indices.append(index - 1)
                    else:
                        indices.append(index)
        
        return sorted(list(set(indices)))  # 去重并排序
    
    def _parse_correct_answer(self, answer: str) -> List[int]:
        """
        解析正确答案
        
        Args:
            answer: 正确答案字符串
            
        Returns:
            正确答案索引列表
        """
        try:
            # 尝试JSON格式
            if answer.startswith('[') and answer.endswith(']'):
                return json.loads(answer)
            
            # 使用_convert_to_indices方法来解析答案
            if ',' in answer:
                # 多选答案格式 "A,B,C"
                parts = [part.strip() for part in answer.split(',')]
                return self._convert_to_indices(parts)
            else:
                # 单选答案格式 "A"
                return self._convert_to_indices([answer.strip()])
            
        except Exception:
            return []
    
    def _compare_answers(self, user_answer: List[int], correct_answer: List[int], 
                       question_type: str) -> bool:
        """
        比较用户答案和正确答案
        
        Args:
            user_answer: 用户答案索引列表
            correct_answer: 正确答案索引列表
            question_type: 题目类型
            
        Returns:
            是否正确
        """
        if question_type == 'single':
            # 单选题：只能选择一个答案
            if len(user_answer) != 1:
                return False
            return user_answer == correct_answer
        
        elif question_type == 'multiple':
            # 多选题：必须完全匹配
            return sorted(user_answer) == sorted(correct_answer)
        
        return False
    
    def _calculate_score(self, is_correct: bool, max_score: int, question_type: str,
                        user_answer: List[int], correct_answer: List[int]) -> int:
        """
        计算得分
        
        Args:
            is_correct: 是否完全正确
            max_score: 满分
            question_type: 题目类型
            user_answer: 用户答案
            correct_answer: 正确答案
            
        Returns:
            得分
        """
        if is_correct:
            return max_score
        
        # 对于多选题，可以实现部分得分逻辑
        if question_type == 'multiple' and len(correct_answer) > 1:
            # 计算部分得分：正确选项数 / 总选项数 * 满分
            correct_selections = set(user_answer) & set(correct_answer)
            wrong_selections = set(user_answer) - set(correct_answer)
            
            # 如果有错误选择，不给分
            if wrong_selections:
                return 0
            
            # 如果没有错误选择，按正确比例给分
            if correct_selections:
                partial_score = (len(correct_selections) / len(correct_answer)) * max_score
                return int(partial_score)
        
        return 0
    
    def _save_submission(self, question: ChoiceQuestion, user, user_answer: List[int], 
                        is_correct: bool, score: int):
        """
        保存提交记录
        
        Args:
            question: 题目对象
            user: 用户对象
            user_answer: 用户答案
            is_correct: 是否正确
            score: 得分
        """
        try:
            submission = ChoiceQuestionSubmission.objects.create(
                question=question,
                user=user,
                user_answer=json.dumps(user_answer),
                is_correct=is_correct,
                score=score,
                submit_time=timezone.now()
            )
            
            # 更新题目统计信息
            question.total_submissions += 1
            if is_correct:
                question.correct_submissions += 1
            question.save(update_fields=['total_submissions', 'correct_submissions'])
            
            return submission
            
        except Exception as e:
            # 记录错误但不影响判题结果
            print(f"保存提交记录失败: {str(e)}")
            return None
    
    def get_answer_analysis(self, question: ChoiceQuestion) -> Dict[str, Any]:
        """
        获取答案分析统计
        
        Args:
            question: 题目对象
            
        Returns:
            答案分析数据
        """
        try:
            options = json.loads(question.options) if question.options else []
            correct_answer = self._parse_correct_answer(question.answer)
            
            # 统计各选项的选择情况
            submissions = ChoiceQuestionSubmission.objects.filter(question=question)
            
            option_stats = {}
            for i, option in enumerate(options):
                option_stats[i] = {
                    'option_text': option,
                    'selection_count': 0,
                    'selection_rate': 0.0,
                    'is_correct': i in correct_answer
                }
            
            total_submissions = submissions.count()
            if total_submissions > 0:
                for submission in submissions:
                    try:
                        user_answer = json.loads(submission.user_answer)
                        for answer_index in user_answer:
                            if answer_index in option_stats:
                                option_stats[answer_index]['selection_count'] += 1
                    except (json.JSONDecodeError, TypeError):
                        continue
                
                # 计算选择率
                for stats in option_stats.values():
                    stats['selection_rate'] = (stats['selection_count'] / total_submissions) * 100
            
            return {
                'question_id': question.id,
                'total_submissions': total_submissions,
                'correct_submissions': question.correct_submissions,
                'accuracy_rate': (question.correct_submissions / total_submissions * 100) if total_submissions > 0 else 0,
                'option_analysis': option_stats,
                'difficulty_assessment': self._assess_difficulty(question.correct_submissions, total_submissions)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'question_id': question.id
            }
    
    def _assess_difficulty(self, correct_count: int, total_count: int) -> str:
        """
        评估题目难度
        
        Args:
            correct_count: 正确次数
            total_count: 总次数
            
        Returns:
            难度评估
        """
        if total_count == 0:
            return 'unknown'
        
        accuracy_rate = correct_count / total_count
        
        if accuracy_rate >= 0.8:
            return 'easy'
        elif accuracy_rate >= 0.5:
            return 'medium'
        else:
            return 'hard'