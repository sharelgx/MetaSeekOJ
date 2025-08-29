<template>
  <div class="choice-question-detail">
    <Panel shadow v-if="question">
      <div slot="title">
        <Icon type="ios-help-circle" />
        题目 #{{ question._id }}: {{ question.title }}
      </div>
      
      <div slot="extra">
        <Button 
          type="error" 
          size="small" 
          @click="addToWrongQuestions"
          v-if="!isInWrongQuestions && hasSubmitted"
        >
          <Icon type="ios-bookmark" />
          加入错题本
        </Button>
      </div>
      
      <!-- 题目信息 -->
      <div class="question-info">
        <Row :gutter="16">
          <Col :span="12">
            <div class="info-item">
              <span class="label">分类：</span>
              <span>{{ question.category ? question.category.name : '未分类' }}</span>
            </div>
          </Col>
          <Col :span="12">
            <div class="info-item">
              <span class="label">难度：</span>
              <Tag :color="getDifficultyColor(question.difficulty)">
                {{ getDifficultyText(question.difficulty) }}
              </Tag>
            </div>
          </Col>
        </Row>
        <Row :gutter="16" style="margin-top: 8px">
          <Col :span="12">
            <div class="info-item">
              <span class="label">题型：</span>
              <span>{{ question.question_type === 'single' ? '单选题' : '多选题' }}</span>
            </div>
          </Col>
          <Col :span="12">
            <div class="info-item">
              <span class="label">分值：</span>
              <span>{{ question.score }} 分</span>
            </div>
          </Col>
        </Row>
        <div class="info-item" style="margin-top: 8px" v-if="question.tags && question.tags.length > 0">
          <span class="label">标签：</span>
          <Tag 
            v-for="tag in question.tags" 
            :key="tag.id"
            :color="tag.color"
            style="margin-right: 4px"
          >
            {{ tag.name }}
          </Tag>
        </div>
      </div>
      
      <!-- 题目内容 -->
      <div class="question-content">
        <h3>题目描述</h3>
        <div class="content" v-html="question.content"></div>
      </div>
      
      <!-- 选项 -->
      <div class="question-options">
        <h3>选项</h3>
        <div v-if="question.question_type === 'single'">
          <RadioGroup v-model="selectedAnswer" :disabled="hasSubmitted">
            <div 
              v-for="(option, index) in question.options" 
              :key="index"
              class="option-item"
              :class="getOptionClass(index)"
            >
              <Radio :label="index">
                <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
                <span class="option-content" v-html="option"></span>
              </Radio>
            </div>
          </RadioGroup>
        </div>
        <div v-else>
          <CheckboxGroup v-model="selectedAnswers" :disabled="hasSubmitted">
            <div 
              v-for="(option, index) in question.options" 
              :key="index"
              class="option-item"
              :class="getOptionClass(index)"
            >
              <Checkbox :label="index">
                <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
                <span class="option-content" v-html="option"></span>
              </Checkbox>
            </div>
          </CheckboxGroup>
        </div>
      </div>
      
      <!-- 提交按钮 -->
      <div class="submit-section" v-if="!hasSubmitted">
        <Button 
          type="primary" 
          size="large"
          @click="submitAnswer"
          :loading="submitting"
          :disabled="!canSubmit"
        >
          提交答案
        </Button>
      </div>
      
      <!-- 答案解析 -->
      <div class="answer-analysis" v-if="hasSubmitted">
        <Divider>答案解析</Divider>
        
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
        
        <div class="correct-answer">
          <h4>正确答案</h4>
          <div v-if="question.question_type === 'single'">
            <span class="answer-label">{{ String.fromCharCode(65 + question.correct_answer[0]) }}</span>
          </div>
          <div v-else>
            <span 
              v-for="(answer, index) in question.correct_answer" 
              :key="index"
              class="answer-label"
              style="margin-right: 8px"
            >
              {{ String.fromCharCode(65 + answer) }}
            </span>
          </div>
        </div>
        
        <div class="explanation" v-if="question.explanation">
          <h4>解析</h4>
          <div class="content" v-html="question.explanation"></div>
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
import api from '../api'

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
      isInWrongQuestions: false
    }
  },
  
  computed: {
    questionId() {
      return this.$route.params.id
    },
    
    canSubmit() {
      if (this.question?.question_type === 'single') {
        return this.selectedAnswer !== null
      } else {
        return this.selectedAnswers.length > 0
      }
    }
  },
  
  mounted() {
    this.getQuestionDetail()
  },
  
  methods: {
    async getQuestionDetail() {
      try {
        const res = await api.getQuestionDetail(this.questionId)
        this.question = res.data.data
      } catch (err) {
        this.$Message.error('获取题目详情失败')
        console.error(err)
      }
    },
    
    async submitAnswer() {
      this.submitting = true
      try {
        let userAnswer
        if (this.question.question_type === 'single') {
          userAnswer = [this.selectedAnswer]
        } else {
          userAnswer = this.selectedAnswers.sort((a, b) => a - b)
        }
        
        const res = await api.submitAnswer({
          question_id: this.question._id,
          user_answer: userAnswer
        })
        
        const result = res.data.data
        this.hasSubmitted = true
        this.isCorrect = result.is_correct
        this.currentScore = result.score
        
        this.$Message.success('提交成功！')
      } catch (err) {
        this.$Message.error('提交失败')
        console.error(err)
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
    
    getDifficultyColor(difficulty) {
      const colorMap = {
        1: 'success',
        2: 'warning', 
        3: 'error'
      }
      return colorMap[difficulty] || 'default'
    },
    
    getDifficultyText(difficulty) {
      const textMap = {
        1: '简单',
        2: '中等',
        3: '困难'
      }
      return textMap[difficulty] || '未知'
    },
    
    getOptionClass(index) {
      if (!this.hasSubmitted) return ''
      
      const isCorrect = this.question.correct_answer.includes(index)
      let isSelected = false
      
      if (this.question.question_type === 'single') {
        isSelected = this.selectedAnswer === index
      } else {
        isSelected = this.selectedAnswers.includes(index)
      }
      
      if (isCorrect) {
        return 'option-correct'
      } else if (isSelected && !isCorrect) {
        return 'option-wrong'
      }
      
      return ''
    }
  }
}
</script>

<style scoped>
.choice-question-detail {
  margin: 20px;
}

.loading-container {
  text-align: center;
  padding: 100px 0;
}

.question-info {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f8f9;
  border-radius: 4px;
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

.question-content {
  margin-bottom: 24px;
}

.question-content h3 {
  margin-bottom: 12px;
  color: #333;
}

.content {
  line-height: 1.6;
  color: #666;
}

.question-options h3 {
  margin-bottom: 16px;
  color: #333;
}

.option-item {
  margin-bottom: 12px;
  padding: 12px;
  border: 1px solid #e8eaec;
  border-radius: 4px;
  transition: all 0.3s;
}

.option-item:hover {
  border-color: #2d8cf0;
  background: #f7f9fc;
}

.option-item.option-correct {
  border-color: #19be6b;
  background: #f0f9ff;
}

.option-item.option-wrong {
  border-color: #ed4014;
  background: #fff2f0;
}

.option-label {
  font-weight: bold;
  margin-right: 8px;
  color: #2d8cf0;
}

.option-content {
  line-height: 1.5;
}

.submit-section {
  margin: 32px 0;
  text-align: center;
}

.answer-analysis {
  margin-top: 24px;
}

.result-info {
  margin-bottom: 20px;
}

.correct-answer {
  margin-bottom: 20px;
}

.correct-answer h4,
.explanation h4 {
  margin-bottom: 12px;
  color: #333;
}

.answer-label {
  display: inline-block;
  padding: 4px 8px;
  background: #19be6b;
  color: white;
  border-radius: 4px;
  font-weight: bold;
}

.explanation .content {
  padding: 12px;
  background: #f8f8f9;
  border-radius: 4px;
  line-height: 1.6;
}
</style>