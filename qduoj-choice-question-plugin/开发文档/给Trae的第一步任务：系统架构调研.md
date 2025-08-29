# 📘 青岛OJ选择题插件开发文档（完整版）


## 一、项目总体目标
基于**青岛OJ（QDUOJ）系统**开发**独立目录结构的选择题功能插件**，核心目标如下：
1. **插件独立性**：后端、前端均采用独立目录开发，不修改OJ核心代码，仅通过插件接口与原系统交互；
2. **无缝集成性**：UI风格、用户体系、权限系统、数据统计完全对齐原OJ，无“第三方插件”割裂感；
3. **完整功能性**：支持单选/多选题、多级分类、标签管理、错题本、批量导入导出等核心功能；
4. **可插拔性**：支持一键安装、卸载、升级，安装时自动完成数据库迁移，卸载时清理残留数据；
5. **低耦合性**：通过原OJ的插件扩展接口（或动态注入方式）实现集成，不依赖原OJ核心代码修改。


## 二、技术栈规范（基于系统架构调研结果）
### 2.1 后端技术栈（需与原OJ版本严格对齐）
- **基础环境**：Python（版本与原OJ一致，通过`python --version`确认）
- **Web框架**：Django（版本与原OJ一致，通过`python manage.py shell -c "import django; print(django.VERSION)"`确认）
- **API框架**：Django REST Framework（版本与原OJ`requirements.txt`中记录一致）
- **数据库**：与原OJ主数据库类型一致（PostgreSQL/MySQL，通过`conf/settings.py`中`DATABASES`配置确认）
- **辅助工具**：
  - 多级分类：django-mptt（版本兼容原OJPython/Django版本）
  - 标签系统：django-taggit（版本兼容）
  - 异步任务：复用原OJ的Celery/Redis配置（通过`requirements.txt`确认版本）
  - 导入导出：openpyxl（兼容原系统依赖）

### 2.2 前端技术栈（需与原OJ版本严格对齐）
- **基础环境**：Node.js、npm（版本与原OJ`node --version`/`npm --version`结果一致）
- **框架核心**：Vue.js（版本与原OJ`package.json`中"vue"版本一致）
- **UI组件库**：与原OJ一致（Element UI/iView，通过`src/main.js`中`use`语句确认）
- **路由与状态**：Vue Router、Vuex（版本与原OJ`package.json`中记录一致）
- **请求工具**：axios（复用原OJ的封装方式，通过`src/api.js`确认拦截器配置）


## 三、插件目录结构设计（独立目录+规范对齐）
插件根目录统一为 `qduoj-choice-plugin/`，内部按“后端-前端-部署脚本”分离，目录结构如下：
```
qduoj-choice-plugin/
├── backend/                # 后端插件目录（独立Django App）
│   ├── choice_plugin/      # 插件核心模块（符合原OJ App命名规范）
│   │   ├── __init__.py
│   │   ├── plugin.py       # 插件入口（声明元信息、生命周期钩子）
│   │   ├── apps.py         # Django App配置（独立注册）
│   │   ├── models/         # 插件独立数据模型（遵循原OJ Model规范）
│   │   │   ├── __init__.py
│   │   │   ├── category.py # 分类模型
│   │   │   ├── question.py # 题目模型（字段命名用snake_case）
│   │   │   └── wrong_book.py # 错题本模型（时间字段用created_at/updated_at）
│   │   ├── api/            # 插件独立API（带插件前缀，遵循原OJ URL规范）
│   │   │   ├── __init__.py
│   │   │   ├── serializers.py # 序列化器（对齐原OJ响应格式）
│   │   │   ├── views.py    # API视图（继承原OJ常用基类如ViewSet）
│   │   │   └── urls.py     # 插件内部URL（不修改原OJ路由）
│   │   ├── migrations/     # 插件独立数据库迁移文件
│   │   └── utils/          # 插件工具类（如导入导出、判题逻辑）
│   ├── requirements.txt    # 插件后端依赖（版本与原OJ兼容）
│   ├── setup.py            # 插件安装脚本（支持pip install）
│   └── uninstall.py        # 插件卸载脚本（清理数据库、配置）
│
├── frontend/               # 前端插件目录（独立Vue模块）
│   ├── src/
│   │   ├── plugin-entry.js # 前端插件入口（声明路由、菜单、生命周期）
│   │   ├── api/            # 插件API封装（请求带插件前缀，复用原OJ axios拦截器）
│   │   ├── components/     # 插件独立组件（命名规范与原OJ一致，如PascalCase）
│   │   ├── views/          # 插件页面（结构对齐原OJ src/pages/oj/）
│   │   │   ├── ChoiceList.vue
│   │   │   ├── ChoiceDetail.vue
│   │   │   └── WrongBook.vue
│   │   ├── store/          # 插件独立状态管理（带命名空间，避免污染原OJ Vuex）
│   │   └── styles/         # 插件样式（复用原OJ CSS变量，如主题色、间距）
│   ├── package.json        # 前端依赖声明（版本与原OJ一致）
│   └── vue.config.js       # 前端构建配置（输出为插件可用资源）
│
└── plugin.json             # 插件元信息（名称、版本、作者、依赖OJ版本、入口文件）
```


## 四、核心功能需求（插件内实现，遵循原系统规范）
| 功能模块       | 具体功能点                                                                 | 实现说明（插件化特性+规范对齐）                                                                 |
|----------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| 1. 题目管理     | 单选/多选题创建/编辑/删除、难度设置、批量导入导出（Excel/CSV）、题目审核发布 | 插件内独立实现，题目数据存储在`choice_plugin_question`表（带前缀）；字段命名遵循原OJ snake_case规范；时间字段用`created_at`/`updated_at`（与原OJ Model层规范一致） |
| 2. 多级分类管理 | 分类增删改、树形结构（拖拽排序）、分类下题目统计、批量移动题目             | 用Django MPTT实现树形结构，分类表`choice_plugin_category`；继承原OJ抽象基类`PluginBaseModel`（若存在）；前端分类树组件样式对齐原OJ同类组件（如问题分类树） |
| 3. 标签管理     | 标签增删改、颜色设置、热门标签统计、题目批量添删标签、标签云展示           | 插件内建Tag模型（`choice_plugin_tag`），热门标签统计通过插件内Redis缓存（键名带`choice_plugin:`前缀，避免冲突）；标签云组件复用原OJ样式变量 |
| 4. 答题功能     | 题目列表（分页/筛选/搜索）、答题界面、实时判题、答题记录、题目收藏         | 答题记录存储在`choice_plugin_submission`表；分页实现复用原OJ分页参数（如`page`/`page_size`，与API层规范一致）；判题逻辑不依赖原OJ判题系统，独立实现 |
| 5. 错题本       | 自动记录错题、分类/标签/时间筛选、错题笔记、重做统计、PDF导出、相似题推荐   | 错题数据存储在`choice_plugin_wrongbook`表，外键关联原OJ`User`表（不修改原用户表）；笔记编辑器复用原OJ富文本组件（若有） |
| 6. 统计分析     | 个人答题统计、分类/标签正确率、答题趋势图、排行榜（总榜/分类榜）           | 统计数据缓存于插件Redis键（带`choice_plugin:`前缀）；图表用ECharts（与原OJ图表库一致）；排行榜独立计算，不干扰原OJ排名 |
| 7. 插件管理     | 安装检测、版本查询、卸载清理、升级兼容                                     | 通过`plugin.json`和安装脚本实现；卸载时自动删除插件表（`choice_plugin_*`前缀）、路由、菜单残留；升级时处理数据库迁移（遵循原OJ迁移规范） |


## 五、编码规范（严格遵循原OJ规范）
### 5.1 后端编码规范
- **Model层**：
  - 字段命名：统一使用snake_case（与原OJ`problem/models.py`等文件规范一致）
  - 时间字段：使用`created_at`（创建时间）、`updated_at`（更新时间）（参考原OJ基类设计）
  - 基类继承：若原OJ存在`AbstractBaseModel`或`BaseModel`，插件模型需继承该基类；否则使用自定义`PluginBaseModel`（含时间字段）
  - 外键关联：关联原OJ用户表`django.contrib.auth.models.User`，不修改原表结构

- **API层**：
  - 视图基类：优先使用与原OJ一致的基类（如`ViewSet`或`GenericAPIView`，通过`problem/views/oj.py`确认）
  - URL命名：API路径带插件前缀`/api/plugin/choice/`，URL名称格式为`choice-<资源名>`（对齐原OJ URL命名规范）
  - 响应格式：统一返回`{"code": 200, "data": {...}, "message": ""}`结构（与原OJAPI响应格式一致）
  - 分页实现：复用原OJ分页类（通过`conf/settings.py`中`REST_FRAMEWORK.PAGINATION_CLASS`确认）

- **权限认证**：
  - 复用原OJ权限装饰器（如`@login_required`、`@permission_required`，通过`account/decorators.py`确认）
  - 管理员权限判断使用`request.user.is_staff`（与原OJ权限逻辑一致）
  - API认证方式与原OJ统一（Session/Token，通过`REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES`确认）


### 5.2 前端编码规范
- **组件规范**：
  - 组件命名：使用PascalCase（如`CategoryTree.vue`），与原OJ`src/components/`目录组件命名一致
  - 导入方式：采用相对路径或别名导入（与原OJ`src/pages/oj/problem/ProblemList.vue`导入规范一致）
  - 样式规范：若原OJ使用Less/SCSS（通过`find src/ -name "*.less"`确认），插件样式也使用相同预处理器；复用原OJ主题变量（如`@primary-color`）

- **API调用**：
  - 封装方式：对齐原OJ`src/api.js`或`src/pages/oj/api/problem.js`的封装格式，统一处理请求/响应拦截
  - 路径前缀：所有API请求带`/api/plugin/choice/`前缀，避免与原OJ接口冲突

- **状态管理**：
  - Vuex模块：使用命名空间（`namespaced: true`），模块名`choicePlugin`（避免与原OJ模块冲突）
  - 状态设计：遵循原OJVuex数据结构规范（如列表用`xxxList`，计数用`xxxCount`）


## 六、任务拆解（分阶段：插件架构→功能开发→集成→部署）
### 阶段1：插件基础架构搭建（优先保障独立目录与可插拔）
#### 1.1 后端插件基础（独立目录初始化）
- 新建 `qduoj-choice-plugin/backend/` 目录，初始化Django App（命名为`choice_plugin`）
- 创建 `choice_plugin/plugin.py`（插件入口文件），声明元信息：
  ```python
  # choice_plugin/plugin.py
  PLUGIN_META = {
      "name": "qduoj-choice-question",
      "version": "1.0.0",
      "author": "xxx",
      "oj_version_require": ">=2.0.0",  # 依赖的OJ版本（需与调研结果一致）
      "description": "青岛OJ选择题功能插件",
      "backend_entry": "choice_plugin.apps.ChoicePluginConfig",  # Django App入口
      "uninstall_clean": ["choice_plugin_*"],  # 卸载时清理的表前缀
      "api_urls": {
          "prefix": "/api/plugin/choice/",  # API前缀，避免冲突
          "urls_module": "choice_plugin.api.urls"
      }
  }
  ```
- 配置 `choice_plugin/apps.py`，使用Django AppConfig实现插件注册：
  ```python
  from django.apps import AppConfig

  class ChoicePluginConfig(AppConfig):
      default_auto_field = "django.db.models.BigAutoField"
      name = "choice_plugin"
      verbose_name = "选择题插件"

      def ready(self):
          import choice_plugin.signals  # 注册信号（如用户删除时清理错题）
  ```
- 编写 `backend/requirements.txt`，声明插件依赖（版本与原OJ兼容）：
  ```txt
  django>=3.2,<4.0  # 与原OJ Django版本一致（通过调研确认）
  djangorestframework>=3.13.0  # 与原OJ DRF版本一致
  django-mptt==0.14.0  # 多级分类
  django-taggit==3.1.0  # 标签
  openpyxl==3.1.2  # Excel导入导出
  ```


#### 1.2 前端插件基础（独立目录与入口）
- 新建 `qduoj-choice-plugin/frontend/` 目录，初始化前端项目：
  ```bash
  cd qduoj-choice-plugin/frontend/
  npm init -y
  npm install vue@2.x vue-router@3.x axios  # 版本与原OJ一致（通过package.json确认）
  npm install element-ui  # 若原OJ使用Element UI（通过src/main.js确认）
  ```
- 创建 `src/plugin-entry.js`（前端插件入口，供OJ动态加载）：
  ```javascript
  // 前端插件元信息与生命周期
  export const ChoicePlugin = {
    meta: {
      name: "qduoj-choice-question",
      version: "1.0.0",
      frontendAssets: ["/plugin/choice/css/main.css", "/plugin/choice/js/main.js"],
    },
    // OJ加载插件时执行：注册路由、菜单
    install(Vue, { router, menuService }) {
      // 动态添加路由（挂载到OJ的"oj"路由下，与原OJ路由结构一致）
      router.addRoute("oj", {
        path: "/plugin/choice/questions",
        name: "ChoiceQuestionList",
        component: () => import("./views/ChoiceList.vue"),
        meta: { title: "选择题题库", permission: "choice:view" }  // 插件自定义权限
      });
      // 注入菜单（父菜单为原OJ的"题库"，保持导航一致性）
      menuService.addMenu({
        parentKey: "problem",
        key: "choice-question",
        title: "选择题",
        icon: "el-icon-edit-outline",  // 与原OJ菜单图标风格一致
        path: "/plugin/choice/questions",
        permission: "choice:view"
      });
      // 注册Vuex模块（带命名空间，避免冲突）
      store.registerModule("choicePlugin", import("./store/choice-store.js"));
    },
    // OJ卸载插件时执行：清理路由、菜单
    uninstall(Vue, { router, menuService, store }) {
      router.removeRoute("ChoiceQuestionList");
      menuService.removeMenu("choice-question");
      store.unregisterModule("choicePlugin");
    }
  };

  // 暴露插件供OJ加载
  if (window.OJPlugin) {
    window.OJPlugin.register(ChoicePlugin);
  }
  ```
- 配置 `vue.config.js`，指定构建输出路径：
  ```javascript
  module.exports = {
    outputDir: "../dist/frontend",
    assetsDir: "static",
    publicPath: "/plugin/choice/",  // 资源访问前缀（避免冲突）
    configureWebpack: {
      output: {
        library: "ChoicePlugin",
        libraryTarget: "umd"
      }
    }
  };
  ```


### 阶段2：插件核心功能开发（独立实现，规范对齐）
#### 2.1 后端功能开发
- **数据模型设计**（插件独立表，遵循原OJ规范）：
  ```python
  # choice_plugin/models/category.py（分类模型）
  from django.db import models
  from mptt.models import MPTTModel, TreeForeignKey
  from .base import PluginBaseModel  # 继承插件基础模型（含时间字段）

  class Category(MPTTModel, PluginBaseModel):
      name = models.CharField(max_length=100, verbose_name="分类名称")  # snake_case命名
      parent = TreeForeignKey(
          "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children", verbose_name="父分类"
      )
      order = models.IntegerField(default=0, verbose_name="排序")
      description = models.TextField(blank=True, verbose_name="描述")
      icon = models.CharField(max_length=50, blank=True, verbose_name="图标类名")
      question_count = models.IntegerField(default=0, verbose_name="题目数量")

      class MPTTMeta:
          order_insertion_by = ["order"]
          verbose_name = "选择题分类"
          verbose_name_plural = "选择题分类"

      class Meta:
          db_table = "choice_plugin_category"  # 表名带插件前缀
  ```

- **API开发**（遵循原OJ接口规范）：
  ```python
  # choice_plugin/api/urls.py
  from django.urls import path
  from .views import CategoryViewSet, QuestionViewSet

  urlpatterns = [
      path("categories/", CategoryViewSet.as_view({"get": "list", "post": "create"}), name="choice-category"),
      path("questions/", QuestionViewSet.as_view({"get": "list", "post": "create"}), name="choice-question"),
  ]

  # choice_plugin/api/views.py（使用与原OJ一致的视图基类）
  from rest_framework.viewsets import ModelViewSet
  from ..models import Category
  from .serializers import CategorySerializer
  from account.permissions import IsAdminUser  # 复用原OJ权限类

  class CategoryViewSet(ModelViewSet):
      queryset = Category.objects.all()
      serializer_class = CategorySerializer
      permission_classes = [IsAdminUser]  # 复用原OJ权限判断
  ```


#### 2.2 前端功能开发
- **核心页面开发**（复用原OJ组件风格）：
  ```vue
  <!-- src/views/ChoiceList.vue -->
  <template>
    <div class="choice-list-page">
      <!-- 复用原OJ的Panel组件，保持UI一致 -->
      <el-panel title="选择题题库">
        <!-- 筛选区：分类+标签 -->
        <el-row :gutter="10">
          <el-col :span="8">
            <category-tree v-model="selectedCategory" />  <!-- 插件内组件 -->
          </el-col>
          <el-col :span="8">
            <tag-select v-model="selectedTags" />  <!-- 插件内组件 -->
          </el-col>
        </el-row>
        <!-- 题目表格（样式与原OJ题目列表一致） -->
        <el-table :data="questionList" border>
          <el-table-column label="题目" prop="title" />
          <el-table-column label="难度" prop="difficulty" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button @click="goToDetail(scope.row.id)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
        <!-- 分页组件（复用原OJ分页参数） -->
        <el-pagination
          :current-page="page"
          :page-size="pageSize"
          :total="total"
          @current-change="handlePageChange"
        />
      </el-panel>
    </div>
  </template>

  <script>
  import { getQuestionList } from "@/api/choice-api";  // 插件内API封装
  import CategoryTree from "@/components/CategoryTree.vue";
  export default {
    data() {
      return { 
        questionList: [], 
        selectedCategory: null, 
        selectedTags: [],
        page: 1,  // 与原OJ分页参数一致
        pageSize: 20,
        total: 0
      };
    },
    methods: {
      async fetchQuestions() {
        const res = await getQuestionList({ 
          category: this.selectedCategory, 
          tags: this.selectedTags,
          page: this.page,
          page_size: this.pageSize  // 与原OJ分页参数名一致
        });
        this.questionList = res.data.results;  // 对齐原OJ分页响应结构
        this.total = res.data.count;
      }
    }
  };
  </script>
  ```


### 阶段3：插件与OJ集成（动态挂载，不修改核心）
#### 3.1 后端集成
- 若原OJ有插件注册机制（通过调研确认）：  
  在OJ后台“插件管理”上传`plugin.json`，OJ自动加载`backend_entry`（Django App）和`api_urls`。

- 若OJ无插件机制：  
  提供 `install_backend.sh` 脚本动态集成：
  ```bash
  # install_backend.sh
  # 1. 链接插件到OJ的apps目录
  ln -s $(pwd)/backend/choice_plugin ../qduoj/apps/
  # 2. 动态添加App到OJ的settings.py（与原OJINSTALLED_APPS格式一致）
  sed -i '/INSTALLED_APPS/a \    "apps.choice_plugin",' ../qduoj/conf/settings.py
  # 3. 动态添加API路由到OJ的主urls.py
  sed -i '/urlpatterns/a \path("api/plugin/choice/", include("apps.choice_plugin.api.urls")),\' ../qduoj/conf/urls.py
  # 4. 执行数据库迁移（遵循原OJ迁移流程）
  cd ../qduoj/ && python manage.py migrate choice_plugin
  ```


#### 3.2 前端集成
- 构建前端资源：
  ```bash
  cd frontend/ && npm run build  # 输出到 ../dist/frontend/
  ```
- 挂载资源到OJ静态目录：
  ```bash
  # install_frontend.sh
  # 1. 复制前端资源到OJ的static/plugin/choice/
  cp -r ../dist/frontend/static/* ../qduoj/static/plugin/choice/
  # 2. 动态引入插件入口（若原OJ支持插件加载机制，优先使用）
  sed -i '</body>/i \    <script src="/static/plugin/choice/js/main.js"></script>' ../qduoj/templates/index.html
  ```


### 阶段4：插件安装/卸载/升级（完整生命周期）
#### 4.1 一键安装脚本（`install.sh`）
```bash
#!/bin/bash
echo "开始安装选择题插件..."

# 1. 安装后端依赖（与原OJ环境兼容）
cd backend/ && pip install -r requirements.txt
# 2. 执行后端集成
./install_backend.sh
# 3. 构建并集成前端
cd ../frontend/ && npm install && npm run build
../install_frontend.sh

echo "插件安装完成！访问OJ的「题库→选择题」即可使用"
```

#### 4.2 一键卸载脚本（`uninstall.sh`）
```bash
#!/bin/bash
echo "开始卸载选择题插件..."

# 1. 清理后端
cd backend/ && ./uninstall_backend.sh  # 反向执行install_backend.sh操作
# 2. 清理前端资源
rm -rf ../qduoj/static/plugin/choice/
sed -i '/static\/plugin\/choice\/js\/main.js/d' ../qduoj/templates/index.html
# 3. 清理数据库表（按plugin.json声明的前缀）
cd ../qduoj/ && python manage.py dbshell -c "DROP TABLE IF EXISTS choice_plugin_category, choice_plugin_question, choice_plugin_wrongbook;"

echo "插件卸载完成！"
```

#### 4.3 版本升级脚本（`upgrade.sh`）
```bash
#!/bin/bash
echo "开始升级选择题插件..."

# 1. 拉取最新代码
git pull
# 2. 升级后端依赖
cd backend/ && pip install -r requirements.txt --upgrade
# 3. 执行数据库迁移（处理版本差异）
cd ../qduoj/ && python manage.py migrate choice_plugin
# 4. 重构前端
cd ../frontend/ && npm install && npm run build
# 5. 刷新静态资源
cp -r ../dist/frontend/static/* ../qduoj/static/plugin/choice/

echo "插件升级完成！当前版本：$(cat plugin.json | jq -r '.version')"
```


## 七、调研任务补充（插件化关键信息）
在原有调研基础上，需重点确认以下信息：
1. **原OJ插件支持机制**：
   - 是否有官方插件目录（如`plugins/`）或`PluginManager`类？
   - `settings.py`是否支持动态引入外部App（如通过`EXTRA_APPS`配置）？
   - 主`urls.py`是否提供动态路由注册接口（如`register_url`函数）？

2. **前端集成能力**：
   - Vue实例是否暴露全局对象（如`window.OJ`）供插件挂载？
   - 菜单系统是否有`menuService.add`等API支持动态菜单？
   - Vuex是否允许注册命名空间模块（避免冲突）？

3. **权限与安全**：
   - 用户认证Token是否在`Authorization`头中携带（插件API需复用）？
   - 原OJ的权限判断逻辑（如`user.has_perm`）是否可直接调用？

4. **静态资源规范**：
   - 静态文件访问是否需要特定前缀（如`STATIC_URL`）？
   - 前端构建是否有特殊配置（如Webpack别名、公共组件路径）？


## 八、验证要点
| 验证模块       | 检查项                                                                 |
|----------------|-----------------------------------------------------------------------|
| 插件独立性     | 1. 插件目录是否完全独立，不修改原OJ核心文件？<br>2. 卸载后原OJ功能是否正常，无残留数据？ |
| 可插拔性       | 1. 执行`install.sh`能否一键安装成功？<br>2. 执行`uninstall.sh`能否完全清理？          |
| 规范一致性     | 1. 后端Model/API是否遵循原OJ命名与格式规范？<br>2. 前端UI/交互是否与原OJ风格统一？     |
| 功能完整性     | 1. 所有选择题功能是否正常（分类、答题、错题本）？<br>2. 数据统计是否与原OJ用户关联？    |
| 兼容性         | 1. 插件版本与OJ版本是否匹配（如Django/Vue版本）？<br>2. 插件API是否与原OJ接口无冲突？  |


## 九、使用建议
1. **开发顺序**：先完成“插件基础架构”（阶段1），确保目录独立、可挂载后，再开发核心功能（阶段2），避免后期重构；
2. **测试优先级**：优先测试“卸载功能”，确保插件不会破坏原OJ系统；
3. **版本管理**：每次迭代更新`plugin.json`的版本号，升级脚本通过版本号判断是否需要迁移数据；
4. **文档同步**：在插件根目录下保留`README.md`，说明安装步骤、功能清单、常见问题，便于其他用户使用。