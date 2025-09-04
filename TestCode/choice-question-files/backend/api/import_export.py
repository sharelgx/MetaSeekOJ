from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from utils.api import APIView as BaseAPIView, validate_serializer
from account.decorators import login_required
# 移除错误的导入，使用继承的self.success和self.error方法
from ..models import ChoiceQuestion
from ..serializers import ChoiceQuestionDetailSerializer
from ..utils.importer import QuestionImporter
from ..utils.exporter import QuestionExporter
from django.db.models import Q
import os
import tempfile


class QuestionImportAPI(BaseAPIView):
    """
    题目导入API
    支持Excel、JSON格式的题目批量导入
    """
    parser_classes = [MultiPartParser, FormParser]
    
    @login_required
    def post(self, request):
        """
        导入题目
        
        参数:
        - file: 上传的文件
        - format: 文件格式 (excel/json)
        - sheet_name: Excel工作表名称(可选)
        - overwrite: 是否覆盖已存在的题目
        """
        file_obj = request.FILES.get('file')
        if not file_obj:
            return self.error("请上传文件")
        
        file_format = request.data.get('format', 'excel')
        sheet_name = request.data.get('sheet_name')
        overwrite = request.data.get('overwrite', False)
        
        # 保存临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_format}')
        try:
            for chunk in file_obj.chunks():
                temp_file.write(chunk)
            temp_file.close()
            
            # 执行导入
            importer = QuestionImporter(user=request.user)
            
            if file_format == 'excel':
                result = importer.import_from_excel(temp_file.name, sheet_name)
            elif file_format == 'json':
                result = importer.import_from_json(temp_file.name)
            else:
                return self.error("不支持的文件格式")
            
            return self.success(result)
            
        except Exception as e:
            return self.error(f"导入失败: {str(e)}")
        finally:
            # 清理临时文件
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)


class QuestionExportAPI(BaseAPIView):
    """
    题目导出API
    支持Excel、JSON、CSV格式的题目批量导出
    """
    
    @login_required
    def get(self, request):
        """
        导出题目
        
        参数:
        - format: 导出格式 (excel/json/csv)
        - category_id: 分类ID
        - difficulty: 难度
        - question_type: 题目类型
        - tags: 标签(逗号分隔)
        - is_public: 是否公开
        - keyword: 关键词搜索
        - ids: 指定题目ID(逗号分隔)
        """
        export_format = request.GET.get('format', 'excel')
        
        # 构建查询条件
        queryset = ChoiceQuestion.objects.all()
        
        # 如果指定了题目ID，只导出指定题目
        ids = request.GET.get('ids')
        if ids:
            id_list = [int(id.strip()) for id in ids.split(',') if id.strip().isdigit()]
            queryset = queryset.filter(id__in=id_list)
        else:
            # 应用筛选条件
            category_id = request.GET.get('category_id')
            if category_id:
                queryset = queryset.filter(category_id=category_id)
            
            difficulty = request.GET.get('difficulty')
            if difficulty:
                queryset = queryset.filter(difficulty=difficulty)
            
            question_type = request.GET.get('question_type')
            if question_type:
                queryset = queryset.filter(question_type=question_type)
            
            tags = request.GET.get('tags')
            if tags:
                tag_list = [tag.strip() for tag in tags.split(',')]
                for tag in tag_list:
                    queryset = queryset.filter(tags__contains=tag)
            
            is_public = request.GET.get('is_public')
            if is_public is not None:
                queryset = queryset.filter(is_public=is_public.lower() == 'true')
            
            keyword = request.GET.get('keyword')
            if keyword:
                queryset = queryset.filter(
                    Q(title__icontains=keyword) | 
                    Q(content__icontains=keyword)
                )
        
        # 权限检查：非管理员只能导出自己创建的题目
        if not request.user.is_admin_role():
            queryset = queryset.filter(created_by=request.user)
        
        # 执行导出
        exporter = QuestionExporter()
        
        try:
            if export_format == 'excel':
                return exporter.export_to_excel(queryset)
            elif export_format == 'json':
                return exporter.export_to_json(queryset)
            elif export_format == 'csv':
                return exporter.export_to_csv(queryset)
            else:
                return self.error("不支持的导出格式")
        except Exception as e:
            return self.error(f"导出失败: {str(e)}")


class QuestionTemplateAPI(BaseAPIView):
    """
    题目模板下载API
    提供导入模板文件下载
    """
    
    def get(self, request):
        """
        下载导入模板
        
        参数:
        - format: 模板格式 (excel/csv)
        """
        template_format = request.GET.get('format', 'excel')
        
        exporter = QuestionExporter()
        
        try:
            return exporter.export_template(template_format)
        except Exception as e:
            return self.error(f"模板下载失败: {str(e)}")


class ImportHistoryAPI(BaseAPIView):
    """
    导入历史记录API
    """
    
    @login_required
    def get(self, request):
        """
        获取导入历史记录
        
        参数:
        - page: 页码
        - limit: 每页数量
        """
        # 这里可以实现导入历史记录的存储和查询
        # 暂时返回空数据
        return self.success({
            'results': [],
            'total': 0
        })


class BatchOperationAPI(BaseAPIView):
    """
    批量操作API
    支持批量删除、批量修改状态等操作
    """
    
    @login_required
    def post(self, request):
        """
        批量操作题目
        
        参数:
        - action: 操作类型 (delete/set_public/set_private/set_visible/set_hidden)
        - question_ids: 题目ID列表
        """
        action = request.data.get('action')
        question_ids = request.data.get('question_ids', [])
        
        if not action or not question_ids:
            return error_response("参数不完整")
        
        # 权限检查：非管理员只能操作自己创建的题目
        queryset = ChoiceQuestion.objects.filter(id__in=question_ids)
        if not request.user.is_admin_role():
            queryset = queryset.filter(created_by=request.user)
        
        affected_count = queryset.count()
        if affected_count == 0:
            return error_response("没有找到可操作的题目")
        
        try:
            if action == 'delete':
                queryset.delete()
            elif action == 'set_public':
                queryset.update(is_public=True)
            elif action == 'set_private':
                queryset.update(is_public=False)
            elif action == 'set_visible':
                queryset.update(visible=True)
            elif action == 'set_hidden':
                queryset.update(visible=False)
            elif action == 'update_difficulty':
                # 批量更新难度
                params = request.data.get('params', {})
                difficulty = params.get('difficulty')
                if not difficulty or difficulty not in ['Easy', 'Medium', 'Hard']:
                    return self.error("无效的难度值")
                queryset.update(difficulty=difficulty)
            elif action == 'update_language':
                # 批量更新编程语言
                params = request.data.get('params', {})
                language = params.get('language')
                if not language:
                    return self.error("编程语言不能为空")
                queryset.update(language=language)
            elif action == 'update':
                # 通用批量更新
                params = request.data.get('params', {})
                if not params:
                    return self.error("更新参数不能为空")
                queryset.update(**params)
            else:
                return self.error("不支持的操作类型")
            
            return self.success({
                'affected_count': affected_count,
                'message': f'成功{action} {affected_count} 道题目'
            })
            
        except Exception as e:
            return self.error(f"批量操作失败: {str(e)}")