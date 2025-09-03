<template>
  <div class="question-card" :class="{ 'answered': hasAnswered, 'correct': isCorrect, 'wrong': isWrong }">
    <div class="card-header">
      <div class="question-id">#{{ question._id }}</div>
      <div class="question-meta">
        <Tag :color="getDifficultyColor(question.difficulty)" size="small">
          {{ getDifficultyText(question.difficulty) }}
        </Tag>
        <Tag color="blue" size="small" v-if="question.question_type">
          {{ question.question_type === 'single' ? '单选' : '多选' }}
        </Tag>
      </div>
    </div>
    
    <div class="card-body">
      <h3 class="question-title" @click="goToDetail">
        {{ question.title }}
      </h3>
      
      <div class="question-info">
        <div class="info-item" v-if="question.category">
          <Icon type="ios-folder" size="14" />
          <span>{{ question.category.name }}</span>
        </div>
        
        <div class="info-item" v-if="question.score">
          <Icon type="ios-star" size="14" />
          <span>{{ question.score }}分</span>
        </div>
        
        <div class="info-item" v-if="question.tags && question.tags.length > 0">
          <Icon type="ios-pricetags" size="14" />
          <div class="tags">
            <Tag 
              v-for="tag in question.tags.slice(0, 2)" 
              :key="tag.id"
              size="small"
              :color="tag.color || 'default'"
            >
              {{ tag.name }}
            </Tag>
            <span v-if="question.tags.length > 2" class="more-tags">
              +{{ question.tags.length - 2 }}
            </span>
          </div>
        </div>
      </div>
      
      <div class="question-stats" v-if="showStats">
        <div class="stat-item">
          <Icon type="ios-people" size="14" />
          <span>{{ question.submission_count || 0 }}人答题</span>
        </div>
        
        <div class="stat-item" v-if="question.accuracy_rate !== undefined">
          <Icon type="ios-analytics" size="14" />
          <span>正确率 {{ (question.accuracy_rate * 100).toFixed(1) }}%</span>
        </div>
      </div>
    </div>
    
    <div class="card-footer">
      <div class="action-buttons">
        <Button type="primary" size="small" @click="goToDetail">
          <Icon type="ios-eye" />
          查看题目
        </Button>
        
        <Button 
          v-if="hasAnswered && !isCorrect" 
          type="warning" 
          size="small" 
          @click="addToWrongBook"
        >
          <Icon type="ios-bookmark" />
          错题本
        </Button>
        
        <Button 
          v-if="showPracticeButton" 
          type="success" 
          size="small" 
          @click="startPractice"
        >
          <Icon type="ios-play" />
          开始练习
        </Button>
      </div>
      
      <div class="answer-status" v-if="hasAnswered">
        <Icon 
          :type="isCorrect ? 'ios-checkmark-circle' : 'ios-close-circle'" 
          :color="isCorrect ? '#19be6b' : '#ed4014'"
          size="18"
        />
        <span :class="{ 'correct-text': isCorrect, 'wrong-text': !isCorrect }">
          {{ isCorrect ? '答对了' : '答错了' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuestionCard',
  props: {
    question: {
      type: Object,
      required: true
    },
    showStats: {
      type: Boolean,
      default: true
    },
    showPracticeButton: {
      type: Boolean,
      default: false
    },
    userSubmission: {
      type: Object,
      default: null
    }
  },
  
  computed: {
    hasAnswered() {
      return this.userSubmission && this.userSubmission.result !== undefined
    },
    
    isCorrect() {
      return this.hasAnswered && this.userSubmission.result === 'AC'
    },
    
    isWrong() {
      return this.hasAnswered && this.userSubmission.result !== 'AC'
    }
  },
  
  methods: {
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
    
    goToDetail() {
      this.$router.push({
        name: 'choice-question-detail',
        params: { id: this.question.id || this.question._id }
      })
    },
    
    addToWrongBook() {
      this.$emit('add-to-wrong-book', this.question)
    },
    
    startPractice() {
      this.$emit('start-practice', this.question)
    }
  }
}
</script>

<style scoped>
.question-card {
  background: #fff;
  border: 1px solid #e8eaec;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.question-card:hover {
  border-color: #2d8cf0;
  box-shadow: 0 2px 8px rgba(45, 140, 240, 0.15);
  transform: translateY(-2px);
}

.question-card.answered {
  border-left: 4px solid #2d8cf0;
}

.question-card.correct {
  border-left-color: #19be6b;
  background: linear-gradient(135deg, #f6ffed 0%, #ffffff 100%);
}

.question-card.wrong {
  border-left-color: #ed4014;
  background: linear-gradient(135deg, #fff2f0 0%, #ffffff 100%);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.question-id {
  font-size: 14px;
  font-weight: 600;
  color: #2d8cf0;
}

.question-meta {
  display: flex;
  gap: 8px;
}

.card-body {
  margin-bottom: 16px;
}

.question-title {
  font-size: 16px;
  font-weight: 600;
  color: #17233d;
  margin: 0 0 12px 0;
  line-height: 1.4;
  cursor: pointer;
  transition: color 0.3s ease;
}

.question-title:hover {
  color: #2d8cf0;
}

.question-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #808695;
}

.tags {
  display: flex;
  align-items: center;
  gap: 4px;
}

.more-tags {
  font-size: 12px;
  color: #c5c8ce;
}

.question-stats {
  display: flex;
  gap: 16px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #808695;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.answer-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
}

.correct-text {
  color: #19be6b;
}

.wrong-text {
  color: #ed4014;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .question-card {
    padding: 12px;
  }
  
  .question-info {
    flex-direction: column;
    gap: 8px;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .action-buttons {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>