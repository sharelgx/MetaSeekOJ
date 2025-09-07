<template>
  <div class="topic-management">
    <Panel :title="$t('m.Topic_Management')">
      <div slot="header">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-input 
              v-model="keyword" 
              prefix-icon="el-icon-search" 
              placeholder="搜索专题标题或描述"
              @keyup.enter.native="filterByKeyword">
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-button type="primary" size="small" @click="filterByKeyword">{{$t('m.Search')}}</el-button>
          </el-col>
          <el-col :span="4">
            <el-button size="small" @click="resetFilter">重置</el-button>
          </el-col>
          <el-col :span="4">
            <el-button type="success" size="small" @click="showCreateDialog">创建专题</el-button>
          </el-col>
          <el-col :span="4">
            <el-button size="small" type="info" @click="debugApiCall">调试 API</el-button>
          </el-col>
        </el-row>
      </div>
      
      <!-- 专题列表表格 -->
      <el-table
        v-loading="loadingTable"
        element-loading-text="loading"
        ref="table"
        :data="topics"
        style="width: 100%">
        <el-table-column width="80" prop="id" label="ID"></el-table-column>
        <el-table-column prop="title" label="专题标题" min-width="200">
          <template slot-scope="{row}">
            <el-link type="primary" @click="viewTopicDetail(row.id)">{{ row.title }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" width="300">
          <template slot-scope="{row}">
            <el-tooltip :content="row.description" placement="top">
              <span>{{ row.description ? row.description.substring(0, 50) + '...' : '-' }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty_level" label="难度" width="100">
          <template slot-scope="scope">
            <el-tag 
              :type="getDifficultyType(scope.row.difficulty_level)" 
              size="small">
              {{ getDifficultyText(scope.row.difficulty_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_questions" label="题目数" width="80"></el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template slot-scope="scope">
            <el-tag 
              :type="scope.row.is_active ? 'success' : 'info'" 
              size="small">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_time" label="创建时间" width="150">
          <template slot-scope="{row}">
            {{ formatTime(row.created_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template slot-scope="{row}">
            <el-button size="mini" @click="editTopic(row)">编辑</el-button>
            <el-button size="mini" type="info" @click="viewTopicDetail(row.id)">查看</el-button>
            <el-button size="mini" type="danger" @click="deleteTopic(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="panel-options">
        <el-pagination
          class="page"
          layout="prev, pager, next"
          @current-change="currentChange"
          :page-size="pageSize"
          :total="total">
        </el-pagination>
      </div>
    </Panel>
    
    <!-- 创建/编辑专题对话框 -->
    <el-dialog
      :title="editingTopic ? '编辑专题' : '创建专题'"
      :visible.sync="showDialog"
      width="800px"
      @close="resetForm">
      <el-form :model="topicForm" :rules="rules" ref="topicForm" label-width="100px">
        <el-form-item label="专题标题" prop="title">
          <el-input v-model="topicForm.title" placeholder="请输入专题标题"></el-input>
        </el-form-item>
        <el-form-item label="专题描述" prop="description">
          <el-input 
            type="textarea" 
            v-model="topicForm.description" 
            placeholder="请输入专题描述"
            :rows="3">
          </el-input>
        </el-form-item>
        <el-form-item label="难度等级" prop="difficulty_level">
          <el-select v-model="topicForm.difficulty_level" placeholder="请选择难度等级">
            <el-option label="入门" :value="1"></el-option>
            <el-option label="简单" :value="2"></el-option>
            <el-option label="中等" :value="3"></el-option>
            <el-option label="困难" :value="4"></el-option>
            <el-option label="专家" :value="5"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="关联题目" prop="question_ids">
          <div style="border: 1px solid #dcdfe6; border-radius: 4px; padding: 10px; max-height: 200px; overflow-y: auto;">
            <el-checkbox-group v-model="topicForm.question_ids">
              <div v-for="question in availableQuestions" :key="question.id" style="margin-bottom: 8px;">
                <el-checkbox :label="question.id">
                  <span style="font-weight: 500;">{{ question.title }}</span>
                  <el-tag size="mini" :type="getDifficultyTagType(question.difficulty)" style="margin-left: 8px;">
                    {{ question.difficulty }}
                  </el-tag>
                  <span style="color: #909399; margin-left: 8px;">分数: {{ question.score }}</span>
                </el-checkbox>
              </div>
            </el-checkbox-group>
            <div v-if="availableQuestions.length === 0" style="text-align: center; color: #909399; padding: 20px;">
              暂无可用题目，请先创建选择题
            </div>
          </div>
          <div style="margin-top: 8px; color: #909399; font-size: 12px;">
            已选择 {{ topicForm.question_ids.length }} 道题目
          </div>
        </el-form-item>
        <el-form-item label="可见性">
          <el-switch v-model="topicForm.is_public" active-text="公开" inactive-text="私有"></el-switch>
        </el-form-item>
        <el-form-item label="及格分数" prop="pass_score">
          <el-input-number v-model="topicForm.pass_score" :min="0" :max="100" :step="5"></el-input-number>
          <span style="margin-left: 10px;">分</span>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="topicForm.is_active" active-text="启用" inactive-text="禁用"></el-switch>
        </el-form-item>
        <el-form-item label="专题分类" prop="category_ids">
          <el-select 
            v-model="topicForm.category_ids" 
            multiple 
            placeholder="请选择分类"
            style="width: 100%">
            <el-option 
              v-for="category in categories"
              :key="category.id"
              :label="category.full_name || category.name"
              :value="category.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="专题标签" prop="tag_ids">
          <el-select 
            v-model="topicForm.tag_ids" 
            multiple 
            placeholder="请选择标签"
            style="width: 100%">
            <el-option 
              v-for="tag in tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id">
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import api from '../../api'
import { mapGetters } from 'vuex'

export default {
  name: 'TopicManagement',
  data() {
    return {
      topics: [],
      loadingTable: false,
      keyword: '',
      currentPage: 1,
      pageSize: 20,
      total: 0,
      showDialog: false,
      editingTopic: null,
      submitting: false,
      categories: [],
      tags: [],
      availableQuestions: [],
      topicForm: {
        title: '',
        description: '',
        difficulty_level: 1,
        pass_score: 60,
        is_active: true,
        is_public: true,
        category_ids: [],
        tag_ids: [],
        question_ids: []
      },
      rules: {
        title: [
          { required: true, message: '请输入专题标题', trigger: 'blur' },
          { min: 1, max: 255, message: '标题长度在 1 到 255 个字符', trigger: 'blur' }
        ],
        description: [
          { max: 1000, message: '描述长度不能超过 1000 个字符', trigger: 'blur' }
        ],
        difficulty_level: [
          { required: true, message: '请选择难度等级', trigger: 'change' }
        ],
        pass_score: [
          { required: true, message: '请输入及格分数', trigger: 'blur' },
          { type: 'number', min: 0, max: 100, message: '及格分数必须在 0-100 之间', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    ...mapGetters(['user', 'isAuthenticated', 'isAdminRole'])
  },
  async mounted() {
    console.log('TopicManagement mounted')
    console.log('Current user:', this.user)
    console.log('Is authenticated:', this.isAuthenticated)
    console.log('Is admin role:', this.isAdminRole)
    
    // 检查用户登录状态
    if (!this.isAuthenticated) {
      console.log('User not authenticated, checking profile...')
      try {
        const profileRes = await api.getProfile()
        if (!profileRes.data.data) {
          console.log('No profile data, redirecting to login')
          this.$router.push({name: 'login', query: {redirect: this.$route.fullPath}})
          return
        }
        // 如果有 profile 数据但 Vuex 状态未更新，手动更新
        this.$store.commit('CHANGE_PROFILE', {profile: profileRes.data.data})
      } catch (err) {
        console.error('Failed to get profile:', err)
        this.$router.push({name: 'login', query: {redirect: this.$route.fullPath}})
        return
      }
    }
    
    // 检查管理员权限
    if (!this.isAdminRole) {
      console.log('User does not have admin role')
      this.$error('您没有访问专题管理的权限')
      this.$router.push('/admin/')
      return
    }
    
    console.log('User authenticated and has admin role, loading topics')
    this.loadInitialData()
  },
  methods: {
    async loadInitialData() {
      // 并行加载所有初始数据
      await Promise.all([
        this.getTopics(),
        this.loadCategories(),
        this.loadTags(),
        this.loadAvailableQuestions()
      ])
    },
    
    async loadCategories() {
      try {
        const res = await api.getChoiceQuestionCategories()
        this.categories = res.data.data || []
        // 为分类添加完整路径名称
        this.categories.forEach(category => {
          if (category.parent) {
            // 如果有父分类，构建完整路径
            const parent = this.categories.find(c => c.id === category.parent)
            if (parent) {
              category.full_name = `${parent.name} > ${category.name}`
            }
          }
        })
      } catch (err) {
        console.error('加载分类失败:', err)
        this.categories = []
      }
    },
    
    async loadTags() {
      try {
        const res = await api.getChoiceQuestionTags()
        this.tags = res.data.data || []
      } catch (err) {
        console.error('加载标签失败:', err)
        this.tags = []
      }
    },
    
    async loadAvailableQuestions() {
      try {
        const res = await api.getChoiceQuestionList(0, 100, '') // 加载前100道题
        this.availableQuestions = res.data.data.results || []
      } catch (err) {
        console.error('加载题目失败:', err)
        this.availableQuestions = []
      }
    },
    
    getDifficultyTagType(difficulty) {
      const typeMap = {
        'Low': 'success',
        'Mid': 'warning', 
        'High': 'danger',
        '简单': 'success',
        '中等': 'warning',
        '困难': 'danger'
      }
      return typeMap[difficulty] || 'info'
    },
    
    async getTopics() {
      this.loadingTable = true
      console.log('Getting topics...')
      
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize
        }
        if (this.keyword) {
          params.keyword = this.keyword
        }
        
        console.log('API call params:', params)
        const res = await api.getTopicList(params)
        console.log('API response:', res)
        
        this.topics = res.data.data.results || []
        this.total = res.data.data.total || 0
        
        console.log('Topics loaded:', this.topics.length)
      } catch (err) {
        console.error('Error getting topics:', err)
        
        // 检查是否是认证错误
        if (err.response && err.response.data && err.response.data.data && 
            err.response.data.data.includes('Please login')) {
          console.log('Authentication error, redirecting to login')
          this.$router.push({name: 'login', query: {redirect: this.$route.fullPath}})
        } else if (err.response && (err.response.status === 401 || err.response.status === 403)) {
          console.log('Authentication/Permission error, redirecting to login')
          this.$router.push({name: 'login', query: {redirect: this.$route.fullPath}})
        } else {
          this.$error('获取专题列表失败: ' + (err.message || '未知错误'))
        }
      } finally {
        this.loadingTable = false
      }
    },
    
    async debugApiCall() {
      console.log('=== Topic Management API Debug ===')
      
      // 检查登录状态
      try {
        console.log('1. Checking profile...')
        const profileRes = await api.getProfile()
        console.log('Profile response:', profileRes)
        console.log('User:', this.user)
        console.log('Is authenticated:', this.isAuthenticated)
        console.log('Is admin role:', this.isAdminRole)
      } catch (err) {
        console.error('Profile error:', err)
      }
      
      // 检查专题 API
      try {
        console.log('2. Testing topic API...')
        const topicsRes = await api.getTopicList({page: 1, page_size: 1})
        console.log('Topics API response:', topicsRes)
      } catch (err) {
        console.error('Topics API error:', err)
        if (err.response) {
          console.error('Error response:', err.response)
        }
      }
      
      console.log('=== Debug End ===')
    },
    
    filterByKeyword() {
      this.currentPage = 1
      this.getTopics()
    },
    
    resetFilter() {
      this.keyword = ''
      this.currentPage = 1
      this.getTopics()
    },
    
    currentChange(page) {
      this.currentPage = page
      this.getTopics()
    },
    
    showCreateDialog() {
      this.editingTopic = null
      this.resetForm()
      this.showDialog = true
    },
    
    editTopic(topic) {
      this.editingTopic = topic
      this.topicForm = {
        title: topic.title,
        description: topic.description || '',
        difficulty_level: topic.difficulty_level,
        pass_score: topic.pass_score,
        is_active: topic.is_active,
        is_public: topic.is_public
      }
      this.showDialog = true
    },
    
    async deleteTopic(topic) {
      this.$confirm(`确定要删除专题"${topic.title}"吗？`, '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await api.deleteTopic(topic.id)
          this.$success('删除成功')
          this.getTopics()
        } catch (err) {
          console.error('Delete topic error:', err)
          this.$error('删除失败: ' + (err.message || '未知错误'))
        }
      })
    },
    
    viewTopicDetail(topicId) {
      this.$router.push(`/admin/topic/detail/${topicId}`)
    },
    
    submitForm() {
      this.$refs.topicForm.validate(async (valid) => {
        if (valid) {
          this.submitting = true
          try {
            if (this.editingTopic) {
              await api.updateTopic(this.editingTopic.id, this.topicForm)
              this.$success('更新成功')
            } else {
              await api.createTopic(this.topicForm)
              this.$success('创建成功')
            }
            this.showDialog = false
            this.getTopics()
          } catch (err) {
            console.error('Submit form error:', err)
            this.$error((this.editingTopic ? '更新失败' : '创建失败') + ': ' + (err.message || '未知错误'))
          } finally {
            this.submitting = false
          }
        }
      })
    },
    
    resetForm() {
      this.topicForm = {
        title: '',
        description: '',
        difficulty_level: 1,
        pass_score: 60,
        is_active: true,
        is_public: true,
        category_ids: [],
        tag_ids: [],
        question_ids: []
      }
      if (this.$refs.topicForm) {
        this.$refs.topicForm.resetFields()
      }
    },
    
    getDifficultyType(level) {
      const types = ['', 'success', 'info', 'warning', 'danger', 'danger']
      return types[level] || 'info'
    },
    
    getDifficultyText(level) {
      const texts = ['', '入门', '简单', '中等', '困难', '专家']
      return texts[level] || '未知'
    },
    
    formatTime(time) {
      if (!time) return '-'
      return new Date(time).toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.topic-management {
  margin: 20px;
}

.panel-options {
  margin-top: 20px;
  text-align: center;
}

.dialog-footer {
  text-align: right;
}
</style>