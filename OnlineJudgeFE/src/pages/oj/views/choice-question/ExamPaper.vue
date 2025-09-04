<template>
  <div class="exam-paper">
    <!-- 考试头部信息 -->
    <div class="exam-header">
      <Row>
        <Col span="16">
          <h2>{{ examPaper.title }}</h2>
          <p class="exam-info">
            <span>总分：{{ examPaper.total_score }}分</span>
            <span class="divider">|</span>
            <span>题目数量：{{ examPaper.question_count }}题</span>
            <span class="divider">|</span>
            <span>考试时长：{{ examPaper.time_limit }}分钟</span>
          </p>
        </Col>
        <Col span="8" class="timer-section">
          <div class="timer" :class="{ 'timer-warning': timeWarning, 'timer-danger': timeDanger }">
            <Icon type="ios-time" size="20" />
            <span class="time-text">剩余时间：{{ formatTime(remainingTime) }}</span>
          </div>
          <Button @click="debugAPI" type="primary" size="small" style="margin-top: 10px;">调试API</Button>
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
                  <Tag :color="currentQuestion.question_type === 'single' ? 'blue' : 'green'">
                    {{ currentQuestion.question_type === 'single' ? '单选题' : '多选题' }}
                  </Tag>
                </div>
              </div>
              
              <div class="question-content">
                <div class="question-text" v-html="currentQuestion.content"></div>
                <div v-if="currentQuestion.description" class="question-description" v-html="currentQuestion.description"></div>
                
                <div class="options">
                  <div 
                    v-for="(option, index) in currentQuestion.options" 
                    :key="index"
                    class="option-item"
                    @click="selectOption(index)"
                  >
                    <Radio 
                      v-if="currentQuestion.question_type === 'single'"
                      :value="isOptionSelected(index)"
                      :disabled="examSession.status === 'submitted'"
                    >
                      <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
                      <span class="option-text" v-html="option.text || option"></span>
                    </Radio>
                    <Checkbox 
                      v-else
                      :value="isOptionSelected(index)"
                      :disabled="examSession.status === 'submitted'"
                    >
                      <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
                      <span class="option-text" v-html="option.text || option"></span>
                    </Checkbox>
                  </div>
                </div>
              </div>
              
              <div class="question-actions">
                <Button 
                  type="default" 
                  @click="previousQuestion" 
                  :disabled="currentQuestionIndex === 0"
                >
                  上一题
                </Button>
                <Button 
                  type="primary" 
                  @click="nextQuestion" 
                  :disabled="currentQuestionIndex === questions.length - 1"
                >
                  下一题
                </Button>
              </div>
            </Card>
          </div>
        </Col>
        
        <!-- 答题卡区域 -->
        <Col span="6">
          <div class="answer-sheet">
            <Card>
              <div slot="title">
                <Icon type="ios-list" />
                答题卡
              </div>
              
              <div class="answer-grid">
                <div 
                  v-for="(question, index) in questions"
                  :key="question.id"
                  class="answer-item"
                  :class="{
                    'current': index === currentQuestionIndex,
                    'answered': isQuestionAnswered(index),
                    'unanswered': !isQuestionAnswered(index)
                  }"
                  @click="goToQuestion(index)"
                >
                  {{ index + 1 }}
                </div>
              </div>
              
              <div class="answer-stats">
                <p>已答题：{{ answeredCount }} / {{ questions.length }}</p>
                <p>未答题：{{ questions.length - answeredCount }}</p>
              </div>
              
              <div class="submit-section">
                <Button 
                  type="error" 
                  long 
                  @click="showSubmitConfirm"
                  :disabled="examSession.status === 'submitted'"
                >
                  提交试卷
                </Button>
              </div>
            </Card>
          </div>
        </Col>
      </Row>
    </div>

    <!-- 提交确认对话框 -->
    <Modal
      v-model="submitModalVisible"
      title="提交确认"
      @on-ok="submitExam"
      @on-cancel="submitModalVisible = false"
    >
      <p>确定要提交试卷吗？提交后将无法修改答案。</p>
      <p>当前已答题：{{ answeredCount }} / {{ questions.length }}</p>
      <p v-if="answeredCount < questions.length" class="warning-text">
        还有 {{ questions.length - answeredCount }} 题未作答，确定提交吗？
      </p>
    </Modal>
  </div>
</template>

<script>
import api from '../../api'

export default {
  name: 'ExamPaper',
  data() {
    return {
      paperId: null,
      examPaper: {},
      examSession: {},
      questions: [],
      currentQuestionIndex: 0,
      answers: {},
      remainingTime: 0,
      timer: null,
      submitModalVisible: false,
      loading: true,
      saveTimer: null, // 防抖定时器
      savingAnswers: {} // 记录正在保存的题目
    }
  },
  
  computed: {
    currentQuestion() {
      return this.questions[this.currentQuestionIndex] || null
    },
    
    answeredCount() {
      return Object.keys(this.answers).length
    },
    
    timeWarning() {
      return this.remainingTime <= 300 && this.remainingTime > 60 // 5分钟警告
    },
    
    timeDanger() {
      return this.remainingTime <= 60 // 1分钟危险
    }
  },
  
  async mounted() {
    // 从路由参数获取paperId
    this.paperId = this.$route.params.paperId
    
    if (!this.paperId) {
      console.error('缺少试卷ID参数')
      this.$Message.error('缺少试卷ID参数')
      this.$router.push({ name: 'choice-question-list' })
      return
    }
    
    console.log('试卷ID:', this.paperId)
    
    // 初始化考试
    await this.initExam()
    
    // 启动计时器
    this.startTimer()
    
    // 初始化代码高亮和数学公式渲染
    this.$nextTick(() => {
      this.highlightCode()
      this.renderMath()
    })
  },
  
  beforeDestroy() {
    if (this.timer) {
      clearInterval(this.timer)
    }
    if (this.saveTimer) {
      clearTimeout(this.saveTimer)
    }
  },
  
  methods: {
    // 代码高亮方法
    highlightCode() {
      try {
        const codeBlocks = this.$el.querySelectorAll('pre code, code')
        codeBlocks.forEach(block => {
          if (block.tagName === 'CODE' && block.parentNode.tagName !== 'PRE') {
            // 行内代码，不需要高亮
            return
          }
          try {
            // 兼容不同版本的 highlight.js
            if (typeof hljs.highlightElement === 'function') {
              hljs.highlightElement(block)
            } else if (typeof hljs.highlightBlock === 'function') {
              hljs.highlightBlock(block)
            } else {
              // 手动高亮
              const result = hljs.highlightAuto(block.textContent)
              block.innerHTML = result.value
              block.className = `hljs ${result.language || ''}`
            }
          } catch (e) {
            console.warn('代码高亮失败:', e)
          }
        })
      } catch (error) {
        console.error('代码高亮处理失败:', error)
      }
    },
    
    // 数学公式渲染方法
    renderMath() {
      try {
        // 扩大选择器范围，包含所有可能包含数学公式的元素
        const mathElements = this.$el.querySelectorAll('.option-text, .question-text, .question-content, p, div')
        mathElements.forEach(element => {
          let html = element.innerHTML
          
          // 跳过已经渲染过的KaTeX元素
          if (element.querySelector('.katex') || element.classList.contains('katex')) {
            return
          }
          
          // 处理块级数学公式 $$...$$
          html = html.replace(/\$\$([^$]+?)\$\$/g, (match, formula) => {
            try {
              const rendered = katex.renderToString(formula.trim(), {
                displayMode: true,
                throwOnError: false
              })
              console.log('渲染块级公式:', formula.trim())
              return rendered
            } catch (e) {
              console.warn('数学公式渲染失败:', formula, e)
              return match
            }
          })
          
          // 处理行内数学公式 $...$（避免匹配$$...$$）
           html = html.replace(/\$([^$\n]+?)\$/g, (match, formula) => {
             // 跳过已经是$$...$$格式的公式
             if (match.includes('$$')) {
               return match
             }
            try {
              const rendered = katex.renderToString(formula.trim(), {
                displayMode: false,
                throwOnError: false
              })
              console.log('渲染行内公式:', formula.trim())
              return rendered
            } catch (e) {
              console.warn('数学公式渲染失败:', formula, e)
              return match
            }
          })
          
          if (html !== element.innerHTML) {
            element.innerHTML = html
          }
        })
      } catch (error) {
        console.error('数学公式渲染处理失败:', error)
      }
    },

    async initExam() {
      try {
        this.loading = true
        
        // 1. 获取试卷详情
        console.log('获取试卷详情, paperId:', this.paperId)
        const paperResponse = await api.getExamPaperDetail(this.paperId)
        this.examPaper = paperResponse.data.data || paperResponse.data || paperResponse
        console.log('试卷详情:', this.examPaper)
        
        // 2. 创建或获取考试会话
        console.log('创建考试会话...')
        const sessionResponse = await api.createExamSession(this.paperId)
        this.examSession = sessionResponse.data.data || sessionResponse.data || sessionResponse
        console.log('考试会话:', this.examSession)
        
        // 验证考试会话是否创建成功
        if (!this.examSession || !this.examSession.id) {
          throw new Error('考试会话创建失败，会话ID为空')
        }
        
        // 3. 如果会话未开始，则开始考试
        if (this.examSession.status === 'created') {
          console.log('开始考试...')
          const startResponse = await api.startExamSession(this.examSession.id)
          this.examSession = startResponse.data.data || startResponse.data || startResponse
          
          // 验证开始考试是否成功
          if (!this.examSession || !this.examSession.id) {
            throw new Error('开始考试失败，会话状态异常')
          }
        }
        
        // 4. 加载题目
        if (this.examSession.question_details) {
          this.questions = this.examSession.question_details
        } else if (this.examSession.questions) {
          // 如果没有详情，根据ID列表加载题目
          await this.loadQuestionsByIds(this.examSession.questions)
        }
        
        console.log('加载题目完成:', this.questions.length, '题')
        
        // 验证和修复每个题目的options数据格式
        this.questions.forEach((question, questionIndex) => {
          if (question.options) {
            console.log(`题目${questionIndex + 1}原始options数据:`, question.options, '类型:', typeof question.options)
            
            // 如果options是字符串，尝试解析为JSON
            if (typeof question.options === 'string') {
              try {
                question.options = JSON.parse(question.options)
                console.log(`题目${questionIndex + 1}解析后的options:`, question.options)
              } catch (parseErr) {
                console.error(`题目${questionIndex + 1}解析options JSON失败:`, parseErr)
                this.$Message.error(`题目${questionIndex + 1}选项数据格式错误`)
                return
              }
            }
            
            // 确保options是数组
            if (!Array.isArray(question.options)) {
              console.error(`题目${questionIndex + 1}options不是数组:`, question.options)
              this.$Message.error(`题目${questionIndex + 1}选项数据格式错误`)
              return
            }
            
            // 验证每个选项的格式
            for (let i = 0; i < question.options.length; i++) {
              const option = question.options[i]
              if (!option || typeof option !== 'object') {
                console.error(`题目${questionIndex + 1}选项${i}格式错误:`, option)
                this.$Message.error(`题目${questionIndex + 1}选项数据格式错误`)
                return
              }
              
              // 确保选项有key和text字段
              if (!option.key || !option.text) {
                console.error(`题目${questionIndex + 1}选项${i}缺少必要字段:`, option)
                this.$Message.error(`题目${questionIndex + 1}选项数据格式错误`)
                return
              }
            }
            
            console.log(`题目${questionIndex + 1}验证通过的options:`, question.options)
          }
        })
        
        // 5. 设置剩余时间
        this.remainingTime = this.examSession.remaining_time || (this.examPaper.duration * 60)
        
        // 6. 恢复已有答案
        if (this.examSession.answers) {
          this.answers = this.examSession.answers
        }
        
      } catch (error) {
        console.error('初始化考试失败:', error)
        this.$Message.error('初始化考试失败：' + (error.message || '未知错误'))
        // 返回列表页
        setTimeout(() => {
          this.$router.push({ name: 'choice-question-list' })
        }, 2000)
      } finally {
        this.loading = false
      }
    },
    
    async createOrGetSession() {
      try {
        // 尝试创建新的考试会话
        const sessionRes = await api.createExamSession(this.examPaper.id)
        this.examSession = sessionRes.data.data || sessionRes.data || sessionRes
        
        // 如果会话已存在，加载已有答案
        if (this.examSession.answers) {
          this.answers = this.examSession.answers
        }
        
        // 计算剩余时间
        this.calculateRemainingTime()
        
        // 如果会话未开始，自动开始
        if (this.examSession.status === 'not_started') {
          await this.startSession()
        }
        
      } catch (err) {
        console.error('创建考试会话失败:', err)
        throw err
      }
    },
    
    async startSession() {
      try {
        const res = await api.startExamSession(this.examSession.id)
        this.examSession = res.data.data
        this.calculateRemainingTime()
      } catch (err) {
        console.error('开始考试失败:', err)
        this.$Message.error('开始考试失败')
      }
    },
    
    async loadQuestionsByIds(questionIds) {
      try {
        // 根据题目ID列表加载题目详情
        const promises = questionIds.map(id => api.getChoiceQuestionDetail(id))
        const responses = await Promise.all(promises)
        
        this.questions = responses.map(response => {
          return response.data.data || response.data || response
        })
        
        console.log('加载题目完成:', this.questions.length, '题')
      } catch (error) {
        console.error('加载题目失败:', error)
        throw new Error('加载题目失败')
      }
    },
    
    calculateRemainingTime() {
      if (this.examSession.start_time && this.examPaper.time_limit) {
        const startTime = new Date(this.examSession.start_time)
        const endTime = new Date(startTime.getTime() + this.examPaper.time_limit * 60 * 1000)
        const now = new Date()
        this.remainingTime = Math.max(0, Math.floor((endTime - now) / 1000))
      }
    },
    
    startTimer() {
      this.timer = setInterval(() => {
        if (this.remainingTime > 0) {
          this.remainingTime--
        } else {
          // 时间到，自动提交
          this.autoSubmit()
        }
      }, 1000)
    },
    
    formatTime(seconds) {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60
      
      if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
      } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`
      }
    },
    
    async selectOption(optionIndex) {
      if (this.examSession.status === 'submitted') return
      
      const questionId = this.currentQuestion.id
      
      if (this.currentQuestion.question_type === 'single') {
        // 单选题
        this.$set(this.answers, questionId, [optionIndex])
      } else {
        // 多选题
        if (!this.answers[questionId]) {
          this.$set(this.answers, questionId, [])
        }
        
        const currentAnswers = [...this.answers[questionId]]
        const index = currentAnswers.indexOf(optionIndex)
        
        if (index > -1) {
          currentAnswers.splice(index, 1)
        } else {
          currentAnswers.push(optionIndex)
        }
        
        this.$set(this.answers, questionId, currentAnswers)
      }
      
      // 自动保存答案
      await this.autoSaveAnswer(questionId)
    },
    
    isOptionSelected(optionIndex) {
      const questionId = this.currentQuestion.id
      const answer = this.answers[questionId]
      return answer && answer.includes(optionIndex)
    },
    
    isQuestionAnswered(questionIndex) {
      const question = this.questions[questionIndex]
      return this.answers[question.id] && this.answers[question.id].length > 0
    },
    
    goToQuestion(index) {
      this.currentQuestionIndex = index
    },
    
    previousQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--
        // 重新渲染代码高亮和数学公式
        this.$nextTick(() => {
          this.highlightCode()
          this.renderMath()
        })
      }
    },
    
    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++
        // 重新渲染代码高亮和数学公式
        this.$nextTick(() => {
          this.highlightCode()
          this.renderMath()
        })
      }
    },
    
    goToQuestion(index) {
      if (index >= 0 && index < this.questions.length) {
        this.currentQuestionIndex = index
        // 重新渲染代码高亮和数学公式
        this.$nextTick(() => {
          this.highlightCode()
          this.renderMath()
        })
      }
    },
    
    async autoSaveAnswer(questionId) {
      if (!questionId) return
      
      // 如果该题目正在保存，则跳过
      if (this.savingAnswers[questionId]) {
        return
      }
      
      // 清除之前的定时器
      if (this.saveTimer) {
        clearTimeout(this.saveTimer)
      }
      
      // 延迟保存，避免频繁请求
      this.saveTimer = setTimeout(async () => {
        try {
          this.savingAnswers[questionId] = true
          const answer = this.answers[questionId] || []
          
          // 确保答案是纯数组，去除Vue的Observer包装
          const cleanAnswer = JSON.parse(JSON.stringify(answer))
          
          const response = await api.submitExamAnswer(this.examSession.id, {
            question_id: questionId,
            answer: cleanAnswer
          })
          
          // 检查响应是否真的成功
          if (response.data && response.data.error) {
            console.error('保存失败:', response.data.data || response.data.error)
            this.$Message.error('保存答案失败：' + (response.data.data || response.data.error))
          } else {
            // 静默保存，不显示成功消息
            console.log('答案已自动保存:', questionId, cleanAnswer)
          }
          
        } catch (err) {
          console.error('保存答案失败:', err)
          // 只在失败时显示错误消息
          this.$Message.error('保存答案失败，请稍后重试')
        } finally {
          // 请求完成后移除标记
          delete this.savingAnswers[questionId]
        }
      }, 500) // 延迟500ms
    },
    
    showSubmitConfirm() {
      this.submitModalVisible = true
    },
    
    async submitExam() {
      try {
        this.loading = true
        
        // 检查考试会话是否存在
        if (!this.examSession || !this.examSession.id) {
          console.error('考试会话不存在或ID为空:', this.examSession)
          this.$Message.error('考试会话异常，无法提交试卷')
          return
        }
        
        // 清除防抖定时器
        if (this.saveTimer) {
          clearTimeout(this.saveTimer)
          this.saveTimer = null
        }
        
        // 等待所有正在保存的答案完成
        while (Object.keys(this.savingAnswers).length > 0) {
          await new Promise(resolve => setTimeout(resolve, 100))
        }
        
        // 清理答案数据，去除Vue的Observer包装
        const cleanAnswers = JSON.parse(JSON.stringify(this.answers))
        
        await api.submitExamSession(this.examSession.id, {
          answers: cleanAnswers
        })
        
        this.$Message.success('试卷提交成功')
        
        // 跳转到结果页面
        this.$router.push({
          name: 'exam-result',
          params: { sessionId: this.examSession.id }
        })
        
      } catch (err) {
        console.error('提交试卷失败:', err)
        this.$Message.error('提交试卷失败：' + (err.message || '未知错误'))
      } finally {
        this.loading = false
        this.submitModalVisible = false
      }
    },
    
    async autoSubmit() {
      if (this.timer) {
        clearInterval(this.timer)
      }
      
      this.$Message.warning('考试时间已到，系统将自动提交试卷')
      await this.submitExam()
    },
    
    async debugAPI() {
      console.log('=== 开始API调试 ===')
      
      try {
        // 1. 检查用户登录状态
        console.log('1. 检查用户登录状态')
        console.log('用户信息:', this.$store.getters.user)
        console.log('是否已认证:', this.$store.getters.isAuthenticated)
        
        // 2. 测试创建考试会话
        console.log('2. 测试创建考试会话')
        const sessionResponse = await api.createExamSession(this.paperId)
        console.log('会话响应:', sessionResponse)
        console.log('会话数据:', sessionResponse.data)
        
        if (sessionResponse.data && sessionResponse.data.data) {
          console.log('会话ID:', sessionResponse.data.data.id)
        }
        
        this.$Message.success('API调试完成，请查看控制台')
        
      } catch (error) {
        console.error('API调试失败:', error)
        console.error('错误响应:', error.response)
        this.$Message.error('API调试失败：' + error.message)
      }
    }
  }
}
</script>

<style scoped>
.exam-paper {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.exam-header {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.exam-header h2 {
  margin: 0 0 10px 0;
  color: #2d8cf0;
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

.timer-section {
  text-align: right;
}

.timer {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 4px;
  color: #2d8cf0;
  font-weight: 500;
}

.timer-warning {
  background: #fff7e6;
  border-color: #ffd591;
  color: #fa8c16;
}

.timer-danger {
  background: #fff2f0;
  border-color: #ffccc7;
  color: #f5222d;
}

.time-text {
  margin-left: 8px;
  font-size: 16px;
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
  margin-bottom: 12px;
  padding: 16px 20px;
  border: 1px solid #e8eaec;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  min-height: 50px;
  display: flex;
  align-items: center;
}

.option-item:hover {
  border-color: #2d8cf0;
  background: #f0f9ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(45, 140, 240, 0.15);
}

.option-label {
  font-weight: 500;
  margin-right: 8px;
}

.option-text {
  color: #333;
}

.question-actions {
  text-align: center;
}

.question-actions .ivu-btn {
  margin: 0 8px;
}

.answer-sheet {
  position: sticky;
  top: 20px;
}

.answer-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin-bottom: 20px;
}

.answer-item {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.answer-item.current {
  background: #2d8cf0;
  color: white;
  border-color: #2d8cf0;
}

.answer-item.answered {
  background: #52c41a;
  color: white;
  border-color: #52c41a;
}

.answer-item.unanswered {
  background: #f5f5f5;
  color: #999;
}

.answer-item:hover {
  border-color: #2d8cf0;
}

.answer-stats {
  margin-bottom: 20px;
  padding: 10px;
  background: #f8f8f9;
  border-radius: 4px;
}

.answer-stats p {
  margin: 5px 0;
  font-size: 14px;
  color: #666;
}

.submit-section {
  margin-top: 20px;
}

.warning-text {
  color: #fa8c16;
  font-weight: 500;
}
</style>