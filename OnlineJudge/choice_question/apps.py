from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class ChoiceQuestionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'choice_question'
    verbose_name = '选择题插件'
    
    def ready(self):
        """插件就绪时执行"""
        try:
            # 注册插件信号处理器
            self._register_signals()
            
            # 初始化插件配置
            self._init_plugin_config()
            
            logger.info(f"选择题插件 {self.verbose_name} 初始化完成")
        except Exception as e:
            logger.error(f"选择题插件初始化失败: {e}")
    
    def _register_signals(self):
        """注册信号处理器"""
        try:
            # 导入信号处理器（如果有的话）
            # from . import signals
            pass
        except ImportError:
            pass
    
    def _init_plugin_config(self):
        """初始化插件配置"""
        # 设置插件默认配置
        from django.conf import settings
        
        # 确保插件相关设置存在
        if not hasattr(settings, 'CHOICE_QUESTION_CONFIG'):
            settings.CHOICE_QUESTION_CONFIG = {
                'DEFAULT_CATEGORY': '默认分类',
                'MAX_OPTIONS': 6,
                'DEFAULT_DIFFICULTY': 1,
                'ENABLE_WRONG_BOOK': True,
                'ENABLE_STATISTICS': True
            }