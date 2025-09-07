<template>
  <div class="view">
    <Panel :title="$t('m.Topic_Practice_Management')">
      <div slot="header">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input 
              v-model="keyword" 
              prefix-icon="el-icon-search" 
              placeholder="搜索用户名或专题名称"
              @keyup.enter.native="filterByKeyword">
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-button type="primary" size="small" @click="filterByKeyword">{{$t('m.Search')}}</el-button>
          </el-col>
          <el-col :span="4">
            <el-button size="small" @click="resetFilter">重置</el-button>
          </el-col>
          <el-col :span="4">
            <el-button type="success" size="small" @click="exportRecords">导出记录</el-button>
          </el-col>
        </el-row>
      </div>
      
      <!-- 统计信息卡片 -->
      <div class="statistics-cards" style="margin-bottom: 20px;">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statistics.totalSessions }}</div>
                <div class="stat-label">总练习次数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statistics.totalUsers }}</div>
                <div class="stat-label">参与用户数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statistics.avgScore }}%</div>
                <div class="stat-label">平均得分</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ statistics.todaySessions }}</div>
                <div class="stat-label">今日练习</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 练习记录表格 -->
      <el-table
        v-loading="loadingTable"
        element-loading-text="loading"
        ref="table"
        :data="practiceRecords"
        style="width: 100%">
        <el-table-column width="80" prop="id" label="ID"></el-table-column>
        <el-table-column prop="username" label="用户" width="120">
          <template slot-scope="{row}">
            <el-link type="primary" @click="viewUserDetail(row.user_id)">{{ row.username }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="topic_name" label="专题名称" width="200">
          <template slot-scope="{row}">
            <el-tooltip :content="row.topic_full_path" placement="top">
              <span>{{ row.topic_name }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag 
              :type="scope.row.status === 'completed' ? 'success' : scope.row.status === 'started' ? 'warning' : 'info'" 
              size="small">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="得分" width="80">
          <template slot-scope="{row}">
            <span :class="getScoreClass(row.score)">{{ row.score }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="correct_count" label="正确/总数" width="100">
          <template slot-scope="{row}">
            {{ row.correct_count }}/{{ row.total_count }}
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="用时" width="100">
          <template slot-scope="{row}">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="160">
          <template slot-scope="scope">
            {{ scope.row.start_time | localtime }}
          </template>
        </el-table-column>
        <el-table-column prop="submit_time" label="提交时间" width="160">
          <template slot-scope="scope">
            {{ scope.row.submit_time | localtime }}
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="150">
          <template slot-scope="scope">
            <el-button size="mini" @click="viewDetail(scope.row)">详情</el-button>
            <el-button size="mini" type="danger" @click="deleteRecord(scope.row.id)">删除</el-button>
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

    <!-- 详情对话框 -->
    <el-dialog
      title="练习详情"
      :visible.sync="detailDialogVisible"
      width="80%"
      :close-on-click-modal="false">
      <div v-if="currentRecord">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户">{{ currentRecord.username }}</el-descriptions-item>
          <el-descriptions-item label="专题">{{ currentRecord.topic_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentRecord.status === 'completed' ? 'success' : 'warning'">
              {{ getStatusText(currentRecord.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="得分">{{ currentRecord.score }}%</el-descriptions-item>
          <el-descriptions-item label="正确题数">{{ currentRecord.correct_count }}/{{ currentRecord.total_count }}</el-descriptions-item>
          <el-descriptions-item label="用时">{{ formatDuration(currentRecord.duration) }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ currentRecord.start_time | localtime }}</el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ currentRecord.submit_time | localtime }}</el-descriptions-item>
        </el-descriptions>
        
        <!-- 答题详情 -->
        <div style="margin-top: 20px;" v-if="currentRecord.answers">
          <h4>答题详情</h4>
          <el-table :data="currentRecord.question_details" style="width: 100%">
            <el-table-column prop="question_id" label="题目ID" width="80"></el-table-column>
            <el-table-column prop="title" label="题目标题"></el-table-column>
            <el-table-column prop="user_answer" label="用户答案" width="100">
              <template slot-scope="{row}">
                <el-tag :type="row.is_correct ? 'success' : 'danger'" size="small">
                  {{ row.user_answer || '未答' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="correct_answer" label="正确答案" width="100"></el-table-column>
            <el-table-column prop="is_correct" label="结果" width="80">
              <template slot-scope="{row}">
                <i :class="row.is_correct ? 'el-icon-check' : 'el-icon-close'" 
                   :style="{color: row.is_correct ? '#67C23A' : '#F56C6C'}"></i>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import api from '../../api'

export default {
  name: 'TopicPracticeManagement',
  data() {
    return {
      practiceRecords: [],
      statistics: {
        totalSessions: 0,
        totalUsers: 0,
        avgScore: 0,
        todaySessions: 0
      },
      loadingTable: false,
      keyword: '',
      currentPage: 1,
      pageSize: 20,
      total: 0,
      detailDialogVisible: false,
      currentRecord: null
    }
  },
  mounted() {
    this.getPracticeRecords()
    this.getStatistics()
  },
  methods: {
    async getPracticeRecords() {
      this.loadingTable = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize
        }
        if (this.keyword) {
          params.keyword = this.keyword
        }
        
        // 调用后端API获取专题练习记录
        const res = await api.getTopicPracticeRecords(params)
        this.practiceRecords = res.data.data.results || []
        this.total = res.data.data.total || 0
      } catch (err) {
        this.$error('获取练习记录失败')
      } finally {
        this.loadingTable = false
      }
    },
    
    async getStatistics() {
      try {
        const res = await api.getTopicPracticeStatistics()
        this.statistics = res.data.data || this.statistics
      } catch (err) {
        console.error('获取统计信息失败', err)
      }
    },
    
    filterByKeyword() {
      this.currentPage = 1
      this.getPracticeRecords()
    },
    
    resetFilter() {
      this.keyword = ''
      this.currentPage = 1
      this.getPracticeRecords()
    },
    
    currentChange(page) {
      this.currentPage = page
      this.getPracticeRecords()
    },
    
    sizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
      this.getPracticeRecords()
    },
    
    async viewDetail(record) {
      try {
        // 获取详细的练习记录信息
        const res = await api.getTopicPracticeRecordDetail(record.id)
        this.currentRecord = res.data.data
        this.detailDialogVisible = true
      } catch (err) {
        this.$error('获取练习详情失败')
      }
    },
    
    viewUserDetail(userId) {
      // 跳转到用户详情页面
      this.$router.push(`/admin/user?id=${userId}`)
    },
    
    async deleteRecord(recordId) {
      this.$confirm('确定要删除这条练习记录吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await api.deleteTopicPracticeRecord(recordId)
          this.$success('删除成功')
          this.getPracticeRecords()
          this.getStatistics()
        } catch (err) {
          this.$error('删除失败')
        }
      })
    },
    
    async exportRecords() {
      try {
        const params = {}
        if (this.keyword) {
          params.keyword = this.keyword
        }
        
        const res = await api.exportTopicPracticeRecords(params)
        
        // 创建下载链接
        const blob = new Blob([res.data], { type: 'application/vnd.ms-excel' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `专题练习记录_${new Date().toISOString().split('T')[0]}.xlsx`
        link.click()
        window.URL.revokeObjectURL(url)
        
        this.$success('导出成功')
      } catch (err) {
        this.$error('导出失败')
      }
    },
    
    getStatusText(status) {
      const statusMap = {
        'started': '进行中',
        'completed': '已完成',
        'timeout': '超时'
      }
      return statusMap[status] || status
    },
    
    getScoreClass(score) {
      if (score >= 90) return 'score-excellent'
      if (score >= 80) return 'score-good'
      if (score >= 60) return 'score-pass'
      return 'score-fail'
    },
    
    formatDuration(duration) {
      if (!duration) return '-'
      const minutes = Math.floor(duration / 60)
      const seconds = duration % 60
      return `${minutes}分${seconds}秒`
    }
  }
}
</script>

<style scoped>
.statistics-cards {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  cursor: default;
}

.stat-content {
  padding: 10px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.score-excellent {
  color: #67C23A;
  font-weight: bold;
}

.score-good {
  color: #E6A23C;
  font-weight: bold;
}

.score-pass {
  color: #409EFF;
}

.score-fail {
  color: #F56C6C;
  font-weight: bold;
}

.panel-options {
  margin-top: 20px;
  text-align: right;
}

.page {
  display: inline-block;
}
</style>