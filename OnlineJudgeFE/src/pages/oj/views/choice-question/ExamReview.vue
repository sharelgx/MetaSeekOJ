<template>
  <div class="exam-review">
    <!-- 考试头部信息 -->
    <div class="exam-header">
      <Row>
        <Col span="16">
          <h2>{{ examSession.exam_paper_title }}</h2>
          <p class="exam-info">
            <span>总分：{{ examSession.max_score }}分</span>
            <span class="divider">|</span>
            <span>题目数量：{{ examSession.question_count }}题</span>
            <span class="divider">|</span>
            <span>考试时间：{{ formatDate(examSession.start_time) }}</span>
          </p>
        </Col>
        <Col span="8" class="score-section">
          <div class="score-display">
            <Icon type="ios-trophy" size="20" />
            <span class="score-text">得分：{{ examSession.total_score }}/{{ examSession.max_score }}</span>
            <span class="score-percentage">({{ examSession.score_percentage }}%)</span>
          </div>
        </Col>
      </Row>
    </div>

    <!-- 考试内容区域 -->
    <div class="exam-content">
      <Row :gutter="20">
        <!-- 题目区域 -->
        <Col span="18">
          <div class="question-area">
            <Card v-if="currentQuestion" class="question-card">
              <div class="question-header">
                <h3>第 {{ currentQuestionIndex + 1 }} 题 ({{ currentQuestion.score }}分)</h3>
                <div class="question-type">
                  <Tag :color="getQuestionTypeColor(currentQuestion.question_type)">
                    {{ getQuestionTypeDisplay(currentQuestion.question_type) }}
                  </Tag>
                  <Tag :color="getDifficultyColor(currentQuestion.difficulty)" style="margin-left: 8px;">
                    {{ getDifficultyDisplay(currentQuestion.difficulty) }}
                  </Tag>
                </div>
              </div>
              
              <div class="question-text" v-html="currentQuestion.text"></div>
              
              <!-- 题目描述 -->
              <div v-if="currentQuestion.description" class="question-description">
                {{ currentQuestion.description }}
              </div>
              
              <!-- 选项 -->
              <div class="options">
                <div 
                  v-for="(option, index) in currentQuestion.options" 
                  :key="index"
                  class="option-item"
                  :class="getOptionClass(index)"
                >
                  <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
                  <span class="option-text">{{ option }}</span>
                  <span v-if="isCorrectOption(index)" class="correct-mark">
                    <Icon type="ios-checkmark-circle" color="#52c41a" size="18" />
                  </span>
                  <span v-else-if="isUserSelectedOption(index)" class="wrong-mark">
                    <Icon type="ios-close-circle" color="#f5222d" size="18" />
                  </span>
                </div>
              </div>
              
              <!-- 答案对比 -->
              <div class="answer-comparison">
                <div class="answer-item">
                  <span class="answer-label">正确答案：</span>
                  <span class="correct-answer">{{ formatAnswer(currentQuestion.correct_answer) }}</span>
                </div>
                <div class="answer-item">
                  <span class="answer-label">你的答案：</span>
                  <span class="user-answer" :class="{ 'wrong': !isAnswerCorrect() }">
                    {{ formatAnswer(getUserAnswer()) || '未作答' }}
                  </span>
                </div>
              </div>
              
              <!-- 题目导航 -->
              <div class="question-actions">
                <Button 
                  @click="previousQuestion" 
                  :disabled="currentQuestionIndex === 0"
                  icon="ios-arrow-back"
                >
                  上一题
                </Button>
                <Button 
                  @click="nextQuestion" 
                  :disabled="currentQuestionIndex === questions.length - 1"
                  icon="ios-arrow-forward"
                  style="margin-left: 10px;"
                >
                  下一题
                </Button>
              </div>
            </Card>
          </div>
        </Col>
        
        <!-- 题目导航面板 -->
        <Col span="6">
          <Card class="navigation-panel">
            <div class="panel-header">
              <h4>题目导航</h4>
            </div>
            
            <div class="question-grid">
              <div 
                v-for="(question, index) in questions" 
                :key="index"
                class="question-nav-item"
                :class="getNavItemClass(index)"
                @click="goToQuestion(index)"
              >
                {{ index + 1 }}
              </div>
            </div>
            
            <div class="legend">
              <div class="legend-item">
                <div class="legend-color correct"></div>
                <span>答对</span>
              </div>
              <div class="legend-item">
                <div class="legend-color wrong"></div>
                <span>答错</span>
              </div>
              <div class="legend-item">
                <div class="legend-color unanswered"></div>
                <span>未答</span>
              </div>
            </div>
            
            <div class="action-buttons">
              <Button @click="goBack" type="default" long style="margin-bottom: 10px;">
                返回结果页
              </Button>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  </div>
</template>

<script>
import api from '../../api'

export default {
  name: 'ExamReview',
  data() {
    return {
      examSession: {},
      questions: [],
      userAnswers: {},
      currentQuestionIndex: 0,
      loading: false
    }
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentQuestionIndex]
    }
  },
  mounted() {
    this.loadExamDetail()
  },
  methods: {
    async loadExamDetail() {
      this.loading = true
      try {
        const sessionId = this.$route.params.sessionId
        const response = await api.getExamSessionDetail(sessionId)
        this.examSession = response.data.data
        this.questions = response.data.data.questions || []
        this.userAnswers = response.data.data.user_answers || {}
      } catch (error) {
        console.error('加载考试详情失败:', error)
        this.$Message.error('加载考试详情失败')
      } finally {
        this.loading = false
      }
    },
    
    previousQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--
      }
    },
    
    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++
      }
    },
    
    goToQuestion(index) {
      this.currentQuestionIndex = index
    },
    
    getUserAnswer() {
      const questionId = this.currentQuestion.id
      return this.userAnswers[questionId] || []
    },
    
    isAnswerCorrect() {
      const userAnswer = this.getUserAnswer()
      const correctAnswer = this.currentQuestion.correct_answer || []
      
      if (userAnswer.length !== correctAnswer.length) {
        return false
      }
      
      return userAnswer.every(answer => correctAnswer.includes(answer))
    },
    
    isCorrectOption(index) {
      return this.currentQuestion.correct_answer && this.currentQuestion.correct_answer.includes(index)
    },
    
    isUserSelectedOption(index) {
      const userAnswer = this.getUserAnswer()
      return userAnswer.includes(index)
    },
    
    getOptionClass(index) {
      const isCorrect = this.isCorrectOption(index)
      const isSelected = this.isUserSelectedOption(index)
      
      if (isCorrect) {
        return 'correct'
      } else if (isSelected) {
        return 'wrong'
      }
      return ''
    },
    
    getNavItemClass(index) {
      const question = this.questions[index]
      const questionId = question.id
      const userAnswer = this.userAnswers[questionId] || []
      const correctAnswer = question.correct_answer || []
      
      let classes = []
      
      if (index === this.currentQuestionIndex) {
        classes.push('current')
      }
      
      if (userAnswer.length === 0) {
        classes.push('unanswered')
      } else if (userAnswer.length === correctAnswer.length && 
                 userAnswer.every(answer => correctAnswer.includes(answer))) {
        classes.push('correct')
      } else {
        classes.push('wrong')
      }
      
      return classes.join(' ')
    },
    
    formatAnswer(answer) {
      if (!answer || answer.length === 0) return ''
      return answer.map(index => String.fromCharCode(65 + index)).join(', ')
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    },
    
    getQuestionTypeColor(type) {
      const colors = {
        'single': 'blue',
        'multiple': 'purple'
      }
      return colors[type] || 'default'
    },
    
    getQuestionTypeDisplay(type) {
      const displays = {
        'single': '单选题',
        'multiple': '多选题'
      }
      return displays[type] || type
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
      this.$router.push({
        name: 'exam-result',
        params: { sessionId: this.$route.params.sessionId }
      })
    }
  }
}
</script>

<style scoped>
.exam-review {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.exam-header {
  background: white;
  padding: 20px;
  border-radius: 6px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.exam-header h2 {
  margin: 0 0 10px 0;
  color: #333;
}

.exam-info {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.exam-info .divider {
  margin: 0 10px;
  color: #ddd;
}

.score-section {
  text-align: right;
}

.score-display {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 4px;
  color: #52c41a;
  font-weight: 500;
}

.score-text {
  margin-left: 8px;
  font-size: 16px;
}

.score-percentage {
  margin-left: 8px;
  font-size: 14px;
}

.exam-content {
  margin-top: 20px;
}

.question-card {
  margin-bottom: 20px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e8eaec;
}

.question-header h3 {
  margin: 0;
  color: #333;
}

.question-text {
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 20px;
  color: #333;
}

.question-description {
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 20px;
  color: #666;
  background: #f8f9fa;
  padding: 12px 16px;
  border-radius: 6px;
  border-left: 4px solid #2d8cf0;
}

.options {
  margin-bottom: 30px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 8px;
  border-radius: 4px;
  border: 1px solid #e8eaec;
  position: relative;
}

.option-item.correct {
  background: #f6ffed;
  border-color: #b7eb8f;
}

.option-item.wrong {
  background: #fff2f0;
  border-color: #ffccc7;
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
  margin-bottom: 20px;
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

.question-actions {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e8eaec;
}

.navigation-panel {
  position: sticky;
  top: 20px;
}

.panel-header h4 {
  margin: 0 0 20px 0;
  color: #333;
  text-align: center;
}

.question-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin-bottom: 20px;
}

.question-nav-item {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e8eaec;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.question-nav-item:hover {
  border-color: #2d8cf0;
  background: #f0f9ff;
}

.question-nav-item.current {
  border-color: #2d8cf0;
  background: #2d8cf0;
  color: white;
}

.question-nav-item.correct {
  background: #f6ffed;
  border-color: #52c41a;
  color: #52c41a;
}

.question-nav-item.wrong {
  background: #fff2f0;
  border-color: #f5222d;
  color: #f5222d;
}

.question-nav-item.unanswered {
  background: #fafafa;
  border-color: #d9d9d9;
  color: #999;
}

.legend {
  margin-bottom: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: #666;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  margin-right: 8px;
}

.legend-color.correct {
  background: #52c41a;
}

.legend-color.wrong {
  background: #f5222d;
}

.legend-color.unanswered {
  background: #d9d9d9;
}

.action-buttons {
  padding-top: 20px;
  border-top: 1px solid #e8eaec;
}
</style>