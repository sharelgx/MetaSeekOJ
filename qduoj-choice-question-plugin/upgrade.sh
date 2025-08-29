#!/bin/bash

# QDUOJ选择题插件升级脚本
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
CURRENT_VERSION="1.0.0"
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OJ_ROOT="${OJ_ROOT:-/opt/OnlineJudge}"
OJ_BACKEND="${OJ_ROOT}/OnlineJudge"
OJ_FRONTEND="${OJ_ROOT}/OnlineJudgeFE"
PLUGIN_BACKEND_DIR="${PLUGIN_DIR}/backend"
PLUGIN_FRONTEND_DIR="${PLUGIN_DIR}/frontend"

# 版本比较函数
version_compare() {
    local version1=$1
    local version2=$2
    
    # 将版本号转换为数字数组进行比较
    IFS='.' read -ra VER1 <<< "$version1"
    IFS='.' read -ra VER2 <<< "$version2"
    
    # 补齐版本号长度
    local max_len=${#VER1[@]}
    if [[ ${#VER2[@]} -gt $max_len ]]; then
        max_len=${#VER2[@]}
    fi
    
    for ((i=0; i<max_len; i++)); do
        local v1=${VER1[i]:-0}
        local v2=${VER2[i]:-0}
        
        if [[ $v1 -gt $v2 ]]; then
            return 1  # version1 > version2
        elif [[ $v1 -lt $v2 ]]; then
            return 2  # version1 < version2
        fi
    done
    
    return 0  # version1 == version2
}

# 获取当前安装的版本
get_installed_version() {
    local version_file="${OJ_BACKEND}/${PLUGIN_NAME}/version.py"
    
    if [[ -f "$version_file" ]]; then
        # 从version.py文件中提取版本号
        grep -o "VERSION = '[^']*'" "$version_file" | cut -d"'" -f2 2>/dev/null || echo "unknown"
    else
        echo "unknown"
    fi
}

# 检查升级要求
check_upgrade_requirements() {
    log_info "检查升级要求..."
    
    # 检查是否为root用户
    if [[ $EUID -eq 0 ]]; then
        log_warning "建议不要使用root用户运行此脚本"
    fi
    
    # 检查QDUOJ是否存在
    if [[ ! -d "$OJ_BACKEND" ]]; then
        log_error "未找到QDUOJ后端目录: $OJ_BACKEND"
        exit 1
    fi
    
    # 检查插件是否已安装
    if [[ ! -d "${OJ_BACKEND}/${PLUGIN_NAME}" ]]; then
        log_error "插件未安装，请先运行install.sh进行安装"
        exit 1
    fi
    
    # 获取当前版本
    INSTALLED_VERSION=$(get_installed_version)
    log_info "当前安装版本: $INSTALLED_VERSION"
    log_info "目标升级版本: $CURRENT_VERSION"
    
    # 比较版本
    if [[ "$INSTALLED_VERSION" == "$CURRENT_VERSION" ]]; then
        log_warning "当前版本已是最新版本，无需升级"
        if [[ "$FORCE_UPGRADE" != "true" ]]; then
            exit 0
        fi
    fi
    
    version_compare "$INSTALLED_VERSION" "$CURRENT_VERSION"
    local result=$?
    
    if [[ $result -eq 1 ]]; then
        log_error "当前版本($INSTALLED_VERSION)高于目标版本($CURRENT_VERSION)，不支持降级"
        exit 1
    fi
    
    log_success "升级要求检查完成"
}

# 备份当前版本
backup_current_version() {
    log_info "备份当前版本..."
    
    BACKUP_DIR="${OJ_ROOT}/backups/choice_question_upgrade_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份后端文件
    if [[ -d "${OJ_BACKEND}/${PLUGIN_NAME}" ]]; then
        cp -r "${OJ_BACKEND}/${PLUGIN_NAME}" "${BACKUP_DIR}/backend_${PLUGIN_NAME}"
        log_info "已备份后端文件到: ${BACKUP_DIR}/backend_${PLUGIN_NAME}"
    fi
    
    # 备份前端文件
    if [[ -d "${OJ_FRONTEND}/src/plugins/${PLUGIN_NAME}" ]]; then
        cp -r "${OJ_FRONTEND}/src/plugins/${PLUGIN_NAME}" "${BACKUP_DIR}/frontend_${PLUGIN_NAME}"
        log_info "已备份前端文件到: ${BACKUP_DIR}/frontend_${PLUGIN_NAME}"
    fi
    
    # 备份数据库数据
    cd "$OJ_BACKEND"
    if python3 manage.py shell -c "from ${PLUGIN_NAME}.models import *; print('Tables exist')" 2>/dev/null; then
        python3 manage.py dumpdata "${PLUGIN_NAME}" --format=json --indent=2 > "${BACKUP_DIR}/plugin_data.json" 2>/dev/null || true
        log_info "已备份数据库数据到: ${BACKUP_DIR}/plugin_data.json"
    fi
    
    # 备份配置文件
    cp "${OJ_BACKEND}/OnlineJudge/settings.py" "${BACKUP_DIR}/settings.py.bak" 2>/dev/null || true
    cp "${OJ_BACKEND}/OnlineJudge/urls.py" "${BACKUP_DIR}/urls.py.bak" 2>/dev/null || true
    
    log_success "版本备份完成: $BACKUP_DIR"
}

# 停止相关服务
stop_services() {
    log_info "停止相关服务..."
    
    # 检查是否使用Docker
    if command -v docker-compose &> /dev/null && [[ -f "${OJ_ROOT}/docker-compose.yml" ]]; then
        log_info "检测到Docker环境，停止容器..."
        cd "$OJ_ROOT"
        docker-compose stop backend frontend || true
    else
        log_warning "请手动停止QDUOJ服务以避免升级过程中的冲突"
    fi
    
    log_success "服务停止完成"
}

# 执行版本特定的升级脚本
run_version_specific_upgrades() {
    log_info "执行版本特定的升级操作..."
    
    # 根据版本执行特定的升级逻辑
    case "$INSTALLED_VERSION" in
        "unknown")
            log_info "从未知版本升级，执行完整升级流程"
            run_full_upgrade
            ;;
        "0.9.0")
            log_info "从0.9.0升级到$CURRENT_VERSION"
            upgrade_from_0_9_0
            ;;
        "0.9.1")
            log_info "从0.9.1升级到$CURRENT_VERSION"
            upgrade_from_0_9_1
            ;;
        *)
            log_info "执行通用升级流程"
            run_generic_upgrade
            ;;
    esac
    
    log_success "版本特定升级完成"
}

# 完整升级流程
run_full_upgrade() {
    log_info "执行完整升级流程..."
    
    # 安装依赖
    install_dependencies
    
    # 更新后端文件
    update_backend_files
    
    # 更新前端文件
    update_frontend_files
    
    # 运行数据库迁移
    run_database_migrations
}

# 通用升级流程
run_generic_upgrade() {
    log_info "执行通用升级流程..."
    
    # 更新依赖
    update_dependencies
    
    # 更新文件
    update_backend_files
    update_frontend_files
    
    # 运行迁移
    run_database_migrations
}

# 从0.9.0版本升级
upgrade_from_0_9_0() {
    log_info "执行从0.9.0的特定升级操作..."
    
    # 0.9.0 -> 1.0.0的特定升级逻辑
    # 例如：数据结构变更、新功能添加等
    
    # 更新数据库结构
    log_info "更新数据库结构..."
    cd "$OJ_BACKEND"
    python3 << 'EOF'
# 执行特定的数据迁移逻辑
from django.core.management import execute_from_command_line
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OnlineJudge.settings')

# 这里可以添加特定的数据迁移代码
print("执行0.9.0到1.0.0的数据迁移")
EOF
    
    # 继续通用升级流程
    run_generic_upgrade
}

# 从0.9.1版本升级
upgrade_from_0_9_1() {
    log_info "执行从0.9.1的特定升级操作..."
    
    # 0.9.1 -> 1.0.0的特定升级逻辑
    
    # 更新配置文件
    log_info "更新配置文件..."
    
    # 继续通用升级流程
    run_generic_upgrade
}

# 安装/更新依赖
install_dependencies() {
    log_info "安装/更新依赖包..."
    
    cd "$OJ_BACKEND"
    
    if [[ -f "${PLUGIN_DIR}/requirements.txt" ]]; then
        pip3 install -r "${PLUGIN_DIR}/requirements.txt" --upgrade
    fi
    
    log_success "依赖包更新完成"
}

# 更新依赖
update_dependencies() {
    log_info "检查并更新依赖包..."
    
    cd "$OJ_BACKEND"
    
    # 比较requirements.txt的变化
    if [[ -f "${PLUGIN_DIR}/requirements.txt" ]]; then
        log_info "更新插件依赖..."
        pip3 install -r "${PLUGIN_DIR}/requirements.txt" --upgrade
    fi
    
    log_success "依赖包检查完成"
}

# 更新后端文件
update_backend_files() {
    log_info "更新后端文件..."
    
    BACKEND_PLUGIN_DIR="${OJ_BACKEND}/${PLUGIN_NAME}"
    
    # 保留用户自定义配置
    TEMP_CONFIG_DIR="/tmp/${PLUGIN_NAME}_config_backup"
    if [[ -f "${BACKEND_PLUGIN_DIR}/config.py" ]]; then
        mkdir -p "$TEMP_CONFIG_DIR"
        cp "${BACKEND_PLUGIN_DIR}/config.py" "${TEMP_CONFIG_DIR}/"
        log_info "已备份用户配置文件"
    fi
    
    # 更新插件文件
    if [[ -d "$BACKEND_PLUGIN_DIR" ]]; then
        rm -rf "$BACKEND_PLUGIN_DIR"
    fi
    
    cp -r "$PLUGIN_BACKEND_DIR/${PLUGIN_NAME}" "$BACKEND_PLUGIN_DIR"
    
    # 恢复用户配置
    if [[ -f "${TEMP_CONFIG_DIR}/config.py" ]]; then
        cp "${TEMP_CONFIG_DIR}/config.py" "${BACKEND_PLUGIN_DIR}/"
        rm -rf "$TEMP_CONFIG_DIR"
        log_info "已恢复用户配置文件"
    fi
    
    # 设置文件权限
    find "$BACKEND_PLUGIN_DIR" -type f -name "*.py" -exec chmod 644 {} \;
    find "$BACKEND_PLUGIN_DIR" -type d -exec chmod 755 {} \;
    
    log_success "后端文件更新完成"
}

# 更新前端文件
update_frontend_files() {
    if [[ "$SKIP_FRONTEND" == "true" ]]; then
        log_warning "跳过前端更新"
        return
    fi
    
    log_info "更新前端文件..."
    
    # 构建新版本前端
    if command -v npm &> /dev/null; then
        cd "$PLUGIN_FRONTEND_DIR"
        
        log_info "安装前端依赖..."
        npm install
        
        log_info "构建前端..."
        npm run build
        
        # 更新前端文件
        FRONTEND_PLUGIN_DIR="${OJ_FRONTEND}/src/plugins/${PLUGIN_NAME}"
        if [[ -d "$FRONTEND_PLUGIN_DIR" ]]; then
            rm -rf "$FRONTEND_PLUGIN_DIR"
        fi
        
        mkdir -p "$FRONTEND_PLUGIN_DIR"
        
        if [[ -d "${PLUGIN_FRONTEND_DIR}/dist" ]]; then
            cp -r "${PLUGIN_FRONTEND_DIR}/dist/"* "$FRONTEND_PLUGIN_DIR/"
        fi
        
        log_success "前端文件更新完成"
    else
        log_warning "未找到npm，跳过前端更新"
    fi
}

# 运行数据库迁移
run_database_migrations() {
    log_info "运行数据库迁移..."
    
    cd "$OJ_BACKEND"
    
    # 创建新的迁移文件
    log_info "创建迁移文件..."
    python3 manage.py makemigrations "$PLUGIN_NAME" || true
    
    # 应用迁移
    log_info "应用数据库迁移..."
    python3 manage.py migrate "$PLUGIN_NAME"
    
    log_success "数据库迁移完成"
}

# 更新版本信息
update_version_info() {
    log_info "更新版本信息..."
    
    VERSION_FILE="${OJ_BACKEND}/${PLUGIN_NAME}/version.py"
    
    cat > "$VERSION_FILE" << EOF
# -*- coding: utf-8 -*-

# 插件版本信息
VERSION = '$CURRENT_VERSION'
VERSION_INFO = {
    'major': $(echo $CURRENT_VERSION | cut -d. -f1),
    'minor': $(echo $CURRENT_VERSION | cut -d. -f2),
    'patch': $(echo $CURRENT_VERSION | cut -d. -f3),
    'release': 'stable',
    'build_date': '$(date +%Y-%m-%d)',
    'build_time': '$(date +%H:%M:%S)'
}

# 升级历史
UPGRADE_HISTORY = [
    {
        'from_version': '$INSTALLED_VERSION',
        'to_version': '$CURRENT_VERSION',
        'upgrade_date': '$(date +%Y-%m-%d %H:%M:%S)',
        'upgrade_type': 'automatic'
    }
]
EOF
    
    log_success "版本信息更新完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 检查是否使用Docker
    if command -v docker-compose &> /dev/null && [[ -f "${OJ_ROOT}/docker-compose.yml" ]]; then
        log_info "检测到Docker环境，启动容器..."
        cd "$OJ_ROOT"
        docker-compose start backend frontend
    else
        log_warning "请手动启动QDUOJ服务"
    fi
    
    log_success "服务启动完成"
}

# 验证升级
verify_upgrade() {
    log_info "验证升级结果..."
    
    # 检查版本
    NEW_VERSION=$(get_installed_version)
    if [[ "$NEW_VERSION" == "$CURRENT_VERSION" ]]; then
        log_success "版本升级成功: $INSTALLED_VERSION -> $NEW_VERSION"
    else
        log_error "版本升级失败，当前版本: $NEW_VERSION"
        return 1
    fi
    
    # 检查文件
    if [[ -d "${OJ_BACKEND}/${PLUGIN_NAME}" ]]; then
        log_success "后端文件检查通过"
    else
        log_error "后端文件检查失败"
        return 1
    fi
    
    # 检查数据库
    cd "$OJ_BACKEND"
    if python3 manage.py showmigrations "$PLUGIN_NAME" | grep -q "\[X\]"; then
        log_success "数据库迁移检查通过"
    else
        log_warning "数据库迁移检查异常，请手动检查"
    fi
    
    log_success "升级验证完成"
}

# 清理临时文件
cleanup() {
    log_info "清理临时文件..."
    
    # 清理Python缓存
    cd "$OJ_BACKEND"
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    log_success "清理完成"
}

# 显示升级信息
show_upgrade_info() {
    log_success "=== 选择题插件升级完成 ==="
    echo
    log_info "升级信息:"
    echo "  插件名称: $PLUGIN_NAME"
    echo "  原版本: $INSTALLED_VERSION"
    echo "  新版本: $CURRENT_VERSION"
    echo "  升级时间: $(date '+%Y-%m-%d %H:%M:%S')"
    if [[ -n "$BACKUP_DIR" ]]; then
        echo "  备份目录: $BACKUP_DIR"
    fi
    echo
    log_info "升级内容:"
    echo "  - 更新了插件代码文件"
    echo "  - 应用了数据库迁移"
    echo "  - 更新了依赖包"
    echo "  - 更新了前端文件"
    echo
    log_warning "注意事项:"
    echo "  - 请确保服务已正常启动"
    echo "  - 如有问题可使用备份文件回滚"
    echo "  - 建议测试所有功能是否正常"
}

# 主函数
main() {
    echo "=== QDUOJ选择题插件升级程序 ==="
    echo "目标版本: $CURRENT_VERSION"
    echo "插件目录: $PLUGIN_DIR"
    echo "QDUOJ目录: $OJ_ROOT"
    echo
    
    # 检查参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                FORCE_UPGRADE=true
                shift
                ;;
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
            --no-backup)
                SKIP_BACKUP=true
                shift
                ;;
            --help|-h)
                echo "用法: $0 [选项]"
                echo "选项:"
                echo "  --force           强制升级，即使版本相同"
                echo "  --skip-frontend   跳过前端更新"
                echo "  --oj-root PATH    指定QDUOJ根目录"
                echo "  --no-backup       跳过备份"
                echo "  --help, -h        显示此帮助信息"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    # 执行升级步骤
    check_upgrade_requirements
    
    if [[ "$SKIP_BACKUP" != "true" ]]; then
        backup_current_version
    fi
    
    stop_services
    run_version_specific_upgrades
    update_version_info
    start_services
    verify_upgrade
    cleanup
    show_upgrade_info
    
    log_success "插件升级完成！"
}

# 错误处理
trap 'log_error "升级过程中发生错误，请检查日志并考虑使用备份恢复"; exit 1' ERR

# 运行主函数
main "$@"