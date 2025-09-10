<template>
  <div class="unified-pagination">
    <!-- 前台样式分页 (ul风格) -->
    <div v-if="mode === 'frontend'" class="pagination">
      <button 
        class="pagination-btn" 
        :disabled="currentPage <= 1"
        @click="handlePageChange(currentPage - 1)"
      >
        <i class="fa fa-chevron-left"></i>
      </button>
      <button 
        v-for="page in visiblePages" 
        :key="page"
        class="pagination-btn"
        :class="{ active: page === currentPage }"
        @click="handlePageChange(page)"
      >
        {{ page }}
      </button>
      <button 
        class="pagination-btn"
        :disabled="currentPage >= totalPages"
        @click="handlePageChange(currentPage + 1)"
      >
        <i class="fa fa-chevron-right"></i>
      </button>
    </div>

    <!-- 后台样式分页 (Element UI风格) -->
    <div v-else-if="mode === 'backend'" class="pagination-wrapper">
      <el-pagination
        :current-page="currentPage"
        :page-sizes="pageSizes"
        :page-size="pageSize"
        :layout="layout"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handlePageChange">
      </el-pagination>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UnifiedPagination',
  props: {
    // 分页模式: 'frontend' | 'backend'
    mode: {
      type: String,
      default: 'frontend',
      validator: value => ['frontend', 'backend'].includes(value)
    },
    // 当前页码
    currentPage: {
      type: Number,
      default: 1
    },
    // 每页显示条数 (后台模式使用)
    pageSize: {
      type: Number,
      default: 10
    },
    // 总条数
    total: {
      type: Number,
      default: 0
    },
    // 每页显示个数选择器的选项设置 (后台模式使用)
    pageSizes: {
      type: Array,
      default: () => [10, 20, 30, 50]
    },
    // 组件布局 (后台模式使用)
    layout: {
      type: String,
      default: 'total, sizes, prev, pager, next, jumper'
    }
  },
  computed: {
    // 总页数
    totalPages() {
      if (this.mode === 'backend') {
        return Math.ceil(this.total / this.pageSize)
      }
      // 前台模式需要外部传入总页数或通过total和pageSize计算
      return Math.ceil(this.total / (this.pageSize || 10))
    },
    
    // 可见页码数组 (前台模式使用)
    visiblePages() {
      if (this.mode !== 'frontend') return []
      
      const current = this.currentPage
      const total = this.totalPages
      const pages = []
      
      if (total <= 7) {
        for (let i = 1; i <= total; i++) {
          pages.push(i)
        }
      } else {
        if (current <= 4) {
          for (let i = 1; i <= 5; i++) {
            pages.push(i)
          }
        } else if (current >= total - 3) {
          for (let i = total - 4; i <= total; i++) {
            pages.push(i)
          }
        } else {
          for (let i = current - 2; i <= current + 2; i++) {
            pages.push(i)
          }
        }
      }
      
      return pages
    }
  },
  methods: {
    // 页码改变处理
    handlePageChange(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        this.$emit('current-change', page)
      }
    },
    
    // 每页条数改变处理 (后台模式使用)
    handleSizeChange(newSize) {
      this.$emit('size-change', newSize)
    }
  }
}
</script>

<style scoped>
/* 前台分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding: 16px;
  margin: 0 20px;
}

.pagination-btn {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  border: 1px solid #e5e6eb;
  background-color: #fff;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.pagination-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.pagination-btn.active {
  background-color: #1890ff;
  color: #fff;
  border-color: #1890ff;
}

.pagination-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
  border-color: #e5e6eb;
  color: #ccc;
}

.pagination-btn:disabled:hover {
  border-color: #e5e6eb;
  color: #ccc;
}

/* FontAwesome图标样式 */
.fa {
  font-family: 'FontAwesome' !important;
  font-style: normal;
  font-weight: normal;
  display: inline-block;
}

/* 后台分页样式 */
.pagination-wrapper {
  text-align: center;
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .pagination {
    flex-wrap: wrap;
    padding: 10px;
    margin: 0 10px;
  }
  
  .pagination-btn {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }
}
</style>