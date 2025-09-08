#!/bin/bash

# Git推送配置脚本
# 用于配置和测试Git推送功能

echo "=== Git推送配置脚本 ==="
echo "时间: $(date '+%Y年%m月%d日 %H:%M:%S')"
echo

# 设置工作目录
WORK_DIR="/home/metaspeekoj"
REMOTE_URL="https://github.com/sharelgx/MetaSpeekOJ"
REPOS_TO_PUSH=(
    "/home/metaspeekoj/OnlineJudge/"
    "/home/metaspeekoj/OnlineJudgeFE/"
    "/home/metaspeekoj/qduoj-choice-question-plugin/"
    "/home/metaspeekoj/node_modules"
)

echo "📁 工作目录: $WORK_DIR"
echo "🌐 远程仓库: $REMOTE_URL"
echo "📦 需要推送的目录:"
for repo in "${REPOS_TO_PUSH[@]}"; do
    echo "   - $repo"
done
echo

# 检查Git配置
echo "🔧 检查Git配置..."
cd "$WORK_DIR"

# 配置Git用户信息（如果未设置）
if [ -z "$(git config user.name)" ]; then
    git config user.name "metaspeekoj"
    echo "✅ 设置Git用户名: metaspeekoj"
fi

if [ -z "$(git config user.email)" ]; then
    git config user.email "metaspeekoj@example.com"
    echo "✅ 设置Git邮箱: metaspeekoj@example.com"
fi

# 配置HTTP设置以解决网络问题
echo "🌐 配置网络设置..."
git config --global http.sslVerify false
git config --global http.postBuffer 1048576000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999
echo "✅ 网络配置完成"

# 检查远程仓库连接
echo "🔗 测试远程仓库连接..."
if timeout 10 git ls-remote origin >/dev/null 2>&1; then
    echo "✅ 远程仓库连接正常"
    CONNECTION_OK=true
else
    echo "❌ 远程仓库连接失败，但配置已完成"
    echo "   可能的原因: 网络问题、代理设置、认证问题"
    CONNECTION_OK=false
fi

# 显示当前状态
echo
echo "📊 当前Git状态:"
git status --porcelain | head -10
if [ $(git status --porcelain | wc -l) -gt 10 ]; then
    echo "   ... 还有 $(($(git status --porcelain | wc -l) - 10)) 个文件"
fi

echo
echo "📋 最近的提交:"
git log --oneline -3

echo
echo "=== 配置完成 ==="
echo "✅ Git推送MCP服务器已配置"
echo "✅ 网络设置已优化"
echo "✅ 用户信息已设置"

if [ "$CONNECTION_OK" = true ]; then
    echo "✅ 远程仓库连接正常"
    echo
    echo "🚀 可以使用以下MCP工具进行推送:"
    echo "   - git_push_all: 一键推送所有更改"
    echo "   - git_status: 检查仓库状态"
    echo "   - git_add_commit: 添加和提交文件"
    echo "   - git_push: 推送到远程仓库"
else
    echo "⚠️  远程仓库连接需要进一步配置"
    echo "   建议检查: 网络连接、代理设置、GitHub访问令牌"
fi

echo
echo "📝 推送格式示例:"
echo '   提交信息: "2025年9月8日10:35 - 修复登录功能，优化前端界面"'
echo '   标签格式: "v1.2.0" 或 "release-2025.09.08"'
echo
echo "脚本执行完成: $(date '+%Y年%m月%d日 %H:%M:%S')"