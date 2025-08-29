import json
import uuid
import hashlib
import random
import string
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from django.utils import timezone
from django.conf import settings


def generate_question_id(prefix: str = 'CQ') -> str:
    """
    生成唯一的题目ID
    
    Args:
        prefix: ID前缀
        
    Returns:
        唯一的题目ID
    """
    timestamp = int(timezone.now().timestamp() * 1000)
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{timestamp}{random_str}"


def generate_short_id(length: int = 8) -> str:
    """
    生成短ID
    
    Args:
        length: ID长度
        
    Returns:
        短ID字符串
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_hash_id(content: str, length: int = 16) -> str:
    """
    基于内容生成哈希ID
    
    Args:
        content: 内容字符串
        length: 哈希长度
        
    Returns:
        哈希ID
    """
    hash_obj = hashlib.sha256(content.encode('utf-8'))
    return hash_obj.hexdigest()[:length]


def format_options(options: Union[str, List[str]]) -> str:
    """
    格式化选项为JSON字符串
    
    Args:
        options: 选项数据（字符串或列表）
        
    Returns:
        JSON格式的选项字符串
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
    
    # 确保所有选项都是字符串
    formatted_options = [str(opt).strip() for opt in options_list if str(opt).strip()]
    
    return json.dumps(formatted_options, ensure_ascii=False)


def parse_options(options_json: str) -> List[str]:
    """
    解析选项JSON字符串
    
    Args:
        options_json: JSON格式的选项字符串
        
    Returns:
        选项列表
    """
    try:
        return json.loads(options_json) if options_json else []
    except json.JSONDecodeError:
        return []


def format_answer(answer: Union[str, List[int], int]) -> str:
    """
    格式化答案为JSON字符串
    
    Args:
        answer: 答案数据（字符串、列表或整数）
        
    Returns:
        JSON格式的答案字符串
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
    
    # 确保所有答案都是整数
    formatted_answer = [int(ans) for ans in answer_list if isinstance(ans, (int, str)) and str(ans).isdigit()]
    
    return json.dumps(formatted_answer)


def parse_answer(answer_json: str) -> List[int]:
    """
    解析答案JSON字符串
    
    Args:
        answer_json: JSON格式的答案字符串
        
    Returns:
        答案索引列表
    """
    try:
        return json.loads(answer_json) if answer_json else []
    except json.JSONDecodeError:
        return []


def calculate_difficulty(accuracy_rate: float) -> str:
    """
    根据正确率计算题目难度
    
    Args:
        accuracy_rate: 正确率（0-100）
        
    Returns:
        难度等级（easy/medium/hard）
    """
    if accuracy_rate >= 80:
        return 'easy'
    elif accuracy_rate >= 50:
        return 'medium'
    else:
        return 'hard'


def calculate_score(is_correct: bool, base_score: int, difficulty: str = 'medium') -> int:
    """
    计算得分
    
    Args:
        is_correct: 是否正确
        base_score: 基础分数
        difficulty: 难度等级
        
    Returns:
        实际得分
    """
    if not is_correct:
        return 0
    
    # 根据难度调整分数
    difficulty_multiplier = {
        'easy': 1.0,
        'medium': 1.2,
        'hard': 1.5
    }
    
    multiplier = difficulty_multiplier.get(difficulty, 1.0)
    return int(base_score * multiplier)


def format_time_duration(seconds: int) -> str:
    """
    格式化时间长度
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时间字符串
    """
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}分{remaining_seconds}秒"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}小时{remaining_minutes}分钟"


def parse_time_duration(duration_str: str) -> int:
    """
    解析时间长度字符串为秒数
    
    Args:
        duration_str: 时间字符串（如"1分30秒"）
        
    Returns:
        总秒数
    """
    import re
    
    total_seconds = 0
    
    # 匹配小时
    hours_match = re.search(r'(\d+)小时', duration_str)
    if hours_match:
        total_seconds += int(hours_match.group(1)) * 3600
    
    # 匹配分钟
    minutes_match = re.search(r'(\d+)分', duration_str)
    if minutes_match:
        total_seconds += int(minutes_match.group(1)) * 60
    
    # 匹配秒
    seconds_match = re.search(r'(\d+)秒', duration_str)
    if seconds_match:
        total_seconds += int(seconds_match.group(1))
    
    return total_seconds


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    import re
    
    # 移除或替换非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # 移除控制字符
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # 限制长度
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:200-len(ext)-1] + '.' + ext if ext else name[:200]
    
    return filename.strip()


def get_client_ip(request) -> str:
    """
    获取客户端IP地址
    
    Args:
        request: Django请求对象
        
    Returns:
        IP地址字符串
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    
    return ip


def get_user_agent(request) -> str:
    """
    获取用户代理字符串
    
    Args:
        request: Django请求对象
        
    Returns:
        用户代理字符串
    """
    return request.META.get('HTTP_USER_AGENT', '')[:500]  # 限制长度


def paginate_queryset(queryset, page: int, page_size: int = 20) -> Dict[str, Any]:
    """
    分页查询集
    
    Args:
        queryset: Django查询集
        page: 页码（从1开始）
        page_size: 每页大小
        
    Returns:
        分页结果字典
    """
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    paginator = Paginator(queryset, page_size)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return {
        'items': list(page_obj.object_list),
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None
        }
    }


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化的文件大小字符串
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def generate_export_filename(prefix: str, format_type: str) -> str:
    """
    生成导出文件名
    
    Args:
        prefix: 文件名前缀
        format_type: 文件格式（excel/json/csv）
        
    Returns:
        文件名
    """
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    
    extensions = {
        'excel': 'xlsx',
        'json': 'json',
        'csv': 'csv'
    }
    
    ext = extensions.get(format_type, 'txt')
    filename = f"{prefix}_{timestamp}.{ext}"
    
    return sanitize_filename(filename)


def validate_json_field(value: str, field_name: str = 'field') -> bool:
    """
    验证JSON字段格式
    
    Args:
        value: JSON字符串
        field_name: 字段名称（用于错误信息）
        
    Returns:
        是否有效
    """
    if not value:
        return True
    
    try:
        json.loads(value)
        return True
    except json.JSONDecodeError:
        return False


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并多个字典
    
    Args:
        *dicts: 要合并的字典
        
    Returns:
        合并后的字典
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def safe_int(value: Any, default: int = 0) -> int:
    """
    安全转换为整数
    
    Args:
        value: 要转换的值
        default: 默认值
        
    Returns:
        整数值
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    安全转换为浮点数
    
    Args:
        value: 要转换的值
        default: 默认值
        
    Returns:
        浮点数值
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        截断后的文本
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def get_random_questions(queryset, count: int, exclude_ids: Optional[List[int]] = None) -> List:
    """
    随机获取题目
    
    Args:
        queryset: 题目查询集
        count: 数量
        exclude_ids: 排除的ID列表
        
    Returns:
        随机题目列表
    """
    if exclude_ids:
        queryset = queryset.exclude(id__in=exclude_ids)
    
    # 获取总数
    total_count = queryset.count()
    if total_count == 0:
        return []
    
    # 如果请求数量大于等于总数，返回所有
    if count >= total_count:
        return list(queryset.order_by('?'))
    
    # 随机选择
    return list(queryset.order_by('?')[:count])


def build_tree_structure(items: List[Dict], parent_field: str = 'parent_id', id_field: str = 'id') -> List[Dict]:
    """
    构建树形结构
    
    Args:
        items: 项目列表
        parent_field: 父级字段名
        id_field: ID字段名
        
    Returns:
        树形结构列表
    """
    # 创建ID到项目的映射
    item_map = {item[id_field]: item for item in items}
    
    # 为每个项目添加children字段
    for item in items:
        item['children'] = []
    
    # 构建树形结构
    root_items = []
    for item in items:
        parent_id = item.get(parent_field)
        if parent_id and parent_id in item_map:
            item_map[parent_id]['children'].append(item)
        else:
            root_items.append(item)
    
    return root_items