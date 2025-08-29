<template>
  <div class="question-management">
    <Panel shadow>
      <div slot="title">
        <Icon type="ios-settings" />
        题目管理
        <Badge :count="total" style="margin-left: 10px" />
      </div>
      
      <div slot="extra">
        <Button type="primary" @click="showCreateModal">
          <Icon type="ios-add" />
          新建题目
        </Button>
      </div>
      
      <!-- 筛选器 -->
      <div class="filter-section">
        <Row :gutter="10">
          <Col :span="5">
            <Input 
              v-model="keyword" 
              placeholder="搜索题目标题或内容"
              @on-enter="getQuestionList"
              clearable
            >
              <Icon type="ios-search" slot="prefix" />
            </Input>
          </Col>
          <Col :span="3">
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
          <Col :span="3">
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
              <Option value="easy">简单</Option>
              <Option value="medium">中等</Option>
              <Option value="hard">困难</Option>
            </Select>
          </Col>
          <Col :span="3">
            <Select v-model="selectedType" placeholder="题型" clearable>
              <Option value="single">单选题</Option>
              <Option value="multiple">多选题</Option>
            </Select>
          </Col>
          <Col :span="3">
            <Select v-model="selectedStatus" placeholder="状态" clearable>
              <Option value="visible">可见</Option>
              <Option value="hidden">隐藏</Option>
              <Option value="public">公开</Option>
              <Option value="private">私有</Option>
            </Select>
          </Col>
          <Col :span="4">
            <Button type="primary" @click="getQuestionList">搜索</Button>
            <Button @click="resetFilter" style="margin-left: 8px">重置</Button>
          </Col>
        </Row>
      </div>
      
      <!-- 批量操作 -->
      <div class="batch-operations" v-if="selectedRows.length > 0">
        <Alert show-icon>
          已选择 {{ selectedRows.length }} 个题目
          <template slot="desc">
            <Button size="small" @click="batchSetVisible(true)">批量显示</Button>
            <Button size="small" @click="batchSetVisible(false)" style="margin-left: 8px">批量隐藏</Button>
            <Button size="small" @click="batchSetPublic(true)" style="margin-left: 8px">批量公开</Button>
            <Button size="small" @click="batchSetPublic(false)" style="margin-left: 8px">批量私有</Button>
            <Button size="small" type="error" @click="batchDelete" style="margin-left: 8px">批量删除</Button>
          </template>
        </Alert>
      </div>
      
      <!-- 题目列表 -->
      <Table 
        :columns="columns"
        :data="questions"
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
    
    <!-- 创建/编辑题目模态框 -->
    <Modal
      v-model="questionModalVisible"
      :title="isEdit ? '编辑题目' : '创建题目'"
      width="80%"
      :mask-closable="false"
      @on-ok="saveQuestion"
      @on-cancel="cancelQuestion"
    >
      <QuestionEditor
        ref="questionEditor"
        :question="currentQuestion"
        :categories="categories"
        :tags="tags"
        @on-change="handleQuestionChange"
      />
    </Modal>
    
    <!-- 导入题目模态框 -->
    <Modal
      v-model="importModalVisible"
      title="批量导入题目"
      @on-ok="importQuestions"
      @on-cancel="cancelImport"
    >
      <div class="import-section">
        <div class="upload-area">
          <Upload
            ref="upload"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            accept=".xlsx,.xls,.json"
            :show-upload-list="false"
          >
            <Button icon="ios-cloud-upload-outline">选择文件</Button>
          </Upload>
          <div class="upload-tip">
            支持 Excel (.xlsx, .xls) 和 JSON 格式文件
          </div>
        </div>
        
        <div class="import-options" v-if="importData">
          <h4>导入预览 ({{ importData.length }} 个题目)</h4>
          <Table
            :columns="importColumns"
            :data="importData.slice(0, 5)"
            size="small"
          />
          <div v-if="importData.length > 5" class="more-tip">
            还有 {{ importData.length - 5 }} 个题目...
          </div>
          
          <div class="import-settings">
            <Checkbox v-model="importSettings.skipDuplicates">跳过重复题目</Checkbox>
            <Checkbox v-model="importSettings.updateExisting">更新已存在的题目</Checkbox>
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import api from '../api'
import QuestionEditor from '../components/QuestionEditor.vue'
import { DIFFICULTY_CHOICES, QUESTION_TYPE_CHOICES } from '../constants'

export default {
  name: 'QuestionManagement',
  components: {
    QuestionEditor
  },
  data() {
    return {
      loading: false,
      questions: [],
      categories: [],
      tags: [],
      selectedRows: [],
      
      // 筛选条件
      keyword: '',
      selectedCategory: null,
      selectedTag: null,
      selectedDifficulty: null,
      selectedType: null,
      selectedStatus: null,
      
      // 分页
      total: 0,
      currentPage: 1,
      pageSize: 20,
      
      // 题目编辑
      questionModalVisible: false,
      isEdit: false,
      currentQuestion: null,
      
      // 导入功能
      importModalVisible: false,
      importData: null,
      importSettings: {
        skipDuplicates: true,
        updateExisting: false
      },
      
      // 表格列定义
      columns: [
        {
          type: 'selection',
          width: 60,
          align: 'center'
        },
        {
          title: 'ID',
          key: '_id',
          width: 80,
          sortable: true
        },
        {
          title: '标题',
          key: 'title',
          minWidth: 200,
          render: (h, params) => {
            return h('div', {
              style: {
                cursor: 'pointer',
                color: '#2d8cf0'
              },
              on: {
                click: () => {
                  this.editQuestion(params.row)
                }
              }
            }, params.row.title)
          }
        },
        {
          title: '分类',
          key: 'category',
          width: 120,
          render: (h, params) => {
            return h('span', params.row.category ? params.row.category.name : '未分类')
          }
        },
        {
          title: '难度',
          key: 'difficulty',
          width: 80,
          render: (h, params) => {
            const colors = {
              'easy': 'success',
              'medium': 'warning', 
              'hard': 'error'
            }
            const texts = {
              'easy': '简单',
              'medium': '中等',
              'hard': '困难'
            }
            return h('Tag', {
              props: {
                color: colors[params.row.difficulty]
              }
            }, texts[params.row.difficulty])
          }
        },
        {
          title: '题型',
          key: 'question_type',
          width: 80,
          render: (h, params) => {
            return h('span', params.row.question_type === 'single' ? '单选' : '多选')
          }
        },
        {
          title: '分值',
          key: 'score',
          width: 60,
          sortable: true
        },
        {
          title: '提交/通过',
          width: 100,
          render: (h, params) => {
            return h('span', `${params.row.total_submit}/${params.row.total_accepted}`)
          }
        },
        {
          title: '正确率',
          width: 80,
          render: (h, params) => {
            return h('span', `${params.row.acceptance_rate}%`)
          }
        },
        {
          title: '状态',
          width: 100,
          render: (h, params) => {
            const tags = []
            if (params.row.visible) {
              tags.push(h('Tag', { props: { color: 'success' } }, '可见'))
            } else {
              tags.push(h('Tag', { props: { color: 'default' } }, '隐藏'))
            }
            if (params.row.is_public) {
              tags.push(h('Tag', { props: { color: 'blue' } }, '公开'))
            } else {
              tags.push(h('Tag', { props: { color: 'orange' } }, '私有'))
            }
            return h('div', tags)
          }
        },
        {
          title: '创建时间',
          key: 'create_time',
          width: 150,
          render: (h, params) => {
            return h('span', this.$moment(params.row.create_time).format('YYYY-MM-DD HH:mm'))
          }
        },
        {
          title: '操作',
          width: 200,
          render: (h, params) => {
            return h('div', [
              h('Button', {
                props: {
                  type: 'primary',
                  size: 'small'
                },
                style: {
                  marginRight: '5px'
                },
                on: {
                  click: () => {
                    this.editQuestion(params.row)
                  }
                }
              }, '编辑'),
              h('Button', {
                props: {
                  type: params.row.visible ? 'warning' : 'success',
                  size: 'small'
                },
                style: {
                  marginRight: '5px'
                },
                on: {
                  click: () => {
                    this.toggleVisible(params.row)
                  }
                }
              }, params.row.visible ? '隐藏' : '显示'),
              h('Button', {
                props: {
                  type: 'error',
                  size: 'small'
                },
                on: {
                  click: () => {
                    this.deleteQuestion(params.row)
                  }
                }
              }, '删除')
            ])
          }
        }
      ],
      
      // 导入预览列
      importColumns: [
        {
          title: '标题',
          key: 'title',
          width: 200
        },
        {
          title: '难度',
          key: 'difficulty',
          width: 80
        },
        {
          title: '题型',
          key: 'question_type',
          width: 80
        },
        {
          title: '分值',
          key: 'score',
          width: 60
        },
        {
          title: '选项数',
          render: (h, params) => {
            return h('span', params.row.options ? params.row.options.length : 0)
          }
        }
      ]
    }
  },
  computed: {
    uploadUrl() {
      return '/api/choice-question/import/'
    },
    uploadHeaders() {
      return {
        'Authorization': `Bearer ${this.$store.getters.token}`
      }
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    async init() {
      await Promise.all([
        this.getQuestionList(),
        this.getCategories(),
        this.getTags()
      ])
    },
    
    async getQuestionList() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize
        }
        
        if (this.keyword) params.keyword = this.keyword
        if (this.selectedCategory) params.category = this.selectedCategory
        if (this.selectedTag) params.tag = this.selectedTag
        if (this.selectedDifficulty) params.difficulty = this.selectedDifficulty
        if (this.selectedType) params.question_type = this.selectedType
        if (this.selectedStatus) {
          if (this.selectedStatus === 'visible') params.visible = true
          else if (this.selectedStatus === 'hidden') params.visible = false
          else if (this.selectedStatus === 'public') params.is_public = true
          else if (this.selectedStatus === 'private') params.is_public = false
        }
        
        const res = await api.getQuestionList(params)
        this.questions = res.data.results
        this.total = res.data.count
      } catch (error) {
        this.$Message.error('获取题目列表失败')
      } finally {
        this.loading = false
      }
    },
    
    async getCategories() {
      try {
        const res = await api.getCategoryList()
        this.categories = res.data.results
      } catch (error) {
        console.error('获取分类列表失败:', error)
      }
    },
    
    async getTags() {
      try {
        const res = await api.getTagList()
        this.tags = res.data.results
      } catch (error) {
        console.error('获取标签列表失败:', error)
      }
    },
    
    resetFilter() {
      this.keyword = ''
      this.selectedCategory = null
      this.selectedTag = null
      this.selectedDifficulty = null
      this.selectedType = null
      this.selectedStatus = null
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
    
    handleSelectionChange(selection) {
      this.selectedRows = selection
    },
    
    showCreateModal() {
      this.isEdit = false
      this.currentQuestion = null
      this.questionModalVisible = true
    },
    
    editQuestion(question) {
      this.isEdit = true
      this.currentQuestion = { ...question }
      this.questionModalVisible = true
    },
    
    async saveQuestion() {
      try {
        const questionData = this.$refs.questionEditor.getQuestionData()
        if (!questionData) {
          return false
        }
        
        if (this.isEdit) {
          await api.updateQuestion(this.currentQuestion.id, questionData)
          this.$Message.success('题目更新成功')
        } else {
          await api.createQuestion(questionData)
          this.$Message.success('题目创建成功')
        }
        
        this.questionModalVisible = false
        this.getQuestionList()
      } catch (error) {
        this.$Message.error(this.isEdit ? '题目更新失败' : '题目创建失败')
        return false
      }
    },
    
    cancelQuestion() {
      this.questionModalVisible = false
      this.currentQuestion = null
    },
    
    handleQuestionChange(question) {
      this.currentQuestion = question
    },
    
    async toggleVisible(question) {
      try {
        await api.updateQuestion(question.id, {
          visible: !question.visible
        })
        this.$Message.success(`题目已${question.visible ? '隐藏' : '显示'}`)
        this.getQuestionList()
      } catch (error) {
        this.$Message.error('操作失败')
      }
    },
    
    deleteQuestion(question) {
      this.$Modal.confirm({
        title: '确认删除',
        content: `确定要删除题目 "${question.title}" 吗？此操作不可恢复。`,
        onOk: async () => {
          try {
            await api.deleteQuestion(question.id)
            this.$Message.success('题目删除成功')
            this.getQuestionList()
          } catch (error) {
            this.$Message.error('题目删除失败')
          }
        }
      })
    },
    
    async batchSetVisible(visible) {
      try {
        const ids = this.selectedRows.map(row => row.id)
        await api.batchUpdateQuestions({
          ids,
          data: { visible }
        })
        this.$Message.success(`批量${visible ? '显示' : '隐藏'}成功`)
        this.getQuestionList()
      } catch (error) {
        this.$Message.error('批量操作失败')
      }
    },
    
    async batchSetPublic(isPublic) {
      try {
        const ids = this.selectedRows.map(row => row.id)
        await api.batchUpdateQuestions({
          ids,
          data: { is_public: isPublic }
        })
        this.$Message.success(`批量${isPublic ? '公开' : '私有'}成功`)
        this.getQuestionList()
      } catch (error) {
        this.$Message.error('批量操作失败')
      }
    },
    
    batchDelete() {
      this.$Modal.confirm({
        title: '确认批量删除',
        content: `确定要删除选中的 ${this.selectedRows.length} 个题目吗？此操作不可恢复。`,
        onOk: async () => {
          try {
            const ids = this.selectedRows.map(row => row.id)
            await api.batchDeleteQuestions({ ids })
            this.$Message.success('批量删除成功')
            this.getQuestionList()
          } catch (error) {
            this.$Message.error('批量删除失败')
          }
        }
      })
    },
    
    showImportModal() {
      this.importModalVisible = true
      this.importData = null
    },
    
    cancelImport() {
      this.importModalVisible = false
      this.importData = null
    },
    
    beforeUpload(file) {
      const isValidType = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                          'application/vnd.ms-excel',
                          'application/json'].includes(file.type)
      if (!isValidType) {
        this.$Message.error('只支持 Excel 和 JSON 格式文件')
        return false
      }
      const isLt10M = file.size / 1024 / 1024 < 10
      if (!isLt10M) {
        this.$Message.error('文件大小不能超过 10MB')
        return false
      }
      return true
    },
    
    handleUploadSuccess(response) {
      if (response.success) {
        this.importData = response.data.questions
        this.$Message.success('文件解析成功')
      } else {
        this.$Message.error(response.message || '文件解析失败')
      }
    },
    
    handleUploadError(error) {
      this.$Message.error('文件上传失败')
    },
    
    async importQuestions() {
      if (!this.importData || this.importData.length === 0) {
        this.$Message.warning('请先上传文件')
        return false
      }
      
      try {
        const res = await api.importQuestions({
          questions: this.importData,
          settings: this.importSettings
        })
        
        this.$Message.success(`导入成功：${res.data.success_count} 个题目，跳过：${res.data.skip_count} 个`)
        this.importModalVisible = false
        this.getQuestionList()
      } catch (error) {
        this.$Message.error('导入失败')
        return false
      }
    },
    
    async exportQuestions() {
      try {
        const params = {}
        if (this.selectedRows.length > 0) {
          params.ids = this.selectedRows.map(row => row.id)
        }
        
        const res = await api.exportQuestions(params)
        
        // 创建下载链接
        const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `choice_questions_${this.$moment().format('YYYY-MM-DD')}.xlsx`
        link.click()
        window.URL.revokeObjectURL(url)
        
        this.$Message.success('导出成功')
      } catch (error) {
        this.$Message.error('导出失败')
      }
    }
  }
}
</script>

<style scoped>
.question-management {
  padding: 20px;
}

.filter-section {
  margin-bottom: 16px;
  padding: 16px;
  background: #f8f8f9;
  border-radius: 4px;
}

.batch-operations {
  margin-bottom: 16px;
}

.pagination {
  margin-top: 16px;
  text-align: right;
}

.import-section {
  padding: 16px 0;
}

.upload-area {
  text-align: center;
  padding: 20px;
  border: 2px dashed #d7dde4;
  border-radius: 4px;
  margin-bottom: 16px;
}

.upload-tip {
  margin-top: 8px;
  color: #999;
  font-size: 12px;
}

.import-options {
  margin-top: 16px;
}

.more-tip {
  text-align: center;
  color: #999;
  margin: 8px 0;
}

.import-settings {
  margin-top: 16px;
  padding: 12px;
  background: #f8f8f9;
  border-radius: 4px;
}

.import-settings .ivu-checkbox-wrapper {
  margin-right: 16px;
}
</style>