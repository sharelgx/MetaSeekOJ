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
            <Select v-model="selectedTag" placeholder="选择标签" clearable @on-change="handleTagChange">
              <Option 
                v-for="tag in tags" 
                :key="tag.id"
                :value="tag.id"
              >
                <Tag :color="tag.color">{{ tag.name }}</Tag>
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
      </div>
      
      <!-- 题目列表 -->
      <Table 
        :columns="columns"
        :data="questions"
        :loading="loading"
        @on-row-click="goToQuestion"
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
import api from './api/index'
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
          width: 100,
          align: 'center',
          render: (h, params) => {
            return h('Button', {
              props: {
                type: 'success',
                size: 'small'
              },
              on: {
                click: (e) => {
                  e.stopPropagation()
                  this.goToQuestion(params.row)
                }
              }
            }, '查看')
          }
        }
      ]
    }
  },
  
  mounted() {
    this.init()
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
        const params = {
          offset: (this.currentPage - 1) * this.pageSize,
          limit: this.pageSize
        }
        
        if (this.keyword) params.keyword = this.keyword
        if (this.selectedCategory) params.category = this.selectedCategory
        if (this.selectedTag) params.tag = this.selectedTag
        if (this.selectedDifficulty) params.difficulty = this.selectedDifficulty
        if (this.selectedType) params.type = this.selectedType
        
        const res = await api.getQuestionList(params)
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
      this.currentPage = 1
      this.getQuestionList()
    },
    
    handleDifficultyChange() {
      this.currentPage = 1
      this.getQuestionList()
    },
    
    goToQuestion(row) {
      console.log('=== 题目列表跳转调试 ===')
      console.log('当前筛选条件:')
      console.log('- selectedCategory:', this.selectedCategory)
      console.log('- selectedTag:', this.selectedTag)
      console.log('- selectedDifficulty:', this.selectedDifficulty)
      console.log('- selectedType:', this.selectedType)
      console.log('- keyword:', this.keyword)
      console.log('点击的题目信息:', row)
      
      // 构建查询参数，传递当前的筛选条件
      const query = {}
      
      if (this.selectedCategory) {
        query.category = this.selectedCategory
        console.log('添加 category 参数:', query.category)
      }
      
      if (this.selectedTag) {
        query.tags = this.selectedTag // 修正字段名：tag -> tags
        console.log('添加 tags 参数:', query.tags)
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