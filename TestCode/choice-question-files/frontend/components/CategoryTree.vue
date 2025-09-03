<template>
  <div class="category-tree">
    <div class="tree-header">
      <h4>
        <Icon type="ios-folder" />
        题目分类
      </h4>
      <Button 
        v-if="showClearButton && selectedCategory" 
        type="text" 
        size="small" 
        @click="clearSelection"
      >
        <Icon type="ios-close" />
        清除
      </Button>
    </div>
    
    <div class="tree-content">
      <!-- 全部分类选项 -->>
      <div 
        class="category-item all-category" 
        :class="{ 'active': !selectedCategory }"
        @click="selectCategory(null)"
      >
        <Icon type="ios-list" class="category-icon" />
        <span class="category-name">全部分类</span>
        <span class="category-count" v-if="totalCount !== undefined">
          ({{ totalCount }})
        </span>
      </div>
      
      <!-- 分类列表 -->>
      <div class="category-list">
        <div 
          v-for="category in categories" 
          :key="category.id"
          class="category-item"
          :class="{ 
            'active': selectedCategory === category.id,
            'has-children': category.children && category.children.length > 0
          }"
          @click="selectCategory(category.id)"
        >
          <div class="category-main">
            <Icon 
              :type="category.children && category.children.length > 0 ? 'ios-folder' : 'ios-document'" 
              class="category-icon"
            />
            <span class="category-name">{{ category.name }}</span>
            <span class="category-count" v-if="category.question_count !== undefined">
              ({{ category.question_count }})
            </span>
          </div>
          
          <!-- 子分类 -->>
          <div 
            v-if="category.children && category.children.length > 0 && (expandedCategories.includes(category.id) || selectedCategory === category.id)"
            class="subcategory-list"
          >
            <div 
              v-for="subcategory in category.children" 
              :key="subcategory.id"
              class="category-item subcategory"
              :class="{ 'active': selectedCategory === subcategory.id }"
              @click.stop="selectCategory(subcategory.id)"
            >
              <Icon type="ios-document" class="category-icon" />
              <span class="category-name">{{ subcategory.name }}</span>
              <span class="category-count" v-if="subcategory.question_count !== undefined">
                ({{ subcategory.question_count }})
              </span>
            </div>
          </div>
          
          <!-- 展开/收起按钮 -->>
          <Button 
            v-if="category.children && category.children.length > 0"
            type="text" 
            size="small"
            class="expand-btn"
            @click.stop="toggleExpand(category.id)"
          >
            <Icon 
              :type="expandedCategories.includes(category.id) ? 'ios-arrow-up' : 'ios-arrow-down'" 
              size="14"
            />
          </Button>
        </div>
      </div>
      
      <!-- 加载状态 -->>
      <div v-if="loading" class="loading-state">
        <Spin size="small" />
        <span>加载中...</span>
      </div>
      
      <!-- 空状态 -->>
      <div v-if="!loading && categories.length === 0" class="empty-state">
        <Icon type="ios-folder-open" size="32" color="#c5c8ce" />
        <p>暂无分类</p>
      </div>
    </div>
    
    <!-- 搜索框 -->>
    <div class="tree-search" v-if="showSearch">
      <Input 
        v-model="searchKeyword"
        placeholder="搜索分类..."
        size="small"
        @on-change="handleSearch"
      >
        <Icon type="ios-search" slot="prefix" />
      </Input>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CategoryTree',
  props: {
    categories: {
      type: Array,
      default: () => []
    },
    selectedCategory: {
      type: [String, Number],
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    },
    showSearch: {
      type: Boolean,
      default: true
    },
    showClearButton: {
      type: Boolean,
      default: true
    },
    totalCount: {
      type: Number,
      default: undefined
    }
  },
  
  data() {
    return {
      expandedCategories: [],
      searchKeyword: '',
      searchTimer: null
    }
  },
  
  computed: {
    filteredCategories() {
      if (!this.searchKeyword) {
        return this.categories
      }
      
      return this.categories.filter(category => {
        const matchesName = category.name.toLowerCase().includes(this.searchKeyword.toLowerCase())
        const hasMatchingChildren = category.children && category.children.some(child => 
          child.name.toLowerCase().includes(this.searchKeyword.toLowerCase())
        )
        return matchesName || hasMatchingChildren
      })
    }
  },
  
  watch: {
    selectedCategory: {
      handler(newVal) {
        if (newVal) {
          // 自动展开包含选中分类的父分类
          this.autoExpandParent(newVal)
        }
      },
      immediate: true
    }
  },
  
  methods: {
    selectCategory(categoryId) {
      this.$emit('category-change', categoryId)
    },
    
    clearSelection() {
      this.$emit('category-change', null)
    },
    
    toggleExpand(categoryId) {
      const index = this.expandedCategories.indexOf(categoryId)
      if (index === -1) {
        this.expandedCategories.push(categoryId)
      } else {
        this.expandedCategories.splice(index, 1)
      }
    },
    
    autoExpandParent(selectedId) {
      // 查找包含选中分类的父分类并自动展开
      for (const category of this.categories) {
        if (category.children && category.children.some(child => child.id === selectedId)) {
          if (!this.expandedCategories.includes(category.id)) {
            this.expandedCategories.push(category.id)
          }
          break
        }
      }
    },
    
    handleSearch() {
      // 防抖搜索
      if (this.searchTimer) {
        clearTimeout(this.searchTimer)
      }
      
      this.searchTimer = setTimeout(() => {
        this.$emit('search', this.searchKeyword)
      }, 300)
    },
    
    // 展开所有分类
    expandAll() {
      this.expandedCategories = this.categories
        .filter(cat => cat.children && cat.children.length > 0)
        .map(cat => cat.id)
    },
    
    // 收起所有分类
    collapseAll() {
      this.expandedCategories = []
    }
  }
}
</script>

<style scoped>
.category-tree {
  background: #fff;
  border: 1px solid #e8eaec;
  border-radius: 6px;
  overflow: hidden;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f8f9;
  border-bottom: 1px solid #e8eaec;
}

.tree-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #17233d;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tree-content {
  max-height: 400px;
  overflow-y: auto;
}

.category-list {
  padding: 8px 0;
}

.category-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.category-item:hover {
  background: #f0f0f0;
}

.category-item.active {
  background: #e6f7ff;
  border-left-color: #2d8cf0;
  color: #2d8cf0;
}

.category-item.all-category {
  font-weight: 600;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 4px;
}

.category-main {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 8px;
}

.category-icon {
  color: #808695;
  flex-shrink: 0;
}

.category-item.active .category-icon {
  color: #2d8cf0;
}

.category-name {
  font-size: 13px;
  flex: 1;
}

.category-count {
  font-size: 12px;
  color: #c5c8ce;
  margin-left: auto;
}

.subcategory-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border-top: 1px solid #f0f0f0;
  z-index: 10;
}

.subcategory {
  padding-left: 40px !important;
  background: #fafafa;
  font-size: 12px;
}

.subcategory:hover {
  background: #f0f0f0;
}

.subcategory.active {
  background: #e6f7ff;
}

.expand-btn {
  padding: 2px 4px;
  min-width: auto;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: #808695;
  font-size: 13px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #c5c8ce;
}

.empty-state p {
  margin: 8px 0 0 0;
  font-size: 13px;
}

.tree-search {
  padding: 12px 16px;
  border-top: 1px solid #e8eaec;
  background: #fafafa;
}

/* 滚动条样式 */
.tree-content::-webkit-scrollbar {
  width: 6px;
}

.tree-content::-webkit-scrollbar-track {
  background: #f0f0f0;
}

.tree-content::-webkit-scrollbar-thumb {
  background: #c5c8ce;
  border-radius: 3px;
}

.tree-content::-webkit-scrollbar-thumb:hover {
  background: #808695;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .tree-content {
    max-height: 300px;
  }
  
  .category-item {
    padding: 10px 12px;
  }
  
  .subcategory {
    padding-left: 32px !important;
  }
}
</style>