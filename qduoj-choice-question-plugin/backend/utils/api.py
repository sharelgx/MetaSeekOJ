# Mock utils.api for testing
from rest_framework.views import APIView as DRFAPIView
from rest_framework.response import Response
from rest_framework import status
from functools import wraps

class APIView(DRFAPIView):
    """Mock APIView for testing"""
    
    def success(self, data=None, msg="success"):
        """返回成功响应"""
        return Response({
            "error": None,
            "data": data,
            "msg": msg
        }, status=status.HTTP_200_OK)
    
    def error(self, msg="error", err=None, status_code=None):
        """返回错误响应"""
        if status_code is None:
            status_code = status.HTTP_400_BAD_REQUEST
        return Response({
            "error": err or msg,
            "data": None,
            "msg": msg
        }, status=status_code)
    
    def success_no_content(self):
        """返回204无内容响应"""
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def paginate_data(self, request, queryset, serializer_class):
        """分页数据"""
        # 简单的分页实现
        page_size = int(request.GET.get('limit', 20))
        page = int(request.GET.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        items = list(queryset[start:end])
        total = queryset.count() if hasattr(queryset, 'count') else len(queryset)
        
        return {
            'results': serializer_class(items, many=True).data,
            'total': total,
            'page': page,
            'limit': page_size
        }

def validate_serializer(serializer_class):
    """Mock validate_serializer decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator