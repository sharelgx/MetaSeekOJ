<template>
  <div class="tag-management">
    <Panel title="选择题标签管理">
      <div slot="header">
        <el-button type="primary" size="small" @click="showCreateDialog" icon="el-icon-plus">
          添加标签
        </el-button>
        <el-button 
          type="danger" 
          size="small" 
          @click="batchDelete" 
          :disabled="selectedTags.length === 0"
          icon="el-icon-delete">
          批量删除 ({{ selectedTags.length }})
        </el-button>
      </div>
      
      <!-- 标签类型筛选 -->
      <div class="filter-section">
        <el-radio-group v-model="filterType" @change="getTags">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button label="difficulty">难度</el-radio-button>
          <el-radio-button label="subject">学科</el-radio-button>
          <el-radio-button label="knowledge">知识点</el-radio-button>
          <el-radio-button label="custom">自定义</el-radio-button>
        </el-radio-group>
        
        <el-input
          v-model="searchKeyword"
          placeholder="搜索标签名称"
          style="width: 200px; margin-left: 20px"
          @keyup.enter="getTags"
          clearable
          @clear="getTags">
          <el-button slot="append" icon="el-icon-search" @click="getTags"></el-button>
        </el-input>
      </div>
      
      <!-- 标签列表 -->
      <el-table
        :data="tagList"
        @selection-change="handleSelectionChange"
        v-loading="loading"
        style="width: 100%">
        
        <el-table-column type="selection" width="55"></el-table-column>
        
        <el-table-column prop="name" label="标签名称" min-width="150">
          <template slot-scope="scope">
            <el-tag 
              :style="{ backgroundColor: scope.row.color + '20', color: scope.row.color, border: `1px solid ${scope.row.color}` }"
              size="medium">
              {{ scope.row.name }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="type" label="类型" width="120">
          <template slot-scope="scope">
            <el-tag :type="getTypeTagType(scope.row.type)" size="small">
              {{ getTypeLabel(scope.row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" min-width="200">
          <template slot-scope="scope">
            {{ scope.row.description || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="color" label="颜色" width="100" align="center">
          <template slot-scope="scope">
            <div 
              class="color-block" 
              :style="{ backgroundColor: scope.row.color }"
              @click="showColorPicker(scope.row)">
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="question_count" label="题目数" width="100" align="center">
          <template slot-scope="scope">
            <el-button type="text" @click="showRelatedQuestions(scope.row)">
              {{ scope.row.question_count || 0 }}
            </el-button>
          </template>
        </el-table-column>
        
        <el-table-column prop="is_enabled" label="状态" width="100" align="center">
          <template slot-scope="scope">
            <el-switch
              v-model="scope.row.is_enabled"
              @change="toggleEnabled(scope.row)">
            </el-switch>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_time" label="创建时间" width="160">
          <template slot-scope="scope">
            {{ formatDate(scope.row.created_time) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template slot-scope="scope">
            <el-button type="text" size="small" @click="showEditDialog(scope.row)">
              编辑
            </el-button>
            <el-button type="text" size="small" style="color: #F56C6C" @click="deleteTag(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total">
        </el-pagination>
      </div>
    </Panel>
    
    <!-- 创建/编辑对话框 -->
    <el-dialog 
      :title="dialogTitle" 
      :visible.sync="dialogVisible"
      width="500px"
      @close="resetForm">
      <el-form :model="tagForm" :rules="rules" ref="tagForm" label-width="100px">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="tagForm.name" placeholder="请输入标签名称"></el-input>
        </el-form-item>
        
        <el-form-item label="标签类型" prop="type">
          <el-select v-model="tagForm.type" placeholder="请选择标签类型" style="width: 100%">
            <el-option label="难度" value="difficulty"></el-option>
            <el-option label="学科" value="subject"></el-option>
            <el-option label="知识点" value="knowledge"></el-option>
            <el-option label="自定义" value="custom"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="标签颜色" prop="color">
          <el-color-picker v-model="tagForm.color"></el-color-picker>
          <span style="margin-left: 10px; color: #909399">{{ tagForm.color }}</span>
        </el-form-item>
        
        <el-form-item label="标签描述">
          <el-input 
            type="textarea" 
            v-model="tagForm.description" 
            :rows="3"
            placeholder="请输入标签描述">
          </el-input>
        </el-form-item>
        
        <el-form-item label="是否启用">
          <el-switch v-model="tagForm.is_enabled"></el-switch>
        </el-form-item>
      </el-form>
      
      <span slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTag" :loading="submitLoading">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </span>
    </el-dialog>
    
    <!-- 颜色选择器弹窗 -->
    <el-dialog 
      title="修改标签颜色" 
      :visible.sync="colorPickerVisible"
      width="300px">
      <el-color-picker 
        v-model="tempColor" 
        show-alpha
        :predefine="predefineColors">
      </el-color-picker>
      <span slot="footer">
        <el-button @click="colorPickerVisible = false">取消</el-button>
        <el-button type="primary" @click="updateTagColor">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'TagManagement',
  data() {
    return {
      tagList: [],
      selectedTags: [],
      loading: false,
      dialogVisible: false,
      colorPickerVisible: false,
      isEdit: false,
      submitLoading: false,
      
      // 筛选和分页
      filterType: '',
      searchKeyword: '',
      currentPage: 1,
      pageSize: 20,
      total: 0,
      
      // 表单数据
      tagForm: {
        name: '',
        type: 'custom',
        color: '#409EFF',
        description: '',
        is_enabled: true
      },
      
      // 临时颜色和选中的标签
      tempColor: '#409EFF',
      selectedTagForColor: null,
      
      // 预定义颜色
      predefineColors: [
        '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399',
        '#00CED1', '#FF6347', '#FFD700', '#9370DB', '#32CD32'
      ],
      
      // 表单验证规则
      rules: {
        name: [
          { required: true, message: '请输入标签名称', trigger: 'blur' },
          { min: 1, max: 30, message: '长度在 1 到 30 个字符', trigger: 'blur' }
        ],
        type: [
          { required: true, message: '请选择标签类型', trigger: 'change' }
        ],
        color: [
          { required: true, message: '请选择标签颜色', trigger: 'change' }
        ]
      }
    }
  },
  
  computed: {
    dialogTitle() {
      return this.isEdit ? '编辑标签' : '创建标签'
    }
  },
  
  mounted() {
    this.getTags()
  },
  
  methods: {
    // 获取标签列表
    async getTags() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          limit: this.pageSize
        }
        
        if (this.filterType) {
          params.type = this.filterType
        }
        
        if (this.searchKeyword) {
          params.keyword = this.searchKeyword
        }
        
        const res = await api.getTagList(params)
        this.tagList = res.data.results || []
        this.total = res.data.total || 0
      } catch (err) {
        this.$error(err.message || '获取标签列表失败')
      } finally {
        this.loading = false
      }
    },
    
    // 获取类型标签样式
    getTypeTagType(type) {
      const typeMap = {
        difficulty: 'danger',
        subject: 'success',
        knowledge: 'warning',
        custom: 'info'
      }
      return typeMap[type] || 'info'
    },
    
    // 获取类型标签文本
    getTypeLabel(type) {
      const labelMap = {
        difficulty: '难度',
        subject: '学科',
        knowledge: '知识点',
        custom: '自定义'
      }
      return labelMap[type] || '自定义'
    },
    
    // 显示创建对话框
    showCreateDialog() {
      this.isEdit = false
      this.resetForm()
      this.dialogVisible = true
    },
    
    // 显示编辑对话框
    showEditDialog(tag) {
      this.isEdit = true
      this.tagForm = {
        id: tag.id,
        name: tag.name,
        type: tag.type,
        color: tag.color,
        description: tag.description || '',
        is_enabled: tag.is_enabled !== false
      }
      this.dialogVisible = true
    },
    
    // 提交标签
    async submitTag() {
      this.$refs.tagForm.validate(async valid => {
        if (!valid) return
        
        this.submitLoading = true
        try {
          if (this.isEdit) {
            await api.updateTag(this.tagForm.id, this.tagForm)
            this.$success('标签更新成功')
          } else {
            await api.createTag(this.tagForm)
            this.$success('标签创建成功')
          }
          this.dialogVisible = false
          this.getTags()
        } catch (err) {
          this.$error(err.message || '操作失败')
        } finally {
          this.submitLoading = false
        }
      })
    },
    
    // 删除标签
    deleteTag(tag) {
      if (tag.question_count > 0) {
        this.$warning(`该标签下有 ${tag.question_count} 道题目，请先处理题目`)
        return
      }
      
      this.$confirm(`确定删除标签 "${tag.name}" 吗？`, '删除确认', {
        type: 'warning'
      }).then(async () => {
        try {
          await api.deleteTag(tag.id)
          this.$success('标签删除成功')
          this.getTags()
        } catch (err) {
          this.$error(err.message || '删除失败')
        }
      })
    },
    
    // 批量删除
    batchDelete() {
      const hasQuestions = this.selectedTags.some(tag => tag.question_count > 0)
      if (hasQuestions) {
        this.$warning('选中的标签中有关联题目，请先处理题目')
        return
      }
      
      this.$confirm(`确定删除选中的 ${this.selectedTags.length} 个标签吗？`, '批量删除确认', {
        type: 'warning'
      }).then(async () => {
        try {
          const ids = this.selectedTags.map(tag => tag.id)
          await api.batchDeleteTags({ ids })
          this.$success('批量删除成功')
          this.getTags()
        } catch (err) {
          this.$error(err.message || '批量删除失败')
        }
      })
    },
    
    // 切换启用状态
    async toggleEnabled(tag) {
      try {
        await api.updateTag(tag.id, {
          is_enabled: tag.is_enabled
        })
        this.$success(`标签已${tag.is_enabled ? '启用' : '禁用'}`)
      } catch (err) {
        this.$error(err.message || '操作失败')
        tag.is_enabled = !tag.is_enabled // 恢复原状
      }
    },
    
    // 显示颜色选择器
    showColorPicker(tag) {
      this.selectedTagForColor = tag
      this.tempColor = tag.color
      this.colorPickerVisible = true
    },
    
    // 更新标签颜色
    async updateTagColor() {
      try {
        await api.updateTag(this.selectedTagForColor.id, {
          color: this.tempColor
        })
        this.selectedTagForColor.color = this.tempColor
        this.$success('颜色更新成功')
        this.colorPickerVisible = false
      } catch (err) {
        this.$error(err.message || '颜色更新失败')
      }
    },
    
    // 显示关联题目
    showRelatedQuestions(tag) {
      this.$router.push({
        path: '/admin/choice-question',
        query: { tag_id: tag.id }
      })
    },
    
    // 处理选择变化
    handleSelectionChange(selection) {
      this.selectedTags = selection
    },
    
    // 处理分页大小变化
    handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      this.getTags()
    },
    
    // 处理页码变化
    handleCurrentChange(page) {
      this.currentPage = page
      this.getTags()
    },
    
    // 重置表单
    resetForm() {
      this.tagForm = {
        name: '',
        type: 'custom',
        color: '#409EFF',
        description: '',
        is_enabled: true
      }
      this.$refs.tagForm && this.$refs.tagForm.clearValidate()
    },
    
    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style lang="less" scoped>
.tag-management {
  .filter-section {
    margin-bottom: 20px;
    display: flex;
    align-items: center;
  }
  
  .color-block {
    width: 30px;
    height: 30px;
    border-radius: 4px;
    cursor: pointer;
    margin: 0 auto;
    border: 1px solid #DCDFE6;
    transition: transform 0.3s;
    
    &:hover {
      transform: scale(1.1);
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    }
  }
  
  .pagination {
    margin-top: 20px;
    text-align: right;
  }
}
</style>