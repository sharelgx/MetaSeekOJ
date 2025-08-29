<template>
  <div class="wrong-question-book">
    <Panel shadow>
      <div slot="title">
        <Icon type="ios-bookmark" />
        我的错题本
        <Badge :count="total" style="margin-left: 10px" />
      </div>
      
      <!-- 简化的筛选器 -->
      <div class="filter-section">
        <Row :gutter="10">
          <Col :span="8">
            <Select v-model="selectedCategory" placeholder="选择分类" clearable>
              <Option 
                v-for="category in categories" 
                :key="category.id"
                :value="category.id"
              >
                {{ category.name }}
              </Option>
            </Select>
          </Col>
          <Col :span="6">
            <Button type="primary" @click="getWrongQuestionList">筛选</Button>
            <Button @click="resetFilter" style="margin-left: 8px">重置</Button>
          </Col>
        </Row>
      </div>

      <!-- 错题列表 -->
      <div class="question-list">
        <div v-if="loading" class="loading-container">
          <Spin size="large" />
        </div>
        <div v-else-if="wrongQuestions.length === 0" class="empty-container">
          <div class="empty-content">
            <Icon type="ios-document" size="64" color="#c5c8ce" />
            <p>暂无错题记录</p>
          </div>
        </div>
        <div v-else>
          <Card 
            v-for="question in wrongQuestions" 
            :key="question.id"
            class="question-card"
            :bordered="false"
            shadow
          >
            <div class="question-header">
              <div class="question-title">
                <Tag :color="question.difficulty === 1 ? 'green' : question.difficulty === 2 ? 'orange' : 'red'">
                  {{ getDifficultyText(question.difficulty) }}
                </Tag>
                <span class="title-text">{{ question.title }}</span>
              </div>
              <div class="question-actions">
                <Button 
                  type="primary" 
                  size="small" 
                  @click="redoQuestion(question)"
                >
                  重做
                </Button>
                <Button 
                  type="error" 
                  size="small" 
                  @click="removeFromWrongBook(question.id)"
                  style="margin-left: 8px"
                >
                  移除
                </Button>
              </div>
            </div>
            
            <div class="question-content">
              <p class="question-text">{{ question.content }}</p>
              <div class="options">
                <div 
                  v-for="(option, index) in question.options" 
                  :key="index"
                  class="option-item"
                  :class="{
                    'correct': question.correct_answer.includes(String.fromCharCode(65 + index)),
                    'wrong': question.user_answer && question.user_answer.includes(String.fromCharCode(65 + index)) && !question.correct_answer.includes(String.fromCharCode(65 + index))
                  }"
                >
                  <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
                  <span class="option-text">{{ option }}</span>
                </div>
              </div>
            </div>
            
            <div class="question-meta">
              <span class="meta-item">
                <Icon type="ios-time" />
                错误时间: {{ formatDate(question.created_at) }}
              </span>
              <span class="meta-item">
                <Icon type="ios-repeat" />
                错误次数: {{ question.wrong_count || 1 }}
              </span>
            </div>
          </Card>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination-container" v-if="total > pageSize">
        <Page 
          :current="currentPage" 
          :total="total" 
          :page-size="pageSize"
          @on-change="handlePageChange"
          show-total
        />
      </div>
    </Panel>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'WrongQuestionBook',
  data() {
    return {
      loading: false,
      wrongQuestions: [],
      categories: [],
      selectedCategory: null,
      currentPage: 1,
      pageSize: 10,
      total: 0
    }
  },
  mounted() {
    this.loadCategories()
    this.getWrongQuestionList()
  },
  methods: {
    async loadCategories() {
      try {
        const response = await api.getCategoryList()
        this.categories = response.data.results || []
      } catch (error) {
        console.error('加载分类失败:', error)
      }
    },
    
    async getWrongQuestionList() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize
        }
        if (this.selectedCategory) {
          params.category = this.selectedCategory
        }
        
        const response = await api.getWrongQuestionList(params)
        this.wrongQuestions = response.data.results || []
        this.total = response.data.count || 0
      } catch (error) {
        console.error('加载错题列表失败:', error)
        this.$Message.error('加载错题列表失败')
      } finally {
        this.loading = false
      }
    },
    
    resetFilter() {
      this.selectedCategory = null
      this.currentPage = 1
      this.getWrongQuestionList()
    },
    
    handlePageChange(page) {
      this.currentPage = page
      this.getWrongQuestionList()
    },
    
    redoQuestion(question) {
      // 跳转到答题页面
      this.$router.push({
        name: 'ChoiceQuestionDetail',
        params: { id: question.question_id }
      })
    },
    
    async removeFromWrongBook(id) {
      try {
        await api.removeFromWrongQuestions(id)
        this.$Message.success('已从错题本移除')
        this.getWrongQuestionList()
      } catch (error) {
        console.error('移除错题失败:', error)
        this.$Message.error('移除错题失败')
      }
    },
    
    getDifficultyText(difficulty) {
      const difficultyMap = {
        1: '简单',
        2: '中等', 
        3: '困难'
      }
      return difficultyMap[difficulty] || '未知'
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.wrong-question-book {
  padding: 20px;
}

.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f8f9;
  border-radius: 4px;
}

.loading-container {
  text-align: center;
  padding: 50px;
}

.empty-container {
  text-align: center;
  padding: 50px;
}

.empty-content p {
  margin-top: 15px;
  color: #c5c8ce;
  font-size: 14px;
}

.question-card {
  margin-bottom: 15px;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.question-title {
  display: flex;
  align-items: center;
}

.title-text {
  margin-left: 10px;
  font-weight: 500;
  font-size: 16px;
}

.question-content {
  margin-bottom: 15px;
}

.question-text {
  margin-bottom: 15px;
  line-height: 1.6;
}

.options {
  margin-left: 20px;
}

.option-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.option-item.correct {
  background-color: #f6ffed;
  border: 1px solid #b7eb8f;
}

.option-item.wrong {
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
}

.option-label {
  font-weight: 500;
  margin-right: 8px;
  min-width: 20px;
}

.option-text {
  flex: 1;
  line-height: 1.5;
}

.question-meta {
  display: flex;
  justify-content: space-between;
  color: #999;
  font-size: 12px;
  border-top: 1px solid #f0f0f0;
  padding-top: 10px;
}

.meta-item {
  display: flex;
  align-items: center;
}

.meta-item i {
  margin-right: 4px;
}

.pagination-container {
  text-align: center;
  margin-top: 20px;
}
</style>