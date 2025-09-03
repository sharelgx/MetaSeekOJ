# -*- coding: utf-8 -*-
"""
选择题插件工具模块
"""

from .importer import QuestionImporter
from .exporter import QuestionExporter
from .judge import ChoiceQuestionJudge
from .statistics import StatisticsCalculator
from .validator import QuestionValidator
from .helpers import (
    generate_question_id,
    generate_short_id,
    generate_hash_id,
    format_options,
    parse_options,
    format_answer,
    parse_answer,
    calculate_difficulty,
    calculate_score,
    format_time_duration,
    parse_time_duration,
    sanitize_filename,
    get_client_ip,
    get_user_agent,
    paginate_queryset,
    format_file_size,
    generate_export_filename,
    validate_json_field,
    merge_dicts,
    safe_int,
    safe_float,
    truncate_text,
    get_random_questions,
    build_tree_structure
)

__all__ = [
    'QuestionImporter',
    'QuestionExporter', 
    'ChoiceQuestionJudge',
    'StatisticsCalculator',
    'QuestionValidator',
    'generate_question_id',
    'generate_short_id',
    'generate_hash_id',
    'format_options',
    'parse_options',
    'format_answer',
    'parse_answer',
    'calculate_difficulty',
    'calculate_score',
    'format_time_duration',
    'parse_time_duration',
    'sanitize_filename',
    'get_client_ip',
    'get_user_agent',
    'paginate_queryset',
    'format_file_size',
    'generate_export_filename',
    'validate_json_field',
    'merge_dicts',
    'safe_int',
    'safe_float',
    'truncate_text',
    'get_random_questions',
    'build_tree_structure'
]