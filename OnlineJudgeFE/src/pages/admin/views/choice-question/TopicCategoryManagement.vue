<template>
  <div class="topic-category-management">
    <Panel :title="$t('m.Topic_Category_Management')">
      <div slot="header">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input 
              v-model="keyword" 
              prefix-icon="el-icon-search" 
              placeholder="搜索分类名称"
              @keyup.enter.native="filterByKeyword">
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-button type="primary" size="small" @click="filterByKeyword">搜索</el-button>
          </el-col>
          <el-col :span="4">
            <el-button size="small" @click="resetFilter">重置</el-button>
          </el-col>
          <el-col :span="4">
            <el-button type="success" size="small" @click="showCreateDialog">创建分类</el-button>
          </el-col>
        </el-row>
      </div>
      
      <!-- 分类树形结构表格 -->
      <el-table
        v-loading="loadingTable"
        element-loading-text="loading"
        ref="table"
        :data="categories"
        style="width: 100%"
        row-key="id"
        :tree-props="{children: 'children', hasChildren: 'hasChildren'}"
        default-expand-all>
        <el-table-column width="80" prop="id" label="ID"></el-table-column>
        <el-table-column prop="name" label="分类名称" min-width="200">
          <template slot-scope="{row}">
            <span :style="{fontWeight: row.level === 0 ? 'bold' : 'normal'}">
              {{ row.name }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" width="300">
          <template slot-scope="{row}">
            <el-tooltip :content="row.description" placement="top">
              <span>{{ row.description ? row.description.substring(0, 50) + '...' : '-' }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="question_count" label="题目数" width="80"></el-table-column>
        <el-table-column prop="order" label="排序" width="80"></el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template slot-scope="scope">
            <el-tag 
              :type="scope.row.is_active ? 'success' : 'info'" 
              size="small">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template slot-scope="{row}">
            <el-button size="mini" @click="editCategory(row)">编辑</el-button>
            <el-button size="mini" type="success" @click="addChildCategory(row)">添加子分类</el-button>
            <el-button size="mini" type="danger" @click="deleteCategory(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </Panel>
    
    <!-- 创建/编辑分类对话框 -->
    <el-dialog
      :title="editingCategory ? '编辑分类' : '创建分类'"
      :visible.sync="showDialog"
      width="600px"
      @close="resetForm">
      <el-form :model="categoryForm" :rules="rules" ref="categoryForm" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称"></el-input>
        </el-form-item>
        <el-form-item label="父级分类" prop="parent">
          <el-select v-model="categoryForm.parent" placeholder="请选择父级分类（留空为顶级分类）" style="width: 100%">
            <el-option label="无（顶级分类）" :value="null"></el-option>
            <el-option 
              v-for="category in availableParents"
              :key="category.id"
              :label="category.full_name || category.name"
              :value="category.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="分类描述" prop="description">
          <el-input 
            type="textarea" 
            v-model="categoryForm.description" 
            placeholder="请输入分类描述"
            :rows="3">
          </el-input>
        </el-form-item>
        <el-form-item label="排序权重" prop="order">
          <el-input-number v-model="categoryForm.order" :min="0" :step="1"></el-input-number>
          <span style="margin-left: 10px; color: #909399;">数字越小排序越靠前</span>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="categoryForm.is_active" active-text="启用" inactive-text="禁用"></el-switch>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import api from '../../api'
import { mapGetters } from 'vuex'

export default {
  name: 'TopicCategoryManagement',
  data() {
    return {
      categories: [],
      flatCategories: [],
      loadingTable: false,
      keyword: '',
      showDialog: false,
      editingCategory: null,
      submitting: false,
      parentCategory: null, // 用于添加子分类时指定父分类
      categoryForm: {
        name: '',
        parent: null,
        description: '',
        order: 0,
        is_active: true
      },
      rules: {
        name: [
          { required: true, message: '请输入分类名称', trigger: 'blur' },
          { min: 1, max: 100, message: '分类名称长度在 1 到 100 个字符', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    ...mapGetters(['user', 'isAuthenticated', 'isAdminRole']),
    availableParents() {
      // 过滤掉当前编辑的分类及其子分类
      if (!this.editingCategory) {
        return this.flatCategories
      }
      return this.flatCategories.filter(category => {
        return category.id !== this.editingCategory.id && 
               !this.isDescendantOf(category, this.editingCategory)
      })
    }
  },
  mounted() {
    this.loadCategories()
  },
  methods: {
    async loadCategories() {
      this.loadingTable = true
      try {
        const res = await api.getChoiceQuestionCategories()
        this.flatCategories = res.data.data || []
        this.categories = this.buildCategoryTree(this.flatCategories)
      } catch (err) {
        console.error('加载分类失败:', err)
        this.$error('加载分类失败')
      } finally {
        this.loadingTable = false
      }
    },
    
    buildCategoryTree(categories) {
      // 构建分类树形结构
      const map = {}
      const roots = []
      
      // 创建映射
      categories.forEach(category => {
        map[category.id] = { ...category, children: [] }
      })
      
      // 构建树形结构
      categories.forEach(category => {
        if (category.parent) {
          if (map[category.parent]) {
            map[category.parent].children.push(map[category.id])
          }
        } else {
          roots.push(map[category.id])
        }
      })
      
      // 排序
      const sortCategories = (categories) => {
        categories.sort((a, b) => {
          if (a.order !== b.order) {
            return a.order - b.order
          }
          return a.name.localeCompare(b.name)
        })
        categories.forEach(category => {
          if (category.children.length > 0) {
            sortCategories(category.children)
          }
        })
      }
      
      sortCategories(roots)
      return roots
    },
    
    isDescendantOf(category, ancestor) {
      // 检查一个分类是否是另一个分类的后代
      if (!category.parent) return false
      if (category.parent === ancestor.id) return true
      
      const parent = this.flatCategories.find(c => c.id === category.parent)
      return parent ? this.isDescendantOf(parent, ancestor) : false
    },
    
    filterByKeyword() {
      if (!this.keyword.trim()) {
        this.resetFilter()
        return
      }
      
      const filtered = this.flatCategories.filter(category =>
        category.name.toLowerCase().includes(this.keyword.toLowerCase()) ||
        (category.description && category.description.toLowerCase().includes(this.keyword.toLowerCase()))
      )
      this.categories = this.buildCategoryTree(filtered)
    },
    
    resetFilter() {
      this.keyword = ''
      this.categories = this.buildCategoryTree(this.flatCategories)
    },
    
    showCreateDialog() {
      this.editingCategory = null
      this.parentCategory = null
      this.resetForm()
      this.showDialog = true
    },
    
    addChildCategory(parent) {
      this.editingCategory = null
      this.parentCategory = parent
      this.resetForm()
      this.categoryForm.parent = parent.id
      this.showDialog = true
    },
    
    editCategory(category) {
      this.editingCategory = category
      this.parentCategory = null
      this.categoryForm = {
        name: category.name,
        parent: category.parent,
        description: category.description || '',
        order: category.order || 0,
        is_active: category.is_active
      }
      this.showDialog = true
    },
    
    async deleteCategory(category) {
      // 检查是否有子分类
      const hasChildren = this.flatCategories.some(c => c.parent === category.id)
      if (hasChildren) {
        this.$error('该分类下还有子分类，请先删除子分类')
        return
      }
      
      this.$confirm(`确定要删除分类"${category.name}"吗？`, '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await api.deleteChoiceQuestionCategory(category.id)
          this.$success('删除成功')
          this.loadCategories()
        } catch (err) {
          console.error('删除分类失败:', err)
          this.$error('删除失败: ' + (err.message || '未知错误'))
        }
      })
    },
    
    submitForm() {
      this.$refs.categoryForm.validate(async (valid) => {
        if (valid) {
          this.submitting = true
          try {
            if (this.editingCategory) {
              await api.updateChoiceQuestionCategory(this.editingCategory.id, this.categoryForm)
              this.$success('更新成功')
            } else {
              await api.createChoiceQuestionCategory(this.categoryForm)
              this.$success('创建成功')
            }
            this.showDialog = false
            this.loadCategories()
          } catch (err) {
            console.error('提交表单失败:', err)
            this.$error((this.editingCategory ? '更新失败' : '创建失败') + ': ' + (err.message || '未知错误'))
          } finally {
            this.submitting = false
          }
        }
      })
    },
    
    resetForm() {
      this.categoryForm = {
        name: '',
        parent: null,
        description: '',
        order: 0,
        is_active: true
      }
      if (this.$refs.categoryForm) {
        this.$refs.categoryForm.resetFields()
      }
    }
  }
}
</script>

<style scoped>
.topic-category-management {
  margin: 20px;
}

.dialog-footer {
  text-align: right;
}
</style>