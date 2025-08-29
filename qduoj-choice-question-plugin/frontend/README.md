# QDUOJ选择题插件 - 前端

这是QDUOJ选择题插件的前端部分，基于Vue.js 2.x开发。

## 功能特性

- 🎯 选择题管理（单选/多选）
- 📊 题目分类和标签系统
- 📈 答题统计和分析
- 📝 错题本功能
- 📤 题目导入导出
- 🎨 响应式UI设计
- 🔌 插件化架构

## 技术栈

- **框架**: Vue.js 2.6+
- **路由**: Vue Router 3.x
- **状态管理**: Vuex 3.x
- **UI组件**: Element UI 2.x
- **HTTP客户端**: Axios
- **构建工具**: Webpack 5.x
- **代码规范**: ESLint + Prettier
- **测试框架**: Jest

## 目录结构

```
frontend/
├── public/                 # 静态资源
│   └── index.html         # HTML模板（开发用）
├── src/                   # 源代码
│   ├── components/        # 通用组件
│   ├── views/            # 页面组件
│   ├── store/            # Vuex状态管理
│   ├── api/              # API接口
│   ├── utils/            # 工具函数
│   ├── assets/           # 静态资源
│   └── styles/           # 样式文件
├── tests/                # 测试文件
├── dist/                 # 构建输出
├── plugin-entry.js       # 插件入口文件
├── package.json          # 项目配置
├── webpack.config.js     # Webpack配置
├── vue.config.js         # Vue CLI配置
└── README.md            # 说明文档
```

## 开发环境设置

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 开发模式

```bash
# 启动开发服务器
npm run serve

# 或使用webpack-dev-server
npm run watch
```

访问 http://localhost:8080 查看开发页面。

### 3. 构建生产版本

```bash
# 构建生产版本
npm run build

# 构建开发版本（包含source map）
npm run build:dev
```

### 4. 代码检查

```bash
# 运行ESLint检查
npm run lint

# 自动修复代码风格问题
npm run lint:fix
```

### 5. 运行测试

```bash
# 运行单元测试
npm test

# 监听模式运行测试
npm run test:watch
```

## 插件架构

### 插件入口

`plugin-entry.js` 是插件的主入口文件，导出一个插件类：

```javascript
export default class ChoiceQuestionPlugin {
  constructor() {
    this.name = 'choice-question'
    this.version = '1.0.0'
  }
  
  async install(context) {
    // 插件安装逻辑
  }
  
  async uninstall() {
    // 插件卸载逻辑
  }
}
```

### 组件懒加载

插件使用动态导入实现组件懒加载：

```javascript
const QuestionList = () => import('./src/views/QuestionList.vue')
const QuestionEdit = () => import('./src/views/QuestionEdit.vue')
```

### 路由配置

插件动态注册路由：

```javascript
const routes = [
  {
    path: '/choice-questions',
    name: 'ChoiceQuestions',
    component: QuestionList,
    meta: { requiresAuth: true }
  }
]
```

### 状态管理

插件注册独立的Vuex模块：

```javascript
const store = {
  namespaced: true,
  state: {},
  mutations: {},
  actions: {},
  getters: {}
}
```

## API接口

### 基础配置

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1/choice-questions',
  timeout: 10000
})
```

### 接口列表

- `GET /questions/` - 获取题目列表
- `POST /questions/` - 创建题目
- `GET /questions/{id}/` - 获取题目详情
- `PUT /questions/{id}/` - 更新题目
- `DELETE /questions/{id}/` - 删除题目
- `POST /questions/import/` - 导入题目
- `GET /questions/export/` - 导出题目
- `POST /submissions/` - 提交答案
- `GET /statistics/` - 获取统计数据

## 组件开发

### 组件规范

1. **命名**: 使用PascalCase命名组件
2. **结构**: 按照 `<template>` → `<script>` → `<style>` 顺序
3. **Props**: 定义类型和默认值
4. **事件**: 使用kebab-case命名
5. **样式**: 使用scoped样式

### 示例组件

```vue
<template>
  <div class="question-item">
    <h3>{{ question.title }}</h3>
    <p>{{ question.description }}</p>
  </div>
</template>

<script>
export default {
  name: 'QuestionItem',
  props: {
    question: {
      type: Object,
      required: true
    }
  },
  data() {
    return {}
  },
  methods: {
    handleClick() {
      this.$emit('question-click', this.question)
    }
  }
}
</script>

<style scoped>
.question-item {
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}
</style>
```

## 样式规范

### CSS变量

使用CSS变量定义主题色彩：

```scss
:root {
  --primary-color: #409EFF;
  --success-color: #67C23A;
  --warning-color: #E6A23C;
  --danger-color: #F56C6C;
  --info-color: #909399;
}
```

### SCSS变量

在 `src/assets/styles/variables.scss` 中定义：

```scss
$primary-color: #409EFF;
$border-radius: 4px;
$box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
```

## 国际化

插件支持多语言，配置文件位于 `src/locales/`：

```javascript
// zh-CN.js
export default {
  question: {
    title: '题目标题',
    description: '题目描述'
  }
}

// en.js
export default {
  question: {
    title: 'Question Title',
    description: 'Question Description'
  }
}
```

## 性能优化

1. **代码分割**: 使用动态导入实现路由级代码分割
2. **组件懒加载**: 大型组件使用异步组件
3. **图片优化**: 小图片转base64，大图片使用CDN
4. **缓存策略**: 合理设置HTTP缓存头
5. **打包优化**: 提取公共代码，压缩资源

## 调试技巧

### Vue DevTools

安装Vue DevTools浏览器扩展，方便调试组件状态。

### 开发环境代理

在 `vue.config.js` 中配置API代理：

```javascript
devServer: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

### 错误处理

全局错误处理：

```javascript
Vue.config.errorHandler = (err, vm, info) => {
  console.error('Vue Error:', err, info)
}
```

## 部署说明

### 构建输出

运行 `npm run build` 后，构建文件位于 `dist/` 目录：

```
dist/
├── plugin-entry.[hash].js    # 插件入口文件
├── vendors.[hash].js         # 第三方库
├── common.[hash].js          # 公共代码
└── static/                   # 静态资源
```

### 集成到主应用

1. 将构建文件复制到主应用的静态资源目录
2. 在主应用中加载插件脚本
3. 调用插件的安装方法

## 常见问题

### Q: 如何添加新的页面？

A: 在 `src/views/` 中创建Vue组件，然后在插件入口文件中添加路由配置。

### Q: 如何自定义主题？

A: 修改 `src/assets/styles/variables.scss` 中的变量值。

### Q: 如何处理API错误？

A: 在axios拦截器中统一处理错误响应。

### Q: 如何优化打包大小？

A: 使用webpack-bundle-analyzer分析打包结果，按需引入第三方库。

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

## 许可证

MIT License