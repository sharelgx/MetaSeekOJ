<template>
  <div class="view">
    <Panel :title="$t('m.Exam_Paper_List')">
      <div slot="header">
        <el-row :gutter="20">
          <el-col :span="4">
            <el-button type="primary" size="small" @click="goCreateExamPaper" icon="el-icon-plus">创建试卷</el-button>
          </el-col>
          <el-col :span="4">
            <el-button type="success" size="small" @click="goImportExamPaper" icon="el-icon-upload2">导入试卷</el-button>
          </el-col>
          <el-col :span="6">
            <el-input v-model="keyword" prefix-icon="el-icon-search" placeholder="搜索试卷标题"></el-input>
          </el-col>
          <el-col :span="6">
            <el-button type="primary" size="small" @click="filterByKeyword">{{$t('m.Search')}}</el-button>
          </el-col>
        </el-row>
      </div>
      
      <!-- 批量操作工具栏 -->
      <div v-if="selectedPapers.length > 0" class="batch-toolbar">
        <el-alert
          :title="`已选择 ${selectedPapers.length} 份试卷`"
          type="info"
          :closable="false"
          show-icon>
          <div slot="default">
            <el-button-group>
              <el-button size="small" @click="clearSelection">取消选择</el-button>
              <el-button size="small" type="primary" @click="showBatchOperationDialog">批量操作</el-button>
              <el-button size="small" type="danger" @click="batchDelete">批量删除</el-button>
            </el-button-group>
          </div>
        </el-alert>
      </div>
      
      <el-table
        v-loading="loadingTable"
        element-loading-text="loading"
        ref="table"
        :data="examPaperList"
        @selection-change="handleSelectionChange"
        style="width: 100%">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column width="80" prop="id" label="ID"></el-table-column>
        <el-table-column prop="title" label="试卷标题" min-width="200">
          <template slot-scope="{row}">
            <a @click="goEdit(row.id)" class="entry">{{ row.title }}</a>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip>
          <template slot-scope="{row}">
            <span>{{ row.description || '暂无描述' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="考试时长" width="100" align="center">
          <template slot-scope="{row}">
            <el-tag size="small">{{ row.duration }}分钟</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="总分" width="80" align="center">
          <template slot-scope="{row}">
            <el-tag type="success" size="small">{{ row.total_score }}分</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="question_count" label="题目数" width="80" align="center">
          <template slot-scope="{row}">
            <el-tag type="info" size="small">{{ row.question_count }}题</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template slot-scope="{row}">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by.username" label="创建者" width="120"></el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180">
          <template slot-scope="scope">
            {{ scope.row.create_time | localtime }}
          </template>
        </el-table-column>
        <el-table-column prop="visible" label="可见" width="80" align="center">
          <template slot-scope="scope">
            <el-switch v-model="scope.row.visible" @change="updateExamPaper(scope.row)"></el-switch>
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="280">
          <template slot-scope="scope">
            <el-button-group>
              <el-button size="mini" type="primary" @click="goEdit(scope.row.id)">编辑</el-button>
              <el-button size="mini" type="success" @click="previewPaper(scope.row.id)">预览</el-button>
              <el-button size="mini" type="warning" @click="startExam(scope.row.id)">开始考试</el-button>
              <el-button size="mini" type="info" @click="viewResults(scope.row.id)">查看结果</el-button>
              <el-button size="mini" type="danger" @click="deleteExamPaper(scope.row.id)">删除</el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="panel-options">
        <el-pagination
          class="page"
          layout="prev, pager, next, sizes, total"
          @current-change="currentChange"
          @size-change="sizeChange"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total">
        </el-pagination>
      </div>
    </Panel>
    
    <!-- 批量操作对话框 -->
    <el-dialog
      title="批量操作"
      :visible.sync="batchDialogVisible"
      width="400px">
      <el-form :model="batchForm" label-width="80px">
        <el-form-item label="操作类型">
          <el-select v-model="batchForm.action" placeholder="请选择操作" style="width: 100%;">
            <el-option value="visible" label="设置可见性"></el-option>
            <el-option value="status" label="设置状态"></el-option>
            <el-option value="delete" label="删除试卷"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="可见性" v-if="batchForm.action === 'visible'">
          <el-select v-model="batchForm.visible" placeholder="请选择可见性" style="width: 100%;">
            <el-option :value="true" label="可见"></el-option>
            <el-option :value="false" label="隐藏"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态" v-if="batchForm.action === 'status'">
          <el-select v-model="batchForm.status" placeholder="请选择状态" style="width: 100%;">
            <el-option value="draft" label="草稿"></el-option>
            <el-option value="published" label="已发布"></el-option>
            <el-option value="archived" label="已归档"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      
      <span slot="footer" class="dialog-footer">
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="executeBatchOperation" :loading="batchOperating">确认操作</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import api from '../../api.js'

export default {
  name: 'ExamPaperList',
  data() {
    return {
      pageSize: 20,
      total: 0,
      examPaperList: [],
      keyword: '',
      loadingTable: false,
      currentPage: 1,
      // 批量操作相关数据
      selectedPapers: [],
      batchDialogVisible: false,
      batchOperating: false,
      batchForm: {
        action: '',
        visible: null,
        status: ''
      }
    }
  },
  
  mounted() {
    this.init()
  },
  
  methods: {
    init() {
      this.loadPapers()
    },
    
    async loadPapers() {
      this.loadingTable = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize
        }
        if (this.keyword) {
          params.keyword = this.keyword
        }
        
        const res = await api.getExamPaperList(params)
        this.examPaperList = res.data.data.results || []
        this.total = res.data.data.total || 0
      } catch (err) {
        console.error('获取试卷列表失败:', err)
        this.$error('获取试卷列表失败')
      } finally {
        this.loadingTable = false
      }
    },
    
    filterByKeyword() {
      this.currentPage = 1
      this.loadPapers()
    },
    
    currentChange(page) {
      this.currentPage = page
      this.loadPapers()
    },
    
    sizeChange(pageSize) {
      this.pageSize = pageSize
      this.currentPage = 1
      this.loadPapers()
    },
    
    handleSelectionChange(selection) {
      this.selectedPapers = selection
    },
    
    clearSelection() {
      this.$refs.table.clearSelection()
      this.selectedPapers = []
    },
    
    showBatchOperationDialog() {
      this.batchDialogVisible = true
      this.batchForm = {
        action: '',
        visible: null,
        status: ''
      }
    },
    
    async executeBatchOperation() {
      if (!this.batchForm.action) {
        this.$error('请选择操作类型')
        return
      }
      
      this.batchOperating = true
      try {
        const paperIds = this.selectedPapers.map(paper => paper.id)
        
        if (this.batchForm.action === 'delete') {
          await this.$confirm('确定要删除选中的试卷吗？', '确认删除', {
            type: 'warning'
          })
          await api.batchDeleteExamPapers(paperIds)
          this.$success('批量删除成功')
        } else {
          const updateData = {}
          if (this.batchForm.action === 'visible') {
            updateData.visible = this.batchForm.visible
          } else if (this.batchForm.action === 'status') {
            updateData.status = this.batchForm.status
          }
          
          await api.batchUpdateExamPapers(paperIds, updateData)
          this.$success('批量操作成功')
        }
        
        this.batchDialogVisible = false
        this.clearSelection()
        this.loadPapers()
      } catch (err) {
        console.error('批量操作失败:', err)
        this.$error('批量操作失败')
      } finally {
        this.batchOperating = false
      }
    },
    
    async batchDelete() {
      if (this.selectedPapers.length === 0) {
        this.$message.warning('请选择要删除的试卷')
        return
      }
      try {
        await this.$confirm(`确定要删除选中的 ${this.selectedPapers.length} 个试卷吗？`, '批量删除', {
          type: 'warning'
        })
        
        const paperIds = this.selectedPapers.map(paper => paper.id)
        await api.batchDeleteExamPapers(paperIds)
        this.$success('批量删除成功')
        this.clearSelection()
        this.loadPapers()
      } catch (err) {
        if (err !== 'cancel') {
          console.error('批量删除失败:', err)
          this.$error('批量删除失败')
        }
      }
    },
    
    goCreateExamPaper() {
      this.$router.push({ name: 'create-exam-paper' })
    },
    
    goImportExamPaper() {
      this.$router.push({ name: 'import-exam-paper' })
    },
    
    goEdit(paperId) {
      this.$router.push({ name: 'exam-paper-edit', params: { examPaperId: paperId } })
    },
    
    previewPaper(paperId) {
      const routeData = this.$router.resolve({
        name: 'exam-paper-preview',
        params: { examPaperId: paperId }
      })
      window.open(routeData.href, '_blank')
    },
    
    startExam(paperId) {
      this.$router.push({ name: 'exam-taking', params: { examPaperId: paperId } })
    },
    
    viewResults(paperId) {
      this.$router.push({ name: 'exam-results', params: { examPaperId: paperId } })
    },
    
    async updateExamPaper(paper) {
      try {
        await api.updateExamPaper(paper.id, { visible: paper.visible })
        this.$success('更新成功')
      } catch (err) {
        console.error('更新失败:', err)
        this.$error('更新失败')
        // 恢复原状态
        paper.visible = !paper.visible
      }
    },
    
    async deleteExamPaper(paperId) {
      try {
        await this.$confirm('确定要删除这份试卷吗？', '确认删除', {
          type: 'warning'
        })
        
        await api.deleteExamPaper(paperId)
        this.$success('删除成功')
        this.loadPapers()
      } catch (err) {
        if (err !== 'cancel') {
          console.error('删除失败:', err)
          this.$error('删除失败')
        }
      }
    },
    
    getStatusType(status) {
      const statusMap = {
        'draft': 'info',
        'published': 'success',
        'archived': 'warning'
      }
      return statusMap[status] || 'info'
    },
    
    getStatusText(status) {
      const statusMap = {
        'draft': '草稿',
        'published': '已发布',
        'archived': '已归档'
      }
      return statusMap[status] || '未知'
    }
  }
}
</script>

<style scoped>
.batch-toolbar {
  margin-bottom: 20px;
}

.entry {
  color: #409EFF;
  cursor: pointer;
  text-decoration: none;
}

.entry:hover {
  text-decoration: underline;
}

.panel-options {
  margin-top: 20px;
  text-align: right;
}

.el-button-group .el-button {
  margin-left: 0;
}
</style>