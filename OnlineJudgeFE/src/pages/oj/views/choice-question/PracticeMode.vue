<template>
  <div class="practice-mode">
    <!-- 练习头部 -->
    <div class="practice-header">
      <Card :bordered="false" class="header-card">
        <div class="header-content">
          <div class="practice-info">
            <div class="practice-title">
              <Icon type="ios-school" size="24" color="#2d8cf0" />
              <h2>选择题练习</h2>
            </div>
            
            <div class="practice-stats">
              <div class="stat-item">
                <span class="stat-label">进度:</span>
                <span class="stat-value">{{ currentIndex + 1 }} / {{ questions.length }}</span>
              </div>
              
              <div class="stat-item">
                <span class="stat-label">正确率:</span>
                <span class="stat-value" :class="accuracyClass">
                  {{ accuracy }}%
                </span>
              </div>
              
              <div class="stat-item">
                <span class="stat-label">用时:</span>
                <span class="stat-value">{{ formatTime(elapsedTime) }}</span>
              </div>
            </div>
          </div>
          
          <div class="practice-actions">
            <Button 
              type="default" 
              @click="pausePractice"
              :disabled="!practiceStarted || practiceCompleted"
            >
              <Icon :type="paused ? 'ios-play' : 'ios-pause'" />
              {{ paused ? '继续' : '暂停' }}
            </Button>
            
            <Button 
              type="error" 
              @click="exitPractice"
            >
              <Icon type="ios-exit" />
              退出练习
            </Button>
          </div>
        </div>
        
        <!-- 进度条 -->
        <div class="progress-section">
          <Progress 
            :percent="progressPercent" 
            :stroke-width="8"
            :show-info="false"
            class="practice-progress"
          />
          
          <div class="progress-indicators">
            <div 
              v-for="(question, index) in questions" 
              :key="question.id"
              class="progress-dot"
              :class="{
                'current': index === currentIndex,
                'answered': answeredQuestions.includes(index),
                'correct': getQuestionResult(index) === 'correct',
                'incorrect': getQuestionResult(index) === 'incorrect'
              }"
              @click="goToQuestion(index)"
            >
              {{ index + 1 }}
            </div>
          </div>
        </div>
      </Card>
    </div>
    
    <!-- 练习内容 -->
    <div class="practice-content" v-if="currentQuestion">
      <Row :gutter="20">
        <!-- 题目区域 -->
        <Col :xs="24" :lg="16">
          <Card :bordered="false" class="question-card">
            <div class="question-header">
              <div class="question-meta">
                <Tag :color="getDifficultyColor(currentQuestion.difficulty)">
                  {{ getDifficultyText(currentQuestion.difficulty) }}
                </Tag>
                <Tag color="blue">{{ getQuestionTypeText(currentQuestion.question_type) }}</Tag>
                <Tag color="green">{{ currentQuestion.score }}分</Tag>
              </div>
              
              <div class="question-timer" v-if="practiceStarted && !paused">
                <Icon type="ios-time" />
                <span>{{ formatTime(questionTime) }}</span>
              </div>
            </div>
            
            <div class="question-content">
              <h3 class="question-title">
                第{{ currentIndex + 1 }}题: {{ currentQuestion.title }}
              </h3>
              
              <div class="question-description" v-html="currentQuestion.description"></div>
              
              <!-- 答题组件 -->
              <AnswerSheet
                :question="currentQuestion"
                v-model="currentAnswer"
                :disabled="paused || isQuestionAnswered"
                :show-result="showCurrentResult"
                :result="currentQuestionResult"
                :submitting="submitting"
                @submit="submitCurrentAnswer"
              />
            </div>
          </Card>
        </Col>
        
        <!-- 侧边栏 -->
        <Col :xs="24" :lg="8">
          <!-- 答题卡 -->
          <Card :bordered="false" class="answer-card" title="答题卡">
            <div class="answer-grid">
              <div 
                v-for="(question, index) in questions" 
                :key="question.id"
                class="answer-item"
                :class="{
                  'current': index === currentIndex,
                  'answered': answeredQuestions.includes(index),
                  'correct': getQuestionResult(index) === 'correct',
                  'incorrect': getQuestionResult(index) === 'incorrect'
                }"
                @click="goToQuestion(index)"
              >
                <span class="answer-number">{{ index + 1 }}</span>
                <Icon 
                  v-if="getQuestionResult(index) === 'correct'" 
                  type="ios-checkmark" 
                  color="#19be6b" 
                  size="12"
                />
                <Icon 
                  v-else-if="getQuestionResult(index) === 'incorrect'" 
                  type="ios-close" 
                  color="#ed4014" 
                  size="12"
                />
              </div>
            </div>
          </Card>
          
          <!-- 练习统计 -->
          <Card :bordered="false" class="stats-card" title="练习统计">
            <div class="stats-list">
              <div class="stats-item">
                <span class="stats-label">总题数:</span>
                <span class="stats-value">{{ questions.length }}</span>
              </div>
              
              <div class="stats-item">
                <span class="stats-label">已答题:</span>
                <span class="stats-value">{{ answeredQuestions.length }}</span>
              </div>
              
              <div class="stats-item">
                <span class="stats-label">正确数:</span>
                <span class="stats-value correct">{{ correctCount }}</span>
              </div>
              
              <div class="stats-item">
                <span class="stats-label">错误数:</span>
                <span class="stats-value incorrect">{{ incorrectCount }}</span>
              </div>
              
              <div class="stats-item">
                <span class="stats-label">正确率:</span>
                <span class="stats-value" :class="accuracyClass">{{ accuracy }}%</span>
              </div>
              
              <div class="stats-item">
                <span class="stats-label">平均用时:</span>
                <span class="stats-value">{{ averageTime }}</span>
              </div>
            </div>
          </Card>
          
          <!-- 操作按钮 -->
          <Card :bordered="false" class="actions-card">
            <div class="action-buttons">
              <Button 
                type="default" 
                block 
                @click="previousQuestion"
                :disabled="currentIndex === 0"
              >
                <Icon type="ios-arrow-back" />
                上一题
              </Button>
              
              <Button 
                type="primary" 
                block 
                @click="nextQuestion"
                :disabled="currentIndex === questions.length - 1"
              >
                下一题
                <Icon type="ios-arrow-forward" />
              </Button>
              
              <Button 
                type="success" 
                block 
                @click="finishPractice"
                :disabled="!canFinish"
              >
                <Icon type="ios-checkmark-circle" />
                完成练习
              </Button>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
    
    <!-- 练习完成 -->
    <Modal
      v-model="showResultModal"
      title="练习完成"
      :closable="false"
      :mask-closable="false"
      width="600"
    >
      <div class="result-content">
        <div class="result-header">
          <Icon type="ios-trophy" size="48" color="#ff9900" />
          <h3>恭喜完成练习！</h3>
        </div>
        
        <div class="result-stats">
          <Row :gutter="16">
            <Col :span="8">
              <div class="result-stat">
                <div class="stat-number">{{ questions.length }}</div>
                <div class="stat-label">总题数</div>
              </div>
            </Col>
            <Col :span="8">
              <div class="result-stat">
                <div class="stat-number correct">{{ correctCount }}</div>
                <div class="stat-label">正确数</div>
              </div>
            </Col>
            <Col :span="8">
              <div class="result-stat">
                <div class="stat-number" :class="accuracyClass">{{ accuracy }}%</div>
                <div class="stat-label">正确率</div>
              </div>
            </Col>
          </Row>
          
          <Row :gutter="16" style="margin-top: 20px;">
            <Col :span="8">
              <div class="result-stat">
                <div class="stat-number">{{ totalScore }}</div>
                <div class="stat-label">总得分</div>
              </div>
            </Col>
            <Col :span="8">
              <div class="result-stat">
                <div class="stat-number">{{ formatTime(elapsedTime) }}</div>
                <div class="stat-label">用时</div>
              </div>
            </Col>
            <Col :span="8">
              <div class="result-stat">
                <div class="stat-number">{{ averageTime }}</div>
                <div class="stat-label">平均用时</div>
              </div>
            </Col>
          </Row>
        </div>
      </div>
      
      <div slot="footer">
        <Button type="default" @click="reviewAnswers">查看解析</Button>
        <Button type="primary" @click="restartPractice">重新练习</Button>
        <Button type="success" @click="exitPractice">返回列表</Button>
      </div>
    </Modal>
  </div>
</template>

<script>
import AnswerSheet from './components/AnswerSheet.vue'

export default {
  name: 'PracticeMode',
  
  components: {
    AnswerSheet
  },
  
  props: {
    questions: {
      type: Array,
      required: true
    },
    practiceConfig: {
      type: Object,
      default: () => ({})
    }
  },
  
  data() {
    return {
      currentIndex: 0,
      currentAnswer: [],
      answers: {},
      results: {},
      
      practiceStarted: false,
      practiceCompleted: false,
      paused: false,
      submitting: false,
      
      startTime: null,
      elapsedTime: 0,
      questionStartTime: null,
      questionTime: 0,
      
      timer: null,
      questionTimer: null,
      
      showResultModal: false
    }
  },
  
  computed: {
    currentQuestion() {
      return this.questions[this.currentIndex]
    },
    
    answeredQuestions() {
      return Object.keys(this.answers).map(key => parseInt(key))
    },
    
    correctCount() {
      return Object.values(this.results).filter(result => result.is_correct === true).length
    },
    
    incorrectCount() {
      return Object.values(this.results).filter(result => result.is_correct === false).length
    },
    
    accuracy() {
      if (this.answeredQuestions.length === 0) return 0
      return Math.round((this.correctCount / this.answeredQuestions.length) * 100)
    },
    
    accuracyClass() {
      if (this.accuracy >= 80) return 'excellent'
      if (this.accuracy >= 60) return 'good'
      return 'poor'
    },
    
    progressPercent() {
      return Math.round((this.answeredQuestions.length / this.questions.length) * 100)
    },
    
    totalScore() {
      return Object.values(this.results).reduce((sum, result) => sum + (result.score || 0), 0)
    },
    
    averageTime() {
      if (this.answeredQuestions.length === 0) return '0s'
      const avgSeconds = Math.round(this.elapsedTime / this.answeredQuestions.length)
      return this.formatTime(avgSeconds)
    },
    
    canFinish() {
      return this.answeredQuestions.length === this.questions.length
    },
    
    isQuestionAnswered() {
      return this.answeredQuestions.includes(this.currentIndex)
    },
    
    showCurrentResult() {
      return this.isQuestionAnswered
    },
    
    currentQuestionResult() {
      return this.results[this.currentIndex] || {}
    }
  },
  
  watch: {
    currentIndex() {
      this.loadCurrentQuestion()
    }
  },
  
  mounted() {
    this.startPractice()
  },
  
  beforeDestroy() {
    this.clearTimers()
  },
  
  methods: {
    startPractice() {
      this.practiceStarted = true
      this.startTime = Date.now()
      this.loadCurrentQuestion()
      this.startTimer()
    },
    
    pausePractice() {
      this.paused = !this.paused
      
      if (this.paused) {
        this.clearTimers()
      } else {
        this.startTimer()
        this.startQuestionTimer()
      }
    },
    
    exitPractice() {
      this.$Modal.confirm({
        title: '确认退出',
        content: '确定要退出练习吗？当前进度将不会保存。',
        onOk: () => {
          this.clearTimers()
          this.$emit('exit')
        }
      })
    },
    
    finishPractice() {
      this.practiceCompleted = true
      this.clearTimers()
      this.showResultModal = true
    },
    
    restartPractice() {
      this.currentIndex = 0
      this.currentAnswer = []
      this.answers = {}
      this.results = {}
      this.practiceStarted = false
      this.practiceCompleted = false
      this.paused = false
      this.elapsedTime = 0
      this.questionTime = 0
      this.showResultModal = false
      
      this.startPractice()
    },
    
    reviewAnswers() {
      this.showResultModal = false
      // 可以跳转到答案解析页面
      this.$emit('review', {
        questions: this.questions,
        answers: this.answers,
        results: this.results
      })
    },
    
    loadCurrentQuestion() {
      if (!this.currentQuestion) return
      
      // 加载当前题目的答案
      this.currentAnswer = this.answers[this.currentIndex] || []
      
      // 开始计时
      this.startQuestionTimer()
    },
    
    goToQuestion(index) {
      if (index >= 0 && index < this.questions.length) {
        this.currentIndex = index
      }
    },
    
    previousQuestion() {
      if (this.currentIndex > 0) {
        this.currentIndex--
      }
    },
    
    nextQuestion() {
      if (this.currentIndex < this.questions.length - 1) {
        this.currentIndex++
      }
    },
    
    submitCurrentAnswer(data) {
      if (this.submitting) return
      
      this.submitting = true
      
      // 保存答案
      this.answers[this.currentIndex] = [...data.answers]
      
      // 模拟提交和判题
      setTimeout(() => {
        const result = this.judgeAnswer(this.currentQuestion, data.answers)
        this.results[this.currentIndex] = result
        
        this.submitting = false
        
        // 自动跳转到下一题
        if (this.practiceConfig.autoNext && this.currentIndex < this.questions.length - 1) {
          setTimeout(() => {
            this.nextQuestion()
          }, 1000)
        }
      }, 500)
    },
    
    judgeAnswer(question, answers) {
      const correctOptions = question.options
        .map((option, index) => option.is_correct ? index : null)
        .filter(index => index !== null)
      
      const isCorrect = answers.length === correctOptions.length && 
        answers.every(answer => correctOptions.includes(answer))
      
      return {
        is_correct: isCorrect,
        score: isCorrect ? question.score : 0,
        correct_answers: correctOptions,
        user_answers: answers
      }
    },
    
    getQuestionResult(index) {
      const result = this.results[index]
      if (!result) return null
      return result.is_correct ? 'correct' : 'incorrect'
    },
    
    startTimer() {
      this.timer = setInterval(() => {
        if (!this.paused) {
          this.elapsedTime = Math.floor((Date.now() - this.startTime) / 1000)
        }
      }, 1000)
    },
    
    startQuestionTimer() {
      this.questionStartTime = Date.now()
      this.questionTime = 0
      
      this.questionTimer = setInterval(() => {
        if (!this.paused) {
          this.questionTime = Math.floor((Date.now() - this.questionStartTime) / 1000)
        }
      }, 1000)
    },
    
    clearTimers() {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
      
      if (this.questionTimer) {
        clearInterval(this.questionTimer)
        this.questionTimer = null
      }
    },
    
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs.toString().padStart(2, '0')}`
    },
    
    getDifficultyColor(difficulty) {
      const colorMap = {
        'Low': 'green',
        'Mid': 'orange', 
        'High': 'red'
      }
      return colorMap[difficulty] || 'default'
    },
    
    getDifficultyText(difficulty) {
      const textMap = {
        'Low': '简单',
        'Mid': '中等',
        'High': '困难'
      }
      return textMap[difficulty] || difficulty
    },
    
    getQuestionTypeText(type) {
      const typeMap = {
        'single': '单选题',
        'multiple': '多选题',
        'judge': '判断题',
        'fill': '填空题'
      }
      return typeMap[type] || type
    }
  }
}
</script>

<style scoped>
.practice-mode {
  min-height: 100vh;
  background: #f5f7fa;
}

.practice-header {
  margin-bottom: 20px;
}

.header-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.practice-info {
  flex: 1;
}

.practice-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.practice-title h2 {
  margin: 0;
  color: #17233d;
}

.practice-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-label {
  font-size: 14px;
  color: #808695;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #17233d;
}

.stat-value.excellent {
  color: #19be6b;
}

.stat-value.good {
  color: #ff9900;
}

.stat-value.poor {
  color: #ed4014;
}

.practice-actions {
  display: flex;
  gap: 12px;
}

.progress-section {
  margin-top: 20px;
}

.practice-progress {
  margin-bottom: 16px;
}

.progress-indicators {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.progress-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f0f0f0;
  color: #c5c8ce;
  border: 2px solid transparent;
}

.progress-dot.current {
  border-color: #2d8cf0;
  background: #2d8cf0;
  color: #fff;
}

.progress-dot.answered {
  background: #e8f4ff;
  color: #2d8cf0;
}

.progress-dot.correct {
  background: #f6ffed;
  color: #19be6b;
}

.progress-dot.incorrect {
  background: #fff2f0;
  color: #ed4014;
}

.practice-content {
  margin-bottom: 20px;
}

.question-card,
.answer-card,
.stats-card,
.actions-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 16px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.question-meta {
  display: flex;
  gap: 8px;
}

.question-timer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #808695;
}

.question-title {
  margin: 0 0 16px 0;
  color: #17233d;
  font-size: 18px;
  line-height: 1.4;
}

.question-description {
  margin-bottom: 24px;
  color: #515a6e;
  line-height: 1.6;
}

.answer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
  gap: 8px;
}

.answer-item {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f0f0f0;
  color: #c5c8ce;
  border: 2px solid transparent;
  position: relative;
}

.answer-item.current {
  border-color: #2d8cf0;
  background: #2d8cf0;
  color: #fff;
}

.answer-item.answered {
  background: #e8f4ff;
  color: #2d8cf0;
}

.answer-item.correct {
  background: #f6ffed;
  color: #19be6b;
}

.answer-item.incorrect {
  background: #fff2f0;
  color: #ed4014;
}

.answer-number {
  font-size: 12px;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stats-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-label {
  font-size: 14px;
  color: #808695;
}

.stats-value {
  font-size: 14px;
  font-weight: 600;
  color: #17233d;
}

.stats-value.correct {
  color: #19be6b;
}

.stats-value.incorrect {
  color: #ed4014;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-content {
  text-align: center;
}

.result-header {
  margin-bottom: 30px;
}

.result-header h3 {
  margin: 16px 0 0 0;
  color: #17233d;
}

.result-stats {
  margin-bottom: 20px;
}

.result-stat {
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: 600;
  color: #17233d;
  margin-bottom: 8px;
}

.stat-number.correct {
  color: #19be6b;
}

.stat-number.excellent {
  color: #19be6b;
}

.stat-number.good {
  color: #ff9900;
}

.stat-number.poor {
  color: #ed4014;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .practice-stats {
    flex-direction: column;
    gap: 12px;
  }
  
  .question-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .progress-indicators {
    justify-content: center;
  }
  
  .answer-grid {
    grid-template-columns: repeat(8, 1fr);
  }
}
</style>