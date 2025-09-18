from django.contrib import admin
from .models import Problem, ProblemTag


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('_id', 'title', 'difficulty', 'is_public', 'visible', 'created_by', 'create_time')
    list_filter = ('difficulty', 'is_public', 'visible', 'rule_type', 'create_time')
    search_fields = ('_id', 'title', 'source')
    readonly_fields = ('create_time', 'last_update_time', 'submission_number', 'accepted_number')
    filter_horizontal = ('tags',)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('_id', 'title', 'difficulty', 'source', 'tags')
        }),
        ('题目内容', {
            'fields': ('description', 'input_description', 'output_description', 'samples', 'hint')
        }),
        ('配置', {
            'fields': ('is_public', 'visible', 'rule_type', 'time_limit', 'memory_limit', 'io_mode')
        }),
        ('测试用例', {
            'fields': ('test_case_id', 'test_case_score')
        }),
        ('特殊判题', {
            'fields': ('spj', 'spj_language', 'spj_code', 'spj_compile_ok')
        }),
        ('模板和语言', {
            'fields': ('languages', 'template')
        }),
        ('统计信息', {
            'fields': ('submission_number', 'accepted_number', 'total_score', 'statistic_info', 'share_submission')
        }),
        ('时间信息', {
            'fields': ('create_time', 'last_update_time', 'created_by')
        })
    )


@admin.register(ProblemTag)
class ProblemTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)