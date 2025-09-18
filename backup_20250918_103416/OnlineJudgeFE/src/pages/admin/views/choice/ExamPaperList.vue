<template>
  <div class="view">
    <Panel :title="$t('m.Exam_Paper_List')">
      <div slot="header">
        <el-row :gutter="20">
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
          show-icon
          :closable="false">
          <template slot="default">
            <el-button-group>
              <el-button size="small" @click="clearSelection">取消选择</el-button>
              <el-button size="small" type="danger" @click="showBatchDeleteDialog" :loading="batchDeleting">批量删除</el-button>
            </el-button-group>
          </template>
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
            <span>{{ row.title }}</span>
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
            <el-tag :type="scope.row.visible ? 'success' : 'info'" size="small">
              {{ scope.row.visible ? '可见' : '隐藏' }}
            </el-tag>
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
    
    <!-- 批量删除确认对话框 -->
    <el-dialog
      title="批量删除确认"
      :visible.sync="batchDeleteDialogVisible"
      width="400px"
      :close-on-click-modal="false">
      <div style="text-align: center; padding: 20px 0;">
        <i class="el-icon-warning" style="font-size: 48px; color: #E6A23C; margin-bottom: 20px;"></i>
        <p style="font-size: 16px; margin-bottom: 20px;">
          您确定要删除选中的 <strong>{{ selectedPapers.length }}</strong> 份试卷吗？
        </p>
        <p style="color: #909399; font-size: 14px;">
          删除后试卷将无法恢复，但试题数据会保留在题库中
        </p>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="batchDeleteDialogVisible = false" :disabled="batchDeleting">取消</el-button>
        <el-button type="danger" @click="executeBatchDelete" :loading="batchDeleting">确认删除</el-button>
      </div>
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
      // 批量操作相关
      selectedPapers: [],
      batchDeleteDialogVisible: false,
      batchDeleting: false
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
        console.log('API响应:', res)
        console.log('API数据类型:', typeof res.data)
        console.log('API数据长度:', res.data.data ? res.data.data.length : 0)
        // 处理新的分页响应格式
        if (res.data.data.results) {
          this.examPaperList = res.data.data.results
          this.total = res.data.data.total
        } else {
          // 兼容旧格式
          this.examPaperList = res.data.data || []
          this.total = res.data.data ? res.data.data.length : 0
        }
        console.log('设置后的记录数:', this.total)
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

    // 批量操作相关方法
    handleSelectionChange(selection) {
      this.selectedPapers = selection
    },
    
    clearSelection() {
      this.$refs.table.clearSelection()
      this.selectedPapers = []
    },
    
    showBatchDeleteDialog() {
      if (this.selectedPapers.length === 0) {
        this.$message.warning('请先选择要删除的试卷')
        return
      }
      this.batchDeleteDialogVisible = true
    },
    
    async executeBatchDelete() {
      this.batchDeleting = true
      try {
        const response = await api.batchDeleteExamPapers(
          this.selectedPapers.map(paper => paper.id)
        )
        
        if (response.data.error === null) {
          this.$success(response.data.data.message || '批量删除成功')
          this.batchDeleteDialogVisible = false
          this.selectedPapers = []
          // 重新加载当前页数据
          this.loadPapers()
        } else {
          this.$error(response.data.data || '删除失败')
        }
      } catch (error) {
        console.error('批量删除失败:', error)
        if (error.response && error.response.data && error.response.data.data) {
          this.$error(error.response.data.data)
        } else {
          this.$error('删除失败，请稍后重试')
        }
      } finally {
        this.batchDeleting = false
      }
    },
    
    goImportExamPaper() {
      this.$router.push({ name: 'import-exam-paper' })
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