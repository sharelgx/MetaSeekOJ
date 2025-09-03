<template>
  <div class="answer-sheet">
    <Card :bordered="false" class="answer-card">
      <div class="answer-header">
        <div class="answer-title">
          <Icon type="ios-clipboard" />
          <span>答题卡</span>
        </div>
        <div class="answer-actions">
          <Button 
            type="text" 
            size="small" 
            @click="toggleExpanded"
            class="expand-btn"
          >
            <Icon :type="expanded ? 'ios-arrow-up' : 'ios-arrow-down'" />
            {{ expanded ? '收起' : '展开' }}
          </Button>
        </div>
      </div>
      
      <div class="answer-content" v-show="expanded">
        <!-- 题目信息 -->
        <div class="question-info">
          <Row :gutter="16">
            <Col :span="8">
              <div class="info-item">
                <span class="info-label">题目ID:</span>
                <span class="info-value">{{ question.id }}</span>
              </div>
            </Col>
            <Col :span="8">
              <div class="info-item">
                <span class="info-label">题型:</span>
                <span class="info-value">{{ getQuestionTypeText(question.question_type) }}</span>
              </div>
            </Col>
            <Col :span="8">
              <div class="info-item">
                <span class="info-label">分值:</span>
                <span class="info-value">{{ question.score }}分</span>
              </div>
            </Col>
          </Row>
        </div>
        
        <!-- 选项列表 -->
        <div class="options-section">
          <div class="section-title">
            <Icon type="ios-list" />
            <span>选择答案</span>
          </div>
          
          <div class="options-list">
            <div 
              v-for="(option, index) in question.options" 
              :key="index"
              class="option-item"
              :class="{
                'selected': isOptionSelected(index),
                'correct': showResult && option.is_correct,
                'incorrect': showResult && isOptionSelected(index) && !option.is_correct,
                'disabled': disabled
              }"
              @click="selectOption(index)"
            >
              <div class="option-marker">
                <div class="option-checkbox" v-if="question.question_type === 'multiple'">
                  <Icon 
                    :type="isOptionSelected(index) ? 'ios-checkmark-circle' : 'ios-radio-button-off'" 
                    :color="getOptionIconColor(index)"
                    size="20"
                  />
                </div>
                <div class="option-radio" v-else>
                  <Icon 
                    :type="isOptionSelected(index) ? 'ios-radio-button-on' : 'ios-radio-button-off'" 
                    :color="getOptionIconColor(index)"
                    size="20"
                  />
                </div>
                <span class="option-label">{{ String.fromCharCode(65 + index) }}</span>
              </div>
              
              <div class="option-content">
                <div class="option-text" v-html="option.content"></div>
                
                <!-- 结果显示 -->
                <div class="option-result" v-if="showResult">
                  <div class="result-indicator" v-if="option.is_correct">
                    <Icon type="ios-checkmark-circle" color="#19be6b" size="16" />
                    <span class="result-text correct">正确答案</span>
                  </div>
                  <div class="result-indicator" v-else-if="isOptionSelected(index)">
                    <Icon type="ios-close-circle" color="#ed4014" size="16" />
                    <span class="result-text incorrect">错误选择</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 答题状态 -->
        <div class="answer-status">
          <div class="status-info">
            <div class="status-item">
              <span class="status-label">已选择:</span>
              <span class="status-value">
                {{ selectedAnswers.length > 0 ? getSelectedOptionsText() : '未选择' }}
              </span>
            </div>
            
            <div class="status-item" v-if="showResult">
              <span class="status-label">结果:</span>
              <span class="status-value" :class="resultClass">
                <Icon :type="resultIcon" :color="resultColor" size="16" />
                {{ resultText }}
              </span>
            </div>
            
            <div class="status-item" v-if="showResult && score !== null">
              <span class="status-label">得分:</span>
              <span class="status-value score">
                {{ score }} / {{ question.score }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="answer-actions-bottom">
          <Button 
            type="default" 
            @click="clearAnswer"
            :disabled="disabled || selectedAnswers.length === 0"
          >
            <Icon type="ios-refresh" />
            清除选择
          </Button>
          
          <Button 
            type="primary" 
            @click="submitAnswer"
            :disabled="disabled || !canSubmit"
            :loading="submitting"
          >
            <Icon type="ios-send" />
            {{ showResult ? '重新提交' : '提交答案' }}
          </Button>
        </div>
      </div>
    </Card>
    
    <!-- 答案解析 -->
    <Card :bordered="false" class="explanation-card" v-if="showResult && question.explanation">
      <div class="explanation-header">
        <Icon type="ios-bulb" />
        <span>答案解析</span>
      </div>
      
      <div class="explanation-content" v-html="question.explanation"></div>
    </Card>
  </div>
</template>

<script>
export default {
  name: 'AnswerSheet',
  
  props: {
    question: {
      type: Object,
      required: true
    },
    value: {
      type: Array,
      default: () => []
    },
    disabled: {
      type: Boolean,
      default: false
    },
    showResult: {
      type: Boolean,
      default: false
    },
    result: {
      type: Object,
      default: () => ({})
    },
    submitting: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      expanded: true,
      selectedAnswers: [...this.value]
    }
  },
  
  computed: {
    canSubmit() {
      return this.selectedAnswers.length > 0
    },
    
    score() {
      return this.result.score !== undefined ? this.result.score : null
    },
    
    isCorrect() {
      return this.result.is_correct === true
    },
    
    resultClass() {
      if (this.isCorrect) return 'correct'
      if (this.result.is_correct === false) return 'incorrect'
      return 'partial'
    },
    
    resultIcon() {
      if (this.isCorrect) return 'ios-checkmark-circle'
      if (this.result.is_correct === false) return 'ios-close-circle'
      return 'ios-information-circle'
    },
    
    resultColor() {
      if (this.isCorrect) return '#19be6b'
      if (this.result.is_correct === false) return '#ed4014'
      return '#ff9900'
    },
    
    resultText() {
      if (this.isCorrect) return '完全正确'
      if (this.result.is_correct === false) return '答案错误'
      return '部分正确'
    }
  },
  
  watch: {
    value: {
      handler(newValue) {
        this.selectedAnswers = [...newValue]
      },
      deep: true
    },
    
    selectedAnswers: {
      handler(newValue) {
        this.$emit('input', [...newValue])
        this.$emit('answer-change', [...newValue])
      },
      deep: true
    }
  },
  
  methods: {
    toggleExpanded() {
      this.expanded = !this.expanded
    },
    
    isOptionSelected(index) {
      return this.selectedAnswers.includes(index)
    },
    
    selectOption(index) {
      if (this.disabled) return
      
      if (this.question.question_type === 'multiple') {
        // 多选题
        const selectedIndex = this.selectedAnswers.indexOf(index)
        if (selectedIndex > -1) {
          this.selectedAnswers.splice(selectedIndex, 1)
        } else {
          this.selectedAnswers.push(index)
        }
      } else {
        // 单选题
        this.selectedAnswers = [index]
      }
    },
    
    clearAnswer() {
      this.selectedAnswers = []
    },
    
    submitAnswer() {
      if (!this.canSubmit || this.disabled) return
      
      this.$emit('submit', {
        questionId: this.question.id,
        answers: [...this.selectedAnswers]
      })
    },
    
    getOptionIconColor(index) {
      if (!this.showResult) {
        return this.isOptionSelected(index) ? '#2d8cf0' : '#c5c8ce'
      }
      
      const option = this.question.options[index]
      if (option.is_correct) {
        return '#19be6b'
      } else if (this.isOptionSelected(index)) {
        return '#ed4014'
      }
      
      return '#c5c8ce'
    },
    
    getSelectedOptionsText() {
      return this.selectedAnswers
        .map(index => String.fromCharCode(65 + index))
        .sort()
        .join(', ')
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
.answer-sheet {
  margin-bottom: 20px;
}

.answer-card,
.explanation-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 16px;
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.answer-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #17233d;
}

.expand-btn {
  color: #2d8cf0;
}

.answer-content {
  padding: 20px 16px 16px;
}

.question-info {
  margin-bottom: 20px;
  padding: 12px;
  background: #f8f8f9;
  border-radius: 6px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-label {
  font-size: 13px;
  color: #808695;
  font-weight: 500;
}

.info-value {
  font-size: 13px;
  color: #17233d;
  font-weight: 600;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-weight: 600;
  color: #17233d;
}

.options-list {
  margin-bottom: 20px;
}

.option-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  border: 2px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.option-item:hover:not(.disabled) {
  border-color: #2d8cf0;
  background: #f7f9fc;
}

.option-item.selected {
  border-color: #2d8cf0;
  background: #f7f9fc;
}

.option-item.correct {
  border-color: #19be6b;
  background: #f6ffed;
}

.option-item.incorrect {
  border-color: #ed4014;
  background: #fff2f0;
}

.option-item.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.option-marker {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.option-label {
  font-weight: 600;
  color: #515a6e;
  font-size: 14px;
  min-width: 20px;
}

.option-content {
  flex: 1;
}

.option-text {
  color: #17233d;
  line-height: 1.6;
}

.option-result {
  margin-top: 8px;
}

.result-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.result-text {
  font-size: 12px;
  font-weight: 500;
}

.result-text.correct {
  color: #19be6b;
}

.result-text.incorrect {
  color: #ed4014;
}

.answer-status {
  margin-bottom: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
}

.status-info {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-label {
  font-size: 13px;
  color: #808695;
  font-weight: 500;
}

.status-value {
  font-size: 13px;
  color: #17233d;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-value.correct {
  color: #19be6b;
}

.status-value.incorrect {
  color: #ed4014;
}

.status-value.partial {
  color: #ff9900;
}

.status-value.score {
  color: #2d8cf0;
}

.answer-actions-bottom {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.explanation-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  font-weight: 600;
  color: #17233d;
}

.explanation-content {
  padding: 16px;
  color: #515a6e;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .answer-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .status-info {
    flex-direction: column;
    gap: 12px;
  }
  
  .answer-actions-bottom {
    flex-direction: column;
  }
  
  .option-item {
    flex-direction: column;
    gap: 8px;
  }
  
  .option-marker {
    align-self: flex-start;
  }
}
</style>