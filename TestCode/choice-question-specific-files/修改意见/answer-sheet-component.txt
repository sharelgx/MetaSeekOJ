<template>
  <div class="answer-sheet">
    <div class="options-container">
      <div 
        v-for="(option, index) in displayOptions" 
        :key="index"
        class="option-item"
        :class="{
          'selected': isSelected(index),
          'correct': showResult && isCorrectOption(index),
          'incorrect': showResult && isSelected(index) && !isCorrectOption(index),
          'disabled': disabled
        }"
        @click="selectOption(index)"
      >
        <div class="option-indicator">
          <Icon 
            v-if="question.question_type === 'single'" 
            :type="isSelected(index) ? 'ios-radio-button-on' : 'ios-radio-button-off'"
            :color="getIndicatorColor(index)"
            size="20"
          />
          <Icon 
            v-else
            :type="isSelected(index) ? 'ios-checkbox' : 'ios-checkbox-outline'"
            :color="getIndicatorColor(index)" 
            size="20"
          />
        </div>
        
        <div class="option-content">
          <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
          <span class="option-text" v-html="getOptionText(option)"></span>
        </div>
        
        <div v-if="showResult" class="option-result">
          <Icon 
            v-if="isCorrectOption(index)" 
            type="ios-checkmark-circle" 
            color="#19be6b" 
            size="20"
          />
          <Icon 
            v-else-if="isSelected(index) && !isCorrectOption(index)" 
            type="ios-close-circle" 
            color="#ed4014" 
            size="20"
          />
        </div>
      </div>
    </div>
    
    <div v-if="!showResult && !disabled" class="answer-actions">
      <Button 
        type="primary" 
        @click="submitAnswer"
        :loading="submitting"
        :disabled="selectedOptions.length === 0"
      >
        <Icon type="ios-send" />
        提交答案
      </Button>
      
      <Button 
        type="default" 
        @click="clearAnswer"
        :disabled="selectedOptions.length === 0"
      >
        <Icon type="ios-refresh" />
        清空选择
      </Button>
    </div>
    
    <div v-if="showResult" class="answer-result">
      <Alert 
        :type="result.is_correct ? 'success' : 'error'"
        show-icon
      >
        <div slot="desc">
          <div class="result-info">
            <p>
              <strong>{{ result.is_correct ? '回答正确！' : '回答错误' }}</strong>
            </p>
            <p v-if="!result.is_correct && correctAnswerText">
              正确答案：{{ correctAnswerText }}
            </p>
            <p v-if="result.score !== undefined">
              得分：{{ result.score }} / {{ question.score }}
            </p>
          </div>
          
          <div v-if="question.explanation" class="explanation">
            <Divider size="small">题目解析</Divider>
            <div v-html="question.explanation"></div>
          </div>
        </div>
      </Alert>
    </div>
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
      selectedOptions: [...this.value]
    }
  },
  
  computed: {
    displayOptions() {
      if (!this.question || !this.question.options) return []
      return this.question.options
    },
    
    correctAnswerText() {
      if (!this.result || !this.result.correct_answers) return ''
      
      const correctIndices = this.result.correct_answers
      if (!Array.isArray(correctIndices)) return ''
      
      return correctIndices
        .map(index => String.fromCharCode(65 + index))
        .join(', ')
    }
  },
  
  watch: {
    value(newVal) {
      this.selectedOptions = [...newVal]
    },
    
    selectedOptions(newVal) {
      this.$emit('input', newVal)
    }
  },
  
  methods: {
    selectOption(index) {
      if (this.disabled || this.showResult) return
      
      if (this.question.question_type === 'single') {
        // 单选题
        this.selectedOptions = [index]
      } else {
        // 多选题
        const idx = this.selectedOptions.indexOf(index)
        if (idx > -1) {
          this.selectedOptions.splice(idx, 1)
        } else {
          this.selectedOptions.push(index)
        }
      }
    },
    
    isSelected(index) {
      return this.selectedOptions.includes(index)
    },
    
    isCorrectOption(index) {
      if (!this.result || !this.result.correct_answers) return false
      return this.result.correct_answers.includes(index)
    },
    
    getIndicatorColor(index) {
      if (this.showResult) {
        if (this.isCorrectOption(index)) return '#19be6b'
        if (this.isSelected(index) && !this.isCorrectOption(index)) return '#ed4014'
      }
      return this.isSelected(index) ? '#2d8cf0' : '#808695'
    },
    
    getOptionText(option) {
      // 处理不同格式的选项
      if (typeof option === 'string') {
        return option
      }
      if (typeof option === 'object') {
        return option.text || option.content || option.label || ''
      }
      return ''
    },
    
    submitAnswer() {
      if (this.selectedOptions.length === 0) {
        this.$Message.warning('请先选择答案')
        return
      }
      
      this.$emit('submit', {
        question_id: this.question.id,
        answers: this.selectedOptions
      })
    },
    
    clearAnswer() {
      this.selectedOptions = []
    }
  }
}
</script>

<style scoped>
.answer-sheet {
  padding: 20px 0;
}

.options-container {
  margin-bottom: 24px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  margin-bottom: 12px;
  background: #fff;
  border: 2px solid #e8eaec;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.option-item:hover:not(.disabled) {
  border-color: #2d8cf0;
  box-shadow: 0 2px 8px rgba(45, 140, 240, 0.15);
}

.option-item.selected {
  border-color: #2d8cf0;
  background: #f0f9ff;
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

.option-indicator {
  flex-shrink: 0;
  margin-right: 12px;
}

.option-content {
  flex: 1;
  display: flex;
  align-items: baseline;
}

.option-label {
  font-weight: 600;
  margin-right: 8px;
  color: #515a6e;
}

.option-text {
  color: #17233d;
  line-height: 1.6;
}

.option-result {
  flex-shrink: 0;
  margin-left: 12px;
}

.answer-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.answer-result {
  margin-top: 24px;
}

.result-info {
  margin-bottom: 16px;
}

.result-info p {
  margin: 8px 0;
}

.explanation {
  margin-top: 16px;
  padding: 16px;
  background: #f8f8f9;
  border-radius: 6px;
}

.explanation >>> p {
  margin: 8px 0;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .option-item {
    padding: 12px 16px;
  }
  
  .option-content {
    flex-direction: column;
  }
  
  .option-label {
    margin-bottom: 4px;
  }
  
  .answer-actions {
    flex-direction: column;
  }
  
  .answer-actions .ivu-btn {
    width: 100%;
  }
}
</style>