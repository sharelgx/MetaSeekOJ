#!/bin/bash

# QDUOJ选择题插件安装脚本
# 版本: 1.0.0
# 作者: QDUOJ Team

set -e  # 遇到错误立即退出

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

# 配置变量
PLUGIN_NAME="choice_question"
PLUGIN_VERSION="1.0.0"
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OJ_ROOT="${OJ_ROOT:-/home/metaspeekoj/OnlineJudge}"
OJ_BACKEND="${OJ_ROOT}"
OJ_FRONTEND="${OJ_ROOT}/../OnlineJudgeFE"
PLUGIN_BACKEND_DIR="${PLUGIN_DIR}/backend"
PLUGIN_FRONTEND_DIR="${PLUGIN_DIR}/frontend"

# 检查函数
check_requirements() {
    log_info "检查安装要求..."
    
    # 检查是否为root用户
    if [[ $EUID -eq 0 ]]; then
        log_warning "建议不要使用root用户运行此脚本"
    fi
    
    # 检查QDUOJ是否存在
    if [[ ! -d "$OJ_BACKEND" ]]; then
        log_error "未找到QDUOJ后端目录: $OJ_BACKEND"
        log_error "请设置正确的OJ_ROOT环境变量或确保QDUOJ已正确安装"
        exit 1
    fi
    
    if [[ ! -d "$OJ_FRONTEND" ]]; then
        log_error "未找到QDUOJ前端目录: $OJ_FRONTEND"
        log_error "请设置正确的OJ_ROOT环境变量或确保QDUOJ已正确安装"
        exit 1
    fi
    
    # 检查Python环境
    if ! command -v python3 &> /dev/null; then
        log_error "未找到Python3，请先安装Python3"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "未找到pip3，请先安装pip3"
        exit 1
    fi
    
    # 检查Node.js和npm（用于前端构建）
    if ! command -v node &> /dev/null; then
        log_warning "未找到Node.js，将跳过前端构建"
        SKIP_FRONTEND=true
    fi
    
    if ! command -v npm &> /dev/null; then
        log_warning "未找到npm，将跳过前端构建"
        SKIP_FRONTEND=true
    fi
    
    log_success "要求检查完成"
}

# 备份函数
backup_files() {
    log_info "备份相关文件..."
    
    BACKUP_DIR="${OJ_ROOT}/backups/choice_question_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份settings.py
    if [[ -f "${OJ_BACKEND}/oj/settings.py" ]]; then
        cp "${OJ_BACKEND}/oj/settings.py" "${BACKUP_DIR}/settings.py.bak"
        log_info "已备份settings.py到 $BACKUP_DIR"
    fi
    
    # 备份urls.py
    if [[ -f "${OJ_BACKEND}/oj/urls.py" ]]; then
        cp "${OJ_BACKEND}/oj/urls.py" "${BACKUP_DIR}/urls.py.bak"
        log_info "已备份urls.py到 $BACKUP_DIR"
    fi
    
    # 备份前端路由文件
    if [[ -f "${OJ_FRONTEND}/src/router/index.js" ]]; then
        cp "${OJ_FRONTEND}/src/router/index.js" "${BACKUP_DIR}/router_index.js.bak"
        log_info "已备份前端路由文件到 $BACKUP_DIR"
    fi
    
    log_success "文件备份完成"
}

# 安装后端依赖
install_backend_dependencies() {
    log_info "安装后端依赖..."
    
    cd "$OJ_BACKEND"
    
    # 检查虚拟环境
    if [[ -n "$VIRTUAL_ENV" ]]; then
        log_info "检测到虚拟环境: $VIRTUAL_ENV"
    else
        log_warning "未检测到虚拟环境，建议在虚拟环境中安装"
    fi
    
    # 安装插件依赖
    if [[ -f "${PLUGIN_DIR}/requirements.txt" ]]; then
        log_info "安装插件依赖包..."
        pip3 install -r "${PLUGIN_DIR}/requirements.txt"
    fi
    
    log_success "后端依赖安装完成"
}

# 复制后端文件
install_backend_files() {
    log_info "安装后端文件..."
    
    # 创建插件目录
    BACKEND_PLUGIN_DIR="${OJ_BACKEND}/${PLUGIN_NAME}"
    if [[ -d "$BACKEND_PLUGIN_DIR" ]]; then
        log_warning "插件目录已存在，将覆盖: $BACKEND_PLUGIN_DIR"
        rm -rf "$BACKEND_PLUGIN_DIR"
    fi
    
    # 复制插件文件
    cp -r "$PLUGIN_BACKEND_DIR/${PLUGIN_NAME}" "$BACKEND_PLUGIN_DIR"
    log_info "已复制插件文件到: $BACKEND_PLUGIN_DIR"
    
    # 设置文件权限
    find "$BACKEND_PLUGIN_DIR" -type f -name "*.py" -exec chmod 644 {} \;
    find "$BACKEND_PLUGIN_DIR" -type d -exec chmod 755 {} \;
    
    log_success "后端文件安装完成"
}

# 注册Django应用
register_django_app() {
    log_info "注册Django应用..."
    
    SETTINGS_FILE="${OJ_BACKEND}/oj/settings.py"
    
    # 检查是否已经注册
    if grep -q "'${PLUGIN_NAME}'" "$SETTINGS_FILE"; then
        log_warning "应用已在INSTALLED_APPS中注册"
    else
        # 在INSTALLED_APPS中添加插件
        log_info "在INSTALLED_APPS中添加插件..."
        
        # 使用Python脚本来修改settings.py
        python3 << EOF
import re

with open('$SETTINGS_FILE', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找INSTALLED_APPS
pattern = r'(INSTALLED_APPS\s*=\s*\[)(.*?)(\])'  
match = re.search(pattern, content, re.DOTALL)

if match:
    start, apps_content, end = match.groups()
    
    # 检查是否已经存在
    if "'$PLUGIN_NAME'" not in apps_content:
        # 在最后一个应用后添加新应用
        apps_lines = apps_content.strip().split('\n')
        
        # 找到最后一个非空行
        last_app_line = -1
        for i in range(len(apps_lines) - 1, -1, -1):
            line = apps_lines[i].strip()
            if line and not line.startswith('#'):
                last_app_line = i
                break
        
        if last_app_line >= 0:
            # 确保最后一行有逗号
            if not apps_lines[last_app_line].rstrip().endswith(','):
                apps_lines[last_app_line] = apps_lines[last_app_line].rstrip() + ','
            
            # 添加新应用
            indent = '    '  # 4个空格缩进
            apps_lines.insert(last_app_line + 1, f"{indent}'$PLUGIN_NAME',")
        
        new_apps_content = '\n'.join(apps_lines)
        new_content = content.replace(match.group(0), f'{start}{new_apps_content}{end}')
        
        with open('$SETTINGS_FILE', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("已添加应用到INSTALLED_APPS")
    else:
        print("应用已存在于INSTALLED_APPS中")
else:
    print("未找到INSTALLED_APPS配置")
EOF
    fi
    
    log_success "Django应用注册完成"
}

# 注册API路由
register_api_routes() {
    log_info "注册API路由..."
    
    URLS_FILE="${OJ_BACKEND}/oj/urls.py"
    
    # 检查是否已经注册
    if grep -q "${PLUGIN_NAME}.urls" "$URLS_FILE"; then
        log_warning "API路由已注册"
    else
        # 添加路由
        log_info "添加API路由..."
        
        python3 << EOF
import re

with open('$URLS_FILE', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找urlpatterns
pattern = r'(urlpatterns\s*=\s*\[)(.*?)(\])'  
match = re.search(pattern, content, re.DOTALL)

if match:
    start, urls_content, end = match.groups()
    
    # 检查是否已经存在
    if "$PLUGIN_NAME.urls" not in urls_content:
        # 在最后添加新路由
        urls_lines = urls_content.strip().split('\n')
        
        # 找到最后一个非空行
        last_url_line = -1
        for i in range(len(urls_lines) - 1, -1, -1):
            line = urls_lines[i].strip()
            if line and not line.startswith('#'):
                last_url_line = i
                break
        
        if last_url_line >= 0:
            # 确保最后一行有逗号
            if not urls_lines[last_url_line].rstrip().endswith(','):
                urls_lines[last_url_line] = urls_lines[last_url_line].rstrip() + ','
            
            # 添加新路由
            indent = '    '  # 4个空格缩进
            urls_lines.insert(last_url_line + 1, f"{indent}path('api/v1/choice-questions/', include('$PLUGIN_NAME.urls')),")
        
        new_urls_content = '\n'.join(urls_lines)
        new_content = content.replace(match.group(0), f'{start}{new_urls_content}{end}')
        
        with open('$URLS_FILE', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("已添加API路由")
    else:
        print("API路由已存在")
else:
    print("未找到urlpatterns配置")
EOF
    fi
    
    log_success "API路由注册完成"
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    cd "$OJ_BACKEND"
    
    # 创建迁移文件
    log_info "创建迁移文件..."
    python3 manage.py makemigrations "$PLUGIN_NAME"
    
    # 应用迁移
    log_info "应用数据库迁移..."
    python3 manage.py migrate "$PLUGIN_NAME"
    
    log_success "数据库迁移完成"
}

# 构建前端
build_frontend() {
    if [[ "$SKIP_FRONTEND" == "true" ]]; then
        log_warning "跳过前端构建"
        return
    fi
    
    log_info "构建前端..."
    
    cd "$PLUGIN_FRONTEND_DIR"
    
    # 安装依赖
    log_info "安装前端依赖..."
    npm install
    
    # 构建生产版本
    log_info "构建生产版本..."
    npm run build
    
    log_success "前端构建完成"
}

# 安装前端文件
install_frontend_files() {
    if [[ "$SKIP_FRONTEND" == "true" ]]; then
        log_warning "跳过前端文件安装"
        return
    fi
    
    log_info "安装前端文件..."
    
    # 创建插件目录
    FRONTEND_PLUGIN_DIR="${OJ_FRONTEND}/src/plugins/${PLUGIN_NAME}"
    mkdir -p "$FRONTEND_PLUGIN_DIR"
    
    # 复制构建文件
    if [[ -d "${PLUGIN_FRONTEND_DIR}/dist" ]]; then
        cp -r "${PLUGIN_FRONTEND_DIR}/dist/"* "$FRONTEND_PLUGIN_DIR/"
        log_info "已复制前端文件到: $FRONTEND_PLUGIN_DIR"
    else
        log_warning "未找到前端构建文件，请手动构建前端"
    fi
    
    log_success "前端文件安装完成"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    
    # 检查是否使用Docker
    if command -v docker-compose &> /dev/null && [[ -f "${OJ_ROOT}/docker-compose.yml" ]]; then
        log_info "检测到Docker环境，重启容器..."
        cd "$OJ_ROOT"
        docker-compose restart backend
        docker-compose restart frontend
    else
        log_warning "请手动重启QDUOJ服务以使插件生效"
        log_info "后端重启命令示例: supervisorctl restart gunicorn"
        log_info "前端重启命令示例: supervisorctl restart nginx"
    fi
    
    log_success "服务重启完成"
}

# 验证安装
verify_installation() {
    log_info "验证安装..."
    
    # 检查后端文件
    if [[ -d "${OJ_BACKEND}/${PLUGIN_NAME}" ]]; then
        log_success "后端文件安装成功"
    else
        log_error "后端文件安装失败"
        return 1
    fi
    
    # 检查前端文件
    if [[ "$SKIP_FRONTEND" != "true" ]]; then
        if [[ -d "${OJ_FRONTEND}/src/plugins/${PLUGIN_NAME}" ]]; then
            log_success "前端文件安装成功"
        else
            log_error "前端文件安装失败"
            return 1
        fi
    fi
    
    # 检查数据库表
    cd "$OJ_BACKEND"
    if python3 manage.py showmigrations "$PLUGIN_NAME" | grep -q "\[X\]"; then
        log_success "数据库迁移成功"
    else
        log_warning "数据库迁移可能未完成，请检查"
    fi
    
    log_success "安装验证完成"
}

# 显示安装信息
show_installation_info() {
    log_success "=== 选择题插件安装完成 ==="
    echo
    log_info "插件信息:"
    echo "  名称: $PLUGIN_NAME"
    echo "  版本: $PLUGIN_VERSION"
    echo "  后端路径: ${OJ_BACKEND}/${PLUGIN_NAME}"
    if [[ "$SKIP_FRONTEND" != "true" ]]; then
        echo "  前端路径: ${OJ_FRONTEND}/src/plugins/${PLUGIN_NAME}"
    fi
    echo
    log_info "访问地址:"
    echo "  管理界面: http://your-domain/admin/choice_question/"
    echo "  API文档: http://your-domain/api/v1/choice-questions/docs/"
    echo
    log_info "下一步:"
    echo "  1. 重启QDUOJ服务"
    echo "  2. 登录管理界面配置插件"
    echo "  3. 开始使用选择题功能"
    echo
    log_warning "注意事项:"
    echo "  - 请确保服务已重启"
    echo "  - 首次使用前请阅读文档"
    echo "  - 如有问题请查看日志文件"
}

# 主函数
main() {
    echo "=== QDUOJ选择题插件安装程序 ==="
    echo "版本: $PLUGIN_VERSION"
    echo "插件目录: $PLUGIN_DIR"
    echo "QDUOJ目录: $OJ_ROOT"
    echo
    
    # 检查参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-frontend)
                SKIP_FRONTEND=true
                shift
                ;;
            --oj-root)
                OJ_ROOT="$2"
                OJ_BACKEND="${OJ_ROOT}/OnlineJudge"
                OJ_FRONTEND="${OJ_ROOT}/OnlineJudgeFE"
                shift 2
                ;;
            --help|-h)
                echo "用法: $0 [选项]"
                echo "选项:"
                echo "  --skip-frontend    跳过前端构建和安装"
                echo "  --oj-root PATH     指定QDUOJ根目录"
                echo "  --help, -h         显示此帮助信息"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    # 执行安装步骤
    check_requirements
    backup_files
    install_backend_dependencies
    install_backend_files
    register_django_app
    register_api_routes
    run_migrations
    build_frontend
    install_frontend_files
    restart_services
    verify_installation
    show_installation_info
    
    log_success "插件安装完成！"
}

# 错误处理
trap 'log_error "安装过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"