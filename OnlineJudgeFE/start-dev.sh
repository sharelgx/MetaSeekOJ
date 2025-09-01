#!/bin/bash
# 启动开发服务器，禁用HMR以避免冲突
export TARGET=http://localhost:8000
export NODE_OPTIONS="--openssl-legacy-provider"
export PORT=8080

# 添加字体MIME类型支持
npm run dev -- --no-hot
