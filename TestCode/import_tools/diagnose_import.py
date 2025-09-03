#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入格式问题诊断脚本
用于分析和诊断选择题导入数据的格式问题
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional, Tuple

class ImportDiagnostic:
    """
    导入数据诊断工具
    """
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suggestions = []
    
    def diagnose_file(self, file_path: str) -> Dict[str, Any]:
        """
        诊断导入文件
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self.diagnose_data(data)
        except json.JSONDecodeError as e:
            return {
                'valid': False,
                'errors': [f'JSON格式错误: {str(e)}'],
                'warnings': [],
                'suggestions': ['请检查JSON格式是否正确，注意逗号、引号等语法']
            }
        except FileNotFoundError:
            return {
                'valid': False,
                'errors': [f'文件不存在: {file_path}'],
                'warnings': [],
                'suggestions': ['请确认文件路径是否正确']
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'读取文件失败: {str(e)}'],
                'warnings': [],
                'suggestions': ['请检查文件权限和编码格式']
            }
    
    def diagnose_data(self, data: Any) -> Dict[str, Any]:
        """
        诊断导入数据
        """
        self.errors = []
        self.warnings = []
        self.suggestions = []
        
        # 检查基本结构
        if not isinstance(data, dict):
            self.errors.append('导入数据必须是JSON对象格式')
            self.suggestions.append('请确保数据格式为: {"questions": [...], "category_id": 1}')
            return self._build_result()
        
        # 检查questions字段
        if 'questions' not in data:
            self.errors.append('缺少必需的questions字段')
            self.suggestions.append('请添加questions字段，包含题目数组')
            return self._build_result()
        
        questions = data['questions']
        if not isinstance(questions, list):
            self.errors.append('questions字段必须是数组格式')
            self.suggestions.append('请将questions设置为数组: "questions": [...]')
            return self._build_result()
        
        if len(questions) == 0:
            self.errors.append('questions数组不能为空')
            self.suggestions.append('请至少添加一个题目')
            return self._build_result()
        
        # 检查每个题目
        for i, question in enumerate(questions):
            self._diagnose_question(question, i + 1)
        
        # 检查可选字段
        if 'category_id' in data:
            category_id = data['category_id']
            if not isinstance(category_id, (int, type(None))):
                self.warnings.append('category_id应该是整数或null')
        
        return self._build_result()
    
    def _diagnose_question(self, question: Any, index: int) -> None:
        """
        诊断单个题目
        """
        prefix = f'题目{index}'
        
        if not isinstance(question, dict):
            self.errors.append(f'{prefix}: 题目必须是对象格式')
            return
        
        # 检查必填字段
        required_fields = {
            'question': '题目内容',
            'type': '题目类型',
            'options': '选项',
            'correct': '正确答案'
        }
        
        for field, desc in required_fields.items():
            if field not in question:
                self.errors.append(f'{prefix}: 缺少必填字段 {field} ({desc})')
            elif not question[field]:
                self.errors.append(f'{prefix}: {desc}不能为空')
        
        # 如果缺少必填字段，跳过后续检查
        missing_required = [f for f in required_fields if f not in question or not question[f]]
        if missing_required:
            self.suggestions.append(f'{prefix}: 请添加缺少的字段: {", ".join(missing_required)}')
            return
        
        # 检查题目类型
        question_type = question['type']
        if question_type not in ['single', 'multiple']:
            self.errors.append(f'{prefix}: 题目类型必须是"single"或"multiple"，当前为"{question_type}"')
            self.suggestions.append(f'{prefix}: 请将type设置为"single"（单选）或"multiple"（多选）')
        
        # 检查选项
        options = question['options']
        if not isinstance(options, list):
            self.errors.append(f'{prefix}: 选项必须是数组格式')
            self.suggestions.append(f'{prefix}: 请将options设置为数组: ["选项A", "选项B", ...]')
        elif len(options) < 2:
            self.errors.append(f'{prefix}: 至少需要2个选项，当前只有{len(options)}个')
            self.suggestions.append(f'{prefix}: 请添加更多选项')
        else:
            # 检查选项内容
            for j, option in enumerate(options):
                if not isinstance(option, str) or not option.strip():
                    self.errors.append(f'{prefix}: 选项{j+1}内容不能为空')
        
        # 检查正确答案
        correct = question['correct']
        if not isinstance(correct, str):
            self.errors.append(f'{prefix}: 正确答案必须是字符串格式')
            self.suggestions.append(f'{prefix}: 请将correct设置为字符串，如"A"或"A,B"')
        else:
            self._diagnose_correct_answer(correct, options, question_type, prefix)
        
        # 检查可选字段
        if 'explanation' in question and question['explanation'] and len(question['explanation']) > 1000:
            self.warnings.append(f'{prefix}: 解析内容过长（{len(question["explanation"])}字符），建议控制在1000字符以内')
        
        if 'id' in question and question['id'] and len(question['id']) > 50:
            self.warnings.append(f'{prefix}: ID过长，建议控制在50字符以内')
    
    def _diagnose_correct_answer(self, correct: str, options: List[str], question_type: str, prefix: str) -> None:
        """
        诊断正确答案格式
        """
        # 解析答案
        if ',' in correct:
            answers = [ans.strip().upper() for ans in correct.split(',')]
        else:
            answers = [correct.strip().upper()]
        
        # 检查答案格式
        for answer in answers:
            if not answer:
                self.errors.append(f'{prefix}: 正确答案不能为空')
                continue
            
            if len(answer) != 1 or not answer.isalpha():
                self.errors.append(f'{prefix}: 答案格式错误"{answer}"，应为A-Z的单个字母')
                self.suggestions.append(f'{prefix}: 请使用A、B、C等字母表示答案')
                continue
            
            # 检查答案是否在选项范围内
            answer_index = ord(answer) - ord('A')
            if answer_index >= len(options):
                self.errors.append(f'{prefix}: 答案"{answer}"超出选项范围（共{len(options)}个选项）')
                max_option = chr(ord('A') + len(options) - 1)
                self.suggestions.append(f'{prefix}: 答案应在A-{max_option}范围内')
        
        # 检查题目类型与答案数量的匹配
        if question_type == 'single' and len(answers) > 1:
            self.errors.append(f'{prefix}: 单选题只能有一个正确答案，当前有{len(answers)}个')
            self.suggestions.append(f'{prefix}: 请将type改为"multiple"或只保留一个正确答案')
        elif question_type == 'multiple' and len(answers) == 1:
            self.warnings.append(f'{prefix}: 多选题只有一个正确答案，建议确认题目类型')
    
    def _build_result(self) -> Dict[str, Any]:
        """
        构建诊断结果
        """
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'suggestions': self.suggestions
        }

def print_diagnosis_result(result: Dict[str, Any]) -> None:
    """
    打印诊断结果
    """
    print("\n" + "=" * 60)
    print("诊断结果")
    print("=" * 60)
    
    if result['valid']:
        print("✅ 数据格式正确，可以导入")
    else:
        print("❌ 数据格式有误，无法导入")
    
    if result['errors']:
        print("\n🚫 错误信息:")
        for i, error in enumerate(result['errors'], 1):
            print(f"  {i}. {error}")
    
    if result['warnings']:
        print("\n⚠️  警告信息:")
        for i, warning in enumerate(result['warnings'], 1):
            print(f"  {i}. {warning}")
    
    if result['suggestions']:
        print("\n💡 修改建议:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"  {i}. {suggestion}")

def main():
    """
    主函数
    """
    print("选择题导入格式诊断工具")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("使用方法: python diagnose_import.py <导入文件路径>")
        print("\n示例:")
        print("  python diagnose_import.py import_data.json")
        print("  python diagnose_import.py import_example.json")
        return
    
    file_path = sys.argv[1]
    
    # 如果是相对路径，转换为绝对路径
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
    
    diagnostic = ImportDiagnostic()
    result = diagnostic.diagnose_file(file_path)
    
    print_diagnosis_result(result)
    
    if not result['valid']:
        print("\n📋 标准格式示例:")
        example = {
            "questions": [
                {
                    "question": "题目内容",
                    "type": "single",
                    "options": ["选项A", "选项B", "选项C", "选项D"],
                    "correct": "A",
                    "explanation": "解析说明（可选）"
                }
            ],
            "category_id": 1
        }
        print(json.dumps(example, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()