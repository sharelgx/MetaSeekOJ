<template>
  <div class="view">
    <Panel :title="$t('m.Tag_Management')">
      <div slot="header">
        <el-button type="primary" @click="showCreateModal = true">
          <i class="el-icon-plus"></i>
          {{ $t('m.Create') }}
        </el-button>
      </div>
      
      <div class="search-bar">
        <el-input 
          v-model="searchKeyword" 
          :placeholder="$t('m.Search')" 
          @input="handleSearch"
          style="width: 300px; margin-bottom: 20px;"
          prefix-icon="el-icon-search"
        >
        </el-input>
      </div>

      <div class="tag-list">
        <el-table :data="filteredTags" style="width: 100%" v-loading="loading">
          <el-table-column prop="name" :label="$t('m.Name')" width="200"></el-table-column>
          <el-table-column prop="description" label="描述"></el-table-column>
          <el-table-column label="颜色" width="120">
            <template slot-scope="scope">
              <el-tag :color="scope.row.color || '#409EFF'" :style="{backgroundColor: scope.row.color || '#409EFF', color: '#fff'}">{{ scope.row.name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template slot-scope="scope">
              <el-button size="mini" @click="editTag(scope.row)">{{ $t('m.Edit') }}</el-button>
              <el-button size="mini" type="danger" @click="deleteTag(scope.row)">{{ $t('m.Delete') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </Panel>

    <!-- 创建/编辑标签模态框 -->
    <el-dialog
      :title="editingTag ? $t('m.Edit') : $t('m.Create')"
      :visible.sync="showCreateModal"
      width="500px"
      @close="resetForm"
    >
      <el-form ref="tagForm" :model="tagForm" :rules="tagRules" label-width="80px">
        <el-form-item :label="$t('m.Name')" prop="name">
          <el-input v-model="tagForm.name" :placeholder="$t('m.Name')"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="tagForm.description" type="textarea" :rows="3" placeholder="标签描述"></el-input>
        </el-form-item>
        <el-form-item label="颜色" prop="color">
          <el-color-picker v-model="tagForm.color" show-alpha></el-color-picker>
          <span style="margin-left: 10px;">{{ tagForm.color || '#409EFF' }}</span>
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
  name: 'TagManagement',
  data() {
    return {
      tags: [],
      filteredTags: [],
      searchKeyword: '',
      showCreateModal: false,
      editingTag: null,
      loading: false,
      submitting: false,
      tagForm: {
        name: '',
        description: '',
        color: '#409EFF'
      },
      tagRules: {
        name: [
          { required: true, message: '请输入标签名称', trigger: 'blur' }
        ]
      }
    }
  },
  mounted() {
    this.getTags()
  },
  methods: {
    async getTags() {
      this.loading = true
      try {
        const res = await api.getChoiceQuestionTags()
        this.tags = res.data.data || []
        this.filteredTags = [...this.tags]
      } catch (err) {
        this.$message.error('获取标签列表失败')
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      if (!this.searchKeyword.trim()) {
        this.filteredTags = [...this.tags]
      } else {
        this.filteredTags = this.tags.filter(tag => 
          tag.name.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
          (tag.description && tag.description.toLowerCase().includes(this.searchKeyword.toLowerCase()))
        )
      }
    },
    editTag(tag) {
      this.editingTag = tag
      this.tagForm = {
        name: tag.name,
        description: tag.description || '',
        color: tag.color || '#409EFF'
      }
      this.showCreateModal = true
    },
    async deleteTag(tag) {
      this.$confirm(`确定要删除标签 "${tag.name}" 吗？`, '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await api.deleteChoiceQuestionTag(tag.id)
          this.$message.success('删除成功')
          this.getTags()
        } catch (err) {
          this.$message.error('删除失败')
          console.error(err)
        }
      }).catch(() => {})
    },
    async handleSubmit() {
      this.$refs.tagForm.validate(async (valid) => {
        if (valid) {
          this.submitting = true
          try {
            if (this.editingTag) {
              await api.updateChoiceQuestionTag(this.editingTag.id, this.tagForm)
              this.$message.success('更新成功')
            } else {
              await api.createChoiceQuestionTag(this.tagForm)
              this.$message.success('创建成功')
            }
            this.showCreateModal = false
            this.resetForm()
            this.getTags()
          } catch (err) {
            this.$message.error(this.editingTag ? '更新失败' : '创建失败')
            console.error(err)
          } finally {
            this.submitting = false
          }
        }
      })
    },
    resetForm() {
      this.editingTag = null
      this.tagForm = {
        name: '',
        description: '',
        color: '#409EFF'
      }
      this.$refs.tagForm && this.$refs.tagForm.resetFields()
    }
  }
}
</script>

<style scoped>
.search-bar {
  margin-bottom: 20px;
}

.tag-list {
  margin-top: 20px;
}
</style>