# UnifiedPagination 统一分页组件

这是一个统一的分页组件，可以同时支持前台的ul样式分页和后台的Element UI样式分页，实现组件复用。

## 功能特性

- **双模式支持**: 支持前台(frontend)和后台(backend)两种显示模式
- **样式统一**: 前台使用自定义按钮样式，后台使用Element UI分页组件
- **功能完整**: 支持页码跳转、每页条数选择、总数显示等功能
- **响应式设计**: 移动端适配优化
- **易于使用**: 统一的API接口，简化使用方式

## Props 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| mode | String | 'frontend' | 分页模式，可选值：'frontend'、'backend' |
| currentPage | Number | 1 | 当前页码 |
| pageSize | Number | 10 | 每页显示条数（后台模式使用） |
| total | Number | 0 | 总条数 |
| pageSizes | Array | [10, 20, 30, 50] | 每页显示个数选择器的选项（后台模式使用） |
| layout | String | 'total, sizes, prev, pager, next, jumper' | 组件布局（后台模式使用） |

## Events 事件

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| current-change | 当前页改变时触发 | 新的页码 |
| size-change | 每页条数改变时触发（仅后台模式） | 新的每页条数 |

## 使用示例

### 前台模式使用

```vue
<template>
  <div>
    <!-- 数据列表 -->
    <div class="data-list">
      <div v-for="item in currentPageData" :key="item.id">
        {{ item.name }}
      </div>
    </div>
    
    <!-- 前台分页组件 -->
    <UnifiedPagination
      mode="frontend"
      :current-page="currentPage"
      :total="totalItems"
      :page-size="pageSize"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script>
import UnifiedPagination from '@/components/UnifiedPagination.vue'

export default {
  components: {
    UnifiedPagination
  },
  data() {
    return {
      currentPage: 1,
      pageSize: 10,
      totalItems: 100,
      dataList: []
    }
  },
  computed: {
    currentPageData() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.dataList.slice(start, end)
    }
  },
  methods: {
    handlePageChange(page) {
      this.currentPage = page
      // 可以在这里添加数据加载逻辑
      this.loadData()
    },
    
    loadData() {
      // 加载数据的逻辑
    }
  }
}
</script>
```

### 后台模式使用

```vue
<template>
  <div>
    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%">
      <el-table-column prop="name" label="名称"></el-table-column>
      <el-table-column prop="status" label="状态"></el-table-column>
      <el-table-column prop="createTime" label="创建时间"></el-table-column>
    </el-table>
    
    <!-- 后台分页组件 -->
    <UnifiedPagination
      mode="backend"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @current-change="handleCurrentChange"
      @size-change="handleSizeChange"
    />
  </div>
</template>

<script>
import UnifiedPagination from '@/components/UnifiedPagination.vue'

export default {
  components: {
    UnifiedPagination
  },
  data() {
    return {
      currentPage: 1,
      pageSize: 20,
      total: 0,
      tableData: []
    }
  },
  methods: {
    handleCurrentChange(page) {
      this.currentPage = page
      this.fetchData()
    },
    
    handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      this.fetchData()
    },
    
    async fetchData() {
      try {
        const params = {
          page: this.currentPage,
          limit: this.pageSize
        }
        const res = await api.getData(params)
        this.tableData = res.data.results
        this.total = res.data.total
      } catch (error) {
        console.error('获取数据失败:', error)
      }
    }
  },
  
  mounted() {
    this.fetchData()
  }
}
</script>
```

## 迁移指南

### 从原有前台分页迁移

**原有代码:**
```vue
<!-- 原有的前台分页 -->
<div class="pagination">
  <button class="pagination-btn" @click="changePage(currentPage - 1)">
    <i class="fa fa-chevron-left"></i>
  </button>
  <!-- ... 更多按钮 -->
</div>
```

**迁移后:**
```vue
<!-- 使用统一分页组件 -->
<UnifiedPagination
  mode="frontend"
  :current-page="currentPage"
  :total="total"
  :page-size="pageSize"
  @current-change="changePage"
/>
```

### 从原有后台分页迁移

**原有代码:**
```vue
<!-- 原有的后台分页 -->
<el-pagination
  :current-page="currentPage"
  :page-size="pageSize"
  :total="total"
  @current-change="handleCurrentChange"
  @size-change="handleSizeChange"
/>
```

**迁移后:**
```vue
<!-- 使用统一分页组件 -->
<UnifiedPagination
  mode="backend"
  :current-page="currentPage"
  :page-size="pageSize"
  :total="total"
  @current-change="handleCurrentChange"
  @size-change="handleSizeChange"
/>
```

## 样式定制

组件提供了完整的CSS样式，可以通过以下方式进行定制：

```vue
<style>
/* 自定义前台分页按钮颜色 */
.unified-pagination .pagination-btn {
  border-color: #your-color;
}

.unified-pagination .pagination-btn.active {
  background-color: #your-active-color;
}

/* 自定义后台分页样式 */
.unified-pagination .pagination-wrapper {
  text-align: left; /* 改为左对齐 */
}
</style>
```

## 注意事项

1. **FontAwesome依赖**: 前台模式需要项目中引入FontAwesome图标库
2. **Element UI依赖**: 后台模式需要项目中引入Element UI组件库
3. **响应式适配**: 组件已内置移动端适配，在小屏幕下会自动调整样式
4. **事件处理**: 确保正确处理`current-change`和`size-change`事件
5. **数据同步**: 页码变化时需要同步更新父组件的数据

## 优势

1. **代码复用**: 一个组件支持两种场景，减少重复代码
2. **维护简单**: 统一的API和样式，降低维护成本
3. **功能完整**: 支持所有常用的分页功能
4. **易于扩展**: 可以轻松添加新的分页模式或功能
5. **向后兼容**: 可以平滑替换现有的分页组件