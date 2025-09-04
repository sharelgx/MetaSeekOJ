<template>
  <div class="choice-question-list">
    <Panel shadow>
      <div slot="title">
        <Icon type="ios-list" />
        选择题列表
        <Badge :count="total" style="margin-left: 10px" />
      </div>
      
      <!-- 筛选器 -->
      <div class="filter-section">
        <Row :gutter="10">
          <Col :span="6">
            <div class="custom-input-wrapper" style="position: relative; display: inline-block; width: 100%;">
              <Icon type="ios-search" style="position: absolute; left: 8px; top: 50%; transform: translateY(-50%); z-index: 1; color: #c5c8ce;" />
              <input 
                v-model="keyword" 
                type="text" 
                class="ivu-input" 
                style="padding-left: 32px;" 
                placeholder="搜索题目标题或内容" 
                @keyup.enter="getQuestionList" 
                @input="getQuestionList" 
              />
            </div>
          </Col>
          <Col :span="4">
            <Select v-model="selectedCategory" placeholder="选择分类" clearable @on-change="handleCategoryChange">
              <Option 
                v-for="category in categories" 
                :key="category.id"
                :value="category.id"
              >
                {{ category.name }}
              </Option>
            </Select>
          </Col>
          <Col :span="4">
            <Select v-model="selectedTag" placeholder="标签" clearable @on-change="handleTagChange" @on-open="onTagSelectOpen" ref="tagSelect">
              <Option 
                v-for="tag in tags" 
                :key="tag.id"
                :value="tag.id"
              >
                <Tag :color="tag.color" @click="selectTag(tag.id)" style="cursor: pointer; display: block; width: 100%; padding: 4px 8px; margin: 0;">{{ tag.name }}</Tag>
              </Option>
            </Select>
          </Col>
          <Col :span="3">
            <Select v-model="selectedDifficulty" placeholder="难度" clearable @on-change="handleDifficultyChange">
              <Option value="1">简单</Option>
              <Option value="2">中等</Option>
              <Option value="3">困难</Option>
            </Select>
          </Col>
          <Col :span="3">
            <Select v-model="selectedType" placeholder="题型" clearable>
              <Option value="single">单选题</Option>
              <Option value="multiple">多选题</Option>
            </Select>
          </Col>
          <Col :span="4">
            <Button type="primary" @click="getQuestionList">搜索</Button>
            <Button @click="resetFilter" style="margin-left: 8px">重置</Button>
          </Col>
        </Row>
        
        <!-- 做题模式选择 -->
        <Row style="margin-top: 20px;" v-if="selectedCategory || selectedTag">
          <Col :span="24">
            <Card :bordered="false" class="mode-selection-card">
              <div class="mode-selection-container">
                <div class="mode-title">
                  <Icon type="ios-school" size="20" color="#2d8cf0" />
                  <h3>选择做题模式</h3>
                </div>
                
                <div class="mode-buttons">
                  <div class="mode-button-wrapper">
                    <Button 
                      type="primary" 
                      size="large" 
                      @click="startPracticeMode" 
                      class="practice-mode-btn"
                    >
                      <Icon type="ios-book" size="18" />
                      <span>练习模式</span>
                    </Button>
                    <p class="mode-description">逐题练习，可查看解析</p>
                  </div>
                  
                  <div class="mode-button-wrapper">
                    <Button 
                      type="warning" 
                      size="large" 
                      @click="showExamModeDialog"
                      class="exam-mode-btn"
                    >
                      <Icon type="ios-timer" size="18" />
                      <span>考试模式</span>
                    </Button>
                    <p class="mode-description">试卷形式，限时答题</p>
                  </div>
                </div>
              </div>
            </Card>
          </Col>
        </Row>
      </div>
      
      <!-- 题目列表 -->
      <Table 
        :columns="columns"
        :data="questions"
        :loading="loading"
      />
      
      <!-- 分页 -->
      <div class="pagination">
        <Page 
          :total="total"
          :page-size="pageSize"
          :current="currentPage"
          @on-change="handlePageChange"
          @on-page-size-change="handlePageSizeChange"
          show-sizer
          show-elevator
          show-total
        />
      </div>
    </Panel>
  </div>
</template>

<script>
import api from '../../api'
import { DIFFICULTY_CHOICES, QUESTION_TYPE_CHOICES } from './constants'

export default {
  name: 'ChoiceQuestionList',
  data() {
    return {
      loading: false,
      questions: [],
      categories: [],
      tags: [],
      total: 0,
      currentPage: 1,
      pageSize: 20,
      
      // 筛选条件
      keyword: '',
      selectedCategory: null,
      selectedTag: null,
      selectedDifficulty: null,
      selectedType: null,
      
      columns: [
        {
          title: 'ID',
          key: '_id',
          width: 80,
          align: 'center'
        },
        {
          title: '题目',
          key: 'title',
          width: 250,
          render: (h, params) => {
            return h('div', {
              style: {
                fontWeight: 'bold',
                fontSize: '14px',
                cursor: 'pointer',
                color: '#2d8cf0'
              },
              on: {
                click: () => this.goToQuestion(params.row)
              }
            }, params.row.title || '无标题')
          }
        },
        {
          title: '分类',
          key: 'category',
          width: 120,
          render: (h, params) => {
            return h('span', params.row.category ? params.row.category.name : '-')
          }
        },
        {
          title: '标签',
          key: 'tags',
          width: 150,
          render: (h, params) => {
            if (!params.row.tags || params.row.tags.length === 0) {
              return h('span', '-')
            }
            return h('div', params.row.tags.map(tag => {
              return h('Tag', {
                props: {
                  color: 'blue'
                },
                style: {
                  marginRight: '4px'
                }
              }, tag.name || tag)
            }))
          }
        },
        {
          title: '难度',
          key: 'difficulty',
          width: 80,
          align: 'center',
          render: (h, params) => {
            const difficultyMap = {
              'easy': { text: '简单', color: 'success' },
              'medium': { text: '中等', color: 'warning' },
              'hard': { text: '困难', color: 'error' }
            }
            const difficulty = difficultyMap[params.row.difficulty] || { text: '未知', color: 'default' }
            return h('Tag', {
              props: {
                color: difficulty.color
              }
            }, difficulty.text)
          }
        },
        {
          title: '题型',
          key: 'question_type',
          width: 80,
          align: 'center',
          render: (h, params) => {
            return h('span', params.row.question_type === 'single' ? '单选' : '多选')
          }
        },
        {
          title: '分值',
          key: 'score',
          width: 80,
          align: 'center'
        },
        {
          title: '创建时间',
          key: 'create_time',
          width: 150,
          render: (h, params) => {
            const date = new Date(params.row.create_time)
            return h('span', date.toLocaleString('zh-CN', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit'
            }))
          }
        },
        {
          title: '操作',
          key: 'action',
          width: 120,
          align: 'center',
          render: (h, params) => {
            return h('Button', {
              props: {
                type: 'primary',
                size: 'small'
              },
              on: {
                click: (e) => {
                  e.stopPropagation()
                  this.goToQuestion(params.row)
                }
              }
            }, '练习')
          }
        }
      ]
    }
  },
  
  async mounted() {
    // 初始化数据
    await this.getCategoryList()
    await this.getTagList()
    await this.getQuestionList()
  },
  
  methods: {
    async init() {
      await Promise.all([
        this.getCategoryList(),
        this.getTagList(),
        this.getQuestionList()
      ])
    },
    
    async getCategoryList() {
      try {
        const res = await api.getCategoryList()
        this.categories = res.data.data || []
      } catch (err) {
        console.error('获取分类列表失败:', err)
        this.categories = []
      }
    },
    
    async getTagList() {
      try {
        const res = await api.getTagList()
        this.tags = res.data.data.results || []
      } catch (err) {
        console.error('获取标签列表失败:', err)
        this.tags = []
      }
    },
    
    async getQuestionList() {
      this.loading = true
      try {
        const offset = (this.currentPage - 1) * this.pageSize
        const limit = this.pageSize
        const params = {}
        
        if (this.keyword) params.keyword = this.keyword
        if (this.selectedCategory) params.category = this.selectedCategory
        if (this.selectedTag) params.tags = this.selectedTag
        if (this.selectedDifficulty) {
          // 转换难度值：1->easy, 2->medium, 3->hard
          const difficultyMap = {
            '1': 'easy',
            '2': 'medium', 
            '3': 'hard'
          }
          params.difficulty = difficultyMap[this.selectedDifficulty] || this.selectedDifficulty
        }
        if (this.selectedType) params.question_type = this.selectedType
        
        const res = await api.getChoiceQuestionList(offset, limit, params)
        this.questions = res.data.data.results || []
        this.total = res.data.data.total || 0
      } catch (err) {
        this.$Message.error('获取题目列表失败')
        console.error(err)
        // 确保在错误情况下也清空数据
        this.questions = []
        this.total = 0
      } finally {
        // 确保loading状态总是被重置
        this.loading = false
      }
    },
    
    resetFilter() {
      this.keyword = ''
      this.selectedCategory = null
      this.selectedTag = null
      this.selectedDifficulty = null
      this.selectedType = null
      this.currentPage = 1
      this.getQuestionList()
    },
    

    
    handlePageChange(page) {
      this.currentPage = page
      this.getQuestionList()
    },
    
    handlePageSizeChange(pageSize) {
      this.pageSize = pageSize
      this.currentPage = 1
      this.getQuestionList()
    },
    
    handleCategoryChange() {
      this.currentPage = 1
      this.getQuestionList()
    },
    
    handleTagChange() {
      console.log('标签选择变化事件触发')
      console.log('选中的标签ID:', this.selectedTag)
      console.log('当前标签列表:', this.tags)
      this.currentPage = 1
      this.getQuestionList()
    },
    
    onTagSelectOpen() {
      console.log('标签下拉框打开')
      console.log('tags数组:', this.tags)
      console.log('tags长度:', this.tags.length)
    },
    
    selectTag(tagId) {
      console.log('Tag被点击，标签ID:', tagId)
      this.selectedTag = tagId
      this.handleTagChange()
      // 关闭下拉框
      this.$nextTick(() => {
        const selectComponent = this.$refs.tagSelect
        if (selectComponent) {
          selectComponent.hideMenu()
        }
      })
    },
    
    handleDifficultyChange() {
      this.currentPage = 1
      this.getQuestionList()
    },
    
    // 开始练习模式
    startPracticeMode() {
      // 检查是否有题目
      if (!this.questions || this.questions.length === 0) {
        this.$Message.warning('当前筛选条件下没有题目，请调整筛选条件')
        return
      }
      
      // 获取第一道题
      const firstQuestion = this.questions[0]
      
      // 构建查询参数，传递当前的筛选条件
      const query = {}
      
      if (this.selectedCategory) {
        query.category = this.selectedCategory
      }
      
      if (this.selectedTag) {
        query.tags = this.selectedTag
      }
      
      if (this.selectedDifficulty) {
        query.difficulty = this.selectedDifficulty
      }
      
      if (this.selectedType) {
        query.question_type = this.selectedType
      }
      
      if (this.keyword) {
        query.keyword = this.keyword
      }
      
      // 直接跳转到第一道题的详情页
      this.$router.push({
        name: 'choice-question-detail',
        params: { id: firstQuestion.id },
        query: query
      })
    },
    
    // 显示考试模式对话框
    async showExamModeDialog() {
      
      try {
        // 创建默认的考试配置
        const examConfig = {
          title: '选择题考试',
          description: '基于当前筛选条件的考试',
          duration: 30, // 30分钟
          question_count: 10, // 默认10题
          total_score: 100, // 总分100分
          categories: this.selectedCategory ? [this.selectedCategory] : [],
          tags: this.selectedTag ? [this.selectedTag] : [],
          difficulty_distribution: {
            easy: 5,
            medium: 3,
            hard: 2
          }
        }
        
        // 通过API创建考试试卷
        const response = await api.createExamPaper(examConfig)
        const paper = response.data.data || response.data
        
        this.$Message.success('试卷创建成功！')
        
        // 跳转到考试页面
        this.$router.push({
          name: 'exam-paper',
          params: { paperId: paper.id }
        })
        
      } catch (error) {
        console.error('创建考试试卷失败:', error)
        this.$Message.error('创建考试试卷失败，请稍后重试')
      }
    },
    
    goToQuestion(row) {
      
      // 构建查询参数，传递当前的筛选条件
      const query = {}
      
      if (this.selectedCategory) {
        query.category = this.selectedCategory
      }
      
      if (this.selectedTag) {
        query.tags = this.selectedTag // 修正字段名：tag -> tags
      }
      
      if (this.selectedDifficulty) {
        query.difficulty = this.selectedDifficulty
        console.log('添加 difficulty 参数:', query.difficulty)
      }
      
      if (this.selectedType) {
        query.question_type = this.selectedType // 修正字段名：type -> question_type
        console.log('添加 question_type 参数:', query.question_type)
      }
      
      if (this.keyword) {
        query.keyword = this.keyword
        console.log('添加 keyword 参数:', query.keyword)
      }
      
      console.log('最终查询参数:', query)
      
      this.$router.push({
          name: 'choice-question-detail',
          params: { id: row.id },
          query: query
        })
      
      console.log('题目列表跳转完成，传递的查询参数:', query)
    },
    


  }
}
</script>

<style scoped>
.choice-question-list {
  margin: 20px;
}

.filter-section {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f8f9;
  border-radius: 4px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

/* 做题模式选择样式 */
.mode-selection-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
  overflow: hidden;
}

.mode-selection-container {
  padding: 24px;
  text-align: center;
}

.mode-title {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  gap: 8px;
}

.mode-title h3 {
  margin: 0;
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.mode-buttons {
  display: flex;
  justify-content: center;
  gap: 32px;
  flex-wrap: wrap;
}

.mode-button-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 160px;
}

.practice-mode-btn,
.exam-mode-btn {
  width: 160px;
  height: 60px;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.practice-mode-btn {
  background: linear-gradient(45deg, #4CAF50, #45a049);
}

.practice-mode-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.exam-mode-btn {
  background: linear-gradient(45deg, #FF9800, #F57C00);
}

.exam-mode-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 152, 0, 0.4);
}

.mode-description {
  margin-top: 12px;
  margin-bottom: 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .mode-buttons {
    flex-direction: column;
    gap: 20px;
  }
  
  .mode-button-wrapper {
    min-width: auto;
  }
  
  .practice-mode-btn,
  .exam-mode-btn {
    width: 200px;
  }
}

/* 表格样式优化 */
::v-deep .ivu-table {
  font-size: 14px;
}

::v-deep .ivu-table-tbody tr {
  height: 60px;
}

::v-deep .ivu-table td {
  padding: 12px 8px;
  vertical-align: middle;
}

::v-deep .ivu-table-row:hover {
  background-color: #f5f7fa;
  cursor: pointer;
}
</style>