#!/bin/bash

# 青岛OJ选择题插件安装脚本
# 使用方法: ./install.sh [QDUOJ_PATH] [QDUOJ_FE_PATH]

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

log_info "青岛OJ选择题插件安装程序"
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

# 检查必要文件
if [ ! -f "$QDUOJ_PATH/manage.py" ]; then
    log_error "无效的青岛OJ后端目录，未找到 manage.py"
    exit 1
fi

if [ ! -f "$QDUOJ_FE_PATH/package.json" ]; then
    log_error "无效的青岛OJ前端目录，未找到 package.json"
    exit 1
fi

# 确认安装
read -p "是否继续安装选择题插件? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "安装已取消"
    exit 0
fi

log_info "开始安装选择题插件..."

# 1. 备份现有配置
log_info "备份现有配置..."
BACKUP_DIR="$PLUGIN_DIR/backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f "$QDUOJ_PATH/oj/settings.py" ]; then
    cp "$QDUOJ_PATH/oj/settings.py" "$BACKUP_DIR/settings.py.bak"
fi

if [ -f "$QDUOJ_PATH/oj/urls.py" ]; then
    cp "$QDUOJ_PATH/oj/urls.py" "$BACKUP_DIR/urls.py.bak"
fi

log_success "配置备份完成: $BACKUP_DIR"

# 2. 安装后端
log_info "安装后端模块..."

# 复制后端文件
cp -r "$PLUGIN_DIR/backend/choice_question" "$QDUOJ_PATH/"
log_success "后端文件复制完成"

# 添加到 INSTALLED_APPS
SETTINGS_FILE="$QDUOJ_PATH/oj/settings.py"
if ! grep -q "choice_question" "$SETTINGS_FILE"; then
    # 在 INSTALLED_APPS 中添加应用
    sed -i "/INSTALLED_APPS = \[/a\    'choice_question'," "$SETTINGS_FILE"
    log_success "已添加 choice_question 到 INSTALLED_APPS"
else
    log_warning "choice_question 已存在于 INSTALLED_APPS 中"
fi

# 添加URL路由
URLS_FILE="$QDUOJ_PATH/oj/urls.py"
if ! grep -q "choice-question" "$URLS_FILE"; then
    # 在 urlpatterns 中添加路由
    sed -i "/urlpatterns = \[/a\    path('api/choice-question/', include('choice_question.urls'))," "$URLS_FILE"
    log_success "已添加选择题模块路由"
else
    log_warning "选择题模块路由已存在"
fi

# 3. 运行数据库迁移
log_info "运行数据库迁移..."
cd "$QDUOJ_PATH"
python3 manage.py makemigrations choice_question
python3 manage.py migrate
log_success "数据库迁移完成"

# 4. 安装前端
log_info "安装前端模块..."

# 创建前端目录
FE_CHOICE_DIR="$QDUOJ_FE_PATH/src/pages/oj/views/choice-question"
mkdir -p "$FE_CHOICE_DIR"

# 复制前端文件
cp -r "$PLUGIN_DIR/frontend/views/"* "$FE_CHOICE_DIR/"
cp -r "$PLUGIN_DIR/frontend/api" "$FE_CHOICE_DIR/"
cp -r "$PLUGIN_DIR/frontend/components" "$FE_CHOICE_DIR/"
log_success "前端文件复制完成"

# 5. 添加前端路由
ROUTER_FILE="$QDUOJ_FE_PATH/src/pages/oj/router/routes.js"
if [ -f "$ROUTER_FILE" ]; then
    if ! grep -q "choice-question" "$ROUTER_FILE"; then
        log_info "请手动添加以下路由到 $ROUTER_FILE:"
        echo ""
        echo "// 选择题模块路由"
        echo "{"
        echo "  name: 'choice-question-list',"
        echo "  path: '/choice-questions',"
        echo "  component: () => import('@oj/views/choice-question/ChoiceQuestionList.vue'),"
        echo "  meta: { title: '选择题练习', requiresAuth: true }"
        echo "},"
        echo "{"
        echo "  name: 'choice-question-detail',"
        echo "  path: '/choice-questions/:id',"
        echo "  component: () => import('@oj/views/choice-question/ChoiceQuestionDetail.vue'),"
        echo "  meta: { title: '选择题详情', requiresAuth: true }"
        echo "},"
        echo "{"
        echo "  name: 'wrong-question-book',"
        echo "  path: '/wrong-questions',"
        echo "  component: () => import('@oj/views/choice-question/WrongQuestionBook.vue'),"
        echo "  meta: { title: '错题本', requiresAuth: true }"
        echo "}"
        echo ""
    else
        log_warning "选择题路由可能已存在"
    fi
else
    log_warning "未找到路由文件: $ROUTER_FILE"
fi

# 6. 创建默认数据
log_info "创建默认数据..."
cd "$QDUOJ_PATH"
python3 manage.py shell << EOF
from choice_question.models import ChoiceQuestionCategory, ChoiceQuestionTag

# 创建默认分类
categories = [
    {'name': '算法基础', 'description': '基础算法题目'},
    {'name': '数据结构', 'description': '数据结构相关题目'},
    {'name': '数学', 'description': '数学相关题目'},
    {'name': '逻辑推理', 'description': '逻辑推理题目'}
]

for cat_data in categories:
    category, created = ChoiceQuestionCategory.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    if created:
        print(f'创建分类: {category.name}')

# 创建默认标签
tags = [
    {'name': '排序', 'color': '#409EFF'},
    {'name': '搜索', 'color': '#67C23A'},
    {'name': '动态规划', 'color': '#E6A23C'},
    {'name': '贪心', 'color': '#F56C6C'},
    {'name': '图论', 'color': '#909399'}
]

for tag_data in tags:
    tag, created = ChoiceQuestionTag.objects.get_or_create(
        name=tag_data['name'],
        defaults={'color': tag_data['color']}
    )
    if created:
        print(f'创建标签: {tag.name}')

print('默认数据创建完成')
EOF

log_success "默认数据创建完成"

# 7. 安装完成
log_success "选择题插件安装完成！"
log_info "请按以下步骤完成配置:"
echo "1. 重启Django服务器"
echo "2. 重新构建前端项目"
echo "3. 在管理后台配置权限"
echo "4. 访问 /choice-questions 测试功能"
echo ""
log_info "备份文件位置: $BACKUP_DIR"
log_info "如需卸载，请运行: ./uninstall.sh"