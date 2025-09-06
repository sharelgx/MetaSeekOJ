import json
import re
from typing import Dict, List, Any, Optional, Tuple
from cerberus import Validator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class QuestionValidator:
    """
    题目验证工具类
    提供题目数据验证和格式化功能
    """
    
    def __init__(self):
        self.validator = Validator()
        self.question_schema = self._get_question_schema()
        self.batch_schema = self._get_batch_schema()
    
    def validate_question(self, question_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证单个题目数据
        
        Args:
            question_data: 题目数据字典
            
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 使用Cerberus进行基础验证
        if not self.validator.validate(question_data, self.question_schema):
            for field, field_errors in self.validator.errors.items():
                for error in field_errors:
                    errors.append(f"{field}: {error}")
        
        # 自定义验证逻辑
        custom_errors = self._validate_question_custom(question_data)
        errors.extend(custom_errors)
        
        return len(errors) == 0, errors
    
    def validate_batch_questions(self, questions_data: List[Dict[str, Any]]) -> Tuple[bool, Dict[int, List[str]]]:
        """
        批量验证题目数据
        
        Args:
            questions_data: 题目数据列表
            
        Returns:
            (是否全部有效, {索引: 错误信息列表})
        """
        all_valid = True
        errors_dict = {}
        
        for index, question_data in enumerate(questions_data):
            is_valid, errors = self.validate_question(question_data)
            if not is_valid:
                all_valid = False
                errors_dict[index] = errors
        
        # 批量验证特有的检查
        batch_errors = self._validate_batch_custom(questions_data)
        if batch_errors:
            all_valid = False
            errors_dict['batch'] = batch_errors
        
        return all_valid, errors_dict
    
    def validate_import_data(self, import_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证导入数据格式
        
        Args:
            import_data: 导入数据
            
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 验证基本结构
        if not isinstance(import_data, dict):
            errors.append("导入数据必须是字典格式")
            return False, errors
        
        # 验证必需字段
        required_fields = ['questions']
        for field in required_fields:
            if field not in import_data:
                errors.append(f"缺少必需字段: {field}")
        
        if errors:
            return False, errors
        
        # 验证题目列表
        questions = import_data.get('questions', [])
        if not isinstance(questions, list):
            errors.append("questions字段必须是列表格式")
            return False, errors
        
        if len(questions) == 0:
            errors.append("题目列表不能为空")
            return False, errors
        
        if len(questions) > 1000:
            errors.append("单次导入题目数量不能超过1000个")
        
        # 验证每个题目
        is_valid, question_errors = self.validate_batch_questions(questions)
        if not is_valid:
            for index, question_error_list in question_errors.items():
                if index == 'batch':
                    errors.extend(question_error_list)
                else:
                    errors.append(f"题目 {index + 1}: {'; '.join(question_error_list)}")
        
        return len(errors) == 0, errors
    
    def validate_question_data(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证单个题目数据
        
        Args:
            question_data: 题目数据
            
        Returns:
            包含验证结果的字典，格式为 {'is_valid': bool, 'errors': List[str]}
        """
        is_valid, errors = self.validate_question(question_data)
        return {
            'is_valid': is_valid,
            'errors': errors
        }
    
    def format_question_data(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化题目数据
        
        Args:
            question_data: 原始题目数据
            
        Returns:
            格式化后的题目数据
        """
        formatted_data = question_data.copy()
        
        # 格式化标题和描述
        if 'title' in formatted_data:
            formatted_data['title'] = self._clean_text(formatted_data['title'])
        
        if 'description' in formatted_data:
            formatted_data['description'] = self._clean_html(formatted_data['description'])
        
        # 格式化选项
        if 'options' in formatted_data:
            formatted_data['options'] = self._format_options(formatted_data['options'])
        
        # 格式化答案
        if 'answer' in formatted_data:
            formatted_data['answer'] = self._format_answer(formatted_data['answer'])
        
        # 格式化解析
        if 'explanation' in formatted_data:
            formatted_data['explanation'] = self._clean_html(formatted_data['explanation'])
        
        # 格式化标签
        if 'tags' in formatted_data:
            formatted_data['tags'] = self._format_tags(formatted_data['tags'])
        
        # 设置默认值
        formatted_data.setdefault('question_type', 'single')
        formatted_data.setdefault('difficulty', 'medium')
        formatted_data.setdefault('score', 1)
        formatted_data.setdefault('is_public', True)
        
        return formatted_data
    
    def _get_question_schema(self) -> Dict[str, Any]:
        """
        获取题目验证模式
        """
        return {
            'title': {
                'type': 'string',
                'required': True,
                'minlength': 1,
                'maxlength': 200,
                'empty': False
            },
            'description': {
                'type': 'string',
                'required': False,
                'maxlength': 5000
            },
            'question': {  # 支持新的JSON格式中的question字段
                'type': 'string',
                'required': False,  # 可选，因为有title字段
                'minlength': 1,
                'maxlength': 2000
            },
            'question_type': {
                'type': 'string',
                'required': False,  # 可选，因为可以从type字段获取
                'allowed': ['single', 'multiple']
            },
            'type': {  # 支持新的JSON格式
                'type': 'string',
                'required': False,
                'allowed': ['single', 'multiple']
            },
            'options': {
                'type': ['string', 'list'],
                'required': True
            },
            'answer': {
                'type': ['string', 'list'],
                'required': False  # correct字段也可以作为答案
            },
            'correct': {  # 支持新的JSON格式中的correct字段
                'type': ['string', 'list'],
                'required': False
            },
            'explanation': {
                'type': 'string',
                'required': False,
                'maxlength': 2000
            },
            'difficulty': {
                'type': 'string',
                'required': False,
                'allowed': ['easy', 'medium', 'hard']
            },
            'score': {
                'type': 'integer',
                'required': False,
                'min': 1,
                'max': 100
            },
            'category': {
                'type': 'string',
                'required': False
            },
            'tags': {
                'type': ['string', 'list'],
                'required': False
            },
            'is_public': {
                'type': 'boolean',
                'required': False
            },
            'row_num': {
                'type': 'integer',
                'required': False
            }
        }
    
    def _get_batch_schema(self) -> Dict[str, Any]:
        """
        获取批量导入验证模式
        """
        return {
            'questions': {
                'type': 'list',
                'required': True,
                'minlength': 1,
                'maxlength': 1000,
                'schema': self.question_schema
            },
            'metadata': {
                'type': 'dict',
                'required': False,
                'schema': {
                    'import_source': {'type': 'string'},
                    'import_time': {'type': 'string'},
                    'version': {'type': 'string'}
                }
            }
        }
    
    def _validate_question_custom(self, question_data: Dict[str, Any]) -> List[str]:
        """
        自定义题目验证逻辑
        """
        errors = []
        
        # 标准化数据格式（支持新的JSON格式）
        normalized_data = self._normalize_question_data(question_data)
        
        # 验证选项格式
        options = normalized_data.get('options')
        if options:
            options_errors = self._validate_options(options)
            errors.extend(options_errors)
        
        # 验证答案格式
        answer = normalized_data.get('answer')
        question_type = normalized_data.get('question_type', 'single')
        if answer:
            answer_errors = self._validate_answer(answer, question_type, options)
            errors.extend(answer_errors)
        
        # 验证标题唯一性（如果需要）
        title = normalized_data.get('title')
        if title:
            title_errors = self._validate_title(title)
            errors.extend(title_errors)
        
        return errors
    
    def _normalize_question_data(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化题目数据格式，支持新的JSON格式
        """
        normalized = question_data.copy()
        
        # 处理标题字段：优先使用title，如果没有则使用question
        if 'title' not in normalized and 'question' in normalized:
            normalized['title'] = normalized['question']
        
        # 处理题目类型字段：优先使用question_type，如果没有则使用type
        if 'question_type' not in normalized and 'type' in normalized:
            normalized['question_type'] = normalized['type']
        
        # 处理答案字段：优先使用answer，如果没有则使用correct
        if 'answer' not in normalized and 'correct' in normalized:
            normalized['answer'] = normalized['correct']
        
        # 设置默认值
        normalized.setdefault('question_type', 'single')
        normalized.setdefault('difficulty', 'medium')
        normalized.setdefault('score', 2)
        
        return normalized
    
    def _validate_batch_custom(self, questions_data: List[Dict[str, Any]]) -> List[str]:
        """
        批量验证自定义逻辑
        """
        errors = []
        
        # 检查标题重复
        titles = [q.get('title', '') for q in questions_data]
        duplicate_titles = [title for title in set(titles) if titles.count(title) > 1 and title]
        
        if duplicate_titles:
            errors.append(f"发现重复标题: {', '.join(duplicate_titles)}")
        
        return errors
    
    def _validate_options(self, options) -> List[str]:
        """
        验证选项格式
        """
        errors = []
        
        # 转换为列表格式
        if isinstance(options, str):
            try:
                options_list = json.loads(options)
            except json.JSONDecodeError:
                # 尝试按行分割
                options_list = [opt.strip() for opt in options.split('\n') if opt.strip()]
        elif isinstance(options, list):
            options_list = options
        else:
            errors.append("选项格式无效，必须是字符串或列表")
            return errors
        
        # 验证选项数量
        if len(options_list) < 2:
            errors.append("至少需要2个选项")
        elif len(options_list) > 10:
            errors.append("选项数量不能超过10个")
        
        # 验证选项内容
        for i, option in enumerate(options_list):
            if not isinstance(option, str):
                errors.append(f"选项 {i + 1} 必须是字符串")
            elif not option.strip():
                errors.append(f"选项 {i + 1} 不能为空")
            elif len(option) > 500:
                errors.append(f"选项 {i + 1} 长度不能超过500字符")
        
        # 检查选项重复
        clean_options = [opt.strip().lower() for opt in options_list if isinstance(opt, str)]
        if len(clean_options) != len(set(clean_options)):
            errors.append("选项不能重复")
        
        return errors
    
    def _validate_answer(self, answer, question_type: str, options) -> List[str]:
        """
        验证答案格式
        """
        errors = []
        
        # 获取选项数量
        if isinstance(options, str):
            try:
                options_list = json.loads(options)
            except json.JSONDecodeError:
                options_list = [opt.strip() for opt in options.split('\n') if opt.strip()]
        elif isinstance(options, list):
            options_list = options
        else:
            options_list = []
        
        options_count = len(options_list)
        
        # 转换答案格式
        answer_list = []
        if isinstance(answer, str):
            try:
                parsed_answer = json.loads(answer)
                if isinstance(parsed_answer, list):
                    answer_list = parsed_answer
                else:
                    answer_list = [parsed_answer]
            except json.JSONDecodeError:
                # 尝试解析为索引
                try:
                    if ',' in answer:
                        answer_list = [int(x.strip()) for x in answer.split(',')]
                    else:
                        answer_list = [int(answer.strip())]
                except ValueError:
                    errors.append("答案格式无效")
                    return errors
        elif isinstance(answer, list):
            answer_list = answer
        elif isinstance(answer, int):
            answer_list = [answer]
        else:
            errors.append("答案格式无效，必须是字符串、列表或整数")
            return errors
        
        # 确保answer_list是列表
        if not isinstance(answer_list, list):
            answer_list = [answer_list]
        
        # 验证答案内容
        if not answer_list:
            errors.append("答案不能为空")
            return errors
        
        # 验证单选题答案
        if question_type == 'single' and len(answer_list) != 1:
            errors.append("单选题只能有一个正确答案")
        
        # 验证多选题答案
        if question_type == 'multiple' and len(answer_list) < 1:
            errors.append("多选题至少需要一个正确答案")
        
        # 验证答案索引范围
        for ans in answer_list:
            if not isinstance(ans, int):
                errors.append(f"答案索引必须是整数: {ans}")
            elif ans < 0 or ans >= options_count:
                errors.append(f"答案索引超出范围: {ans}，有效范围是 0-{options_count-1}")
        
        # 检查答案重复
        if len(answer_list) != len(set(answer_list)):
            errors.append("答案索引不能重复")
        
        return errors
    
    def _validate_title(self, title: str) -> List[str]:
        """
        验证标题
        """
        errors = []
        
        # 检查是否全是空白字符
        if not title.strip():
            errors.append("标题不能为空或只包含空白字符")
        
        # 如果包含<pre>标签，说明是代码块，放宽验证
        if '<pre>' in title and '</pre>' in title:
            # 对于代码块，只检查是否有恶意脚本标签
            if re.search(r'<script|</script|javascript:', title, re.IGNORECASE):
                errors.append("标题不能包含脚本代码")
        else:
            # 对于普通标题，检查危险字符
            allowed_tags = ['<code>', '</code>', '<br>', '<br/>']
            temp_title = title
            for tag in allowed_tags:
                temp_title = temp_title.replace(tag, '')
            
            if re.search(r'[<>"\\]', temp_title):
                errors.append("标题不能包含特殊字符 < > \" \\（除了允许的HTML标签）")
        
        return errors
    
    def _format_options(self, options) -> str:
        """
        格式化选项为JSON字符串
        """
        if isinstance(options, str):
            try:
                # 尝试解析为JSON
                options_list = json.loads(options)
            except json.JSONDecodeError:
                # 按行分割
                options_list = [opt.strip() for opt in options.split('\n') if opt.strip()]
        elif isinstance(options, list):
            options_list = options
        else:
            options_list = []
        
        # 清理选项文本
        cleaned_options = [self._clean_text(opt) for opt in options_list if opt]
        
        return json.dumps(cleaned_options, ensure_ascii=False)
    
    def _format_answer(self, answer) -> str:
        """
        格式化答案为JSON字符串
        """
        if isinstance(answer, str):
            try:
                answer_list = json.loads(answer)
            except json.JSONDecodeError:
                # 尝试解析为索引
                try:
                    if ',' in answer:
                        answer_list = [int(x.strip()) for x in answer.split(',')]
                    else:
                        answer_list = [int(answer.strip())]
                except ValueError:
                    answer_list = []
        elif isinstance(answer, list):
            answer_list = answer
        elif isinstance(answer, int):
            answer_list = [answer]
        else:
            answer_list = []
        
        return json.dumps(answer_list)
    
    def _format_tags(self, tags) -> List[str]:
        """
        格式化标签
        """
        if isinstance(tags, str):
            if tags.startswith('[') and tags.endswith(']'):
                try:
                    tags_list = json.loads(tags)
                except json.JSONDecodeError:
                    tags_list = [tags]
            else:
                # 按逗号或分号分割
                tags_list = [tag.strip() for tag in re.split(r'[,;，；]', tags) if tag.strip()]
        elif isinstance(tags, list):
            tags_list = tags
        else:
            tags_list = []
        
        # 清理标签文本
        cleaned_tags = []
        for tag in tags_list:
            if isinstance(tag, str):
                clean_tag = self._clean_text(tag)
                if clean_tag and len(clean_tag) <= 50:
                    cleaned_tags.append(clean_tag)
        
        return cleaned_tags
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本内容
        """
        if not isinstance(text, str):
            return str(text)
        
        # 移除首尾空白
        text = text.strip()
        
        # 替换多个空白字符为单个空格
        text = re.sub(r'\s+', ' ', text)
        
        # 移除危险字符
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text
    
    def _clean_html(self, html: str) -> str:
        """
        清理HTML内容
        """
        if not isinstance(html, str):
            return str(html)
        
        # 基础文本清理
        html = self._clean_text(html)
        
        # 移除危险的HTML标签和属性
        dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form', 'input']
        for tag in dangerous_tags:
            html = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', html, flags=re.IGNORECASE | re.DOTALL)
            html = re.sub(f'<{tag}[^>]*/?>', '', html, flags=re.IGNORECASE)
        
        # 移除危险属性
        html = re.sub(r'\s*on\w+\s*=\s*["\'][^"\'>]*["\']', '', html, flags=re.IGNORECASE)
        html = re.sub(r'\s*javascript\s*:', '', html, flags=re.IGNORECASE)
        
        return html