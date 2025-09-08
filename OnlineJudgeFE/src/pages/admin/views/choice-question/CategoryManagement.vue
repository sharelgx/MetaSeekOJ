<template>
  <div class="category-management">
    <div style="margin-bottom: 20px;">
      <el-button type="primary" @click="showCreateDialog">
        <i class="el-icon-plus"></i> 添加分类
      </el-button>
      <el-button @click="refreshCategories">
        <i class="el-icon-refresh"></i> 刷新
      </el-button>
    </div>
    

    
    <el-table
        :data="flattenCategories"
        v-loading="loading"
        row-key="id"
        border
        class="category-table"
      >
      <el-table-column label="分类名称" min-width="280">
         <template slot-scope="scope">
           <div class="category-name-cell">
             <i class="el-icon-rank drag-handle" title="拖拽排序" @mousedown="startDrag(scope.row, scope.$index)"></i>
             <i :class="getCategoryIcon(scope.row)" class="category-icon"></i>
             <span class="category-name">{{ scope.row.displayName || scope.row.name }}</span>
             <el-tag v-if="scope.row.children && scope.row.children.length > 0" size="mini" type="info" class="children-count">
               {{ scope.row.children.length }}个子分类
             </el-tag>
           </div>
         </template>
       </el-table-column>
      <el-table-column prop="description" label="描述" min-width="150">
        <template slot-scope="scope">
          <span class="description-text">{{ scope.row.description || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="question_count" label="题目数量" width="100" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.question_count > 0 ? 'success' : 'info'" size="mini">
            {{ scope.row.question_count || 0 }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="排序" width="120" align="center">
         <template slot-scope="scope">
           <div class="sort-controls">
             <el-input-number
               v-model="scope.row.sort_order"
               :min="0"
               :max="9999"
               size="mini"
               controls-position="right"
               @change="handleSortChange(scope.row)"
               style="width: 80px;"
             ></el-input-number>
           </div>
         </template>
       </el-table-column>
      <el-table-column label="状态" width="80" align="center">
        <template slot-scope="scope">
          <el-switch
            v-model="scope.row.is_enabled"
            @change="handleStatusChange(scope.row)"
            active-color="#13ce66"
            inactive-color="#ff4949">
          </el-switch>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" align="center">
        <template slot-scope="scope">
          <el-button size="mini" type="success" @click="handleAddChild(scope.row)">
            <i class="el-icon-plus"></i> 子分类
          </el-button>
          <el-button size="mini" type="primary" @click="handleEdit(scope.row)">
            <i class="el-icon-edit"></i> 编辑
          </el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)">
            <i class="el-icon-delete"></i> 删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 创建/编辑对话框 -->
    <el-dialog 
      :title="dialogTitle" 
      :visible.sync="dialogVisible"
      width="500px"
      @close="resetForm">
      <el-form :model="categoryForm" :rules="rules" ref="categoryForm" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称"></el-input>
        </el-form-item>
        
        <el-form-item label="父级分类">
          <el-select v-model="categoryForm.parent" placeholder="不选择则为顶级分类" clearable style="width: 100%">
            <el-option
              v-for="category in parentOptions"
              :key="category.id"
              :label="category.name"
              :value="category.id"
              :disabled="category.id === editingCategoryId">
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="分类描述">
          <el-input 
            type="textarea" 
            v-model="categoryForm.description" 
            :rows="3"
            placeholder="请输入分类描述">
          </el-input>
        </el-form-item>
        
        <el-form-item label="排序值">
          <el-input-number 
            v-model="categoryForm.sort_order" 
            :min="0" 
            :max="9999"
            placeholder="排序值，数字越小越靠前">
          </el-input-number>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch 
            v-model="categoryForm.is_enabled"
            active-text="启用"
            inactive-text="禁用">
          </el-switch>
        </el-form-item>
      </el-form>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import api from '../../api'
import draggable from 'vuedraggable'

export default {
  name: 'CategoryManagement',
  components: {
    draggable
  },
  data() {
    return {
      categories: [],
      loading: false,
      dialogVisible: false,
      editingCategoryId: null,
      submitting: false,
      dragOptions: {
        animation: 200,
        group: 'categories',
        disabled: false,
        ghostClass: 'ghost'
      },
      categoryForm: {
        name: '',
        description: '',
        parent: null,
        sort_order: 0,
        is_enabled: true
      },
      formRules: {
        name: [
          { required: true, message: '请输入分类名称', trigger: 'blur' },
          { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
        ]
      }
    }
  },
  
  computed: {
    dialogTitle() {
      return this.editingCategoryId ? '编辑分类' : '创建分类'
    },
    
    flattenCategories() {
      // 扁平化分类数据用于表格显示，确保按sort_order排序
      const flatten = (categories, level = 0) => {
        let result = []
        // 先按sort_order排序
        const sortedCategories = [...categories].sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
        
        sortedCategories.forEach(category => {
          const flatCategory = {
            ...category,
            level: level,
            displayName: '　'.repeat(level) + category.name
          }
          result.push(flatCategory)
          if (category.children && category.children.length > 0) {
            result = result.concat(flatten(category.children, level + 1))
          }
        })
        return result
      }
      return flatten(this.categories)
    },
    
    parentOptions() {
      // 递归获取所有分类，但排除当前编辑的分类及其子分类
      const getAllCategories = (categories, level = 0) => {
        let result = []
        categories.forEach(category => {
          if (category.id !== this.editingCategoryId) {
            result.push({
              id: category.id,
              name: '　'.repeat(level) + category.name,
              level: level
            })
            if (category.children && category.children.length > 0) {
              result = result.concat(getAllCategories(category.children, level + 1))
            }
          }
        })
        return result
      }
      return getAllCategories(this.categories)
    }
  },
  
  mounted() {
    this.getCategories()
  },
  
  methods: {
    getCategoryIcon(category) {
      if (category.children && category.children.length > 0) {
        return 'el-icon-folder'
      }
      return 'el-icon-document'
    },
    
    async handleSortChange(category) {
      try {
        // 先更新本地数据以立即反映UI变化
        const updateCategory = (categories) => {
          categories.forEach(cat => {
            if (cat.id === category.id) {
              cat.sort_order = category.sort_order
            }
            if (cat.children && cat.children.length > 0) {
              updateCategory(cat.children)
            }
          })
        }
        updateCategory(this.categories)
        
        // 强制触发Vue响应式更新
        this.$forceUpdate()
        
        // 然后更新到数据库
        await api.updateChoiceQuestionCategory(category.id, {
          sort_order: category.sort_order
        })
        this.$message.success('排序更新成功')
      } catch (error) {
        console.error('更新排序失败:', error)
        this.$message.error('更新排序失败')
        // 发生错误时刷新数据恢复原状态
        this.getCategories()
      }
    },
    
    async handleStatusChange(category) {
       try {
         await api.updateChoiceQuestionCategory(category.id, {
           is_enabled: category.is_enabled
         })
         this.$message.success('状态更新成功')
       } catch (error) {
         console.error('更新状态失败:', error)
         this.$message.error('更新状态失败')
         // 回滚状态
         category.is_enabled = !category.is_enabled
       }
     },
     
     startDrag(category, index) {
       // 简化的拖拽实现，使用上下移动按钮
       this.showMoveDialog(category, index)
     },
     
     showMoveDialog(category, currentIndex) {
       const options = []
       this.categories.forEach((cat, index) => {
         if (index !== currentIndex) {
           options.push({
             label: `移动到 "${cat.name}" ${index < currentIndex ? '前面' : '后面'}`,
             value: index
           })
         }
       })
       
       this.$prompt('选择新位置', '移动分类', {
         confirmButtonText: '确定',
         cancelButtonText: '取消',
         inputType: 'select',
         inputOptions: options
       }).then(({ value }) => {
         this.moveCategory(currentIndex, parseInt(value))
       }).catch(() => {
         // 用户取消
       })
     },
     
     async moveCategory(fromIndex, toIndex) {
       if (fromIndex === toIndex) {
         return
       }
       
       // 保存原始数据用于回滚
       const originalCategories = [...this.categories]
       
       try {
         // 立即更新本地排序
         const updatedCategories = [...this.categories]
         const movedItem = updatedCategories.splice(fromIndex, 1)[0]
         updatedCategories.splice(toIndex, 0, movedItem)
         
         // 重新计算排序值并更新本地数据
         updatedCategories.forEach((category, index) => {
           category.sort_order = index * 10
         })
         
         // 立即更新UI
         this.categories = updatedCategories
         
         // 后台更新服务器数据
         const updatePromises = updatedCategories.map((category, index) => {
           const newSortOrder = index * 10
           return api.updateChoiceQuestionCategory(category.id, {
             sort_order: newSortOrder
           })
         })
         
         await Promise.all(updatePromises)
         this.$message.success('排序更新成功')
         // 不再重新获取数据，保持当前排序
       } catch (error) {
         console.error('移动分类失败:', error)
         this.$message.error('排序更新失败')
         // 发生错误时回滚到原始数据
         this.categories = originalCategories
       }
     },
    
    async getCategories() {
      this.loading = true
      try {
        console.log('开始获取分类数据...')
        const res = await api.getChoiceQuestionCategories()
        console.log('API响应:', res)
        
        // 处理不同的数据结构
        let categoriesData = []
        if (res.data && res.data.data) {
          if (Array.isArray(res.data.data)) {
            categoriesData = res.data.data
          } else if (res.data.data.results && Array.isArray(res.data.data.results)) {
            categoriesData = res.data.data.results
          }
        }
        
        console.log('处理后的分类数据:', categoriesData)
        const treeData = this.buildTree(categoriesData)
        console.log('构建的树结构:', treeData)
        
        // 使用Vue.set强制触发响应式更新
        this.$set(this, 'categories', treeData)
        
        // 强制重新渲染
        this.$forceUpdate()
        
        console.log('更新后的categories:', this.categories)
        
      } catch (error) {
        console.error('获取分类列表失败:', error)
        this.$message.error('获取分类列表失败: ' + (error.message || '未知错误'))
        this.categories = []
      } finally {
        this.loading = false
      }
    },
    
    buildTree(categories) {
      console.log('buildTree输入数据:', categories)
      
      if (!Array.isArray(categories) || categories.length === 0) {
        console.log('分类数据为空或不是数组')
        return []
      }
      
      const map = {}
      const roots = []
      
      // 创建映射，确保字段名正确映射
      categories.forEach(category => {
        console.log('处理分类:', category)
        map[category.id] = { 
          ...category, 
          children: [],
          hasChildren: false, // 初始化hasChildren属性
          sort_order: category.order || category.sort_order || 0, // 支持多种字段名
          is_enabled: category.is_active !== undefined ? category.is_active : 
                     (category.is_enabled !== undefined ? category.is_enabled : true),
          level: 0 // 添加层级字段
        }
      })
      
      console.log('映射表:', map)
      
      // 构建树结构
      categories.forEach(category => {
        if (category.parent) {
          if (map[category.parent]) {
            map[category.parent].children.push(map[category.id])
            map[category.parent].hasChildren = true // 设置父节点有子节点
            map[category.id].level = (map[category.parent].level || 0) + 1
          } else {
            console.warn('找不到父分类:', category.parent, '对于分类:', category.name)
            roots.push(map[category.id]) // 如果找不到父分类，作为根分类处理
          }
        } else {
          roots.push(map[category.id])
        }
      })
      
      // 按sort_order排序
      const sortCategories = (categories) => {
        categories.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
        categories.forEach(category => {
          if (category.children && category.children.length > 0) {
            sortCategories(category.children)
          }
        })
      }
      
      sortCategories(roots)
      console.log('构建完成的树结构:', roots)
      return roots
    },
    
    refreshCategories() {
      this.getCategories()
    },
    
    showCreateDialog() {
      this.editingCategoryId = null
      this.resetForm()
      this.dialogVisible = true
    },
    
    handleEdit(category) {
      this.editingCategoryId = category.id
      this.categoryForm = {
        name: category.name,
        description: category.description || '',
        parent: category.parent,
        sort_order: category.sort_order || 0,
        is_enabled: category.is_enabled
      }
      this.dialogVisible = true
    },
    
    handleAddChild(parentCategory) {
      this.editingCategoryId = null
      this.categoryForm = {
        name: '',
        description: '',
        parent: parentCategory.id,
        sort_order: 0,
        is_enabled: true
      }
      this.dialogVisible = true
    },
    
    async handleDelete(category) {
      if (category.children && category.children.length > 0) {
        this.$message.warning('该分类下还有子分类，请先删除子分类')
        return
      }
      
      if (category.question_count > 0) {
        this.$message.warning('该分类下还有题目，请先移除题目')
        return
      }
      
      try {
        await this.$confirm('确定要删除这个分类吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await api.deleteChoiceQuestionCategory(category.id)
        this.$message.success('删除成功')
        this.getCategories()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除分类失败:', error)
          this.$message.error('删除失败')
        }
      }
    },
    
    async handleSubmit() {
      try {
        await this.$refs.categoryForm.validate()
        this.submitting = true
        
        if (this.editingCategoryId) {
          await api.updateChoiceQuestionCategory(this.editingCategoryId, this.categoryForm)
          this.$message.success('更新成功')
        } else {
          await api.createChoiceQuestionCategory(this.categoryForm)
          this.$message.success('创建成功')
        }
        
        this.dialogVisible = false
        this.getCategories()
      } catch (error) {
        console.error('保存分类失败:', error)
        this.$message.error('保存失败')
      } finally {
        this.submitting = false
      }
    },
    
    resetForm() {
      this.categoryForm = {
        name: '',
        description: '',
        parent: null,
        sort_order: 0,
        is_enabled: true
      }
      if (this.$refs.categoryForm) {
        this.$refs.categoryForm.resetFields()
      }
    }
  }
}
</script>

<style lang="less" scoped>
.category-management {
  .category-table {
    .category-name-cell {
      display: flex;
      align-items: center;
      
      .drag-handle {
        color: #909399;
        margin-right: 8px;
        cursor: move;
        font-size: 14px;
        transition: color 0.3s;
        
        &:hover {
          color: #409EFF;
        }
      }
      
      .category-icon {
        color: #409EFF;
        margin-right: 8px;
        font-size: 16px;
      }
      
      .category-name {
        flex: 1;
        font-weight: 500;
        color: #303133;
      }
      
      .children-count {
        margin-left: 8px;
      }
    }
    
    .description-text {
      color: #606266;
      font-size: 13px;
    }
    
    .sort-controls {
      display: flex;
      justify-content: center;
    }
    
    // 表格行样式
    /deep/ .el-table__row {
      transition: background-color 0.3s;
      
      &:hover {
        background-color: #f5f7fa;
        
        .drag-handle {
          color: #409EFF;
        }
      }
    }
    
    // 拖拽时的样式
    .ghost {
      opacity: 0.5;
      background-color: #f0f9ff;
    }
  }
  
  // 按钮组样式优化
  .el-button + .el-button {
    margin-left: 8px;
  }
  
  // 对话框样式
  /deep/ .el-dialog {
    .el-dialog__header {
      background-color: #f8f9fa;
      border-bottom: 1px solid #e9ecef;
    }
  }
}
</style>
