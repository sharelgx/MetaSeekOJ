#!/bin/bash

# 青岛OJ选择题插件卸载脚本
# 使用方法: ./uninstall.sh [QDUOJ_PATH] [QDUOJ_FE_PATH]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"

# 默认路径
DEFAULT_QDUOJ_PATH="/home/metaspeekoj/OnlineJudge"
DEFAULT_QDUOJ_FE_PATH="/home/metaspeekoj/OnlineJudgeFE"

# 获取参数
QDUOJ_PATH="${1:-$DEFAULT_QDUOJ_PATH}"
QDUOJ_FE_PATH="${2:-$DEFAULT_QDUOJ_FE_PATH}"

log_info "青岛OJ选择题插件卸载程序"
log_info "插件目录: $PLUGIN_DIR"
log_info "后端目录: $QDUOJ_PATH"
log_info "前端目录: $QDUOJ_FE_PATH"

# 检查目录是否存在
if [ ! -d "$QDUOJ_PATH" ]; then
    log_error "青岛OJ后端目录不存在: $QDUOJ_PATH"
    exit 1
fi

if [ ! -d "$QDUOJ_FE_PATH" ]; then
    log_error "青岛OJ前端目录不存在: $QDUOJ_FE_PATH"
    exit 1
fi

# 警告用户
log_warning "警告: 卸载插件将删除所有选择题相关的数据和文件！"
log_warning "建议在卸载前备份重要数据。"
echo ""

# 询问是否保留数据
read -p "是否保留数据库中的选择题数据? (y/N): " -n 1 -r
echo
KEEP_DATA=false
if [[ $REPLY =~ ^[Yy]$ ]]; then
    KEEP_DATA=true
    log_info "将保留数据库数据"
else
    log_warning "将删除所有数据库数据"
fi

# 确认卸载
read -p "确定要卸载选择题插件吗? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "卸载已取消"
    exit 0
fi

log_info "开始卸载选择题插件..."

# 1. 备份数据（如果需要）
if [ "$KEEP_DATA" = true ]; then
    log_info "备份选择题数据..."
    BACKUP_DIR="$PLUGIN_DIR/backup/uninstall_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    cd "$QDUOJ_PATH"
    python3 manage.py dumpdata choice_question > "$BACKUP_DIR/choice_question_data.json"
    log_success "数据备份完成: $BACKUP_DIR/choice_question_data.json"
fi

# 2. 移除前端文件
log_info "移除前端文件..."
FE_CHOICE_DIR="$QDUOJ_FE_PATH/src/pages/oj/views/choice-question"
if [ -d "$FE_CHOICE_DIR" ]; then
    rm -rf "$FE_CHOICE_DIR"
    log_success "前端文件已删除"
else
    log_warning "前端目录不存在: $FE_CHOICE_DIR"
fi

# 3. 移除后端配置
log_info "移除后端配置..."

# 从 INSTALLED_APPS 移除
SETTINGS_FILE="$QDUOJ_PATH/oj/settings.py"
if [ -f "$SETTINGS_FILE" ]; then
    if grep -q "choice_question" "$SETTINGS_FILE"; then
        sed -i "/^[[:space:]]*'choice_question',/d" "$SETTINGS_FILE"
        log_success "已从 INSTALLED_APPS 移除 choice_question"
    else
        log_warning "choice_question 不在 INSTALLED_APPS 中"
    fi
fi

# 从 URL 配置移除
URLS_FILE="$QDUOJ_PATH/oj/urls.py"
if [ -f "$URLS_FILE" ]; then
    if grep -q "choice-question" "$URLS_FILE"; then
        sed -i "/choice-question/d" "$URLS_FILE"
        log_success "已移除选择题模块路由"
    else
        log_warning "选择题模块路由不存在"
    fi
fi

# 4. 处理数据库
if [ "$KEEP_DATA" = false ]; then
    log_info "删除数据库表..."
    cd "$QDUOJ_PATH"
    
    # 删除数据库表
    python3 manage.py shell << EOF
import django
from django.db import connection

tables_to_drop = [
    'choice_question_choicequestioncategory',
    'choice_question_choicequestiontag',
    'choice_question_choicequestion_tags',
    'choice_question_choicequestion',
    'choice_question_choicequestionsubmission',
    'choice_question_wrongquestion'
]

with connection.cursor() as cursor:
    for table in tables_to_drop:
        try:
            cursor.execute(f'DROP TABLE IF EXISTS {table};')
            print(f'删除表: {table}')
        except Exception as e:
            print(f'删除表 {table} 失败: {e}')

print('数据库表删除完成')
EOF
    
    # 删除迁移文件
    MIGRATIONS_DIR="$QDUOJ_PATH/choice_question/migrations"
    if [ -d "$MIGRATIONS_DIR" ]; then
        find "$MIGRATIONS_DIR" -name "*.py" ! -name "__init__.py" -delete
        log_success "迁移文件已删除"
    fi
    
    log_success "数据库清理完成"
else
    log_info "跳过数据库删除（数据已备份）"
fi

# 5. 删除后端文件
log_info "删除后端文件..."
BACKEND_DIR="$QDUOJ_PATH/choice_question"
if [ -d "$BACKEND_DIR" ]; then
    rm -rf "$BACKEND_DIR"
    log_success "后端文件已删除"
else
    log_warning "后端目录不存在: $BACKEND_DIR"
fi

# 6. 清理缓存
log_info "清理缓存..."
cd "$QDUOJ_PATH"
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
log_success "缓存清理完成"

# 7. 卸载完成
log_success "选择题插件卸载完成！"
log_info "请按以下步骤完成清理:"
echo "1. 重启Django服务器"
echo "2. 重新构建前端项目"
echo "3. 检查并清理相关权限配置"
echo "4. 清理前端路由配置（如果手动添加过）"
echo ""

if [ "$KEEP_DATA" = true ]; then
    log_info "数据备份位置: $BACKUP_DIR/choice_question_data.json"
    log_info "如需恢复数据，请使用: python3 manage.py loaddata choice_question_data.json"
fi

log_info "感谢使用青岛OJ选择题插件！"