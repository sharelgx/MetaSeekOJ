<template>
  <div class="question-answering">
    <!-- 题目头部信息 -->
    <Card class="question-header">
      <div class="question-meta">
        <div class="meta-left">
          <Tag color="blue">{{ question.difficulty }}</Tag>
          <Tag color="green">{{ questionTypeText }}</Tag>
          <Tag color="orange">{{ question.score }}分</Tag>
          <Tag v-if="question.category" color="purple">{{ question.category.name }}</Tag>
        </div>
        <div class="meta-right">
          <div v-if="timeLimit > 0" class="timer" :class="{ 'timer-warning': timeRemaining <= 30 }">
            <Icon type="ios-time" />
            {{ formatTime(timeRemaining) }}
          </div>
          <Button 
            v-if="!isSubmitted && !readonly" 
            type="primary" 
            @click="submitAnswer"
            :loading="submitting"
            :disabled="!hasAnswer"
          >
            提交答案
          </Button>
        </div>
      </div>
    </Card>
    
    <!-- 题目内容 -->
    <Card class="question-content">
      <div slot="title">
        <span class="question-title">{{ question.title }}</span>
      </div>
      <div slot="extra" v-if="!readonly">
        <ButtonGroup>
          <Button 
            v-if="question.hint_count > 0 && hintsUsed < question.hint_count"
            @click="getHint"
            size="small"
          >
            <Icon type="ios-help-circle" />
            提示 ({{ hintsUsed }}/{{ question.hint_count }})
          </Button>
          <Button @click="addToWrongBook" size="small">
            <Icon type="ios-bookmark" />
            加入错题本
          </Button>
        </ButtonGroup>
      </div>
      
      <div class="content-body" v-html="question.content"></div>
      
      <!-- 提示信息 -->
      <div v-if="hints.length > 0" class="hints-section">
        <h4><Icon type="ios-bulb" /> 提示信息</h4>
        <div v-for="(hint, index) in hints" :key="index" class="hint-item">
          <Alert type="info" show-icon>
            {{ hint }}
          </Alert>
        </div>
      </div>
    </Card>
    
    <!-- 选项区域 -->
    <Card class="options-section">
      <div slot="title">
        <Icon type="ios-list" />
        {{ question.question_type === 'single_choice' ? '请选择一个答案' : '请选择一个或多个答案' }}
      </div>
      
      <div class="options-container">
        <div 
          v-for="(option, index) in question.options"
          :key="index"
          class="option-item"
          :class="getOptionClass(option, index)"
          @click="selectOption(index)"
        >
          <div class="option-content">
            <div class="option-prefix">
              <!-- 单选题使用Radio，多选题使用Checkbox -->
              <Radio 
                v-if="question.question_type === 'single_choice'"
                :value="selectedAnswers.includes(index)"
                :disabled="readonly"
              >
                {{ String.fromCharCode(65 + index) }}
              </Radio>
              <Checkbox 
                v-else
                :value="selectedAnswers.includes(index)"
                :disabled="readonly"
              >
                {{ String.fromCharCode(65 + index) }}
              </Checkbox>
            </div>
            <div class="option-text">{{ option.content }}</div>
            
            <!-- 答案状态图标 -->
            <div class="option-status" v-if="isSubmitted || readonly">
              <Icon 
                v-if="option.is_correct"
                type="ios-checkmark-circle"
                color="#19be6b"
                size="20"
              />
              <Icon 
                v-else-if="selectedAnswers.includes(index) && !option.is_correct"
                type="ios-close-circle"
                color="#ed4014"
                size="20"
              />
            </div>
          </div>
          
          <!-- 选项解释 -->
          <div 
            v-if="(isSubmitted || readonly) && option.explanation"
            class="option-explanation"
          >
            <div class="explanation-content">
              <Icon type="ios-information-circle" color="#2d8cf0" />
              {{ option.explanation }}
            </div>
          </div>
        </div>
      </div>
    </Card>
    
    <!-- 答题结果 -->
    <Card v-if="isSubmitted || readonly" class="result-section">
      <div slot="title">
        <Icon :type="isCorrect ? 'ios-checkmark-circle' : 'ios-close-circle'" />
        <span :class="isCorrect ? 'correct-text' : 'incorrect-text'">
          {{ isCorrect ? '回答正确' : '回答错误' }}
        </span>
      </div>
      
      <div class="result-details">
        <Row :gutter="16">
          <Col :span="6">
            <Statistic title="得分" :value="currentScore" suffix="分" />
          </Col>
          <Col :span="6">
            <Statistic title="用时" :value="answerTime" suffix="秒" />
          </Col>
          <Col :span="6">
            <Statistic title="正确答案" :value="correctAnswersText" />
          </Col>
          <Col :span="6">
            <Statistic title="你的答案" :value="userAnswersText" />
          </Col>
        </Row>
      </div>
      
      <!-- 题目解析 -->
      <div v-if="question.explanation" class="explanation-section">
        <h4><Icon type="ios-document" /> 题目解析</h4>
        <div class="explanation-content">
          {{ question.explanation }}
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="result-actions">
        <Button v-if="!readonly" type="primary" @click="retryQuestion">
          <Icon type="ios-refresh" />
          重新答题
        </Button>
        <Button @click="viewSimilarQuestions">
          <Icon type="ios-search" />
          相似题目
        </Button>
        <Button v-if="!isCorrect" @click="addToWrongBook">
          <Icon type="ios-bookmark" />
          加入错题本
        </Button>
      </div>
    </Card>
    
    <!-- 相似题目模态框 -->
    <Modal
      v-model="similarModal"
      title="相似题目"
      width="800"
      :footer-hide="true"
    >
      <div class="similar-questions">
        <div 
          v-for="similar in similarQuestions"
          :key="similar.id"
          class="similar-item"
          @click="goToQuestion(similar.id)"
        >
          <div class="similar-title">{{ similar.title }}</div>
          <div class="similar-meta">
            <Tag size="small" color="blue">{{ similar.difficulty }}</Tag>
            <Tag size="small" color="green">{{ similar.question_type === 'single_choice' ? '单选' : '多选' }}</Tag>
            <span class="similar-score">{{ similar.score }}分</span>
          </div>
        </div>
        
        <div v-if="similarQuestions.length === 0" class="no-similar">
          <Icon type="ios-information-circle" size="48" color="#c5c8ce" />
          <p>暂无相似题目</p>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'QuestionAnswering',
  props: {
    question: {
      type: Object,
      required: true
    },
    readonly: {
      type: Boolean,
      default: false
    },
    initialAnswers: {
      type: Array,
      default: () => []
    },
    showResult: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      selectedAnswers: [],
      isSubmitted: false,
      submitting: false,
      
      // 计时相关
      startTime: null,
      timeRemaining: 0,
      timer: null,
      
      // 提示相关
      hints: [],
      hintsUsed: 0,
      
      // 答题结果
      isCorrect: false,
      currentScore: 0,
      answerTime: 0,
      
      // 相似题目
      similarModal: false,
      similarQuestions: []
    }
  },
  computed: {
    questionTypeText() {
      return this.question.question_type === 'single_choice' ? '单选题' : '多选题'
    },
    
    timeLimit() {
      return this.question.time_limit || 0
    },
    
    hasAnswer() {
      return this.selectedAnswers.length > 0
    },
    
    correctAnswersText() {
      const correctIndexes = this.question.options
        .map((opt, index) => opt.is_correct ? index : -1)
        .filter(index => index !== -1)
      return correctIndexes.map(index => String.fromCharCode(65 + index)).join(', ')
    },
    
    userAnswersText() {
      return this.selectedAnswers
        .map(index => String.fromCharCode(65 + index))
        .join(', ') || '未作答'
    }
  },
  watch: {
    question: {
      handler() {
        this.init()
      },
      immediate: true
    },
    
    initialAnswers: {
      handler(newVal) {
        if (newVal && newVal.length > 0) {
          this.selectedAnswers = [...newVal]
        }
      },
      immediate: true
    },
    
    showResult: {
      handler(newVal) {
        if (newVal) {
          this.isSubmitted = true
          this.checkAnswer()
        }
      },
      immediate: true
    }
  },
  beforeDestroy() {
    this.clearTimer()
  },
  methods: {
    init() {
      this.selectedAnswers = this.initialAnswers ? [...this.initialAnswers] : []
      this.isSubmitted = this.showResult
      this.submitting = false
      this.hints = []
      this.hintsUsed = 0
      this.startTime = Date.now()
      
      if (this.timeLimit > 0) {
        this.timeRemaining = this.timeLimit
        this.startTimer()
      }
      
      if (this.showResult) {
        this.checkAnswer()
      }
    },
    
    startTimer() {
      this.clearTimer()
      this.timer = setInterval(() => {
        this.timeRemaining--
        if (this.timeRemaining <= 0) {
          this.timeUp()
        }
      }, 1000)
    },
    
    clearTimer() {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
    },
    
    timeUp() {
      this.clearTimer()
      this.$Message.warning('时间到，自动提交答案')
      this.submitAnswer()
    },
    
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    },
    
    selectOption(index) {
      if (this.readonly || this.isSubmitted) {
        return
      }
      
      if (this.question.question_type === 'single_choice') {
        // 单选题：只能选择一个
        this.selectedAnswers = [index]
      } else {
        // 多选题：可以选择多个
        const currentIndex = this.selectedAnswers.indexOf(index)
        if (currentIndex > -1) {
          this.selectedAnswers.splice(currentIndex, 1)
        } else {
          this.selectedAnswers.push(index)
        }
      }
      
      this.$emit('answer-change', this.selectedAnswers)
    },
    
    getOptionClass(option, index) {
      const classes = ['option-clickable']
      
      if (this.selectedAnswers.includes(index)) {
        classes.push('option-selected')
      }
      
      if (this.isSubmitted || this.readonly) {
        if (option.is_correct) {
          classes.push('option-correct')
        } else if (this.selectedAnswers.includes(index)) {
          classes.push('option-incorrect')
        }
      }
      
      return classes
    },
    
    async submitAnswer() {
      if (!this.hasAnswer) {
        this.$Message.warning('请先选择答案')
        return
      }
      
      this.submitting = true
      this.clearTimer()
      
      try {
        const submitData = {
          question_id: this.question.id,
          user_answer: this.selectedAnswers,
          time_used: Math.floor((Date.now() - this.startTime) / 1000)
        }
        
        const res = await api.submitChoiceQuestion(submitData)
        
        this.isSubmitted = true
        this.isCorrect = res.data.is_correct
        this.currentScore = res.data.score
        this.answerTime = res.data.time_used
        
        this.$emit('submit', {
          ...res.data,
          user_answer: this.selectedAnswers
        })
        
        if (this.isCorrect) {
          this.$Message.success('回答正确！')
        } else {
          this.$Message.error('回答错误')
        }
      } catch (error) {
        this.$Message.error('提交失败，请重试')
      } finally {
        this.submitting = false
      }
    },
    
    checkAnswer() {
      const correctAnswers = this.question.options
        .map((opt, index) => opt.is_correct ? index : -1)
        .filter(index => index !== -1)
      
      // 检查答案是否完全匹配
      const sortedCorrect = correctAnswers.sort()
      const sortedUser = [...this.selectedAnswers].sort()
      
      this.isCorrect = sortedCorrect.length === sortedUser.length &&
        sortedCorrect.every((val, index) => val === sortedUser[index])
      
      this.currentScore = this.isCorrect ? this.question.score : 0
      this.answerTime = this.timeLimit > 0 ? this.timeLimit - this.timeRemaining : 0
    },
    
    async getHint() {
      if (this.hintsUsed >= this.question.hint_count) {
        return
      }
      
      try {
        const res = await api.getQuestionHint(this.question.id, this.hintsUsed + 1)
        this.hints.push(res.data.hint)
        this.hintsUsed++
        
        this.$emit('hint-used', this.hintsUsed)
      } catch (error) {
        this.$Message.error('获取提示失败')
      }
    },
    
    async addToWrongBook() {
      try {
        await api.addToWrongBook({
          question_id: this.question.id,
          error_type: this.isSubmitted && !this.isCorrect ? 'wrong_answer' : 'manual_add',
          note: ''
        })
        
        this.$Message.success('已加入错题本')
        this.$emit('added-to-wrong-book')
      } catch (error) {
        if (error.response && error.response.status === 400) {
          this.$Message.warning('该题目已在错题本中')
        } else {
          this.$Message.error('加入错题本失败')
        }
      }
    },
    
    retryQuestion() {
      this.selectedAnswers = []
      this.isSubmitted = false
      this.isCorrect = false
      this.currentScore = 0
      this.answerTime = 0
      this.hints = []
      this.hintsUsed = 0
      this.startTime = Date.now()
      
      if (this.timeLimit > 0) {
        this.timeRemaining = this.timeLimit
        this.startTimer()
      }
      
      this.$emit('retry')
    },
    
    async viewSimilarQuestions() {
      try {
        const res = await api.getSimilarQuestions(this.question.id)
        this.similarQuestions = res.data
        this.similarModal = true
      } catch (error) {
        this.$Message.error('获取相似题目失败')
      }
    },
    
    goToQuestion(questionId) {
      this.similarModal = false
      this.$emit('navigate-to-question', questionId)
    }
  }
}
</script>

<style scoped>
.question-answering {
  max-width: 1000px;
  margin: 0 auto;
}

.question-header {
  margin-bottom: 16px;
}

.question-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meta-left {
  display: flex;
  gap: 8px;
  align-items: center;
}

.meta-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.timer {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 16px;
  font-weight: bold;
  color: #2d8cf0;
}

.timer-warning {
  color: #ed4014;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.question-content {
  margin-bottom: 16px;
}

.question-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.content-body {
  margin: 16px 0;
  line-height: 1.6;
  color: #666;
}

.hints-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e8eaec;
}

.hints-section h4 {
  margin-bottom: 12px;
  color: #333;
}

.hint-item {
  margin-bottom: 8px;
}

.options-section {
  margin-bottom: 16px;
}

.options-container {
  margin-top: 16px;
}

.option-item {
  margin-bottom: 12px;
  border: 2px solid #dcdee2;
  border-radius: 6px;
  background: #fff;
  transition: all 0.3s ease;
}

.option-clickable {
  cursor: pointer;
}

.option-clickable:hover {
  border-color: #2d8cf0;
  box-shadow: 0 2px 8px rgba(45, 140, 240, 0.15);
}

.option-selected {
  border-color: #2d8cf0;
  background: #f0f9ff;
}

.option-correct {
  border-color: #19be6b;
  background: #f6ffed;
}

.option-incorrect {
  border-color: #ed4014;
  background: #fff2f0;
}

.option-content {
  display: flex;
  align-items: center;
  padding: 16px;
}

.option-prefix {
  margin-right: 12px;
}

.option-text {
  flex: 1;
  line-height: 1.5;
}

.option-status {
  margin-left: 12px;
}

.option-explanation {
  padding: 12px 16px;
  background: #f8f8f9;
  border-top: 1px solid #e8eaec;
}

.explanation-content {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: #666;
  line-height: 1.5;
}

.result-section {
  margin-bottom: 16px;
}

.correct-text {
  color: #19be6b;
}

.incorrect-text {
  color: #ed4014;
}

.result-details {
  margin: 20px 0;
}

.explanation-section {
  margin: 20px 0;
  padding: 16px;
  background: #f0f9ff;
  border-radius: 6px;
  border-left: 4px solid #2d8cf0;
}

.explanation-section h4 {
  margin-bottom: 12px;
  color: #2d8cf0;
}

.result-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
}

.similar-questions {
  max-height: 400px;
  overflow-y: auto;
}

.similar-item {
  padding: 12px;
  margin-bottom: 8px;
  border: 1px solid #dcdee2;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.similar-item:hover {
  border-color: #2d8cf0;
  background: #f0f9ff;
}

.similar-title {
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.similar-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.similar-score {
  color: #666;
  font-size: 12px;
}

.no-similar {
  text-align: center;
  padding: 40px;
  color: #c5c8ce;
}

.no-similar p {
  margin-top: 12px;
  font-size: 14px;
}
</style>