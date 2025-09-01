<template>
  <div class="choice-question-detail">
    <Panel shadow v-if="question" class="main-panel">
      <div slot="title" class="panel-title">
        <Icon type="ios-help-circle" class="title-icon" />
        <span class="question-number">#{{ question._id }}</span>
        <span class="question-title">{{ question.title }}</span>
      </div>
      
      <div slot="extra">
        
        <!-- 加入错题本按钮 -->
        <Button 
          type="error" 
          size="small" 
          @click="addToWrongQuestions"
          v-if="!isInWrongQuestions && hasSubmitted"
          class="bookmark-btn"
        >
          <Icon type="ios-bookmark" />
          加入错题本
        </Button>
      </div>
      
      <!-- 题目信息 -->
      <div class="question-info">
        <div class="info-grid">
          <div class="info-card">
            <div class="info-icon">
              <Icon type="ios-folder" />
            </div>
            <div class="info-content">
              <div class="info-label">分类</div>
              <div class="info-value">{{ question.category ? question.category.name : '未分类' }}</div>
            </div>
          </div>
          
          <div class="info-card">
            <div class="info-icon difficulty-icon">
              <Icon type="ios-speedometer" />
            </div>
            <div class="info-content">
              <div class="info-label">难度</div>
              <div class="info-value">
                <Tag :color="getDifficultyColor(question.difficulty)" class="difficulty-tag">
                  {{ getDifficultyText(question.difficulty) }}
                </Tag>
              </div>
            </div>
          </div>
          
          <div class="info-card">
            <div class="info-icon">
              <Icon type="ios-list" />
            </div>
            <div class="info-content">
              <div class="info-label">题型</div>
              <div class="info-value">{{ question.question_type === 'single' ? '单选题' : '多选题' }}</div>
            </div>
          </div>
          
          <div class="info-card">
            <div class="info-icon">
              <Icon type="ios-star" />
            </div>
            <div class="info-content">
              <div class="info-label">分值</div>
              <div class="info-value">{{ question.score }} 分</div>
            </div>
          </div>
        </div>
        
        <div class="tags-section" v-if="question.tags && question.tags.length > 0">
          <div class="tags-label">
            <Icon type="ios-pricetags" />
            标签
          </div>
          <div class="tags-container">
            <Tag 
              v-for="tag in question.tags" 
              :key="tag.id"
              :color="tag.color"
              class="question-tag"
            >
              {{ tag.name }}
            </Tag>
          </div>
        </div>
      </div>
      
      <!-- 题目内容 -->
      <div class="question-content">
        <div class="section-header">
          <Icon type="ios-document" class="section-icon" />
          <h3>题目描述</h3>
        </div>
        <div class="content-box">
          <div class="content" v-html="question.description"></div>
        </div>
      </div>
      
      <!-- 选项 -->
      <div class="question-options">
        <div class="section-header">
          <Icon type="ios-radio-button-on" class="section-icon" />
          <h3>选择答案</h3>
        </div>
        <div v-if="question.question_type === 'single'">
          <RadioGroup v-model="selectedAnswer" :disabled="hasSubmitted">
            <div v-for="(option, index) in question.options" 
                 :key="index"
                 class="option-item" 
                 :class="[getOptionClass(option.key), { selected: selectedAnswer === option.key }]"
               >
              <Radio :label="option.key">
                <span class="option-label">{{ option.key }}.</span>
                <span class="option-content" v-html="option.text"></span>
              </Radio>
            </div>
          </RadioGroup>
        </div>
        <div v-else>
          <CheckboxGroup v-model="selectedAnswers" :disabled="hasSubmitted">
            <div v-for="(option, index) in question.options" 
                 :key="index"
                 class="option-item" 
                 :class="[getOptionClass(option.key), { selected: selectedAnswers.includes(option.key) }]"
               >
              <Checkbox :label="String.fromCharCode(65 + index)">
                <span class="option-label">{{ option.key }}.</span>
                <span class="option-content" v-html="option.text"></span>
              </Checkbox>
            </div>
          </CheckboxGroup>
        </div>
      </div>
      
      <!-- 提交按钮 -->
      <div class="submit-section">
        <div class="submit-container">
          <Button 
            type="primary" 
            size="large"
            @click="submitAnswer"
            :loading="submitting"
            :disabled="hasSubmitted || !canSubmit"
            class="submit-btn"
          >
            <Icon type="ios-checkmark-circle" v-if="!submitting" />
            {{ hasSubmitted ? '已提交' : '提交答案' }}
          </Button>
          <div class="submit-hint" v-if="!hasSubmitted && !canSubmit">
            <Icon type="ios-information-circle" />
            <span v-if="!isAuthenticated">请先登录后再提交答案</span>
            <span v-else>请选择答案后提交</span>
          </div>
          
          <!-- 登录按钮 -->
          <div class="login-section" v-if="!isAuthenticated && !hasSubmitted">
            <Button 
              type="success" 
              size="large"
              @click="showLoginModal"
              class="login-btn"
            >
              <Icon type="ios-log-in" />
              立即登录
            </Button>
          </div>
        </div>
        
        <!-- 导航按钮 -->
        <div class="navigation-section" v-if="showNavigation">
          <div class="navigation-buttons">
            <Button 
              type="default" 
              size="large"
              @click="goToPreviousQuestion"
              :disabled="!hasPreviousQuestion"
              class="nav-btn prev-btn"
            >
              <Icon type="ios-arrow-back" />
              上一题
            </Button>
            
            <div class="question-progress">
              <span class="progress-text">
                {{ currentIndex + 1 }} / {{ questionList.length }}
              </span>
            </div>
            
            <Button 
              type="default" 
              size="large"
              @click="goToNextQuestion"
              :disabled="!hasNextQuestion"
              class="nav-btn next-btn"
            >
              下一题
              <Icon type="ios-arrow-forward" />
            </Button>
          </div>
        </div>
      </div>
      
      <!-- 答案解析 -->
      <div class="answer-analysis" v-if="hasSubmitted">
        <div class="section-header analysis-header">
          <Icon type="ios-analytics" class="section-icon" />
          <h3>答案解析</h3>
        </div>
        
        <div class="result-info">
          <Alert 
            :type="isCorrect ? 'success' : 'error'"
            :show-icon="true"
          >
            <span slot="desc">
              {{ isCorrect ? '回答正确！' : '回答错误！' }}
              得分：{{ currentScore }} / {{ question.score }}
            </span>
          </Alert>
        </div>
        
        <div class="analysis-content">
          <div class="correct-answer-section">
            <div class="analysis-subsection-header">
              <Icon type="ios-checkmark-circle" class="subsection-icon" />
              <h4>正确答案</h4>
            </div>
            <div class="correct-answer-content">
              <div v-if="question.question_type === 'single'">
                <span class="answer-label">{{ question.correct_answer }}</span>
              </div>
              <div v-else>
                <span 
                  v-for="(answer, index) in question.correct_answer.split(',')" 
                  :key="index"
                  class="answer-label"
                >
                  {{ answer.trim() }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="explanation-section" v-if="question.explanation">
            <div class="analysis-subsection-header">
              <Icon type="ios-bulb" class="subsection-icon" />
              <h4>详细解析</h4>
            </div>
            <div class="explanation-content">
              <div class="content" v-html="question.explanation"></div>
            </div>
          </div>
        </div>
      </div>
    </Panel>
    
    <!-- 加载状态 -->
    <div v-else class="loading-container">
      <Spin size="large">加载中...</Spin>
    </div>
  </div>
</template>

<script>
import api from './api/index'
import { mapGetters } from 'vuex'

export default {
  name: 'ChoiceQuestionDetail',
  data() {
    return {
      question: null,
      selectedAnswer: null, // 单选答案
      selectedAnswers: [], // 多选答案
      hasSubmitted: false,
      submitting: false,
      isCorrect: false,
      currentScore: 0,
      isInWrongQuestions: false,
      questionList: [], // 当前筛选条件下的题目列表
      currentIndex: -1, // 当前题目在列表中的索引
      // 筛选条件（从URL参数获取）
      filterParams: {
        category: null,
        tags: null,
        difficulty: null,
        question_type: null
      }
    }
  },
  
  computed: {
    ...mapGetters(['isAuthenticated', 'user']),
    
    questionId() {
      return this.$route.params.id
    },
    
    canSubmit() {
      if (!this.isAuthenticated) {
        return false
      }
      if (this.question && this.question.question_type === 'single') {
        return this.selectedAnswer !== null
      } else {
        return this.selectedAnswers.length > 0
      }
    },
    
    hasPreviousQuestion() {
      return this.currentIndex > 0
    },
    
    hasNextQuestion() {
      return this.currentIndex >= 0 && this.currentIndex < this.questionList.length - 1
    },
    
    // 是否显示导航按钮（有筛选条件时显示）
    showNavigation() {
      const hasFilters = this.filterParams.category || 
                        this.filterParams.tags || 
                        this.filterParams.difficulty || 
                        this.filterParams.question_type
      
      console.log('=== 导航按钮显示条件检查 ===')
      console.log('筛选参数:', this.filterParams)
      console.log('是否有筛选条件:', hasFilters)
      console.log('题目列表长度:', this.questionList.length)
      console.log('当前索引:', this.currentIndex)
      
      return hasFilters && this.questionList.length > 1
    }
  },
  
  watch: {
    '$route'(to, from) {
      if (to.params.id !== from.params.id) {
        console.log('路由参数变化，重新加载数据')
        console.log('从题目:', from.params.id, '到题目:', to.params.id)
        
        this.resetQuestionState()
        this.getQuestionDetail()
        this.getQuestionListForNavigation()
      }
      
      // 监听查询参数变化（筛选条件变化）
      if (JSON.stringify(to.query) !== JSON.stringify(from.query)) {
        console.log('筛选条件变化，重新加载题目列表')
        this.getQuestionListForNavigation()
      }
    },
    
    // 监听数据变化
    question: {
      handler() {
        if (this.question) {
          this.handleImageResize();
        }
      },
      deep: true
    }
  },
  
  mounted() {
    console.log('=== 组件挂载调试信息 ===')
    console.log('当前路由:', this.$route)
    console.log('路由参数:', this.$route.params)
    console.log('查询参数:', this.$route.query)
    console.log('题目ID:', this.questionId)
    
    // 获取用户信息，确保登录状态
    this.$store.dispatch('getProfile')
    
    // 从URL获取筛选条件
    this.getFilterParamsFromRoute()
    console.log('获取的筛选参数:', this.filterParams)
    
    // 获取题目详情和列表
    this.getQuestionDetail()
    this.getQuestionListForNavigation()
  },
  
  methods: {
    resetQuestionState() {
      this.selectedAnswer = null
      this.selectedAnswers = []
      this.hasSubmitted = false
      this.submitting = false
      this.isCorrect = false
      this.currentScore = 0
      this.isInWrongQuestions = false
    },
    
    // 处理图片尺寸的方法
    handleImageResize() {
      // 等待DOM更新后处理图片
      this.$nextTick(() => {
        const images = this.$el.querySelectorAll('.content img, .option-content img, .explanation .content img');
        images.forEach(img => {
          // 强制设置图片样式
          img.style.maxWidth = '400px';
          img.style.width = 'auto';
          img.style.height = 'auto';
          img.style.display = 'block';
          img.style.margin = '10px auto';
          
          // 图片加载完成后确保样式生效
          img.onload = function() {
            // 样式已通过CSS设置，无需额外处理
          };
        });
      });
    },
    
    async getQuestionDetail() {
      try {
        const res = await api.getQuestionDetail(this.questionId)
        this.question = res.data.data
        
        // 验证题目数据完整性
        if (!this.question) {
          throw new Error('题目数据为空')
        }
        
        // 数据加载完成后处理图片
        this.handleImageResize();
        
      } catch (err) {
        this.$Message.error('获取题目详情失败')
        
        // 如果题目不存在，可能需要跳转回列表页
        if (err.response && err.response.status === 404) {
          this.$Message.error('题目不存在，即将返回列表页')
          setTimeout(() => {
            this.$router.push('/choice-questions')
          }, 2000)
        }
      }
    },
    
    goToPreviousQuestion() {
      if (this.hasPreviousQuestion) {
        const previousQuestion = this.questionList[this.currentIndex - 1]
        this.navigateToQuestion(previousQuestion.id)
      }
    },

    goToNextQuestion() {
      if (this.hasNextQuestion) {
        const nextQuestion = this.questionList[this.currentIndex + 1]
        this.navigateToQuestion(nextQuestion.id)
      }
    },
    
    navigateToQuestion(questionId) {
      // 防止导航到相同题目
      if (questionId.toString() === this.questionId.toString()) {
        console.log('避免重复导航到当前题目:', questionId)
        return
      }
      
      // 保持当前的筛选条件
      const query = { ...this.$route.query }
      
      try {
        // 使用 replace 替代 push 减少历史记录重复
        this.$router.replace({
          path: `/choice-question/${questionId}`,
          query
        })
      } catch (err) {
        // 捕获 NavigationDuplicated 错误
        if (err.name === 'NavigationDuplicated') {
          console.log('导航重复错误已捕获，继续执行')
        } else {
          console.error('导航错误:', err)
        }
      }
    },
    
    async getQuestionListForNavigation() {
      try {
        // 获取当前筛选条件（从路由查询参数或localStorage获取）
        const filters = this.getNavigationFilters()
        const res = await api.getQuestionList({
          limit: 1000, // 获取足够多的题目用于导航
          ...filters
        })
        
        this.questionList = res.data.data.results || res.data.data || []
        
        // 添加调试信息
        console.log('题目列表数据结构:', this.questionList)
        console.log('当前题目ID:', this.questionId, '类型:', typeof this.questionId)
        
        if (this.questionList.length > 0) {
          console.log('第一个题目的所有字段:', this.questionList[0])
          this.questionList.forEach((item, index) => {
            console.log(`题目${index + 1}:`, {
              id: item.id,
              _id: item._id,
              database_id: item.database_id,
              title: item.title
            })
          })
        }
        
        // 增强匹配逻辑：支持多种ID字段匹配
        let currentIndex = -1
        const currentId = this.questionId
        
        // 尝试不同的匹配方式
        currentIndex = this.questionList.findIndex(q => {
          // 尝试匹配 id 字段（数据库索引ID）
          if (q.id && q.id.toString() === currentId.toString()) {
            console.log('通过id字段匹配成功:', q.id)
            return true
          }
          // 尝试匹配 _id 字段（业务ID）
          if (q._id && q._id.toString() === currentId.toString()) {
            console.log('通过_id字段匹配成功:', q._id)
            return true
          }
          // 尝试匹配 database_id 字段
          if (q.database_id && q.database_id.toString() === currentId.toString()) {
            console.log('通过database_id字段匹配成功:', q.database_id)
            return true
          }
          return false
        })
        
        this.currentIndex = currentIndex
        console.log('匹配结果 - 当前索引:', this.currentIndex)
        
        if (this.currentIndex >= 0) {
          console.log('匹配到的题目:', this.questionList[this.currentIndex])
        } else {
          console.warn('未找到匹配的题目，可能的原因：')
          console.warn('1. 题目ID不在当前筛选结果中')
          console.warn('2. ID字段名不匹配')
          console.warn('3. 数据类型不匹配')
        }
      } catch (err) {
        console.error('获取题目列表失败:', err)
        this.questionList = []
         this.currentIndex = -1
       }
     },
    
    getNavigationFilters() {
      // 从路由查询参数获取筛选条件
      const query = this.$route.query
      const filters = {}
      
      if (query.category) filters.category = query.category
      if (query.tags) filters.tags = query.tags
      if (query.difficulty) filters.difficulty = query.difficulty
      if (query.question_type) filters.question_type = query.question_type
      if (query.keyword) filters.keyword = query.keyword
      
      console.log('导航筛选条件:', filters)
      return filters
    },
    
    // 从URL获取筛选条件
    getFilterParamsFromRoute() {
      console.log('=== 从路由获取筛选参数 ===')
      console.log('原始查询参数:', this.$route.query)
      
      this.filterParams = {
        category: this.$route.query.category || null,
        tags: this.$route.query.tags ? this.$route.query.tags.split(',') : [],
        difficulty: this.$route.query.difficulty || null,
        question_type: this.$route.query.question_type || null,
        keyword: this.$route.query.keyword || null
      }
      
      console.log('解析后的筛选参数:', this.filterParams)
      
      // 检查是否有任何筛选条件
      const hasFilters = Object.values(this.filterParams).some(value =>
        value !== null && (Array.isArray(value) ? value.length > 0 : true)
      )
      console.log('是否有筛选条件:', hasFilters)
    },
    
    async submitAnswer() {
      this.submitting = true
      
      // 添加调试信息
      console.log('题目信息:', this.question)
      console.log('题目ID:', this.question._id)
      console.log('单选答案:', this.selectedAnswer)
      console.log('多选答案:', this.selectedAnswers)
      console.log('题目类型:', this.question.question_type)
      
      try {
        // 检查用户是否已登录
        if (!this.$store.getters.isAuthenticated) {
          this.$Message.error('请先登录')
          this.$router.push('/login')
          return
        }
        
        // 验证题目数据
        if (!this.question || !this.question._id) {
          throw new Error('题目数据无效')
        }
        
        let userAnswer = []
        let selectedAnswerString = ''
        
        if (this.question.question_type === 'single') {
          // 单选题处理
          if (this.selectedAnswer === null || this.selectedAnswer === undefined) {
            throw new Error('请选择答案')
          }
          
          // 添加详细的调试信息
          console.log('单选答案原始值:', this.selectedAnswer)
          console.log('单选答案类型:', typeof this.selectedAnswer)
          
          // 智能转换：处理字符串和数字格式
          let answerIndex
          if (typeof this.selectedAnswer === 'string') {
            // 如果是字符串格式（'A', 'B'），转换为数字索引
            if (this.selectedAnswer.length === 1 && this.selectedAnswer >= 'A' && this.selectedAnswer <= 'Z') {
              answerIndex = this.selectedAnswer.charCodeAt(0) - 65
            } else {
              // 如果是数字字符串，转换为数字
              const num = parseInt(this.selectedAnswer)
              answerIndex = isNaN(num) ? null : num
            }
          } else if (typeof this.selectedAnswer === 'number') {
            // 如果已经是数字，直接使用
            answerIndex = this.selectedAnswer
          } else {
            answerIndex = null
          }
          
          console.log('处理后的单选索引:', answerIndex)
          
          if (answerIndex === null || answerIndex === undefined) {
            throw new Error('选择的答案无效')
          }
          
          userAnswer = [answerIndex]
          selectedAnswerString = String.fromCharCode(65 + answerIndex)
          
          console.log('处理后的单选字符串:', selectedAnswerString)
        } else {
          // 多选题处理
          if (!this.selectedAnswers || this.selectedAnswers.length === 0) {
            throw new Error('请至少选择一个答案')
          }
          
          console.log('原始多选答案:', this.selectedAnswers)
          console.log('答案类型:', this.selectedAnswers.map(item => typeof item))
          
          // 智能转换：处理字符串和数字格式
          userAnswer = this.selectedAnswers.map(item => {
            if (typeof item === 'string') {
              // 如果是字符串格式（'A', 'B'），转换为数字索引
              if (item.length === 1 && item >= 'A' && item <= 'Z') {
                return item.charCodeAt(0) - 65
              }
              // 如果是数字字符串，转换为数字
              const num = parseInt(item)
              return isNaN(num) ? null : num
            } else if (typeof item === 'number') {
              // 如果已经是数字，直接使用
              return item
            }
            return null
          }).filter(item => 
            item !== null && item !== undefined && typeof item === 'number'
          ).sort((a, b) => a - b)
          
          console.log('转换后的答案:', userAnswer)
          
          if (userAnswer.length === 0) {
            throw new Error('选择的答案无效')
          }
          
          selectedAnswerString = userAnswer.map(index => String.fromCharCode(65 + index)).join(',')
        }
        
        // 构建提交数据，使用索引ID保持一致性并添加用户信息
        const submitData = {
          question: parseInt(this.questionId), // 使用索引ID而不是业务ID
          selected_answer: selectedAnswerString, // 转换为 "A,B,C" 格式
          user: this.user.id, // 添加用户ID
          time_spent: 0, // 可以添加计时功能
          is_correct: false // 后端要求的字段，前端先设为false
        }
        
        console.log('用户认证状态:', this.isAuthenticated)
        console.log('当前用户:', this.user)
        console.log('索引ID类型:', typeof this.questionId, '值:', this.questionId)
        console.log('submitData中question的类型:', typeof submitData.question, '值:', submitData.question)
        console.log('最终提交数据:', submitData)
        
        const res = await api.submitAnswer(this.questionId, submitData)
        
        const result = res.data.data
        this.hasSubmitted = true
        this.isCorrect = result.is_correct
        this.currentScore = result.score
        
        // 如果答案错误，自动添加到错题本
        if (!result.is_correct) {
          try {
            await api.addToWrongQuestions({
              question_id: this.question._id
            })
            this.isInWrongQuestions = true
          } catch (err) {
            // 静默处理错误，可能是已经在错题本中了
            console.log('自动添加到错题本失败:', err)
          }
        }
        
        this.$Message.success('提交成功！')
        
        // 重新获取题目列表以更新导航状态
        await this.getQuestionListForNavigation()
      } catch (err) {
        console.error('提交错误详情:', err)
        if (err.response && err.response.data) {
          console.error('后端返回错误:', err.response.data)
        }
        let errorMsg = '提交失败'
        if (err.response && err.response.data && err.response.data.data) {
          if (typeof err.response.data.data === 'string') {
            errorMsg = err.response.data.data
          } else if (err.response.data.data.user) {
            errorMsg = '用户认证失败，请重新登录'
          }
        }
        this.$Message.error(errorMsg)
      } finally {
        this.submitting = false
      }
    },
    
    async addToWrongQuestions() {
      try {
        await api.addToWrongQuestions({
          question_id: this.question._id
        })
        this.isInWrongQuestions = true
        this.$Message.success('已加入错题本')
      } catch (err) {
        this.$Message.error('加入错题本失败')
        console.error(err)
      }
    },

    toggleMultipleChoice(optionKey) {
      if (this.hasSubmitted) return
      
      const index = this.selectedAnswers.indexOf(optionKey)
      if (index > -1) {
        this.selectedAnswers.splice(index, 1)
      } else {
        this.selectedAnswers.push(optionKey)
      }
    },
    
    getDifficultyColor(difficulty) {
      const colorMap = {
        'easy': 'success',
        'medium': 'warning', 
        'hard': 'error'
      }
      return colorMap[difficulty] || 'default'
    },

    getDifficultyText(difficulty) {
      const textMap = {
        'easy': '简单',
        'medium': '中等',
        'hard': '困难'
      }
      return textMap[difficulty] || '未知'
    },
    
    getOptionClass(optionKey) {
      if (!this.hasSubmitted) return ''
      
      let isCorrect = false
      if (this.question.question_type === 'single') {
        isCorrect = this.question.correct_answer === optionKey
      } else {
        const correctAnswers = this.question.correct_answer.split(',').map(a => a.trim())
        isCorrect = correctAnswers.includes(optionKey)
      }
      
      let isSelected = false
      if (this.question.question_type === 'single') {
        isSelected = this.selectedAnswer === optionKey
      } else {
        isSelected = this.selectedAnswers.includes(optionKey)
      }
      
      if (isCorrect) {
        return 'option-correct'
      } else if (isSelected && !isCorrect) {
        return 'option-wrong'
      }
      
      return ''
    },
    
    showLoginModal() {
      // 显示登录模态框
      this.$store.dispatch('changeModalStatus', {
        mode: 'login',
        visible: true
      })
    },

    // 获取题目列表（根据筛选条件）
    async getQuestionList() {
      try {
        const params = {}
        if (this.filterParams.category) {
          params.category = this.filterParams.category
        }
        if (this.filterParams.tags) {
          params.tags = this.filterParams.tags
        }
        if (this.filterParams.difficulty) {
          params.difficulty = this.filterParams.difficulty
        }
        if (this.filterParams.question_type) {
          params.question_type = this.filterParams.question_type
        }
        
        const res = await api.getQuestionList(params)
        this.questionList = res.data.data.results || []
        
        // 找到当前题目在列表中的索引
        this.currentIndex = this.questionList.findIndex(q => q.id.toString() === this.questionId)
      } catch (err) {
        console.error('获取题目列表失败:', err)
        this.questionList = []
        this.currentIndex = -1
      }
    },

    // 上一题
    async goToPreviousQuestion() {
      if (!this.hasPreviousQuestion) return
      
      const previousQuestion = this.questionList[this.currentIndex - 1]
      await this.navigateToQuestion(previousQuestion.id)
    },

    // 下一题
    async goToNextQuestion() {
      if (!this.hasNextQuestion) return
      
      const nextQuestion = this.questionList[this.currentIndex + 1]
      await this.navigateToQuestion(nextQuestion.id)
    },

    // 导航到指定题目
    async navigateToQuestion(questionId) {
      // 重置答题状态
      this.resetAnswerState()
      
      // 更新路由
      this.$router.push({
        name: 'choice-question-detail',
        params: { id: questionId.toString() },
        query: this.$route.query // 保持筛选条件
      })
    },

    // 重置答题状态
    resetAnswerState() {
      this.selectedAnswer = null
      this.selectedAnswers = []
      this.hasSubmitted = false
      this.isCorrect = false
      this.currentScore = 0
    },

    // 从URL获取筛选条件
    getFilterParamsFromRoute() {
      const query = this.$route.query
      this.filterParams = {
        category: query.category || null,
        tags: query.tags || null,
        difficulty: query.difficulty || null,
        question_type: query.question_type || null
      }
    }
  },

  mounted() {
    // 从URL获取筛选条件
    this.getFilterParamsFromRoute()
    
    // 获取题目详情
    this.getQuestionDetail()
    
    // 获取题目列表（用于导航）
    this.getQuestionList()
  },

  watch: {
    // 监听路由变化，重新加载题目
    '$route'(to, from) {
      if (to.params.id !== from.params.id) {
        this.getFilterParamsFromRoute()
        this.getQuestionDetail()
        this.getQuestionList()
      }
    }
  }
}
</script>

<style scoped>
.choice-question-detail {
  margin: 20px;
  max-width: 1200px;
  margin: 20px auto;
}

.main-panel {
  border-radius: 8px;
  overflow: hidden;
}

.panel-title {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
}

.title-icon {
  margin-right: 8px;
  color: #2d8cf0;
}

.question-number {
  color: #2d8cf0;
  font-weight: bold;
  margin-right: 8px;
}

.question-title {
  color: #333;
}

.bookmark-btn {
  border-radius: 4px;
}

.loading-container {
  text-align: center;
  padding: 100px 0;
}

/* 题目信息卡片样式 */
.question-info {
  margin-bottom: 32px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.info-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px;
  border: 1px solid #e8eaec;
  transition: all 0.3s ease;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.info-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #2d8cf0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  color: white;
  font-size: 18px;
}

.difficulty-icon {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
}

.info-content {
  flex: 1;
}

.info-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.difficulty-tag {
  font-weight: bold;
}

.tags-section {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e8eaec;
}

.tags-label {
  display: flex;
  align-items: center;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}

.tags-label .ivu-icon {
  margin-right: 6px;
  color: #2d8cf0;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.question-tag {
  font-weight: 500;
}

.info-item {
  margin-bottom: 8px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: bold;
  color: #666;
  margin-right: 8px;
}

/* 内容区域样式 */
.question-content {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e8eaec;
}

.section-icon {
  margin-right: 8px;
  color: #2d8cf0;
  font-size: 18px;
}

.section-header h3 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.content-box {
  padding: 20px;
  background: #fafbfc;
  border-radius: 8px;
  border: 1px solid #e8eaec;
}

.question-content h3 {
  margin-bottom: 12px;
  color: #333;
}

.content {
  line-height: 1.8;
  color: #333;
  font-size: 15px;
}

/* 富文本内容中的图片尺寸控制 */
.content img {
  max-width: 400px;
  width: auto;
  height: auto;
}

/* 选项区域样式 */
.question-options {
  margin-bottom: 32px;
}

.question-options h3 {
  margin-bottom: 16px;
  color: #333;
}

/* 选项样式优化 */
.option-item {
  margin-bottom: 16px;
  padding: 16px;
  border: 2px solid #e8eaec;
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
  background: #fff;
  position: relative;
  overflow: hidden;
}

.option-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 4px;
  background: transparent;
  transition: all 0.3s ease;
}

.option-item:hover {
  border-color: #2d8cf0;
  background: #f7f9fc;
  transform: translateX(4px);
}

.option-item:hover::before {
  background: #2d8cf0;
}

.option-item.selected {
  border-color: #2d8cf0;
  background: #e6f7ff;
  transform: translateX(4px);
}

.option-item.selected::before {
  background: #2d8cf0;
}

.option-item.option-correct {
  border-color: #19be6b !important;
  background: #f0f9ff !important;
}

.option-item.option-correct::before {
  background: #19be6b !important;
}

.option-item.option-wrong {
  border-color: #ed4014 !important;
  background: #fff2f0 !important;
}

.option-item.option-wrong::before {
  background: #ed4014 !important;
}

.option-label {
  font-weight: bold;
  margin-right: 12px;
  color: #2d8cf0;
  font-size: 16px;
  min-width: 24px;
  display: inline-block;
}

.option-content {
  line-height: 1.6;
  font-size: 15px;
  color: #333;
}

/* 选项内容中的图片尺寸控制 */
.option-content img {
  max-width: 400px;
  width: auto;
  height: auto;
}

/* 提交区域样式 */
.submit-section {
  margin: 40px 0;
  text-align: center;
}

.submit-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.submit-btn {
  padding: 12px 32px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  min-width: 160px;
  box-shadow: 0 4px 12px rgba(45, 140, 240, 0.3);
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(45, 140, 240, 0.4);
}

.submit-hint {
  display: flex;
  align-items: center;
  color: #999;
  font-size: 14px;
  gap: 4px;
}

.navigation-section {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 16px;
}

.nav-btn {
  min-width: 100px;
  height: 40px;
  font-size: 14px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.nav-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.next-btn {
  background: linear-gradient(135deg, #52c41a, #73d13d);
  border-color: #52c41a;
}

.next-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.4);
}

/* 答案解析样式 */
.answer-analysis {
  margin-top: 32px;
  border-top: 1px solid #e8eaec;
  padding-top: 24px;
}

.analysis-header {
  margin-bottom: 24px;
}

.result-info {
  margin-bottom: 24px;
}

.analysis-content {
  display: grid;
  gap: 24px;
}

.correct-answer-section,
.explanation-section {
  background: #fafbfc;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e8eaec;
}

.analysis-subsection-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.subsection-icon {
  margin-right: 8px;
  color: #19be6b;
  font-size: 16px;
}

.analysis-subsection-header h4 {
  margin: 0;
  color: #333;
  font-size: 15px;
  font-weight: 600;
}

.correct-answer-content {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.answer-label {
  display: inline-block;
  padding: 8px 16px;
  background: linear-gradient(135deg, #19be6b, #16a085);
  color: white;
  border-radius: 20px;
  font-weight: bold;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(25, 190, 107, 0.3);
}

.explanation-content .content {
  padding: 16px;
  background: #fff;
  border-radius: 6px;
  line-height: 1.8;
  border: 1px solid #e8eaec;
  color: #333;
}

/* 图片自适应样式 - 最大宽度400px，高度自适应 */
.choice-question-detail >>> .content img,
.choice-question-detail ::v-deep .content img,
.choice-question-detail /deep/ .content img,
.choice-question-detail .ivu-panel-body .content img,
.choice-question-detail .option-item .option-content img,
.choice-question-detail .answer-analysis .explanation .content img {
  max-width: 400px !important;
  width: auto !important;
  height: auto !important;
  display: block !important;
  margin: 10px auto !important;
  object-fit: contain !important;
  border: 1px solid #e8eaec;
  border-radius: 4px;
}

/* 导航按钮样式 */
.navigation-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e8eaec;
}

.navigation-buttons {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.nav-btn {
  min-width: 120px;
  height: 40px;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.question-progress {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  background: #f8f9fa;
  border-radius: 20px;
  border: 1px solid #e8eaec;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: #666;
}

/* 确保父容器没有限制 */
.choice-question-detail .content,
.choice-question-detail .option-content,
.choice-question-detail .explanation .content {
  max-width: 100%;
  word-wrap: break-word;
  overflow-wrap: break-word;
  overflow: hidden;
}

/* 登录按钮样式 */
.login-section {
  margin-top: 16px;
  text-align: center;
}

.login-btn {
  min-width: 120px;
  border-radius: 20px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(25, 190, 107, 0.3);
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(25, 190, 107, 0.4);
}
</style>