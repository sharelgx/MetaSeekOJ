<template>
  <div class="practice-mode">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <Spin size="large">
        <Icon type="ios-loading" size=18 class="spin-icon-load"></Icon>
        <div>正在加载题目...</div>
      </Spin>
    </div>
    
    <!-- 调试信息 -->
    <div v-if="!loading && questions.length > 0 && !practiceStarted" class="debug-info" style="padding: 20px; background: #f0f0f0; margin: 20px; border-radius: 4px;">
      <h4>调试信息:</h4>
      <p>loading: {{loading}}</p>
      <p>questions.length: {{questions.length}}</p>
      <p>practiceStarted: {{practiceStarted}}</p>
      <p>_isMounted: {{_isMounted}}</p>
      <p>等待练习开始...</p>
      <Button type="primary" @click="startPractice" style="margin-top: 10px;">手动开始练习</Button>
    </div>
    
    <!-- 练习内容 -->
    <div v-else-if="questions.length > 0 && practiceStarted">
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
            
            <!-- 筛选条件显示 -->
            <div class="filter-info" v-if="hasFilters">
              <div class="filter-title">
                <Icon type="ios-funnel" size="16" />
                <span>当前筛选条件:</span>
              </div>
              <div class="filter-tags">
                <Tag v-if="filterParams.category" color="blue">
                  分类: {{ getCategoryName(filterParams.category) }}
                </Tag>
                <Tag v-if="filterParams.difficulty" color="orange">
                  难度: {{ getDifficultyText(filterParams.difficulty) }}
                </Tag>
                <Tag v-if="filterParams.question_type" color="green">
                  题型: {{ getQuestionTypeText(filterParams.question_type) }}
                </Tag>
                <Tag v-if="filterParams.keyword" color="purple">
                  关键词: {{ filterParams.keyword }}
                </Tag>
                <Tag v-if="filterParams.tags" color="cyan">
                  标签: {{ filterParams.tags }}
                </Tag>
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
    
    <!-- 题目已加载但练习未开始状态 -->
    <div v-else-if="questions.length > 0 && !practiceStarted" class="loading-container">
      <Spin size="large">
        <Icon type="ios-loading" size=18 class="spin-icon-load"></Icon>
        <div>正在初始化练习...</div>
      </Spin>
    </div>
    
    <!-- 无题目状态 -->
    <div v-else class="no-questions-container">
      <div class="no-questions-content">
        <Icon type="ios-document" size="48" color="#c5c8ce" />
        <h3>暂无题目</h3>
        <p>没有找到符合条件的题目，请调整筛选条件后重试。</p>
        <Button type="primary" @click="$router.push('/choice-questions')">返回题目列表</Button>
      </div>
    </div>
  </div>
</template>

<script>
import AnswerSheet from './components/AnswerSheet.vue'
import api from '../../api'

export default {
  name: 'PracticeMode',
  
  components: {
    AnswerSheet
  },
  
  props: {
    practiceConfig: {
      type: Object,
      default: () => ({})
    }
  },
  
  data() {
    console.log('PracticeMode - data初始化')
    return {
      _isMounted: false,
      questions: [],
      loading: false,
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
      
      showResultModal: false,
      
      // 筛选参数
      filterParams: {}
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
    },
    
    hasFilters() {
      return Object.values(this.filterParams).some(value => value !== null && value !== '')
    }
  },
  
  watch: {
    currentIndex() {
      this.loadCurrentQuestion()
    },
    
    questions: {
      handler(newVal, oldVal) {
        console.log('PracticeMode - questions数组变化:', {
          oldLength: oldVal ? oldVal.length : 0,
          newLength: newVal ? newVal.length : 0,
          practiceStarted: this.practiceStarted
        })
      },
      deep: true
    }
  },
  
  async mounted() {
    // 防止重复挂载，但如果没有题目数据则允许重新加载
    if (this._isMounted && this.questions.length > 0) {
      console.log('PracticeMode - 防止重复挂载（已有题目数据）')
      return
    }
    this._isMounted = true
    console.log('PracticeMode - 开始挂载，当前题目数量:', this.questions.length)
    
    // 从路由查询参数中获取筛选条件
    const query = this.$route.query
    console.log('PracticeMode mounted - 路由查询参数:', query)
    
    // 解析筛选参数
    this.filterParams = {
      category: query.category || null,
      difficulty: query.difficulty || null,
      tags: query.tags || null,
      question_type: query.question_type || null,
      keyword: query.keyword || null,
      is_public: query.is_public || null
    }
    
    console.log('PracticeMode - 解析的筛选参数:', this.filterParams)
    
    await this.loadQuestions(this.filterParams)
    if (this.questions.length > 0) {
      this.startPractice()
    }
  },
  
  beforeDestroy() {
    this.clearTimers()
    this._isMounted = false
    console.log('PracticeMode - 组件销毁，重置挂载标志')
  },
  
  methods: {
    async loadQuestions(filterParams = {}) {
      this.loading = true
      try {
        // 构建API请求参数，移除空值
        const params = {
          offset: 0,
          limit: 100  // 练习模式获取更多题目
        }
        
        // 添加筛选参数（只添加非空值）
        if (filterParams.category) params.category = filterParams.category
        if (filterParams.difficulty) params.difficulty = filterParams.difficulty
        if (filterParams.tags) params.tags = filterParams.tags
        if (filterParams.question_type) params.question_type = filterParams.question_type
        if (filterParams.keyword) params.keyword = filterParams.keyword
        if (filterParams.is_public !== null) params.is_public = filterParams.is_public
        
        console.log('PracticeMode - API请求参数:', params)
        
        // 练习模式使用getQuestionList
        const res = await api.getQuestionList(params)
        this.questions = (res.data.data && res.data.data.results) || res.data.results || []
        
        console.log('PracticeMode - 获取到的题目数量:', this.questions.length)
        
        if (this.questions.length === 0) {
          this.$Message.warning('没有找到符合条件的题目，请调整筛选条件')
          // 不自动跳转，让用户可以调整筛选条件
          // this.$router.push('/choice-questions')
        }
      } catch (err) {
        console.error('获取题目失败:', err)
        this.$Message.error('获取题目失败: ' + (err.response && err.response.data && err.response.data.error ? err.response.data.error : err.message))
        // this.$router.push('/choice-questions')
      } finally {
        this.loading = false
      }
    },
    
    startPractice() {
      console.log('=== startPractice 开始 ===', {
        questionsLength: this.questions.length,
        loading: this.loading,
        practiceStarted: this.practiceStarted
      })
      
      this.practiceStarted = true
      this.startTime = Date.now()
      
      console.log('startPractice - 设置practiceStarted为true，开始时间:', this.startTime)
      
      this.loadCurrentQuestion()
      this.startTimer()
      
      console.log('=== startPractice 结束 ===', {
        practiceStarted: this.practiceStarted,
        currentIndex: this.currentIndex,
        currentQuestion: !!this.currentQuestion
      })
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
          this.$router.push('/choice-questions')
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
      console.log('=== loadCurrentQuestion 开始 ===', {
        currentIndex: this.currentIndex,
        questionsLength: this.questions.length,
        currentQuestion: !!this.currentQuestion,
        currentQuestionId: this.currentQuestion ? this.currentQuestion.id : null
      })
      
      if (!this.currentQuestion) {
        console.log('loadCurrentQuestion - 当前题目为空，返回')
        return
      }
      
      // 加载当前题目的答案
      this.currentAnswer = this.answers[this.currentIndex] || []
      
      console.log('loadCurrentQuestion - 加载答案:', {
        currentAnswer: this.currentAnswer,
        allAnswers: this.answers
      })
      
      // 开始计时
      this.startQuestionTimer()
      
      console.log('=== loadCurrentQuestion 结束 ===')
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
    },
    
    getCategoryName(categoryId) {
      // 这里可以根据实际情况从分类列表中获取分类名称
      // 暂时直接返回ID
      return `分类${categoryId}`
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

.filter-info {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e8eaec;
}

.filter-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #808695;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  text-align: center;
}

.spin-icon-load {
  animation: ani-demo-spin 1s linear infinite;
}

@keyframes ani-demo-spin {
  from { transform: rotate(0deg);}
  50%  { transform: rotate(180deg);}
  to   { transform: rotate(360deg);}
}

.no-questions-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  text-align: center;
}

.no-questions-content h3 {
  margin: 16px 0 8px 0;
  color: #17233d;
}

.no-questions-content p {
  margin-bottom: 16px;
  color: #808695;
}
</style>