<template>
  <div class="view">
    <Panel :title="$t('m.Category_Management')">
      <div slot="header">
        <el-button type="primary" @click="showCreateModal = true">
          <i class="el-icon-plus"></i>
          {{ $t('m.Create') }}
        </el-button>
      </div>
      
      <div class="category-list">
        <el-table :data="categories" style="width: 100%" v-loading="loading">
          <el-table-column prop="name" :label="$t('m.Name')" width="200"></el-table-column>
          <el-table-column prop="description" label="描述"></el-table-column>
          <el-table-column prop="parent_name" label="父分类" width="150"></el-table-column>
          <el-table-column label="操作" width="200">
            <template slot-scope="scope">
              <el-button size="mini" @click="editCategory(scope.row)">{{ $t('m.Edit') }}</el-button>
              <el-button size="mini" type="danger" @click="deleteCategory(scope.row)">{{ $t('m.Delete') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </Panel>

    <!-- 创建/编辑分类模态框 -->
    <el-dialog
      :title="editingCategory ? $t('m.Edit') : $t('m.Create')"
      :visible.sync="showCreateModal"
      width="500px"
      @close="resetForm"
    >
      <el-form ref="categoryForm" :model="categoryForm" :rules="categoryRules" label-width="80px">
        <el-form-item :label="$t('m.Name')" prop="name">
          <el-input v-model="categoryForm.name" :placeholder="$t('m.Name')"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="categoryForm.description" type="textarea" :rows="3" placeholder="分类描述"></el-input>
        </el-form-item>
        <el-form-item label="父分类" prop="parent">
          <el-select v-model="categoryForm.parent" clearable placeholder="选择父分类" style="width: 100%">
            <el-option v-for="category in flatCategories" :key="category.id" :value="category.id" :label="category.name">
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showCreateModal = false">{{ $t('m.Cancel') }}</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">{{ $t('m.OK') }}</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import api from '@admin/api'

export default {
  name: 'CategoryManagement',
  data() {
    return {
      categories: [],
      flatCategories: [],
      showCreateModal: false,
      editingCategory: null,
      loading: false,
      submitting: false,
      categoryForm: {
        name: '',
        description: '',
        parent: null
      },
      categoryRules: {
        name: [
          { required: true, message: '请输入分类名称', trigger: 'blur' }
        ]
      }
    }
  },
  mounted() {
    this.getCategories()
  },
  methods: {
    async getCategories() {
      this.loading = true
      try {
        const res = await api.getChoiceQuestionCategories()
        this.categories = res.data.data || []
        // 添加父分类名称
        this.categories.forEach(category => {
          if (category.parent) {
            const parent = this.categories.find(c => c.id === category.parent)
            category.parent_name = parent ? parent.name : ''
          } else {
            category.parent_name = ''
          }
        })
        this.buildFlatCategories()
      } catch (err) {
        this.$error('获取分类列表失败')
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    buildFlatCategories() {
      this.flatCategories = this.categories.filter(cat => !this.editingCategory || cat.id !== this.editingCategory.id)
    },

    editCategory(category) {
      this.editingCategory = category
      this.categoryForm = {
        name: category.name,
        description: category.description || '',
        parent: category.parent
      }
      this.buildFlatCategories()
      this.showCreateModal = true
    },
    async deleteCategory(category) {
      this.$confirm(`确定要删除分类 "${category.name}" 吗？`, '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await api.deleteChoiceQuestionCategory(category.id)
          this.$message.success('删除成功')
          this.getCategories()
        } catch (err) {
          this.$message.error('删除失败')
          console.error(err)
        }
      }).catch(() => {})
    },
    async handleSubmit() {
      this.$refs.categoryForm.validate(async (valid) => {
        if (valid) {
          this.submitting = true
          try {
            if (this.editingCategory) {
              await api.updateChoiceQuestionCategory(this.editingCategory.id, this.categoryForm)
              this.$message.success('更新成功')
            } else {
              await api.createChoiceQuestionCategory(this.categoryForm)
              this.$message.success('创建成功')
            }
            this.showCreateModal = false
            this.resetForm()
            this.getCategories()
          } catch (err) {
            this.$message.error(this.editingCategory ? '更新失败' : '创建失败')
            console.error(err)
          } finally {
            this.submitting = false
          }
        }
      })
    },
    resetForm() {
      this.editingCategory = null
      this.categoryForm = {
        name: '',
        description: '',
        parent: null
      }
      this.$refs.categoryForm && this.$refs.categoryForm.resetFields()
    }
  }
}
</script>

<style scoped>
.category-list {
  margin-top: 20px;
}
</style>