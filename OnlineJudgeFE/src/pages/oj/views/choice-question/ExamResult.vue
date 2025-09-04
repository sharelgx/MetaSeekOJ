<template>
  <div class="exam-result">
    <div class="result-container">
      <!-- 考试结果头部 -->
      <Card class="result-header">
        <div class="result-title">
          <Icon type="ios-checkmark-circle" size="48" color="#52c41a" />
          <h1>考试完成</h1>
        </div>
        
        <div class="exam-info">
          <h2>{{ examSession.exam_paper_title }}</h2>
          <p class="exam-meta">
            <span>考试时间：{{ formatDate(examSession.start_time) }}</span>
            <span class="divider">|</span>
            <span>用时：{{ formatDuration(examSession.duration) }}</span>
          </p>
        </div>
      </Card>

      <!-- 成绩概览 -->
      <Row :gutter="20" class="score-overview">
        <Col span="6">
          <Card>
            <div class="score-item">
              <div class="score-value" :class="getScoreClass(examSession.score_percentage)">
                {{ examSession.total_score }}
              </div>
              <div class="score-label">总分</div>
              <div class="score-max">满分 {{ examSession.max_score }}</div>
            </div>
          </Card>
        </Col>
        
        <Col span="6">
          <Card>
            <div class="score-item">
              <div class="score-value score-percentage">
                {{ examSession.score_percentage }}%
              </div>
              <div class="score-label">得分率</div>
            </div>
          </Card>
        </Col>
        
        <Col span="6">
          <Card>
            <div class="score-item">
              <div class="score-value score-correct">
                {{ examSession.correct_count }}
              </div>
              <div class="score-label">正确题数</div>
              <div class="score-max">共 {{ examSession.total_count }} 题</div>
            </div>
          </Card>
        </Col>
        
        <Col span="6">
          <Card>
            <div class="score-item">
              <div class="score-value score-accuracy">
                {{ examSession.accuracy_rate }}%
              </div>
              <div class="score-label">正确率</div>
            </div>
          </Card>
        </Col>
      </Row>

      <!-- 答题情况分析 -->
      <Card class="analysis-section">
        <div slot="title">
          <Icon type="ios-analytics" />
          答题情况分析
        </div>
        
        <Row :gutter="20">
          <Col span="12">
            <!-- 题型分析 -->
            <div class="analysis-item">
              <h4>按题型统计</h4>
              <div class="type-stats">
                <div v-for="stat in typeStats" :key="stat.type" class="type-stat">
                  <div class="type-name">{{ stat.type_display }}</div>
                  <div class="type-progress">
                    <Progress 
                      :percent="stat.accuracy" 
                      :stroke-color="getProgressColor(stat.accuracy)"
                      :show-info="false"
                    />
                    <span class="type-detail">
                      {{ stat.correct }}/{{ stat.total }} ({{ stat.accuracy }}%)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </Col>
          
          <Col span="12">
            <!-- 难度分析 -->
            <div class="analysis-item">
              <h4>按难度统计</h4>
              <div class="difficulty-stats">
                <div v-for="stat in difficultyStats" :key="stat.difficulty" class="difficulty-stat">
                  <div class="difficulty-name">
                    <Tag :color="getDifficultyColor(stat.difficulty)">{{ stat.difficulty_display }}</Tag>
                  </div>
                  <div class="difficulty-progress">
                    <Progress 
                      :percent="stat.accuracy" 
                      :stroke-color="getProgressColor(stat.accuracy)"
                      :show-info="false"
                    />
                    <span class="difficulty-detail">
                      {{ stat.correct }}/{{ stat.total }} ({{ stat.accuracy }}%)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </Col>
        </Row>
      </Card>

      <!-- 错题回顾 -->
      <Card class="wrong-questions-section" v-if="wrongQuestions.length > 0">
        <div slot="title">
          <Icon type="ios-close-circle" color="#f5222d" />
          错题回顾 ({{ wrongQuestions.length }} 题)
        </div>
        
        <div class="wrong-questions">
          <div v-for="(question, index) in wrongQuestions" :key="question.id" class="wrong-question">
            <div class="question-header">
              <h4>第 {{ question.order || (index + 1) }} 题</h4>
              <Tag color="red">{{ question.question_type === 'single' ? '单选题' : '多选题' }}</Tag>
            </div>
            
            <div class="question-content">
              <p class="question-text">{{ question.content }}</p>
              
              <div class="options">
                <div 
                  v-for="(option, optionIndex) in question.options" 
                  :key="optionIndex"
                  class="option"
                  :class="{
                    'correct': question.correct_answer.includes(optionIndex),
                    'wrong': question.user_answer.includes(optionIndex) && !question.correct_answer.includes(optionIndex),
                    'selected': question.user_answer.includes(optionIndex)
                  }"
                >
                  <span class="option-label">{{ String.fromCharCode(65 + optionIndex) }}.</span>
                  <span class="option-text">{{ option }}</span>
                  <span v-if="question.correct_answer.includes(optionIndex)" class="correct-mark">
                    <Icon type="ios-checkmark" color="#52c41a" />
                  </span>
                  <span v-else-if="question.user_answer.includes(optionIndex)" class="wrong-mark">
                    <Icon type="ios-close" color="#f5222d" />
                  </span>
                </div>
              </div>
              
              <div class="answer-comparison">
                <div class="answer-item">
                  <span class="answer-label">正确答案：</span>
                  <span class="correct-answer">
                    {{ formatAnswer(question.correct_answer) }}
                  </span>
                </div>
                <div class="answer-item">
                  <span class="answer-label">你的答案：</span>
                  <span class="user-answer" :class="{ 'wrong': !question.is_correct }">
                    {{ formatAnswer(question.user_answer) || '未作答' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <Button type="default" size="large" @click="goBack">
          返回题目列表
        </Button>
        <Button type="primary" size="large" @click="reviewExam">
          查看完整试卷
        </Button>
        <Button type="success" size="large" @click="practiceWrongQuestions" v-if="wrongQuestions.length > 0">
          练习错题
        </Button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../api'

export default {
  name: 'ExamResult',
  data() {
    return {
      examSession: {},
      wrongQuestions: [],
      typeStats: [],
      difficultyStats: [],
      loading: true
    }
  },
  
  async mounted() {
    await this.loadExamResult()
  },
  
  methods: {
    async loadExamResult() {
      try {
        const sessionId = this.$route.params.sessionId
        
        // 获取考试会话详情
        const res = await api.getExamSessionDetail(sessionId)
        this.examSession = res.data.data
        
        // 处理统计数据
        this.processStats()
        
        // 获取错题
        this.processWrongQuestions()
        
      } catch (err) {
        console.error('加载考试结果失败:', err)
        this.$Message.error('加载考试结果失败')
      } finally {
        this.loading = false
      }
    },
    
    processStats() {
      // 处理题型统计
      const typeMap = {}
      const difficultyMap = {}
      
      if (this.examSession.questions) {
        this.examSession.questions.forEach(question => {
          // 题型统计
          const type = question.question_type
          if (!typeMap[type]) {
            typeMap[type] = {
              type,
              type_display: type === 'single' ? '单选题' : '多选题',
              total: 0,
              correct: 0
            }
          }
          typeMap[type].total++
          if (question.is_correct) {
            typeMap[type].correct++
          }
          
          // 难度统计
          const difficulty = question.difficulty
          if (!difficultyMap[difficulty]) {
            difficultyMap[difficulty] = {
              difficulty,
              difficulty_display: this.getDifficultyDisplay(difficulty),
              total: 0,
              correct: 0
            }
          }
          difficultyMap[difficulty].total++
          if (question.is_correct) {
            difficultyMap[difficulty].correct++
          }
        })
      }
      
      // 计算准确率
      this.typeStats = Object.values(typeMap).map(stat => ({
        ...stat,
        accuracy: stat.total > 0 ? Math.round((stat.correct / stat.total) * 100) : 0
      }))
      
      this.difficultyStats = Object.values(difficultyMap).map(stat => ({
        ...stat,
        accuracy: stat.total > 0 ? Math.round((stat.correct / stat.total) * 100) : 0
      }))
    },
    
    processWrongQuestions() {
      if (this.examSession.questions) {
        this.wrongQuestions = this.examSession.questions.filter(q => !q.is_correct)
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    },
    
    formatDuration(seconds) {
      if (!seconds) return '0分钟'
      const minutes = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${minutes}分${secs}秒`
    },
    
    formatAnswer(answer) {
      if (!answer || answer.length === 0) return ''
      return answer.map(index => String.fromCharCode(65 + index)).join(', ')
    },
    
    getScoreClass(percentage) {
      if (percentage >= 90) return 'score-excellent'
      if (percentage >= 80) return 'score-good'
      if (percentage >= 60) return 'score-pass'
      return 'score-fail'
    },
    
    getProgressColor(percentage) {
      if (percentage >= 80) return '#52c41a'
      if (percentage >= 60) return '#faad14'
      return '#f5222d'
    },
    
    getDifficultyColor(difficulty) {
      const colors = {
        'easy': 'green',
        'medium': 'orange', 
        'hard': 'red'
      }
      return colors[difficulty] || 'default'
    },
    
    getDifficultyDisplay(difficulty) {
      const displays = {
        'easy': '简单',
        'medium': '中等',
        'hard': '困难'
      }
      return displays[difficulty] || difficulty
    },
    
    goBack() {
      this.$router.push({ name: 'choice-question-list' })
    },
    
    reviewExam() {
      // 跳转到试卷查看页面（只读模式）
      this.$router.push({
        name: 'exam-review',
        params: { sessionId: this.examSession.id }
      })
    },
    
    practiceWrongQuestions() {
      // 跳转到错题本页面进行练习，传递当前考试的错题ID列表
      const wrongQuestionIds = this.wrongQuestions.map(q => q.id)
      this.$router.push({
        name: 'wrong-question-book',
        query: {
          examSessionId: this.examSession.id,
          questionIds: wrongQuestionIds.join(',')
        }
      })
    }
  }
}
</script>

<style scoped>
.exam-result {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.result-container {
  max-width: 1200px;
  margin: 0 auto;
}

.result-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 40px 20px;
}

.result-title {
  margin-bottom: 20px;
}

.result-title h1 {
  margin: 10px 0 0 0;
  color: #52c41a;
  font-size: 32px;
}

.exam-info h2 {
  margin: 0 0 10px 0;
  color: #333;
}

.exam-meta {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.exam-meta .divider {
  margin: 0 10px;
  color: #ddd;
}

.score-overview {
  margin-bottom: 30px;
}

.score-item {
  text-align: center;
  padding: 20px;
}

.score-value {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 8px;
}

.score-excellent {
  color: #52c41a;
}

.score-good {
  color: #1890ff;
}

.score-pass {
  color: #faad14;
}

.score-fail {
  color: #f5222d;
}

.score-percentage {
  color: #1890ff;
}

.score-correct {
  color: #52c41a;
}

.score-accuracy {
  color: #722ed1;
}

.score-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.score-max {
  font-size: 12px;
  color: #999;
}

.analysis-section {
  margin-bottom: 30px;
}

.analysis-item {
  padding: 20px;
}

.analysis-item h4 {
  margin: 0 0 20px 0;
  color: #333;
}

.type-stat, .difficulty-stat {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.type-name, .difficulty-name {
  width: 80px;
  flex-shrink: 0;
}

.type-progress, .difficulty-progress {
  flex: 1;
  display: flex;
  align-items: center;
  margin-left: 15px;
}

.type-detail, .difficulty-detail {
  margin-left: 10px;
  font-size: 12px;
  color: #666;
  white-space: nowrap;
}

.wrong-questions-section {
  margin-bottom: 30px;
}

.wrong-question {
  border: 1px solid #e8eaec;
  border-radius: 6px;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e8eaec;
}

.question-header h4 {
  margin: 0;
  color: #333;
}

.question-text {
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 15px;
  color: #333;
}

.options {
  margin-bottom: 20px;
}

.option {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: 8px;
  border-radius: 4px;
  border: 1px solid #e8eaec;
  position: relative;
}

.option.correct {
  background: #f6ffed;
  border-color: #b7eb8f;
}

.option.wrong {
  background: #fff2f0;
  border-color: #ffccc7;
}

.option.selected {
  background: #e6f7ff;
  border-color: #91d5ff;
}

.option-label {
  font-weight: 500;
  margin-right: 8px;
  min-width: 20px;
}

.option-text {
  flex: 1;
}

.correct-mark, .wrong-mark {
  margin-left: 8px;
}

.answer-comparison {
  background: #fafafa;
  padding: 15px;
  border-radius: 4px;
}

.answer-item {
  margin-bottom: 8px;
}

.answer-item:last-child {
  margin-bottom: 0;
}

.answer-label {
  font-weight: 500;
  color: #666;
}

.correct-answer {
  color: #52c41a;
  font-weight: 500;
}

.user-answer {
  color: #1890ff;
  font-weight: 500;
}

.user-answer.wrong {
  color: #f5222d;
}

.action-buttons {
  text-align: center;
  padding: 40px 0;
}

.action-buttons .ivu-btn {
  margin: 0 10px;
}
</style>