<template>
  <div class="exam-history">
    <Panel shadow>
      <div slot="title">
        <Icon type="ios-time" />
        考试历史记录
        <Badge :count="total" style="margin-left: 10px" />
      </div>
      
      <!-- 筛选器 -->
      <div class="filter-section">
        <Row :gutter="10">
          <Col :span="4">
            <Select v-model="selectedStatus" placeholder="考试状态" clearable>
              <Option value="submitted">已提交</Option>
              <Option value="timeout">超时</Option>
            </Select>
          </Col>
          <Col :span="6">
            <DatePicker 
              v-model="dateRange" 
              type="daterange" 
              placeholder="选择日期范围"
              style="width: 100%"
              clearable
            />
          </Col>
          <Col :span="6">
            <Button type="primary" @click="getExamHistoryList">筛选</Button>
            <Button @click="resetFilter" style="margin-left: 8px">重置</Button>
          </Col>
        </Row>
      </div>
      
      <!-- 历史记录列表 -->
      <Table 
        :columns="columns"
        :data="examHistory"
        :loading="loading"
      />
      
      <!-- 分页 -->
      <div class="pagination">
        <Page 
          :total="total"
          :page-size="pageSize"
          :current="currentPage"
          @on-change="handlePageChange"
          @on-page-size-change="handlePageSizeChange"
          show-sizer
          show-elevator
          show-total
        />
      </div>
    </Panel>
    
    <!-- 考试详情模态框 -->
    <Modal
      v-model="detailModalVisible"
      title="考试详情"
      width="800"
      :footer-hide="true"
    >
      <div v-if="currentExamDetail">
        <Row :gutter="16">
          <Col :span="12">
            <Card>
              <p slot="title">基本信息</p>
              <p><strong>试卷名称：</strong>{{ currentExamDetail.paper.title }}</p>
              <p><strong>考试时长：</strong>{{ currentExamDetail.paper.duration }}分钟</p>
              <p><strong>开始时间：</strong>{{ formatTime(currentExamDetail.start_time) }}</p>
              <p><strong>结束时间：</strong>{{ formatTime(currentExamDetail.end_time) }}</p>
              <p><strong>考试状态：</strong>
                <Tag :color="getStatusColor(currentExamDetail.status)">{{ getStatusText(currentExamDetail.status) }}</Tag>
              </p>
            </Card>
          </Col>
          <Col :span="12">
            <Card>
              <p slot="title">成绩统计</p>
              <p><strong>得分：</strong>{{ currentExamDetail.score || 0 }}分</p>
              <p><strong>正确题数：</strong>{{ currentExamDetail.correct_count }}/{{ currentExamDetail.total_count }}</p>
              <p><strong>正确率：</strong>{{ getAccuracyRate(currentExamDetail) }}%</p>
              <Progress 
                :percent="getAccuracyRate(currentExamDetail)" 
                :stroke-color="getProgressColor(getAccuracyRate(currentExamDetail))"
              />
            </Card>
          </Col>
        </Row>
        
        <!-- 答题详情 -->
        <Card style="margin-top: 16px;">
          <p slot="title">答题详情</p>
          <div v-if="currentExamDetail.question_details">
            <div 
              v-for="(question, index) in currentExamDetail.question_details" 
              :key="question.id"
              class="question-item"
            >
              <div class="question-header">
                <span class="question-number">第{{ index + 1 }}题</span>
                <Tag 
                  :color="isAnswerCorrect(question, currentExamDetail.answers[question.id]) ? 'success' : 'error'"
                >
                  {{ isAnswerCorrect(question, currentExamDetail.answers[question.id]) ? '正确' : '错误' }}
                </Tag>
              </div>
              <div class="question-content">
                <p><strong>{{ question.title }}</strong></p>
                <div class="options">
                  <div 
                    v-for="(option, optionIndex) in question.options" 
                    :key="optionIndex"
                    class="option-item"
                    :class="{
                      'correct-option': isCorrectOption(question, optionIndex),
                      'user-selected': isUserSelected(question, currentExamDetail.answers[question.id], optionIndex),
                      'wrong-selected': isWrongSelected(question, currentExamDetail.answers[question.id], optionIndex)
                    }"
                  >
                    {{ String.fromCharCode(65 + optionIndex) }}. {{ option }}
                  </div>
                </div>
                <div v-if="question.explanation" class="explanation">
                  <p><strong>解析：</strong>{{ question.explanation }}</p>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </Modal>
  </div>
</template>

<script>
import api from '../../api'

export default {
  name: 'ExamHistory',
  data() {
    return {
      loading: false,
      examHistory: [],
      total: 0,
      currentPage: 1,
      pageSize: 20,
      
      // 筛选条件
      selectedStatus: null,
      dateRange: [],
      
      // 详情模态框
      detailModalVisible: false,
      currentExamDetail: null,
      
      columns: [
        {
          title: 'ID',
          key: 'id',
          width: 80,
          align: 'center'
        },
        {
          title: '试卷名称',
          key: 'paper.title',
          minWidth: 200,
          render: (h, params) => {
            return h('div', [
              h('div', {
                style: {
                  fontWeight: 'bold',
                  marginBottom: '4px'
                }
              }, params.row.paper.title),
              h('div', {
                style: {
                  fontSize: '12px',
                  color: '#999'
                }
              }, `时长: ${params.row.paper.duration}分钟 | 总分: ${params.row.paper.total_score}分`)
            ])
          }
        },
        {
          title: '考试状态',
          key: 'status',
          width: 100,
          align: 'center',
          render: (h, params) => {
            return h('Tag', {
              props: {
                color: this.getStatusColor(params.row.status)
              }
            }, this.getStatusText(params.row.status))
          }
        },
        {
          title: '得分',
          key: 'score',
          width: 80,
          align: 'center',
          render: (h, params) => {
            return h('span', {
              style: {
                fontWeight: 'bold',
                color: params.row.score >= 60 ? '#19be6b' : '#ed4014'
              }
            }, `${params.row.score || 0}分`)
          }
        },
        {
          title: '正确率',
          key: 'accuracy',
          width: 100,
          align: 'center',
          render: (h, params) => {
            const accuracy = this.getAccuracyRate(params.row)
            return h('span', {
              style: {
                color: accuracy >= 60 ? '#19be6b' : '#ed4014'
              }
            }, `${accuracy}%`)
          }
        },
        {
          title: '开始时间',
          key: 'start_time',
          width: 150,
          render: (h, params) => {
            return h('span', this.formatTime(params.row.start_time))
          }
        },
        {
          title: '结束时间',
          key: 'end_time',
          width: 150,
          render: (h, params) => {
            return h('span', this.formatTime(params.row.end_time))
          }
        },
        {
          title: '操作',
          key: 'action',
          width: 120,
          align: 'center',
          render: (h, params) => {
            return h('div', [
              h('Button', {
                props: {
                  type: 'primary',
                  size: 'small'
                },
                style: {
                  marginRight: '5px'
                },
                on: {
                  click: () => this.viewDetail(params.row.id)
                }
              }, '查看详情')
            ])
          }
        }
      ]
    }
  },
  
  mounted() {
    this.getExamHistoryList()
  },
  
  methods: {
    async getExamHistoryList() {
      this.loading = true
      try {
        const params = {
          offset: (this.currentPage - 1) * this.pageSize,
          limit: this.pageSize
        }
        
        if (this.selectedStatus) params.status = this.selectedStatus
        if (this.dateRange && this.dateRange.length === 2) {
          params.start_date = this.formatDate(this.dateRange[0])
          params.end_date = this.formatDate(this.dateRange[1])
        }
        
        const res = await api.getExamHistoryList(params)
        this.examHistory = res.data.data.results
        this.total = res.data.data.total
      } catch (err) {
        this.$Message.error('获取考试历史失败')
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    
    resetFilter() {
      this.selectedStatus = null
      this.dateRange = []
      this.currentPage = 1
      this.getExamHistoryList()
    },
    
    handlePageChange(page) {
      this.currentPage = page
      this.getExamHistoryList()
    },
    
    handlePageSizeChange(pageSize) {
      this.pageSize = pageSize
      this.currentPage = 1
      this.getExamHistoryList()
    },
    
    async viewDetail(sessionId) {
      try {
        const res = await api.getExamSessionDetail(sessionId)
        this.currentExamDetail = res.data.data
        this.detailModalVisible = true
      } catch (err) {
        this.$Message.error('获取考试详情失败')
        console.error(err)
      }
    },
    
    getStatusColor(status) {
      const colorMap = {
        'submitted': 'success',
        'timeout': 'warning',
        'started': 'processing',
        'created': 'default'
      }
      return colorMap[status] || 'default'
    },
    
    getStatusText(status) {
      const textMap = {
        'submitted': '已提交',
        'timeout': '超时',
        'started': '进行中',
        'created': '已创建'
      }
      return textMap[status] || '未知'
    },
    
    getAccuracyRate(exam) {
      if (!exam.total_count || exam.total_count === 0) return 0
      return Math.round((exam.correct_count / exam.total_count) * 100)
    },
    
    getProgressColor(rate) {
      if (rate >= 80) return '#19be6b'
      if (rate >= 60) return '#ff9900'
      return '#ed4014'
    },
    
    formatTime(timeStr) {
      if (!timeStr) return '-'
      return new Date(timeStr).toLocaleString('zh-CN')
    },
    
    formatDate(date) {
      if (!date) return ''
      // 如果是字符串，先转换为Date对象
      if (typeof date === 'string') {
        date = new Date(date)
      }
      // 确保是有效的Date对象
      if (!(date instanceof Date) || isNaN(date.getTime())) {
        return ''
      }
      return date.toISOString().split('T')[0]
    },
    
    isAnswerCorrect(question, userAnswer) {
      if (!userAnswer) return false
      if (question.question_type === 'single') {
        return userAnswer === question.correct_answer
      } else if (question.question_type === 'multiple') {
        if (Array.isArray(userAnswer) && Array.isArray(question.correct_answer)) {
          return JSON.stringify(userAnswer.sort()) === JSON.stringify(question.correct_answer.sort())
        }
      }
      return false
    },
    
    isCorrectOption(question, optionIndex) {
      if (question.question_type === 'single') {
        return optionIndex === question.correct_answer
      } else if (question.question_type === 'multiple') {
        return Array.isArray(question.correct_answer) && question.correct_answer.includes(optionIndex)
      }
      return false
    },
    
    isUserSelected(question, userAnswer, optionIndex) {
      if (!userAnswer) return false
      if (question.question_type === 'single') {
        return userAnswer === optionIndex
      } else if (question.question_type === 'multiple') {
        return Array.isArray(userAnswer) && userAnswer.includes(optionIndex)
      }
      return false
    },
    
    isWrongSelected(question, userAnswer, optionIndex) {
      return this.isUserSelected(question, userAnswer, optionIndex) && !this.isCorrectOption(question, optionIndex)
    }
  }
}
</script>

<style scoped>
.exam-history {
  margin: 20px;
}

.filter-section {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f8f9;
  border-radius: 4px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.question-item {
  margin-bottom: 20px;
  padding: 16px;
  border: 1px solid #e8eaec;
  border-radius: 4px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.question-number {
  font-weight: bold;
  color: #2d8cf0;
}

.question-content {
  margin-top: 12px;
}

.options {
  margin: 12px 0;
}

.option-item {
  padding: 8px 12px;
  margin: 4px 0;
  border-radius: 4px;
  background: #f8f8f9;
}

.correct-option {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #52c41a;
}

.user-selected {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
}

.wrong-selected {
  background: #fff2e8;
  border: 1px solid #ffbb96;
  color: #fa541c;
}

.explanation {
  margin-top: 12px;
  padding: 12px;
  background: #fafafa;
  border-left: 4px solid #2d8cf0;
  border-radius: 4px;
}
</style>