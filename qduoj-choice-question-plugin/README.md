# QDUOJ选择题插件

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-3.2+-green.svg)](https://www.djangoproject.com/)
[![Vue Version](https://img.shields.io/badge/vue-2.6+-brightgreen.svg)](https://vuejs.org/)

一个功能完整的QDUOJ选择题插件，支持单选题和多选题的创建、管理、导入导出、自动判分和统计分析。

## ✨ 功能特性

- 🎯 **多种题型**：支持单选题和多选题
- 📚 **分类管理**：支持题目分类和标签系统
- 🎨 **难度等级**：简单、中等、困难三个难度等级
- 📝 **在线答题**：支持在线答题和自动评分
- 📖 **错题本**：自动收集错题，支持重做和笔记
- 📊 **统计分析**：详细的答题统计和趋势分析
- 🔐 **权限管理**：完善的用户权限控制
- 🎛️ **管理后台**：集成Django管理后台

## 🚀 快速开始

### 系统要求

- Python >= 3.6
- Django >= 2.2.0
- Vue.js >= 2.6.0
- 青岛OJ >= 2.0.0

### 安装

1. **下载插件**
```bash
git clone https://github.com/QingdaoU/qduoj-choice-question-plugin.git
cd qduoj-choice-question-plugin
```

2. **运行安装脚本**
```bash
./scripts/install.sh /path/to/OnlineJudge /path/to/OnlineJudgeFE
```

3. **重启服务**
```bash
# 重启Django服务器
cd /path/to/OnlineJudge
python3 manage.py runserver

# 重新构建前端
cd /path/to/OnlineJudgeFE
npm run build
```

### 使用

1. 访问 `/choice-questions` 开始练习选择题
2. 访问 `/wrong-questions` 查看和管理错题本
3. 在Django管理后台创建和管理题目

## 📁 项目结构

```
qduoj-choice-question-plugin/
├── backend/                 # 后端Django应用
│   ├── choice_question/     # 选择题模块
│   │   ├── models.py        # 数据模型
│   │   ├── views.py         # API视图
│   │   ├── serializers.py   # 序列化器
│   │   ├── urls.py          # URL路由
│   │   ├── admin.py         # 管理后台
│   │   └── migrations/      # 数据库迁移
│   ├── requirements.txt     # 后端依赖
│   └── README.md           # 后端文档
├── frontend/               # 前端Vue组件
│   ├── views/              # 页面组件
│   ├── components/         # 子组件
│   ├── api/                # API接口
│   ├── router/             # 路由配置
│   └── store/              # Vuex状态管理
├── docs/                   # 详细文档
│   └── README.md          # 完整使用文档
├── scripts/                # 安装脚本
│   ├── install.sh         # 安装脚本
│   └── uninstall.sh       # 卸载脚本
├── plugin.json            # 插件配置文件
└── README.md              # 项目说明
```

## 🔧 API 接口

### 题目管理
- `GET /api/choice-question/questions/` - 获取题目列表
- `GET /api/choice-question/questions/{id}/` - 获取题目详情
- `POST /api/choice-question/questions/` - 创建题目
- `PUT /api/choice-question/questions/{id}/` - 更新题目
- `DELETE /api/choice-question/questions/{id}/` - 删除题目

### 答题功能
- `POST /api/choice-question/submissions/` - 提交答案
- `GET /api/choice-question/submissions/` - 获取提交记录

### 错题本
- `GET /api/choice-question/wrong-questions/` - 获取错题列表
- `POST /api/choice-question/wrong-questions/` - 添加错题
- `DELETE /api/choice-question/wrong-questions/{id}/` - 移除错题

### 统计信息
- `GET /api/choice-question/stats/` - 获取统计信息

## 📖 详细文档

查看 [docs/README.md](docs/README.md) 获取完整的安装、配置和使用文档。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [青岛OJ 主项目](https://github.com/QingdaoU/OnlineJudge)
- [青岛OJ 文档](https://docs.onlinejudge.me/)
- [问题反馈](https://github.com/QingdaoU/qduoj-choice-question-plugin/issues)

## 📞 支持

如果您在使用过程中遇到问题，可以通过以下方式获取帮助：

- 查看 [文档](docs/README.md)
- 提交 [Issue](https://github.com/QingdaoU/qduoj-choice-question-plugin/issues)
- 联系青岛OJ社区

---

**Made with ❤️ for QDUOJ Community**