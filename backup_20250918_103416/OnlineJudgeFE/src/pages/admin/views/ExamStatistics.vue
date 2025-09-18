<template>
  <div class="exam-statistics">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>考试统计仪表板</span>
      </div>
      
      <!-- 统计概览 -->
      <div class="stats-overview">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-icon total">
                <i class="el-icon-document"></i>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ totalExams }}</div>
                <div class="stat-label">总考试次数</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-icon active">
                <i class="el-icon-user"></i>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ activeUsers }}</div>
                <div class="stat-label">活跃用户数</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-icon average">
                <i class="el-icon-star-on"></i>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ averageScore }}%</div>
                <div class="stat-label">平均分数</div>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-icon papers">
                <i class="el-icon-files"></i>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ totalPapers }}</div>
                <div class="stat-label">试卷总数</div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="chart-card">
              <div slot="header">考试趋势</div>
              <div id="examTrendChart" style="height: 300px;"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="chart-card">
              <div slot="header">分数分布</div>
              <div id="scoreDistributionChart" style="height: 300px;"></div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <el-card class="chart-card">
              <div slot="header">题型统计</div>
              <div id="questionTypeChart" style="height: 300px;"></div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="chart-card">
              <div slot="header">难度分布</div>
              <div id="difficultyChart" style="height: 300px;"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 详细统计表格 -->
      <div class="detailed-stats">
        <el-card class="table-card">
          <div slot="header">
            <span>试卷统计详情</span>
            <el-button style="float: right; padding: 3px 0" type="text" @click="exportData">导出数据</el-button>
          </div>
          
          <el-table :data="paperStats" style="width: 100%" v-loading="loading">
            <el-table-column prop="title" label="试卷名称" width="200"></el-table-column>
            <el-table-column prop="exam_count" label="考试次数" width="100"></el-table-column>
            <el-table-column prop="average_score" label="平均分" width="100">
              <template slot-scope="scope">
                {{ scope.row.average_score }}%
              </template>
            </el-table-column>
            <el-table-column prop="pass_rate" label="通过率" width="100">
              <template slot-scope="scope">
                {{ scope.row.pass_rate }}%
              </template>
            </el-table-column>
            <el-table-column prop="difficulty" label="难度" width="100">
              <template slot-scope="scope">
                <el-tag :type="getDifficultyType(scope.row.difficulty)">{{ scope.row.difficulty }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_time" label="创建时间" width="150">
              <template slot-scope="scope">
                {{ formatDate(scope.row.created_time) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template slot-scope="scope">
                <el-button size="mini" @click="viewDetails(scope.row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
          
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
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import api from '@admin/api'

export default {
  name: 'ExamStatistics',
  data() {
    return {
      loading: false,
      totalExams: 0,
      activeUsers: 0,
      averageScore: 0,
      totalPapers: 0,
      paperStats: [],
      currentPage: 1,
      pageSize: 10,
      total: 0,
      examTrendChart: null,
      scoreDistributionChart: null,
      questionTypeChart: null,
      difficultyChart: null
    }
  },
  mounted() {
    this.loadStatistics()
    this.loadPaperStats()
    this.initCharts()
  },
  beforeDestroy() {
    if (this.examTrendChart) {
      this.examTrendChart.dispose()
    }
    if (this.scoreDistributionChart) {
      this.scoreDistributionChart.dispose()
    }
    if (this.questionTypeChart) {
      this.questionTypeChart.dispose()
    }
    if (this.difficultyChart) {
      this.difficultyChart.dispose()
    }
  },
  methods: {
    async loadStatistics() {
      try {
        const res = await api.getExamStatistics()
        this.totalExams = res.data.total_exams
        this.activeUsers = res.data.active_users
        this.averageScore = res.data.average_score
        this.totalPapers = res.data.total_papers
        
        // 更新图表数据
        this.updateCharts(res.data)
      } catch (err) {
        this.$error('加载统计数据失败')
      }
    },
    
    async loadPaperStats() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize
        }
        const res = await api.getPaperStatistics(params)
        this.paperStats = res.data.results
        this.total = res.data.total
      } catch (err) {
        this.$error('加载试卷统计失败')
      } finally {
        this.loading = false
      }
    },
    
    initCharts() {
      // 考试趋势图
      this.examTrendChart = echarts.init(document.getElementById('examTrendChart'))
      
      // 分数分布图
      this.scoreDistributionChart = echarts.init(document.getElementById('scoreDistributionChart'))
      
      // 题型统计图
      this.questionTypeChart = echarts.init(document.getElementById('questionTypeChart'))
      
      // 难度分布图
      this.difficultyChart = echarts.init(document.getElementById('difficultyChart'))
      
      // 监听窗口大小变化
      window.addEventListener('resize', this.handleResize)
    },
    
    updateCharts(data) {
      // 更新考试趋势图
      const trendOption = {
        title: {
          text: '近30天考试趋势'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: data.trend_dates || []
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          data: data.trend_counts || [],
          type: 'line',
          smooth: true,
          itemStyle: {
            color: '#409EFF'
          }
        }]
      }
      this.examTrendChart.setOption(trendOption)
      
      // 更新分数分布图
      const scoreOption = {
        title: {
          text: '分数分布'
        },
        tooltip: {
          trigger: 'item'
        },
        xAxis: {
          type: 'category',
          data: ['0-60', '60-70', '70-80', '80-90', '90-100']
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          data: data.score_distribution || [0, 0, 0, 0, 0],
          type: 'bar',
          itemStyle: {
            color: '#67C23A'
          }
        }]
      }
      this.scoreDistributionChart.setOption(scoreOption)
      
      // 更新题型统计图
      const typeOption = {
        title: {
          text: '题型分布'
        },
        tooltip: {
          trigger: 'item'
        },
        series: [{
          type: 'pie',
          radius: '50%',
          data: data.question_types || [],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      this.questionTypeChart.setOption(typeOption)
      
      // 更新难度分布图
      const difficultyOption = {
        title: {
          text: '难度分布'
        },
        tooltip: {
          trigger: 'item'
        },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          data: data.difficulty_distribution || [],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      this.difficultyChart.setOption(difficultyOption)
    },
    
    handleResize() {
      if (this.examTrendChart) {
        this.examTrendChart.resize()
      }
      if (this.scoreDistributionChart) {
        this.scoreDistributionChart.resize()
      }
      if (this.questionTypeChart) {
        this.questionTypeChart.resize()
      }
      if (this.difficultyChart) {
        this.difficultyChart.resize()
      }
    },
    
    handleSizeChange(val) {
      this.pageSize = val
      this.loadPaperStats()
    },
    
    handleCurrentChange(val) {
      this.currentPage = val
      this.loadPaperStats()
    },
    
    getDifficultyType(difficulty) {
      const typeMap = {
        '简单': 'success',
        '中等': 'warning',
        '困难': 'danger'
      }
      return typeMap[difficulty] || 'info'
    },
    
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN')
    },
    
    viewDetails(row) {
      this.$router.push({
        name: 'exam-paper-list',
        query: { id: row.id }
      })
    },
    
    exportData() {
      // 导出统计数据
      const csvContent = this.generateCSV()
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', '考试统计数据.csv')
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    
    generateCSV() {
      const headers = ['试卷名称', '考试次数', '平均分', '通过率', '难度', '创建时间']
      const rows = this.paperStats.map(item => [
        item.title,
        item.exam_count,
        item.average_score + '%',
        item.pass_rate + '%',
        item.difficulty,
        this.formatDate(item.created_time)
      ])
      
      const csvContent = [headers, ...rows]
        .map(row => row.map(field => `"${field}"`).join(','))
        .join('\n')
      
      return '\uFEFF' + csvContent // 添加BOM以支持中文
    }
  }
}
</script>

<style scoped>
.exam-statistics {
  padding: 20px;
}

.stats-overview {
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: #fff;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.active {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.average {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.papers {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-card {
  height: 380px;
}

.table-card {
  margin-top: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .exam-statistics {
    padding: 10px;
  }
  
  .stat-card {
    margin-bottom: 15px;
  }
  
  .chart-card {
    height: 300px;
    margin-bottom: 15px;
  }
}
</style>