#!/bin/bash

# QDUOJ选择题插件测试运行脚本
# 用于运行后端和前端的所有测试

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

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

# 显示帮助信息
show_help() {
    echo "QDUOJ选择题插件测试运行脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示此帮助信息"
    echo "  -b, --backend       仅运行后端测试"
    echo "  -f, --frontend      仅运行前端测试"
    echo "  -c, --coverage      生成覆盖率报告"
    echo "  -v, --verbose       详细输出"
    echo "  --unit              仅运行单元测试"
    echo "  --integration       仅运行集成测试"
    echo "  --clean             清理测试缓存和临时文件"
    echo ""
    echo "示例:"
    echo "  $0                  # 运行所有测试"
    echo "  $0 -b -c           # 运行后端测试并生成覆盖率报告"
    echo "  $0 -f --unit       # 仅运行前端单元测试"
}

# 检查依赖
check_dependencies() {
    log_info "检查测试依赖..."
    
    # 检查Python和Django
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查Node.js和npm
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 设置测试环境
setup_test_environment() {
    log_info "设置测试环境..."
    
    # 设置环境变量
    export DJANGO_SETTINGS_MODULE="oj.settings"
    export PYTHONPATH="$PROJECT_ROOT/backend:$PYTHONPATH"
    
    # 创建测试数据库（如果需要）
    if [ "$RUN_BACKEND" = true ]; then
        cd "$PROJECT_ROOT/backend"
        
        # 检查是否有Django项目
        if [ -f "manage.py" ]; then
            log_info "准备Django测试环境..."
            python3 manage.py collectstatic --noinput --clear > /dev/null 2>&1 || true
        else
            log_warning "未找到Django项目，跳过Django环境设置"
        fi
    fi
    
    log_success "测试环境设置完成"
}

# 运行后端测试
run_backend_tests() {
    log_info "运行后端测试..."
    
    cd "$PROJECT_ROOT/backend"
    
    # 构建测试命令
    TEST_CMD="python3 -m pytest choice_question/tests/"
    
    if [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD -v"
    fi
    
    if [ "$COVERAGE" = true ]; then
        TEST_CMD="$TEST_CMD --cov=choice_question --cov-report=html --cov-report=term"
    fi
    
    if [ "$UNIT_ONLY" = true ]; then
        TEST_CMD="$TEST_CMD -k 'not integration'"
    elif [ "$INTEGRATION_ONLY" = true ]; then
        TEST_CMD="$TEST_CMD -k 'integration'"
    fi
    
    # 运行测试
    if eval $TEST_CMD; then
        log_success "后端测试通过"
        BACKEND_SUCCESS=true
    else
        log_error "后端测试失败"
        BACKEND_SUCCESS=false
    fi
    
    # 显示覆盖率报告位置
    if [ "$COVERAGE" = true ] && [ "$BACKEND_SUCCESS" = true ]; then
        log_info "后端覆盖率报告已生成: $PROJECT_ROOT/backend/htmlcov/index.html"
    fi
}

# 运行前端测试
run_frontend_tests() {
    log_info "运行前端测试..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # 检查是否安装了依赖
    if [ ! -d "node_modules" ]; then
        log_info "安装前端依赖..."
        npm install
    fi
    
    # 构建测试命令
    TEST_CMD="npm run test"
    
    if [ "$COVERAGE" = true ]; then
        TEST_CMD="npm run test:coverage"
    fi
    
    if [ "$UNIT_ONLY" = true ]; then
        TEST_CMD="$TEST_CMD -- --testPathPattern=unit"
    elif [ "$INTEGRATION_ONLY" = true ]; then
        TEST_CMD="$TEST_CMD -- --testPathPattern=integration"
    fi
    
    if [ "$VERBOSE" = true ]; then
        TEST_CMD="$TEST_CMD -- --verbose"
    fi
    
    # 运行测试
    if eval $TEST_CMD; then
        log_success "前端测试通过"
        FRONTEND_SUCCESS=true
    else
        log_error "前端测试失败"
        FRONTEND_SUCCESS=false
    fi
    
    # 显示覆盖率报告位置
    if [ "$COVERAGE" = true ] && [ "$FRONTEND_SUCCESS" = true ]; then
        log_info "前端覆盖率报告已生成: $PROJECT_ROOT/frontend/tests/coverage/index.html"
    fi
}

# 清理测试文件
clean_test_files() {
    log_info "清理测试缓存和临时文件..."
    
    # 清理后端测试文件
    if [ -d "$PROJECT_ROOT/backend" ]; then
        cd "$PROJECT_ROOT/backend"
        rm -rf .pytest_cache/ htmlcov/ .coverage
        find . -name "*.pyc" -delete
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    fi
    
    # 清理前端测试文件
    if [ -d "$PROJECT_ROOT/frontend" ]; then
        cd "$PROJECT_ROOT/frontend"
        rm -rf tests/coverage/ node_modules/.cache/
    fi
    
    log_success "清理完成"
}

# 生成测试报告
generate_test_report() {
    log_info "生成测试报告..."
    
    REPORT_FILE="$PROJECT_ROOT/test_report.txt"
    
    {
        echo "QDUOJ选择题插件测试报告"
        echo "生成时间: $(date)"
        echo "="*50
        echo ""
        
        if [ "$RUN_BACKEND" = true ]; then
            echo "后端测试结果: $([ "$BACKEND_SUCCESS" = true ] && echo "通过" || echo "失败")"
        fi
        
        if [ "$RUN_FRONTEND" = true ]; then
            echo "前端测试结果: $([ "$FRONTEND_SUCCESS" = true ] && echo "通过" || echo "失败")"
        fi
        
        echo ""
        echo "测试配置:"
        echo "- 覆盖率报告: $([ "$COVERAGE" = true ] && echo "启用" || echo "禁用")"
        echo "- 详细输出: $([ "$VERBOSE" = true ] && echo "启用" || echo "禁用")"
        echo "- 测试类型: $([ "$UNIT_ONLY" = true ] && echo "仅单元测试" || ([ "$INTEGRATION_ONLY" = true ] && echo "仅集成测试" || echo "全部测试"))"
        
    } > "$REPORT_FILE"
    
    log_success "测试报告已生成: $REPORT_FILE"
}

# 主函数
main() {
    # 默认参数
    RUN_BACKEND=true
    RUN_FRONTEND=true
    COVERAGE=false
    VERBOSE=false
    UNIT_ONLY=false
    INTEGRATION_ONLY=false
    CLEAN_ONLY=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -b|--backend)
                RUN_BACKEND=true
                RUN_FRONTEND=false
                shift
                ;;
            -f|--frontend)
                RUN_BACKEND=false
                RUN_FRONTEND=true
                shift
                ;;
            -c|--coverage)
                COVERAGE=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --unit)
                UNIT_ONLY=true
                shift
                ;;
            --integration)
                INTEGRATION_ONLY=true
                shift
                ;;
            --clean)
                CLEAN_ONLY=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 如果只是清理，执行清理后退出
    if [ "$CLEAN_ONLY" = true ]; then
        clean_test_files
        exit 0
    fi
    
    # 显示测试配置
    log_info "测试配置:"
    echo "  - 后端测试: $([ "$RUN_BACKEND" = true ] && echo "启用" || echo "禁用")"
    echo "  - 前端测试: $([ "$RUN_FRONTEND" = true ] && echo "启用" || echo "禁用")"
    echo "  - 覆盖率报告: $([ "$COVERAGE" = true ] && echo "启用" || echo "禁用")"
    echo "  - 详细输出: $([ "$VERBOSE" = true ] && echo "启用" || echo "禁用")"
    echo ""
    
    # 检查依赖
    check_dependencies
    
    # 设置测试环境
    setup_test_environment
    
    # 运行测试
    BACKEND_SUCCESS=true
    FRONTEND_SUCCESS=true
    
    if [ "$RUN_BACKEND" = true ]; then
        run_backend_tests
    fi
    
    if [ "$RUN_FRONTEND" = true ]; then
        run_frontend_tests
    fi
    
    # 生成测试报告
    generate_test_report
    
    # 显示最终结果
    echo ""
    log_info "测试完成!"
    
    if [ "$RUN_BACKEND" = true ] && [ "$BACKEND_SUCCESS" = false ]; then
        log_error "后端测试失败"
        exit 1
    fi
    
    if [ "$RUN_FRONTEND" = true ] && [ "$FRONTEND_SUCCESS" = false ]; then
        log_error "前端测试失败"
        exit 1
    fi
    
    log_success "所有测试通过!"
}

# 运行主函数
main "$@"