# 选择题批量导入功能相关文件

## 问题描述
用户反馈导入格式不正确，需要检查和修复批量导入功能。

## 文件结构

### 核心文件
- `choice_question/` - 选择题应用目录
  - `models.py` - 数据模型定义
  - `views.py` - API视图，包含导入接口
  - `serializers.py` - 数据序列化器
  - `import_serializers.py` - 导入专用序列化器
  - `utils/validator.py` - 数据验证工具
  - `urls.py` - URL路由配置

### 支持文件
- `utils/` - 工具类目录
  - `api.py` - API基类
- `account/` - 用户认证模块
  - `decorators.py` - 权限装饰器
- `oj/` - Django项目配置
- `manage.py` - Django管理脚本

## 导入数据格式

### 当前支持的格式
```json
{
  "questions": [
    {
      "id": "可选，题目ID",
      "question": "题目内容（必填）",
      "type": "single或multiple（必填）",
      "options": ["选项A", "选项B", "选项C", "选项D"],
      "correct": "A或A,B（正确答案）",
      "explanation": "可选，解析说明"
    }
  ],
  "category_id": "可选，分类ID"
}
```

### 验证规则
1. `question` - 必填，题目内容
2. `type` - 必填，只能是 'single' 或 'multiple'
3. `options` - 必填，至少2个选项
4. `correct` - 必填，格式为A-Z的字母，多选用逗号分隔
5. 正确答案必须在选项范围内
6. 单选题只能有一个正确答案

## 常见问题

### 1. 导入格式错误
- 检查JSON格式是否正确
- 确认必填字段是否完整
- 验证正确答案格式（A、B、C等）

### 2. 题目验证失败
- 题目内容不能为空
- 选项数量至少2个
- 正确答案超出选项范围

### 3. 权限问题
- 导入功能需要超级管理员权限
- 确认用户已登录且有相应权限

## API接口
- POST `/api/choice-question/import/` - 批量导入选择题

## 使用说明
1. 准备符合格式的JSON数据
2. 使用超级管理员账号登录
3. 调用导入API接口
4. 检查返回结果中的错误信息