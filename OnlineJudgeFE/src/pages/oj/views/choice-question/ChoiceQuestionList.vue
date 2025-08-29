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
            <Input 
              v-model="keyword" 
              placeholder="搜索题目标题或内容"
              @on-enter="getQuestionList"
              clearable
            >
              <Icon type="ios-search" slot="prefix" />
            </Input>
          </Col>
          <Col :span="4">
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
          <Col :span="4">
            <Select v-model="selectedTag" placeholder="选择标签" clearable>
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
            <Select v-model="selectedDifficulty" placeholder="难度" clearable>
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
import api from './api'
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
          minWidth: 200,
          render: (h, params) => {
            return h('div', [
              h('div', {
                style: {
                  fontWeight: 'bold',
                  marginBottom: '4px'
                }
              }, params.row.title),
              h('div', {
                style: {
                  fontSize: '12px',
                  color: '#999'
                },
                domProps: {
                  innerHTML: params.row.content.substring(0, 100) + '...'
                }
              })
            ])
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
                  color: tag.color
                },
                style: {
                  marginRight: '4px'
                }
              }, tag.name)
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
              1: { text: '简单', color: 'success' },
              2: { text: '中等', color: 'warning' },
              3: { text: '困难', color: 'error' }
            }
            const difficulty = difficultyMap[params.row.difficulty]
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
            return h('span', this.$moment(params.row.create_time).format('YYYY-MM-DD HH:mm'))
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
        this.categories = res.data.data
      } catch (err) {
        console.error('获取分类列表失败:', err)
      }
    },
    
    async getTagList() {
      try {
        const res = await api.getTagList()
        this.tags = res.data.data
      } catch (err) {
        console.error('获取标签列表失败:', err)
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
        this.questions = res.data.data.results
        this.total = res.data.data.total
      } catch (err) {
        this.$Message.error('获取题目列表失败')
        console.error(err)
      } finally {
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
    
    goToQuestion(row) {
      this.$router.push({
        name: 'choice-question-detail',
        params: { id: row._id }
      })
    }
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
</style>