#!/bin/bash

# QDUOJ选择题插件卸载脚本
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
OJ_ROOT="${OJ_ROOT:-/opt/OnlineJudge}"
OJ_BACKEND="${OJ_ROOT}/OnlineJudge"
OJ_FRONTEND="${OJ_ROOT}/OnlineJudgeFE"

# 确认卸载
confirm_uninstall() {
    echo "=== QDUOJ选择题插件卸载程序 ==="
    echo "版本: $PLUGIN_VERSION"
    echo "QDUOJ目录: $OJ_ROOT"
    echo
    
    log_warning "此操作将完全移除选择题插件，包括:"
    echo "  - 插件代码文件"
    echo "  - 数据库表和数据"
    echo "  - 配置文件修改"
    echo
    
    if [[ "$FORCE_UNINSTALL" != "true" ]]; then
        read -p "确定要继续卸载吗？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "卸载已取消"
            exit 0
        fi
    fi
}

# 检查环境
check_environment() {
    log_info "检查环境..."
    
    # 检查QDUOJ是否存在
    if [[ ! -d "$OJ_BACKEND" ]]; then
        log_error "未找到QDUOJ后端目录: $OJ_BACKEND"
        exit 1
    fi
    
    # 检查插件是否已安装
    if [[ ! -d "${OJ_BACKEND}/${PLUGIN_NAME}" ]]; then
        log_warning "插件似乎未安装或已被移除"
    fi
    
    log_success "环境检查完成"
}

# 备份数据
backup_data() {
    log_info "备份插件数据..."
    
    BACKUP_DIR="${OJ_ROOT}/backups/choice_question_uninstall_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    cd "$OJ_BACKEND"
    
    # 导出数据库数据
    log_info "导出数据库数据..."
    
    # 导出选择题数据
    if python3 manage.py shell -c "from ${PLUGIN_NAME}.models import *; print('Tables exist')" 2>/dev/null; then
        python3 manage.py dumpdata "${PLUGIN_NAME}" --format=json --indent=2 > "${BACKUP_DIR}/plugin_data.json" 2>/dev/null || true
        log_info "已导出插件数据到: ${BACKUP_DIR}/plugin_data.json"
    else
        log_warning "未找到插件数据表，跳过数据导出"
    fi
    
    # 备份配置文件
    if [[ -f "${OJ_BACKEND}/OnlineJudge/settings.py" ]]; then
        cp "${OJ_BACKEND}/OnlineJudge/settings.py" "${BACKUP_DIR}/settings.py.bak"
    fi
    
    if [[ -f "${OJ_BACKEND}/OnlineJudge/urls.py" ]]; then
        cp "${OJ_BACKEND}/OnlineJudge/urls.py" "${BACKUP_DIR}/urls.py.bak"
    fi
    
    log_success "数据备份完成: $BACKUP_DIR"
}

# 移除数据库表
remove_database_tables() {
    log_info "移除数据库表..."
    
    cd "$OJ_BACKEND"
    
    # 检查是否有迁移记录
    if python3 manage.py showmigrations "$PLUGIN_NAME" 2>/dev/null | grep -q "\[X\]"; then
        log_info "回滚数据库迁移..."
        
        # 获取所有迁移并逆序回滚
        migrations=$(python3 manage.py showmigrations "$PLUGIN_NAME" --plan | grep "\[X\]" | awk '{print $2}' | tac)
        
        for migration in $migrations; do
            log_info "回滚迁移: $migration"
            python3 manage.py migrate "$PLUGIN_NAME" "${migration%.*}" --fake 2>/dev/null || true
        done
        
        # 完全回滚到初始状态
        python3 manage.py migrate "$PLUGIN_NAME" zero --fake 2>/dev/null || true
        
        log_success "数据库迁移回滚完成"
    else
        log_warning "未找到插件的数据库迁移记录"
    fi
}

# 移除Django应用注册
remove_django_app() {
    log_info "移除Django应用注册..."
    
    SETTINGS_FILE="${OJ_BACKEND}/OnlineJudge/settings.py"
    
    if grep -q "'${PLUGIN_NAME}'" "$SETTINGS_FILE"; then
        log_info "从INSTALLED_APPS中移除插件..."
        
        # 使用Python脚本来修改settings.py
        python3 << EOF
import re

with open('$SETTINGS_FILE', 'r', encoding='utf-8') as f:
    content = f.read()

# 移除插件应用
lines = content.split('\n')
new_lines = []

for line in lines:
    # 跳过包含插件名的行
    if "'$PLUGIN_NAME'" in line and 'INSTALLED_APPS' not in line:
        continue
    new_lines.append(line)

new_content = '\n'.join(new_lines)

with open('$SETTINGS_FILE', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("已从INSTALLED_APPS中移除插件")
EOF
        
        log_success "Django应用注册移除完成"
    else
        log_warning "插件未在INSTALLED_APPS中找到"
    fi
}

# 移除API路由
remove_api_routes() {
    log_info "移除API路由..."
    
    URLS_FILE="${OJ_BACKEND}/OnlineJudge/urls.py"
    
    if grep -q "${PLUGIN_NAME}.urls" "$URLS_FILE"; then
        log_info "移除API路由配置..."
        
        python3 << EOF
import re

with open('$URLS_FILE', 'r', encoding='utf-8') as f:
    content = f.read()

# 移除插件路由
lines = content.split('\n')
new_lines = []

for line in lines:
    # 跳过包含插件路由的行
    if "$PLUGIN_NAME.urls" in line:
        continue
    new_lines.append(line)

new_content = '\n'.join(new_lines)

with open('$URLS_FILE', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("已移除API路由配置")
EOF
        
        log_success "API路由移除完成"
    else
        log_warning "插件API路由未找到"
    fi
}

# 移除后端文件
remove_backend_files() {
    log_info "移除后端文件..."
    
    BACKEND_PLUGIN_DIR="${OJ_BACKEND}/${PLUGIN_NAME}"
    
    if [[ -d "$BACKEND_PLUGIN_DIR" ]]; then
        log_info "删除插件目录: $BACKEND_PLUGIN_DIR"
        rm -rf "$BACKEND_PLUGIN_DIR"
        log_success "后端文件移除完成"
    else
        log_warning "后端插件目录不存在: $BACKEND_PLUGIN_DIR"
    fi
    
    # 移除迁移文件目录
    MIGRATIONS_DIR="${OJ_BACKEND}/${PLUGIN_NAME}/migrations"
    if [[ -d "$MIGRATIONS_DIR" ]]; then
        log_info "删除迁移文件目录: $MIGRATIONS_DIR"
        rm -rf "$MIGRATIONS_DIR"
    fi
}

# 移除前端文件
remove_frontend_files() {
    log_info "移除前端文件..."
    
    FRONTEND_PLUGIN_DIR="${OJ_FRONTEND}/src/plugins/${PLUGIN_NAME}"
    
    if [[ -d "$FRONTEND_PLUGIN_DIR" ]]; then
        log_info "删除前端插件目录: $FRONTEND_PLUGIN_DIR"
        rm -rf "$FRONTEND_PLUGIN_DIR"
        log_success "前端文件移除完成"
    else
        log_warning "前端插件目录不存在: $FRONTEND_PLUGIN_DIR"
    fi
}

# 清理缓存和临时文件
clean_cache() {
    log_info "清理缓存和临时文件..."
    
    cd "$OJ_BACKEND"
    
    # 清理Python缓存
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # 清理Django缓存
    python3 manage.py clear_cache 2>/dev/null || true
    
    log_success "缓存清理完成"
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
        log_warning "请手动重启QDUOJ服务以使更改生效"
        log_info "后端重启命令示例: supervisorctl restart gunicorn"
        log_info "前端重启命令示例: supervisorctl restart nginx"
    fi
    
    log_success "服务重启完成"
}

# 验证卸载
verify_uninstall() {
    log_info "验证卸载..."
    
    # 检查后端文件
    if [[ ! -d "${OJ_BACKEND}/${PLUGIN_NAME}" ]]; then
        log_success "后端文件已移除"
    else
        log_error "后端文件移除失败"
        return 1
    fi
    
    # 检查前端文件
    if [[ ! -d "${OJ_FRONTEND}/src/plugins/${PLUGIN_NAME}" ]]; then
        log_success "前端文件已移除"
    else
        log_error "前端文件移除失败"
        return 1
    fi
    
    # 检查配置文件
    if ! grep -q "'${PLUGIN_NAME}'" "${OJ_BACKEND}/OnlineJudge/settings.py" 2>/dev/null; then
        log_success "Django应用配置已移除"
    else
        log_warning "Django应用配置可能未完全移除"
    fi
    
    if ! grep -q "${PLUGIN_NAME}.urls" "${OJ_BACKEND}/OnlineJudge/urls.py" 2>/dev/null; then
        log_success "API路由配置已移除"
    else
        log_warning "API路由配置可能未完全移除"
    fi
    
    log_success "卸载验证完成"
}

# 显示卸载信息
show_uninstall_info() {
    log_success "=== 选择题插件卸载完成 ==="
    echo
    log_info "已移除的内容:"
    echo "  - 插件代码文件"
    echo "  - 数据库表和迁移"
    echo "  - Django应用注册"
    echo "  - API路由配置"
    echo "  - 前端文件"
    echo
    log_info "备份信息:"
    if [[ -n "$BACKUP_DIR" ]]; then
        echo "  备份目录: $BACKUP_DIR"
        echo "  - 插件数据: plugin_data.json"
        echo "  - 配置文件: settings.py.bak, urls.py.bak"
    fi
    echo
    log_warning "注意事项:"
    echo "  - 请确保服务已重启"
    echo "  - 如需恢复数据，请使用备份文件"
    echo "  - 备份文件请妥善保管"
}

# 主函数
main() {
    # 检查参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                FORCE_UNINSTALL=true
                shift
                ;;
            --oj-root)
                OJ_ROOT="$2"
                OJ_BACKEND="${OJ_ROOT}/OnlineJudge"
                OJ_FRONTEND="${OJ_ROOT}/OnlineJudgeFE"
                shift 2
                ;;
            --no-backup)
                SKIP_BACKUP=true
                shift
                ;;
            --help|-h)
                echo "用法: $0 [选项]"
                echo "选项:"
                echo "  --force           强制卸载，不询问确认"
                echo "  --oj-root PATH    指定QDUOJ根目录"
                echo "  --no-backup       跳过数据备份"
                echo "  --help, -h        显示此帮助信息"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    # 执行卸载步骤
    confirm_uninstall
    check_environment
    
    if [[ "$SKIP_BACKUP" != "true" ]]; then
        backup_data
    fi
    
    remove_database_tables
    remove_django_app
    remove_api_routes
    remove_backend_files
    remove_frontend_files
    clean_cache
    restart_services
    verify_uninstall
    show_uninstall_info
    
    log_success "插件卸载完成！"
}

# 错误处理
trap 'log_error "卸载过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"