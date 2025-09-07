<template>
  <div class="topic-category-management">
    <el-row :gutter="20">
      <!-- 分类树 -->
      <el-col :span="12">
        <el-card header="分类树">
          <div slot="header">
            <span>分类树</span>
            <el-button 
              style="float: right; padding: 3px 0" 
              type="text" 
              @click="showCreateDialog()">
              添加根分类
            </el-button>
          </div>
          
          <el-tree
            :data="categoryTree"
            node-key="id"
            :props="treeProps"
            :expand-on-click-node="false"
            default-expand-all
            ref="categoryTree">
            <span class="tree-node" slot-scope="{ node, data }">
              <span class="node-label">
                <i :class="data.is_active ? 'el-icon-folder-opened' : 'el-icon-folder'"></i>
                {{ data.name }}
                <el-tag v-if="!data.is_active" size="mini" type="info">禁用</el-tag>
                <el-tag size="mini">{{ data.topic_count || 0 }}个专题</el-tag>
              </span>
              <span class="node-actions">
                <el-button
                  type="text"
                  size="mini"
                  @click="showCreateDialog(data)">
                  添加子分类
                </el-button>
                <el-button
                  type="text"
                  size="mini"
                  @click="editCategory(data)">
                  编辑
                </el-button>
                <el-button
                  type="text"
                  size="mini"
                  @click="deleteCategory(data)">
                  删除
                </el-button>
              </span>
            </span>
          </el-tree>
        </el-card>
      </el-col>
      
      <!-- 分类详情 -->
      <el-col :span="12">
        <el-card header="分类详情">
          <div v-if="selectedCategory">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="分类名称">{{ selectedCategory.name }}</el-descriptions-item>
              <el-descriptions-item label="完整路径">{{ selectedCategory.full_name }}</el-descriptions-item>
              <el-descriptions-item label="父分类">{{ selectedCategory.parent_name || '无' }}</el-descriptions-item>
              <el-descriptions-item label="分类描述">{{ selectedCategory.description || '无' }}</el-descriptions-item>
              <el-descriptions-item label="排序">{{ selectedCategory.order }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="selectedCategory.is_active ? 'success' : 'info'">
                  {{ selectedCategory.is_active ? '启用' : '禁用' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="层级">{{ selectedCategory.level }}</el-descriptions-item>
              <el-descriptions-item label="子分类数">{{ selectedCategory.children_count }}</el-descriptions-item>
              <el-descriptions-item label="题目数">{{ selectedCategory.question_count }}</el-descriptions-item>
              <el-descriptions-item label="专题数">{{ selectedCategory.topic_count }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ selectedCategory.create_time | localtime }}</el-descriptions-item>
            </el-descriptions>
            
            <div style="margin-top: 20px;">
              <el-button type="primary" @click="editCategory(selectedCategory)">编辑分类</el-button>
              <el-button type="danger" @click="deleteCategory(selectedCategory)">删除分类</el-button>
            </div>
          </div>
          <div v-else class="no-selection">
            <p>请从左侧选择一个分类查看详情</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建/编辑分类对话框 -->
    <el-dialog 
      :title="dialogMode === 'create' ? '创建分类' : '编辑分类'" 
      :visible.sync="showCategoryDialog"
      width="50%">
      <el-form 
        :model="categoryForm" 
        :rules="categoryFormRules" 
        ref="categoryForm" 
        label-width="100px">
        
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称"></el-input>
        </el-form-item>
        
        <el-form-item label="父分类">
          <el-cascader
            v-model="categoryForm.parent_path"
            :options="categoryOptions"
            :props="cascaderProps"
            placeholder="请选择父分类（留空为根分类）"
            clearable
            change-on-select>
          </el-cascader>
        </el-form-item>
        
        <el-form-item label="分类描述">
          <el-input 
            type="textarea" 
            v-model="categoryForm.description" 
            :rows="3"
            placeholder="请输入分类描述（可选）">
          </el-input>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number 
                v-model="categoryForm.order" 
                :min="0"
                placeholder="排序值">
              </el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否启用">
              <el-switch v-model="categoryForm.is_active"></el-switch>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="showCategoryDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCategory" :loading="submitting">
          {{ dialogMode === 'create' ? '创建' : '更新' }}
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import api from '@admin/api'

export default {
  name: 'TopicCategoryManagement',
  data () {
    return {
      // 分类树数据
      categoryTree: [],
      selectedCategory: null,
      
      // 树配置
      treeProps: {
        children: 'children',
        label: 'name'
      },
      
      // 表单数据
      showCategoryDialog: false,
      dialogMode: 'create', // create, edit
      categoryForm: {
        name: '',
        parent_id: null,
        parent_path: [],
        description: '',
        order: 0,
        is_active: true
      },
      categoryFormRules: {
        name: [
          { required: true, message: '请输入分类名称', trigger: 'blur' },
          { min: 1, max: 100, message: '分类名称长度在 1 到 100 个字符', trigger: 'blur' }
        ]
      },
      submitting: false,
      
      // 级联选择器数据
      categoryOptions: [],
      cascaderProps: {
        value: 'id',
        label: 'name',
        children: 'children',
        checkStrictly: true
      }
    }
  },
  
  mounted () {
    this.loadCategoryTree()
  },
  
  methods: {
    async loadCategoryTree () {
      try {
        const res = await api.getTopicCategoryTree({ include_topic_count: true })
        this.categoryTree = res.data.data
        this.buildCategoryOptions()
      } catch (err) {
        this.$error('加载分类树失败: ' + (err.response && err.response.data && err.response.data.error || err.message))
      }
    },
    
    buildCategoryOptions () {
      // 构建级联选择器的选项数据
      const buildOptions = (categories) => {
        return categories.map(category => ({
          id: category.id,
          name: category.name,
          children: category.children && category.children.length > 0 ? buildOptions(category.children) : undefined
        }))
      }
      
      this.categoryOptions = buildOptions(this.categoryTree)
    },
    
    // 分类操作
    showCreateDialog (parentCategory = null) {
      this.dialogMode = 'create'
      this.resetCategoryForm()
      
      if (parentCategory) {
        this.categoryForm.parent_id = parentCategory.id
        // 构建父分类路径
        this.categoryForm.parent_path = this.getCategoryPath(parentCategory.id)
      }
      
      this.showCategoryDialog = true
    },
    
    editCategory (category) {
      this.dialogMode = 'edit'
      this.selectedCategory = category
      
      this.categoryForm = {
        id: category.id,
        name: category.name,
        parent_id: category.parent,
        parent_path: category.parent ? this.getCategoryPath(category.parent) : [],
        description: category.description || '',
        order: category.order || 0,
        is_active: category.is_active
      }
      
      this.showCategoryDialog = true
    },
    
    getCategoryPath (categoryId, tree = this.categoryTree, path = []) {
      for (const category of tree) {
        const currentPath = [...path, category.id]
        if (category.id === categoryId) {
          return currentPath
        }
        if (category.children && category.children.length > 0) {
          const result = this.getCategoryPath(categoryId, category.children, currentPath)
          if (result) {
            return result
          }
        }
      }
      return null
    },
    
    resetCategoryForm () {
      this.categoryForm = {
        name: '',
        parent_id: null,
        parent_path: [],
        description: '',
        order: 0,
        is_active: true
      }
      if (this.$refs.categoryForm) {
        this.$refs.categoryForm.clearValidate()
      }
    },
    
    async submitCategory () {
      if (!this.$refs.categoryForm) return
      
      this.$refs.categoryForm.validate(async (valid) => {
        if (!valid) return
        
        this.submitting = true
        try {
          const formData = {
            name: this.categoryForm.name,
            description: this.categoryForm.description,
            order: this.categoryForm.order,
            is_active: this.categoryForm.is_active
          }
          
          // 处理父分类ID
          if (this.categoryForm.parent_path && this.categoryForm.parent_path.length > 0) {
            formData.parent_id = this.categoryForm.parent_path[this.categoryForm.parent_path.length - 1]
          }
          
          if (this.dialogMode === 'create') {
            await api.createTopicCategory(formData)
            this.$success('分类创建成功')
          } else {
            await api.updateTopicCategory(this.categoryForm.id, formData)
            this.$success('分类更新成功')
          }
          
          this.showCategoryDialog = false
          this.loadCategoryTree()
          this.$emit('category-updated')
        } catch (err) {
          this.$error('操作失败: ' + (err.response && err.response.data && err.response.data.error || err.message))
        } finally {
          this.submitting = false
        }
      })
    },
    
    async deleteCategory (category) {
      try {
        await this.$confirm(
          `确定要删除分类 "${category.name}" 吗？此操作将同时删除所有子分类。`, 
          '确认删除', 
          { type: 'warning' }
        )
        
        await api.deleteTopicCategory(category.id)
        this.$success('删除成功')
        this.loadCategoryTree()
        this.$emit('category-updated')
        
        if (this.selectedCategory && this.selectedCategory.id === category.id) {
          this.selectedCategory = null
        }
      } catch (err) {
        if (err !== 'cancel') {
          this.$error('删除失败: ' + (err.response && err.response.data && err.response.data.error || err.message))
        }
      }
    },
    
    // 树节点点击
    handleNodeClick (data) {
      this.selectedCategory = data
    }
  }
}
</script>

<style lang="less" scoped>
.topic-category-management {
  .tree-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 14px;
    padding-right: 8px;
    
    .node-label {
      display: flex;
      align-items: center;
      gap: 8px;
      
      i {
        color: #409eff;
      }
    }
    
    .node-actions {
      .el-button {
        padding: 0;
        margin-left: 8px;
      }
    }
  }
  
  .no-selection {
    text-align: center;
    color: #999;
    padding: 50px 0;
  }
}
</style>
