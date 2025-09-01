<template>
  <div class="wrong-question-book">
    <Panel shadow>
      <div slot="title">
        <Icon type="ios-bookmark" />
        我的错题本
        <Badge :count="total" style="margin-left: 10px" />
      </div>
      
      <!-- 筛选器 -->
      <div class="filter-section">
        <Row :gutter="10">
          <Col :span="6">
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
            <Select v-model="selectedDifficulty" placeholder="难度" clearable>
              <Option value="1">简单</Option>
              <Option value="2">中等</Option>
              <Option value="3">困难</Option>
            </Select>
          </Col>
          <Col :span="4">
            <Select v-model="selectedType" placeholder="题型" clearable>
              <Option value="single">单选题</Option>
              <Option value="multiple">多选题</Option>
            </Select>
          </Col>
          <Col :span="6">
            <Button type="primary" @click="getWrongQuestionList">筛选</Button>
            <Button @click="resetFilter" style="margin-left: 8px">重置</Button>
            <Button 
              type="success" 
              @click="batchRedo" 
              style="margin-left: 8px"
              :disabled="selectedRows.length === 0"
            >
              批量重做 ({{ selectedRows.length }})
            </Button>
          </Col>
        </Row>
      </div>
      
      <!-- 错题列表 -->
      <Table 
        :columns="columns"
        :data="wrongQuestions"
        :loading="loading"
        @on-selection-change="handleSelectionChange"
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
    
    <!-- 笔记编辑模态框 -->
    <Modal
      v-model="noteModalVisible"
      title="编辑笔记"
      @on-ok="saveNote"
      @on-cancel="cancelNote"
    >
      <Input 
        v-model="currentNote"
        type="textarea"
        :rows="6"
        placeholder="在这里记录你的学习笔记..."
      />
    </Modal>
  </div>
</template>

<script>
import api from './api'

export default {
  name: 'WrongQuestionBook',
  data() {
    return {
      loading: false,
      wrongQuestions: [],
      categories: [],
      total: 0,
      currentPage: 1,
      pageSize: 20,
      selectedRows: [],
      
      // 筛选条件
      selectedCategory: null,
      selectedDifficulty: null,
      selectedType: null,
      
      // 笔记编辑
      noteModalVisible: false,
      currentNote: '',
      editingWrongQuestion: null,
      
      columns: [
        {
          type: 'selection',
          width: 60,
          align: 'center'
        },
        {
          title: 'ID',
          key: 'question.id',
          width: 80,
          align: 'center',
          render: (h, params) => {
            return h('span', params.row.question.id)
          }
        },
        {
          title: '题目',
          key: 'question.title',
          minWidth: 200,
          render: (h, params) => {
            return h('div', [
              h('div', {
                style: {
                  fontWeight: 'bold',
                  marginBottom: '4px',
                  cursor: 'pointer',
                  color: '#2d8cf0'
                },
                on: {
                  click: () => this.goToQuestion(params.row.question.id)
                }
              }, params.row.question.title),
              h('div', {
                style: {
                  fontSize: '12px',
                  color: '#999'
                }
              }, `${params.row.question.question_type === 'single' ? '单选题' : '多选题'} | 难度: ${params.row.question.difficulty} | 分数: ${params.row.question.score}`)
            ])
          }
        },
        {
          title: '分类',
          key: 'question.category',
          width: 120,
          render: (h, params) => {
            return h('span', params.row.question.category ? params.row.question.category.name : '-')
          }
        },
        {
          title: '难度',
          key: 'question.difficulty',
          width: 80,
          align: 'center',
          render: (h, params) => {
            const difficultyMap = {
              1: { text: '简单', color: 'success' },
              2: { text: '中等', color: 'warning' },
              3: { text: '困难', color: 'error' }
            }
            const difficulty = difficultyMap[params.row.question.difficulty] || { text: '未知', color: 'default' }
            return h('Tag', {
              props: {
                color: difficulty.color
              }
            }, difficulty.text)
          }
        },
        {
          title: '题型',
          key: 'question.question_type',
          width: 80,
          align: 'center',
          render: (h, params) => {
            return h('span', params.row.question.question_type === 'single' ? '单选' : '多选')
          }
        },
        {
          title: '错误次数',
          key: 'wrong_count',
          width: 100,
          align: 'center',
          render: (h, params) => {
            return h('Badge', {
              props: {
                count: params.row.wrong_count,
                'overflow-count': 99
              }
            })
          }
        },
        {
          title: '笔记',
          key: 'note',
          width: 150,
          render: (h, params) => {
            const hasNote = params.row.note && params.row.note.trim()
            return h('div', [
              hasNote ? h('div', {
                style: {
                  fontSize: '12px',
                  color: '#666',
                  marginBottom: '4px',
                  maxHeight: '40px',
                  overflow: 'hidden'
                }
              }, params.row.note.substring(0, 50) + (params.row.note.length > 50 ? '...' : '')) : null,
              h('Button', {
                props: {
                  type: 'text',
                  size: 'small'
                },
                on: {
                  click: () => this.editNote(params.row)
                }
              }, hasNote ? '编辑笔记' : '添加笔记')
            ])
          }
        },
        {
          title: '加入时间',
          key: 'create_time',
          width: 150,
          render: (h, params) => {
            return h('span', new Date(params.row.create_time).toLocaleString('zh-CN'))
          }
        },
        {
          title: '操作',
          key: 'action',
          width: 150,
          align: 'center',
          render: (h, params) => {
            return h('div', [
              h('Button', {
                props: {
                  type: 'primary',
                  size: 'small'
                },
                style: {
                  marginRight: '8px'
                },
                on: {
                  click: () => this.redoQuestion(params.row.question.id)
                }
              }, '重做'),
              h('Button', {
                props: {
                  type: 'error',
                  size: 'small'
                },
                on: {
                  click: () => this.removeFromWrongQuestions(params.row.id)
                }
              }, '移除')
            ])
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
        this.getWrongQuestionList()
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
    
    async getWrongQuestionList() {
      this.loading = true
      try {
        const params = {
          offset: (this.currentPage - 1) * this.pageSize,
          limit: this.pageSize
        }
        
        if (this.selectedCategory) params.category = this.selectedCategory
        if (this.selectedDifficulty) params.difficulty = this.selectedDifficulty
        if (this.selectedType) params.type = this.selectedType
        
        const res = await api.getWrongQuestionList(params)
        this.wrongQuestions = res.data.data.results
        this.total = res.data.data.total
      } catch (err) {
        this.$Message.error('获取错题列表失败')
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    
    resetFilter() {
      this.selectedCategory = null
      this.selectedDifficulty = null
      this.selectedType = null
      this.currentPage = 1
      this.getWrongQuestionList()
    },
    
    handlePageChange(page) {
      this.currentPage = page
      this.getWrongQuestionList()
    },
    
    handlePageSizeChange(pageSize) {
      this.pageSize = pageSize
      this.currentPage = 1
      this.getWrongQuestionList()
    },
    
    handleSelectionChange(selection) {
      this.selectedRows = selection
    },
    
    goToQuestion(questionId) {
      this.$router.push({
        name: 'choice-question-detail',
        params: { id: questionId }
      })
    },
    
    redoQuestion(questionId) {
      this.$router.push({
        name: 'choice-question-detail',
        params: { id: questionId },
        query: { from: 'wrong-book' }
      })
    },
    
    batchRedo() {
      if (this.selectedRows.length === 0) {
        this.$Message.warning('请选择要重做的题目')
        return
      }
      
      // 可以实现批量重做逻辑，比如打开新标签页或者创建练习集
      this.$Message.info('批量重做功能开发中...')
    },
    
    editNote(wrongQuestion) {
      this.editingWrongQuestion = wrongQuestion
      this.currentNote = wrongQuestion.note || ''
      this.noteModalVisible = true
    },
    
    async saveNote() {
      try {
        await api.updateWrongQuestionNote(this.editingWrongQuestion.id, {
          note: this.currentNote
        })
        
        // 更新本地数据
        this.editingWrongQuestion.note = this.currentNote
        
        this.$Message.success('笔记保存成功')
        this.noteModalVisible = false
      } catch (err) {
        this.$Message.error('保存笔记失败')
        console.error(err)
      }
    },
    
    cancelNote() {
      this.noteModalVisible = false
      this.currentNote = ''
      this.editingWrongQuestion = null
    },
    
    async removeFromWrongQuestions(id) {
      this.$Modal.confirm({
        title: '确认移除',
        content: '确定要从错题本中移除这道题目吗？',
        onOk: async () => {
          try {
            await api.removeFromWrongQuestions(id)
            this.$Message.success('移除成功')
            this.getWrongQuestionList()
          } catch (err) {
            this.$Message.error('移除失败')
            console.error(err)
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.wrong-question-book {
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