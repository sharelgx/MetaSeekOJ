from django.contrib import admin
from .models import ChoiceQuestionCategory, ChoiceQuestionTag, ChoiceQuestion, ChoiceQuestionSubmission, WrongQuestion


@admin.register(ChoiceQuestionCategory)
class ChoiceQuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_time')
    search_fields = ('name', 'description')
    list_filter = ('created_time',)
    ordering = ('name',)


@admin.register(ChoiceQuestionTag)
class ChoiceQuestionTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_time')
    search_fields = ('name',)
    list_filter = ('created_time',)
    ordering = ('name',)


@admin.register(ChoiceQuestion)
class ChoiceQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'difficulty', 'question_type', 'score', 'created_by', 'created_time')
    list_filter = ('category', 'difficulty', 'question_type', 'created_time')
    search_fields = ('title', 'content')
    filter_horizontal = ('tags',)
    readonly_fields = ('created_time', 'last_update_time')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'category', 'tags', 'difficulty', 'question_type', 'score')
        }),
        ('题目内容', {
            'fields': ('content', 'options', 'correct_answer', 'explanation')
        }),
        ('创建信息', {
            'fields': ('created_by', 'created_time', 'last_update_time'),
            'classes': ('collapse',)
        })
    )


@admin.register(ChoiceQuestionSubmission)
class ChoiceQuestionSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question', 'selected_answer', 'is_correct', 'score', 'submit_time')
    list_filter = ('is_correct', 'submit_time', 'question__category', 'question__difficulty')
    search_fields = ('user__username', 'question__title')
    readonly_fields = ('submit_time',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(WrongQuestion)
class WrongQuestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'wrong_count', 'added_time', 'last_wrong_time')
    list_filter = ('added_time', 'last_wrong_time', 'question__category', 'question__difficulty')
    search_fields = ('user__username', 'question__title', 'note')
    readonly_fields = ('added_time', 'last_wrong_time')
    
    def has_add_permission(self, request):
        return False