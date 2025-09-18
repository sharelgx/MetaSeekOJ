<template>
  <el-select 
    :value="value" 
    @input="$emit('input', $event)"
    @change="$emit('change', $event)"
    :clearable="clearable"
    :placeholder="placeholder"
    :style="style"
    :size="size"
    :disabled="disabled"
    :multiple="multiple"
    :filterable="filterable"
  >
    <el-option 
      v-if="showAllOption" 
      :label="allOptionLabel" 
      :value="allOptionValue"
    ></el-option>
    <el-option
      v-for="category in flattenedCategories"
      :key="category.id"
      :label="category.displayName"
      :value="category.id"
      :disabled="category.disabled"
    >
    </el-option>
  </el-select>
</template>

<script>
import api from '../api'

export default {
  name: 'CategorySelector',
  props: {
    value: {
      type: [String, Number, Array],
      default: ''
    },
    // 基本属性
    clearable: {
      type: Boolean,
      default: true
    },
    placeholder: {
      type: String,
      default: '请选择分类'
    },
    style: {
      type: [String, Object],
      default: 'width: 150px;'
    },
    size: {
      type: String,
      default: 'small'
    },
    disabled: {
      type: Boolean,
      default: false
    },
    multiple: {
      type: Boolean,
      default: false
    },
    filterable: {
      type: Boolean,
      default: false
    },
    // 显示"全部"选项
    showAllOption: {
      type: Boolean,
      default: true
    },
    allOptionLabel: {
      type: String,
      default: '全部分类'
    },
    allOptionValue: {
      type: [String, Number],
      default: ''
    },
    // 分类数据源
    categories: {
      type: Array,
      default: () => []
    },
    // 是否自动加载分类数据
    autoLoad: {
      type: Boolean,
      default: true
    },
    // API端点
    apiEndpoint: {
      type: String,
      default: '/admin/choice_question/category/'
    },
    // 禁用的分类ID列表
    disabledIds: {
      type: Array,
      default: () => []
    }
  },
  
  data() {
    return {
      localCategories: [],
      loading: false
    }
  },
  
  computed: {
    // 使用传入的categories或本地加载的categories
    currentCategories() {
      return this.categories.length > 0 ? this.categories : this.localCategories
    },
    
    // 扁平化分类数据，支持层级显示
    flattenedCategories() {
      const categories = this.currentCategories
      if (!categories || categories.length === 0) {
        return []
      }
      
      // 递归去重处理 - 彻底清除所有层级的重复数据
      const globalSeenIds = new Set()
      const deepDeduplication = (cats) => {
        const result = []
        cats.forEach(cat => {
          if (!globalSeenIds.has(cat.id)) {
            globalSeenIds.add(cat.id)
            const cleanCat = { ...cat }
            if (cleanCat.children && cleanCat.children.length > 0) {
              cleanCat.children = deepDeduplication(cleanCat.children)
            }
            result.push(cleanCat)
          }
        })
        return result
      }
      
      const uniqueCategories = deepDeduplication(categories)
      
      // 如果数据已经是扁平化的（没有children属性），构建层级关系
      const hasChildren = uniqueCategories.some(cat => cat.children && cat.children.length > 0)
      if (!hasChildren) {
        // 对于扁平化数据，根据parent_id构建层级关系
        const categoryMap = new Map()
        const rootCategories = []
        
        // 先创建所有分类的映射
        uniqueCategories.forEach(cat => {
          categoryMap.set(cat.id, { ...cat, children: [] })
        })
        
        // 构建父子关系
        uniqueCategories.forEach(cat => {
          const categoryNode = categoryMap.get(cat.id)
          if (cat.parent_id && categoryMap.has(cat.parent_id)) {
            categoryMap.get(cat.parent_id).children.push(categoryNode)
          } else {
            rootCategories.push(categoryNode)
          }
        })
        
        // 递归扁平化
        const flatten = (categories, level = 0) => {
          let result = []
          const sortedCategories = [...categories].sort((a, b) => (a.order || 0) - (b.order || 0))
          
          sortedCategories.forEach(category => {
            const flatCategory = {
              ...category,
              level: level,
              displayName: '　'.repeat(level) + category.name,
              disabled: this.disabledIds.includes(category.id)
            }
            result.push(flatCategory)
            
            if (category.children && category.children.length > 0) {
              result = result.concat(flatten(category.children, level + 1))
            }
          })
          
          return result
        }
        
        return flatten(rootCategories)
      } else {
        // 对于已有层级结构的数据，只处理根分类（没有parent_id或parent_id为null的分类）
        const rootCategories = uniqueCategories.filter(cat => !cat.parent_id)
        
        const flatten = (categories, level = 0) => {
          let result = []
          const sortedCategories = [...categories].sort((a, b) => (a.order || 0) - (b.order || 0))
          
          sortedCategories.forEach(category => {
            const flatCategory = {
              ...category,
              level: level,
              displayName: '　'.repeat(level) + category.name,
              disabled: this.disabledIds.includes(category.id)
            }
            result.push(flatCategory)
            
            if (category.children && category.children.length > 0) {
              result = result.concat(flatten(category.children, level + 1))
            }
          })
          
          return result
        }
        
        return flatten(rootCategories)
      }
    }
  },
  
  mounted() {
    if (this.autoLoad && this.categories.length === 0) {
      this.loadCategories()
    }
  },
  
  methods: {
    async loadCategories() {
      if (this.loading) return
      
      this.loading = true
      try {
        const res = await api.getChoiceQuestionCategories()
        this.localCategories = res.data.data || []
      } catch (error) {
        console.error('加载分类失败:', error)
        this.$message.error('加载分类失败')
      } finally {
        this.loading = false
      }
    },
    
    // 刷新分类数据
    refresh() {
      this.loadCategories()
    },
    
    // 获取选中分类的完整信息
    getSelectedCategory() {
      if (!this.value) return null
      return this.flattenedCategories.find(cat => cat.id === this.value)
    },
    
    // 获取选中分类的名称
    getSelectedCategoryName() {
      const category = this.getSelectedCategory()
      return category ? category.name : ''
    }
  }
}
</script>

<style scoped>
/* 分类选择器样式 */
.el-select {
  width: 100%;
}

/* 层级缩进样式 */
.el-select-dropdown__item {
  font-family: 'Courier New', monospace;
}
</style>