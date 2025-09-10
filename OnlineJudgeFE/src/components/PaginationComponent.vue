<template>
  <div class="pagination-wrapper">
    <el-pagination
      :current-page="currentPage"
      :page-sizes="pageSizes"
      :page-size="pageSize"
      :layout="layout"
      :total="total"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange">
    </el-pagination>
  </div>
</template>

<script>
export default {
  name: 'PaginationComponent',
  props: {
    // 当前页码
    currentPage: {
      type: Number,
      default: 1
    },
    // 每页显示条数
    pageSize: {
      type: Number,
      default: 10
    },
    // 总条数
    total: {
      type: Number,
      default: 0
    },
    // 每页显示个数选择器的选项设置
    pageSizes: {
      type: Array,
      default: () => [10, 20, 30, 50]
    },
    // 组件布局，子组件名用逗号分隔
    layout: {
      type: String,
      default: 'total, sizes, prev, pager, next, jumper'
    }
  },
  methods: {
    // 每页条数改变时触发
    handleSizeChange(newSize) {
      this.$emit('size-change', newSize)
    },
    // 当前页改变时触发
    handleCurrentChange(newPage) {
      this.$emit('current-change', newPage)
    }
  }
}
</script>

<style scoped>
.pagination-wrapper {
  text-align: center;
  margin-top: 20px;
}
</style>