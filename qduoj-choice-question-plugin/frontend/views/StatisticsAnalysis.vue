<template>
  <div class="statistics-analysis">
    <!-- 简化的统计卡片 -->
    <Row :gutter="16" class="stats-cards">
      <Col :span="8">
        <Card>
          <div class="stat-card">
            <div class="stat-icon">
              <Icon type="ios-help-circle" size="32" color="#2d8cf0" />
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ stats.total_questions || 0 }}</div>
              <div class="stat-label">总题目数</div>
            </div>
          </div>
        </Card>
      </Col>
      <Col :span="8">
        <Card>
          <div class="stat-card">
            <div class="stat-icon">
              <Icon type="ios-paper" size="32" color="#19be6b" />
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ stats.total_submissions || 0 }}</div>
              <div class="stat-label">总提交数</div>
            </div>
          </div>
        </Card>
      </Col>
      <Col :span="8">
        <Card>
          <div class="stat-card">
            <div class="stat-icon">
              <Icon type="ios-checkmark-circle" size="32" color="#19be6b" />
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ stats.correct_rate || '0%' }}</div>
              <div class="stat-label">正确率</div>
            </div>
          </div>
        </Card>
      </Col>
    </Row>

    <!-- 基础统计表格 -->
    <Card style="margin-top: 20px;">
      <div slot="title">
        <Icon type="ios-stats" />
        基础统计
      </div>
      <Table :columns="columns" :data="tableData" :loading="loading">
      </Table>
    </Card>
  </div>
</template>

<script>
import api from '@/api'

export default {
  name: 'StatisticsAnalysis',
  data() {
    return {
      loading: false,
      stats: {
        total_questions: 0,
        total_submissions: 0,
        correct_rate: '0%'
      },
      columns: [
        {
          title: '分类',
          key: 'category_name'
        },
        {
          title: '题目数量',
          key: 'question_count'
        },
        {
          title: '提交次数',
          key: 'submission_count'
        },
        {
          title: '正确率',
          key: 'correct_rate'
        }
      ],
      tableData: []
    }
  },
  mounted() {
    this.loadStatistics()
  },
  methods: {
    async loadStatistics() {
      this.loading = true
      try {
        const response = await api.getQuestionStats()
        this.stats = response.data || this.stats
        this.tableData = response.data.category_stats || []
      } catch (error) {
        console.error('加载统计数据失败:', error)
        this.$Message.error('加载统计数据失败')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.statistics-analysis {
  padding: 20px;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  margin-right: 15px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}
</style>
              <div class="stat-number">{{ overallStats.submission_stats.overall_accuracy }}%</div>
              <div class="stat-label">总体正确率</div>
            </div>
          </div>
        </Card>
      </Col>
    </Row>
    
    <!-- 图表区域 -->
    <Row :gutter="16" class="charts-section">
      <!-- 提交趋势图 -->
      <Col :span="12">
        <Card>
          <div slot="title">
            <Icon type="ios-analytics" />
            提交趋势
          </div>
          <div slot="extra">
            <Select v-model="trendDays" @on-change="getSubmissionTrend" style="width: 100px">
              <Option :value="7">7天</Option>
              <Option :value="30">30天</Option>
              <Option :value="90">90天</Option>
            </Select>
          </div>
          <div ref="submissionTrendChart" style="height: 300px;"></div>
        </Card>
      </Col>
      
      <!-- 难度分布图 -->
      <Col :span="12">
        <Card>
          <div slot="title">
            <Icon type="ios-pie" />
            难度分布
          </div>
          <div ref="difficultyChart" style="height: 300px;"></div>
        </Card>
      </Col>
    </Row>
    
    <Row :gutter="16" class="charts-section">
      <!-- 分类统计图 -->
      <Col :span="12">
        <Card>
          <div slot="title">
            <Icon type="ios-folder" />
            分类统计
          </div>
          <div ref="categoryChart" style="height: 300px;"></div>
        </Card>
      </Col>
      
      <!-- 用户活跃度图 -->
      <Col :span="12">
        <Card>
          <div slot="title">
            <Icon type="ios-person" />
            用户活跃度
          </div>
          <div ref="userActivityChart" style="height: 300px;"></div>
        </Card>
      </Col>
    </Row>
    
    <!-- 详细统计表格 -->
    <Row :gutter="16" class="tables-section">
      <!-- 热门题目 -->
      <Col :span="12">
        <Card>
          <div slot="title">
            <Icon type="ios-flame" />
            热门题目
          </div>
          <div slot="extra">
            <Select v-model="popularSort" @on-change="getPopularQuestions" style="width: 120px">
              <Option value="submissions">按提交数</Option>
              <Option value="acceptance_rate">按正确率</Option>
              <Option value="difficulty">按难度</Option>
            </Select>
          </div>
          <Table
            :columns="popularColumns"
            :data="popularQuestions"
            :loading="popularLoading"
            size="small"
          />
        </Card>
      </Col>
      
      <!-- 分类详情 -->
      <Col :span="12">
        <Card>
          <div slot="title">
            <Icon type="ios-list" />
            分类详情
          </div>
          <Table
            :columns="categoryColumns"
            :data="categoryStats"
            :loading="categoryLoading"
            size="small"
          />
        </Card>
      </Col>
    </Row>
    
    <!-- 系统健康状态 -->
    <Row :gutter="16" class="health-section" v-if="isAdmin">
      <Col :span="24">
        <Card>
          <div slot="title">
            <Icon type="ios-pulse" />
            系统健康状态
          </div>
          <div class="health-overview">
            <Row :gutter="16">
              <Col :span="6">
                <div class="health-item">
                  <div class="health-score" :class="getHealthScoreClass(systemHealth.health_score)">
                    {{ systemHealth.health_score }}
                  </div>
                  <div class="health-label">健康评分</div>
                </div>
              </Col>
              <Col :span="6">
                <div class="health-item">
                  <div class="health-number">{{ systemHealth.data_completeness }}%</div>
                  <div class="health-label">数据完整性</div>
                </div>
              </Col>
              <Col :span="6">
                <div class="health-item">
                  <div class="health-number">{{ systemHealth.questions_without_category }}</div>
                  <div class="health-label">未分类题目</div>
                </div>
              </Col>
              <Col :span="6">
                <div class="health-item">
                  <div class="health-number">{{ systemHealth.questions_without_tags }}</div>
                  <div class="health-label">无标签题目</div>
                </div>
              </Col>
            </Row>
          </div>
          
          <div class="health-details" v-if="healthDetails">
            <Tabs>
              <TabPane label="数据一致性" name="consistency">
                <div v-if="healthDetails.data_consistency.categories_need_update > 0">
                  <Alert type="warning" show-icon>
                    发现 {{ healthDetails.data_consistency.categories_need_update }} 个分类的题目数量不一致
                    <template slot="desc">
                      <ul>
                        <li v-for="category in healthDetails.data_consistency.inconsistent_categories" :key="category.id">
                          {{ category.name }}: 记录 {{ category.recorded_count }}，实际 {{ category.actual_count }}
                        </li>
                      </ul>
                    </template>
                  </Alert>
                </div>
                
                <div v-if="healthDetails.data_consistency.tags_need_update > 0" style="margin-top: 16px">
                  <Alert type="warning" show-icon>
                    发现 {{ healthDetails.data_consistency.tags_need_update }} 个标签的题目数量不一致
                    <template slot="desc">
                      <ul>
                        <li v-for="tag in healthDetails.data_consistency.inconsistent_tags" :key="tag.id">
                          {{ tag.name }}: 记录 {{ tag.recorded_count }}，实际 {{ tag.actual_count }}
                        </li>
                      </ul>
                    </template>
                  </Alert>
                </div>
                
                <div v-if="healthDetails.data_consistency.categories_need_update === 0 && healthDetails.data_consistency.tags_need_update === 0">
                  <Alert type="success" show-icon>
                    数据一致性检查通过，所有统计数据准确
                  </Alert>
                </div>
              </TabPane>
              
              <TabPane label="最近活动" name="activity">
                <Row :gutter="16">
                  <Col :span="12">
                    <Statistic title="24小时提交数" :value="healthDetails.recent_activity.submissions_24h" />
                  </Col>
                  <Col :span="12">
                    <Statistic title="24小时错题数" :value="healthDetails.recent_activity.wrong_questions_24h" />
                  </Col>
                </Row>
              </TabPane>
            </Tabs>
          </div>
        </Card>
      </Col>
    </Row>
  </div>
</template>

<script>
import api from '../api'
import * as echarts from 'echarts'

export default {
  name: 'StatisticsAnalysis',
  data() {
    return {
      loading: false,
      
      // 总体统计
      overallStats: {
        question_stats: { total: 0 },
        submission_stats: { total: 0, overall_accuracy: 0 },
        user_stats: { active_users: 0 }
      },
      
      // 图表相关
      trendDays: 30,
      submissionTrend: [],
      difficultyDistribution: [],
      categoryStats: [],
      userActivity: [],
      
      // 热门题目
      popularQuestions: [],
      popularSort: 'submissions',
      popularLoading: false,
      
      // 分类统计
      categoryLoading: false,
      
      // 系统健康
      systemHealth: {
        health_score: 0,
        data_completeness: 0,
        questions_without_category: 0,
        questions_without_tags: 0
      },
      healthDetails: null,
      
      // 表格列定义
      popularColumns: [
        {
          title: 'ID',
          key: '_id',
          width: 60
        },
        {
          title: '标题',
          key: 'title',
          minWidth: 150,
          render: (h, params) => {
            return h('a', {
              on: {
                click: () => {
                  this.$router.push(`/choice-question/${params.row.id}`)
                }
              }
            }, params.row.title)
          }
        },
        {
          title: '难度',
          key: 'difficulty',
          width: 80,
          render: (h, params) => {
            const colors = {
              '简单': 'success',
              '中等': 'warning',
              '困难': 'error'
            }
            return h('Tag', {
              props: {
                color: colors[params.row.difficulty]
              }
            }, params.row.difficulty)
          }
        },
        {
          title: '提交数',
          key: 'total_submit',
          width: 80,
          sortable: true
        },
        {
          title: '正确率',
          key: 'acceptance_rate',
          width: 80,
          render: (h, params) => {
            return h('span', `${params.row.acceptance_rate}%`)
          }
        }
      ],
      
      categoryColumns: [
        {
          title: '分类',
          key: 'name',
          minWidth: 120
        },
        {
          title: '题目数',
          key: 'question_count',
          width: 80,
          sortable: true
        },
        {
          title: '提交数',
          key: 'total_submissions',
          width: 80,
          sortable: true
        },
        {
          title: '正确率',
          key: 'acceptance_rate',
          width: 80,
          render: (h, params) => {
            return h('span', `${params.row.acceptance_rate}%`)
          }
        }
      ]
    }
  },
  computed: {
    isAdmin() {
      return this.$store.getters.user.admin_type === 'Super Admin'
    }
  },
  mounted() {
    this.init()
  },
  beforeDestroy() {
    // 销毁图表实例
    if (this.submissionTrendChart) {
      this.submissionTrendChart.dispose()
    }
    if (this.difficultyChart) {
      this.difficultyChart.dispose()
    }
    if (this.categoryChart) {
      this.categoryChart.dispose()
    }
    if (this.userActivityChart) {
      this.userActivityChart.dispose()
    }
  },
  methods: {
    async init() {
      this.loading = true
      try {
        await Promise.all([
          this.getOverallStatistics(),
          this.getSubmissionTrend(),
          this.getDifficultyDistribution(),
          this.getCategoryStatistics(),
          this.getPopularQuestions(),
          this.isAdmin ? this.getSystemHealth() : Promise.resolve()
        ])
        
        this.$nextTick(() => {
          this.initCharts()
        })
      } catch (error) {
        this.$Message.error('加载统计数据失败')
      } finally {
        this.loading = false
      }
    },
    
    async getOverallStatistics() {
      try {
        const res = await api.getOverallStatistics()
        this.overallStats = res.data
      } catch (error) {
        console.error('获取总体统计失败:', error)
      }
    },
    
    async getSubmissionTrend() {
      try {
        const res = await api.getSubmissionTrend({ days: this.trendDays })
        this.submissionTrend = res.data
        
        if (this.submissionTrendChart) {
          this.updateSubmissionTrendChart()
        }
      } catch (error) {
        console.error('获取提交趋势失败:', error)
      }
    },
    
    async getDifficultyDistribution() {
      try {
        const res = await api.getDifficultyStatistics()
        this.difficultyDistribution = res.data
        
        if (this.difficultyChart) {
          this.updateDifficultyChart()
        }
      } catch (error) {
        console.error('获取难度分布失败:', error)
      }
    },
    
    async getCategoryStatistics() {
      this.categoryLoading = true
      try {
        const res = await api.getCategoryStatistics()
        this.categoryStats = res.data
        
        if (this.categoryChart) {
          this.updateCategoryChart()
        }
      } catch (error) {
        console.error('获取分类统计失败:', error)
      } finally {
        this.categoryLoading = false
      }
    },
    
    async getPopularQuestions() {
      this.popularLoading = true
      try {
        const res = await api.getPopularQuestions({
          sort_by: this.popularSort,
          limit: 10
        })
        this.popularQuestions = res.data
      } catch (error) {
        console.error('获取热门题目失败:', error)
      } finally {
        this.popularLoading = false
      }
    },
    
    async getSystemHealth() {
      try {
        const res = await api.getSystemHealth()
        this.systemHealth = res.data.system_health
        this.healthDetails = res.data
      } catch (error) {
        console.error('获取系统健康状态失败:', error)
      }
    },
    
    initCharts() {
      this.initSubmissionTrendChart()
      this.initDifficultyChart()
      this.initCategoryChart()
      this.initUserActivityChart()
    },
    
    initSubmissionTrendChart() {
      this.submissionTrendChart = echarts.init(this.$refs.submissionTrendChart)
      this.updateSubmissionTrendChart()
    },
    
    updateSubmissionTrendChart() {
      const dates = this.submissionTrend.map(item => item.date)
      const totalSubmissions = this.submissionTrend.map(item => item.total_submissions)
      const correctSubmissions = this.submissionTrend.map(item => item.correct_submissions)
      const accuracyRates = this.submissionTrend.map(item => item.accuracy_rate)
      
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['总提交', '正确提交', '正确率']
        },
        xAxis: {
          type: 'category',
          data: dates
        },
        yAxis: [
          {
            type: 'value',
            name: '提交数',
            position: 'left'
          },
          {
            type: 'value',
            name: '正确率(%)',
            position: 'right',
            max: 100
          }
        ],
        series: [
          {
            name: '总提交',
            type: 'bar',
            data: totalSubmissions,
            itemStyle: {
              color: '#2d8cf0'
            }
          },
          {
            name: '正确提交',
            type: 'bar',
            data: correctSubmissions,
            itemStyle: {
              color: '#19be6b'
            }
          },
          {
            name: '正确率',
            type: 'line',
            yAxisIndex: 1,
            data: accuracyRates,
            itemStyle: {
              color: '#ff9900'
            }
          }
        ]
      }
      
      this.submissionTrendChart.setOption(option)
    },
    
    initDifficultyChart() {
      this.difficultyChart = echarts.init(this.$refs.difficultyChart)
      this.updateDifficultyChart()
    },
    
    updateDifficultyChart() {
      const data = this.difficultyDistribution.map(item => ({
        name: item.difficulty_name,
        value: item.question_count
      }))
      
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: data.map(item => item.name)
        },
        series: [
          {
            name: '难度分布',
            type: 'pie',
            radius: '50%',
            data: data,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
      
      this.difficultyChart.setOption(option)
    },
    
    initCategoryChart() {
      this.categoryChart = echarts.init(this.$refs.categoryChart)
      this.updateCategoryChart()
    },
    
    updateCategoryChart() {
      const categories = this.categoryStats.map(item => item.name)
      const questionCounts = this.categoryStats.map(item => item.question_count)
      const submissionCounts = this.categoryStats.map(item => item.total_submissions)
      
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['题目数', '提交数']
        },
        xAxis: {
          type: 'category',
          data: categories,
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: [
          {
            type: 'value',
            name: '题目数'
          },
          {
            type: 'value',
            name: '提交数'
          }
        ],
        series: [
          {
            name: '题目数',
            type: 'bar',
            data: questionCounts,
            itemStyle: {
              color: '#2d8cf0'
            }
          },
          {
            name: '提交数',
            type: 'bar',
            yAxisIndex: 1,
            data: submissionCounts,
            itemStyle: {
              color: '#19be6b'
            }
          }
        ]
      }
      
      this.categoryChart.setOption(option)
    },
    
    initUserActivityChart() {
      this.userActivityChart = echarts.init(this.$refs.userActivityChart)
      
      // 模拟用户活跃度数据
      const hours = Array.from({ length: 24 }, (_, i) => i)
      const activityData = hours.map(hour => Math.floor(Math.random() * 100))
      
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: hours.map(h => `${h}:00`),
          name: '时间'
        },
        yAxis: {
          type: 'value',
          name: '活跃用户数'
        },
        series: [
          {
            name: '活跃用户',
            type: 'line',
            data: activityData,
            smooth: true,
            itemStyle: {
              color: '#ff9900'
            },
            areaStyle: {
              color: 'rgba(255, 153, 0, 0.3)'
            }
          }
        ]
      }
      
      this.userActivityChart.setOption(option)
    },
    
    getHealthScoreClass(score) {
      if (score >= 90) return 'health-excellent'
      if (score >= 70) return 'health-good'
      if (score >= 50) return 'health-warning'
      return 'health-danger'
    }
  }
}
</script>

<style scoped>
.statistics-analysis {
  padding: 20px;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
}

.stat-icon {
  margin-right: 16px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
}

.charts-section {
  margin-bottom: 20px;
}

.tables-section {
  margin-bottom: 20px;
}

.health-section {
  margin-bottom: 20px;
}

.health-overview {
  margin-bottom: 20px;
}

.health-item {
  text-align: center;
  padding: 16px;
}

.health-score {
  font-size: 32px;
  font-weight: bold;
  line-height: 1;
}

.health-excellent {
  color: #19be6b;
}

.health-good {
  color: #2d8cf0;
}

.health-warning {
  color: #ff9900;
}

.health-danger {
  color: #ed4014;
}

.health-number {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  line-height: 1;
}

.health-label {
  font-size: 14px;
  color: #999;
  margin-top: 8px;
}

.health-details {
  margin-top: 20px;
}

.health-details ul {
  margin: 8px 0;
  padding-left: 20px;
}

.health-details li {
  margin: 4px 0;
}
</style>