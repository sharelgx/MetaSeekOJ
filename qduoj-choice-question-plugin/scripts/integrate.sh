#!/bin/bash

# QDUOJ选择题插件自动集成脚本
# 使用方法: ./integrate.sh [QDUOJ_BACKEND_PATH] [QDUOJ_FRONTEND_PATH]

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
DEFAULT_BACKEND_PATH="/home/metaspeekoj/OnlineJudge"
DEFAULT_FRONTEND_PATH="/home/metaspeekoj/OnlineJudgeFE"

# 获取命令行参数或使用默认值
BACKEND_PATH="${1:-$DEFAULT_BACKEND_PATH}"
FRONTEND_PATH="${2:-$DEFAULT_FRONTEND_PATH}"

log_info "QDUOJ选择题插件自动集成脚本"
log_info "插件目录: $PLUGIN_DIR"
log_info "后端路径: $BACKEND_PATH"
log_info "前端路径: $FRONTEND_PATH"

# 检查路径是否存在
check_paths() {
    log_info "检查路径..."
    
    if [ ! -d "$PLUGIN_DIR" ]; then
        log_error "插件目录不存在: $PLUGIN_DIR"
        exit 1
    fi
    
    if [ ! -d "$BACKEND_PATH" ]; then
        log_error "QDUOJ后端目录不存在: $BACKEND_PATH"
        log_info "请指定正确的后端路径: ./integrate.sh [BACKEND_PATH] [FRONTEND_PATH]"
        exit 1
    fi
    
    if [ ! -d "$FRONTEND_PATH" ]; then
        log_error "QDUOJ前端目录不存在: $FRONTEND_PATH"
        log_info "请指定正确的前端路径: ./integrate.sh [BACKEND_PATH] [FRONTEND_PATH]"
        exit 1
    fi
    
    # 检查关键文件
    if [ ! -f "$BACKEND_PATH/manage.py" ]; then
        log_error "后端目录中未找到manage.py文件，请确认路径正确"
        exit 1
    fi
    
    if [ ! -f "$FRONTEND_PATH/package.json" ]; then
        log_error "前端目录中未找到package.json文件，请确认路径正确"
        exit 1
    fi
    
    log_success "路径检查完成"
}

# 备份原始文件
backup_files() {
    log_info "备份原始文件..."
    
    BACKUP_DIR="$PLUGIN_DIR/backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份后端配置文件
    if [ -f "$BACKEND_PATH/oj/settings.py" ]; then
        cp "$BACKEND_PATH/oj/settings.py" "$BACKUP_DIR/settings.py.bak"
    fi
    
    if [ -f "$BACKEND_PATH/oj/urls.py" ]; then
        cp "$BACKEND_PATH/oj/urls.py" "$BACKUP_DIR/urls.py.bak"
    fi
    
    # 备份前端配置文件
    if [ -f "$FRONTEND_PATH/src/pages/oj/router/routes.js" ]; then
        cp "$FRONTEND_PATH/src/pages/oj/router/routes.js" "$BACKUP_DIR/oj_routes.js.bak"
    fi
    
    if [ -f "$FRONTEND_PATH/src/pages/admin/router.js" ]; then
        cp "$FRONTEND_PATH/src/pages/admin/router.js" "$BACKUP_DIR/admin_router.js.bak"
    fi
    
    log_success "文件备份完成: $BACKUP_DIR"
}

# 集成后端
integrate_backend() {
    log_info "开始集成后端..."
    
    # 复制choice_question应用
    if [ -d "$PLUGIN_DIR/backend/choice_question" ]; then
        log_info "复制choice_question应用..."
        cp -r "$PLUGIN_DIR/backend/choice_question" "$BACKEND_PATH/"
        log_success "choice_question应用复制完成"
    else
        log_error "未找到choice_question应用目录"
        exit 1
    fi
    
    # 更新settings.py
    log_info "更新settings.py..."
    SETTINGS_FILE="$BACKEND_PATH/oj/settings.py"
    
    if ! grep -q "choice_question" "$SETTINGS_FILE"; then
        # 在LOCAL_APPS中添加choice_question
        sed -i "/LOCAL_APPS = \[/,/\]/ s/\]/    'choice_question',\n]/" "$SETTINGS_FILE"
        log_success "settings.py更新完成"
    else
        log_warning "choice_question已存在于settings.py中"
    fi
    
    # 更新urls.py
    log_info "更新urls.py..."
    URLS_FILE="$BACKEND_PATH/oj/urls.py"
    
    if ! grep -q "choice-question" "$URLS_FILE"; then
        # 在urlpatterns中添加choice-question路由
        sed -i '/urlpatterns = \[/a\    url(r"^api/choice-question/", include("choice_question.urls")),' "$URLS_FILE"
        log_success "urls.py更新完成"
    else
        log_warning "choice-question路由已存在于urls.py中"
    fi
    
    log_success "后端集成完成"
}

# 集成前端
integrate_frontend() {
    log_info "开始集成前端..."
    
    # 创建插件目录
    PLUGIN_FRONTEND_DIR="$FRONTEND_PATH/src/plugins/choice-question"
    mkdir -p "$PLUGIN_FRONTEND_DIR"
    
    # 复制前端文件
    if [ -d "$PLUGIN_DIR/frontend" ]; then
        log_info "复制前端文件..."
        cp -r "$PLUGIN_DIR/frontend"/* "$PLUGIN_FRONTEND_DIR/"
        log_success "前端文件复制完成"
    else
        log_error "未找到前端文件目录"
        exit 1
    fi
    
    # 更新OJ路由
    log_info "更新OJ路由配置..."
    OJ_ROUTES_FILE="$FRONTEND_PATH/src/pages/oj/router/routes.js"
    
    if [ -f "$OJ_ROUTES_FILE" ]; then
        # 检查是否已经添加了选择题路由
        if ! grep -q "choice-question" "$OJ_ROUTES_FILE"; then
            # 在文件开头添加导入语句
            sed -i '1i\// Choice Question Plugin Imports' "$OJ_ROUTES_FILE"
            sed -i '2i\import QuestionManagement from "@/plugins/choice-question/views/QuestionManagement.vue"' "$OJ_ROUTES_FILE"
            sed -i '3i\import QuestionAnswering from "@/plugins/choice-question/components/QuestionAnswering.vue"' "$OJ_ROUTES_FILE"
            sed -i '4i\import WrongQuestionBook from "@/plugins/choice-question/views/WrongQuestionBook.vue"' "$OJ_ROUTES_FILE"
            sed -i '5i\import QuestionStatistics from "@/plugins/choice-question/views/QuestionStatistics.vue"' "$OJ_ROUTES_FILE"
            sed -i '6i\' "$OJ_ROUTES_FILE"
            
            # 在路由数组中添加选择题路由
            cat >> "$OJ_ROUTES_FILE" << 'EOF'
  // Choice Question Plugin Routes
  {
    name: 'choice-question-list',
    path: '/choice-question',
    meta: { title: 'Choice Question Practice' },
    component: QuestionManagement
  },
  {
    name: 'choice-question-answering',
    path: '/choice-question/:questionId/answer',
    meta: { title: 'Answer Question', requiresAuth: true },
    component: QuestionAnswering
  },
  {
    name: 'choice-question-wrong-book',
    path: '/choice-question/wrong-book',
    meta: { title: 'Wrong Question Book', requiresAuth: true },
    component: WrongQuestionBook
  },
  {
    name: 'choice-question-statistics',
    path: '/choice-question/statistics',
    meta: { title: 'Practice Statistics', requiresAuth: true },
    component: QuestionStatistics
  },
EOF
            log_success "OJ路由配置更新完成"
        else
            log_warning "OJ路由中已存在选择题配置"
        fi
    else
        log_error "未找到OJ路由配置文件"
    fi
    
    # 更新Admin路由
    log_info "更新Admin路由配置..."
    ADMIN_ROUTER_FILE="$FRONTEND_PATH/src/pages/admin/router.js"
    
    if [ -f "$ADMIN_ROUTER_FILE" ]; then
        if ! grep -q "choice-question" "$ADMIN_ROUTER_FILE"; then
            # 在导入部分添加选择题组件导入
            sed -i '/import.*views/a\import QuestionManagement from "@/plugins/choice-question/views/QuestionManagement.vue"' "$ADMIN_ROUTER_FILE"
            sed -i '/import.*views/a\import CategoryManagement from "@/plugins/choice-question/views/CategoryManagement.vue"' "$ADMIN_ROUTER_FILE"
            sed -i '/import.*views/a\import QuestionEditor from "@/plugins/choice-question/components/QuestionEditor.vue"' "$ADMIN_ROUTER_FILE"
            sed -i '/import.*views/a\import QuestionStatistics from "@/plugins/choice-question/views/QuestionStatistics.vue"' "$ADMIN_ROUTER_FILE"
            
            log_success "Admin路由配置更新完成"
        else
            log_warning "Admin路由中已存在选择题配置"
        fi
    else
        log_error "未找到Admin路由配置文件"
    fi
    
    log_success "前端集成完成"
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    cd "$BACKEND_PATH"
    
    # 检查Python环境
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "未找到Python命令"
        exit 1
    fi
    
    # 生成迁移文件
    log_info "生成迁移文件..."
    $PYTHON_CMD manage.py makemigrations choice_question
    
    # 运行迁移
    log_info "应用数据库迁移..."
    $PYTHON_CMD manage.py migrate
    
    log_success "数据库迁移完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装依赖包..."
    
    # 安装Python依赖
    cd "$BACKEND_PATH"
    if [ -f "requirements.txt" ]; then
        pip install openpyxl python-docx
        log_success "Python依赖安装完成"
    fi
    
    # 安装Node.js依赖
    cd "$FRONTEND_PATH"
    if [ -f "package.json" ]; then
        if command -v npm &> /dev/null; then
            npm install
            log_success "Node.js依赖安装完成"
        elif command -v yarn &> /dev/null; then
            yarn install
            log_success "Node.js依赖安装完成"
        else
            log_warning "未找到npm或yarn，请手动安装前端依赖"
        fi
    fi
}

# 验证集成
verify_integration() {
    log_info "验证集成结果..."
    
    # 检查后端文件
    if [ -d "$BACKEND_PATH/choice_question" ]; then
        log_success "✓ 后端choice_question应用已安装"
    else
        log_error "✗ 后端choice_question应用未找到"
    fi
    
    # 检查前端文件
    if [ -d "$FRONTEND_PATH/src/plugins/choice-question" ]; then
        log_success "✓ 前端插件文件已安装"
    else
        log_error "✗ 前端插件文件未找到"
    fi
    
    # 检查配置文件
    if grep -q "choice_question" "$BACKEND_PATH/oj/settings.py"; then
        log_success "✓ settings.py配置已更新"
    else
        log_error "✗ settings.py配置未更新"
    fi
    
    if grep -q "choice-question" "$BACKEND_PATH/oj/urls.py"; then
        log_success "✓ urls.py配置已更新"
    else
        log_error "✗ urls.py配置未更新"
    fi
    
    log_success "集成验证完成"
}

# 显示后续步骤
show_next_steps() {
    log_info "集成完成！后续步骤："
    echo
    echo "1. 重启QDUOJ后端服务："
    echo "   cd $BACKEND_PATH"
    echo "   python manage.py runserver"
    echo
    echo "2. 重启QDUOJ前端服务："
    echo "   cd $FRONTEND_PATH"
    echo "   npm run dev"
    echo
    echo "3. 访问选择题功能："
    echo "   - 普通用户: http://localhost:8080/choice-question"
    echo "   - 管理员: http://localhost:8080/admin/#/choice-question"
    echo
    echo "4. 如果遇到问题，请查看备份文件："
    echo "   $BACKUP_DIR"
    echo
    log_success "选择题插件集成完成！"
}

# 主函数
main() {
    log_info "开始集成QDUOJ选择题插件..."
    
    check_paths
    backup_files
    integrate_backend
    integrate_frontend
    run_migrations
    install_dependencies
    verify_integration
    show_next_steps
}

# 错误处理
trap 'log_error "集成过程中发生错误，请检查日志"' ERR

# 运行主函数
main "$@"