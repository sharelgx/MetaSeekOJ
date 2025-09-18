<template>
  <div class="view">
    <Panel title="试卷管理">
      <div slot="header">
        <el-button 
          type="success" 
          size="small" 
          @click="$router.push({name: 'import-exam-paper'})"
          icon="el-icon-upload"
        >
          导入试卷
        </el-button>
      </div>
      
      <!-- 筛选区域 -->
      <el-card class="filter-card" shadow="never" style="margin-bottom: 20px;">
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="分类">
            <CategorySelector
              v-model="filterForm.categoryId"
              @change="loadPapers"
              :categories="categories"
              :auto-load="false"
              placeholder="选择分类"
              style="width: 150px;"
            />
          </el-form-item>
          
          <el-form-item label="试卷类型">
            <el-select 
              v-model="filterForm.paperType" 
              @change="loadPapers" 
              clearable 
              placeholder="选择类型"
              style="width: 120px;"
            >
              <el-option label="全部类型" value=""></el-option>
              <el-option label="固定题目" value="fixed"></el-option>
              <el-option label="动态生成" value="dynamic"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="排序方式">
            <el-select 
              v-model="filterForm.orderBy" 
              @change="loadPapers"
              style="width: 120px;"
            >
              <el-option label="按创建时间" value="-create_time"></el-option>
              <el-option label="按导入顺序" value="import_order"></el-option>
              <el-option label="按标题" value="title"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="关键词">
            <el-input
              v-model="filterForm.keyword"
              placeholder="搜索试卷标题"
              @keyup.enter.native="loadPapers"
              style="width: 200px;"
            >
              <el-button slot="append" icon="el-icon-search" @click="loadPapers"></el-button>
            </el-input>
          </el-form-item>
          
          <el-form-item>
            <el-button @click="resetFilter">重置</el-button>
            <el-button type="success" icon="el-icon-plus" @click="createDialogVisible = true">创建试卷</el-button>
            <el-button 
              type="danger" 
              icon="el-icon-delete" 
              @click="batchDelete"
              :disabled="selectedPapers.length === 0"
            >
              批量删除 ({{ selectedPapers.length }})
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- 试卷列表 -->
      <el-table 
        :data="papers" 
        :loading="loading"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center"></el-table-column>
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        
        <el-table-column prop="title" label="试卷标题" min-width="200">
          <template slot-scope="scope">
            <span 
              class="editable-title" 
              @click="openEditDialog(scope.row)"
              :title="'点击编辑试卷：' + scope.row.title"
            >
              {{ scope.row.title }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip>
          <template slot-scope="scope">
            {{ scope.row.description || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="categories" label="分类" width="120">
          <template slot-scope="scope">
            <span v-if="scope.row.categories && scope.row.categories.length > 0">
              {{ scope.row.categories.map(cat => cat.name).join(', ') }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="paper_type" label="类型" width="100" align="center">
          <template slot-scope="scope">
            <el-tag :type="scope.row.paper_type === 'fixed' ? 'success' : 'info'" size="small">
              {{ scope.row.paper_type === 'fixed' ? '固定题目' : '动态生成' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="question_count" label="题目数" width="80" align="center"></el-table-column>
        
        <el-table-column prop="duration" label="时长(分钟)" width="100" align="center"></el-table-column>
        
        <el-table-column prop="total_score" label="总分" width="80" align="center"></el-table-column>
        
        <el-table-column prop="create_time" label="创建时间" width="160">
          <template slot-scope="scope">
            {{ formatDate(scope.row.create_time) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" align="center">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="primary"
              icon="el-icon-edit"
              @click="openEditDialog(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              size="mini"
              type="danger"
              icon="el-icon-delete"
              @click="deleteSingle(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>

      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <PaginationComponent
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange">
        </PaginationComponent>
      </div>
    </Panel>
    
    <!-- 试卷编辑对话框 -->
    <el-dialog
      title="编辑试卷"
      :visible.sync="editDialogVisible"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="editForm"
        :model="editForm"
        :rules="editRules"
        label-width="100px"
      >
        <el-form-item label="试卷标题" prop="title">
          <el-input
            v-model="editForm.title"
            placeholder="请输入试卷标题"
            maxlength="200"
            show-word-limit
          ></el-input>
        </el-form-item>
        
        <el-form-item label="试卷描述" prop="description">
          <el-input
            type="textarea"
            v-model="editForm.description"
            placeholder="请输入试卷描述"
            :rows="3"
            maxlength="500"
            show-word-limit
          ></el-input>
        </el-form-item>
        
        <el-form-item label="所属分类" prop="categories">
          <!-- 统一的分类选择器 -->
          <div class="category-selector-wrapper">
            <div 
              class="category-display" 
              :class="{ active: showEditCategoryDropdown }"
              @click="toggleEditCategoryDropdown"
            >
              <span 
                class="selected-text" 
                :class="{ placeholder: !selectedEditCategoriesText }"
              >
                {{ selectedEditCategoriesText || '请选择分类' }}
              </span>
              <i 
                class="el-icon-arrow-down" 
                :class="{ rotate: showEditCategoryDropdown }"
              ></i>
            </div>
            
            <div v-if="showEditCategoryDropdown" class="category-dropdown">
              <ul class="category-list">
                <li 
                  v-for="category in flattenedCategories" 
                  :key="category.id"
                  class="category-item"
                  :class="[
                    `level-${category.level}`,
                    { selected: editForm.categories.includes(category.id) }
                  ]"
                  @click="toggleEditCategorySelection(category)"
                >
                  <span class="category-indent" v-for="i in category.level" :key="i"></span>
                  <i class="category-icon el-icon-folder"></i>
                  <span class="category-name">{{ category.name }}</span>
                </li>
              </ul>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="考试时长" prop="duration">
          <el-input-number
            v-model="editForm.duration"
            :min="1"
            :max="300"
            placeholder="分钟"
            style="width: 100%"
          ></el-input-number>
          <span style="margin-left: 10px; color: #909399;">分钟</span>
        </el-form-item>
        
        <el-form-item label="题目数量" prop="question_count">
          <el-input-number
            v-model="editForm.question_count"
            :min="1"
            :max="100"
            placeholder="题目数量"
            style="width: 100%"
          ></el-input-number>
          <span style="margin-left: 10px; color: #909399;">题</span>
        </el-form-item>
        
        <el-form-item label="总分" prop="total_score">
          <el-input-number
            v-model="editForm.total_score"
            :min="1"
            :max="1000"
            placeholder="总分"
            style="width: 100%"
          ></el-input-number>
          <span style="margin-left: 10px; color: #909399;">分</span>
        </el-form-item>
      </el-form>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="editDialogVisible = false" :disabled="saving">取消</el-button>
        <el-button type="primary" @click="saveExamPaper" :loading="saving">保存</el-button>
      </div>
    </el-dialog>

    <!-- 创建试卷对话框 -->
    <el-dialog
      title="创建试卷"
      :visible.sync="createDialogVisible"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createForm"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="试卷标题" prop="title">
          <el-input
            v-model="createForm.title"
            placeholder="请输入试卷标题"
            maxlength="200"
            show-word-limit
          ></el-input>
        </el-form-item>
        
        <el-form-item label="试卷描述" prop="description">
          <el-input
            type="textarea"
            v-model="createForm.description"
            placeholder="请输入试卷描述"
            :rows="3"
            maxlength="500"
            show-word-limit
          ></el-input>
        </el-form-item>
        
        <el-form-item label="所属分类" prop="categories">
          <!-- 统一的分类选择器 -->
          <div class="category-selector-wrapper">
            <div 
              class="category-display" 
              :class="{ active: showCategoryDropdown }"
              @click="toggleCategoryDropdown"
            >
              <span 
                class="selected-text" 
                :class="{ placeholder: !selectedCategoriesText }"
              >
                {{ selectedCategoriesText || '请选择分类' }}
              </span>
              <i 
                class="el-icon-arrow-down" 
                :class="{ rotate: showCategoryDropdown }"
              ></i>
            </div>
            
            <div v-if="showCategoryDropdown" class="category-dropdown">
              <ul class="category-list">
                <li 
                  v-for="category in flattenedCategories" 
                  :key="category.id"
                  class="category-item"
                  :class="[
                    `level-${category.level}`,
                    { selected: createForm.categories.includes(category.id) }
                  ]"
                  @click="toggleCategorySelection(category)"
                >
                  <span class="category-indent" v-for="i in category.level" :key="i"></span>
                  <i class="category-icon el-icon-folder"></i>
                  <span class="category-name">{{ category.name }}</span>
                </li>
              </ul>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="考试时长" prop="duration">
          <el-input-number
            v-model="createForm.duration"
            :min="1"
            :max="300"
            placeholder="分钟"
            style="width: 100%"
          ></el-input-number>
          <span style="margin-left: 10px; color: #909399;">分钟</span>
        </el-form-item>
        
        <el-form-item label="题目数量" prop="question_count">
          <el-input-number
            v-model="createForm.question_count"
            :min="1"
            :max="100"
            placeholder="题目数量"
            style="width: 100%"
          ></el-input-number>
          <span style="margin-left: 10px; color: #909399;">题</span>
        </el-form-item>
        
        <el-form-item label="总分" prop="total_score">
          <el-input-number
            v-model="createForm.total_score"
            :min="1"
            :max="1000"
            placeholder="总分"
            style="width: 100%"
          ></el-input-number>
          <span style="margin-left: 10px; color: #909399;">分</span>
        </el-form-item>
      </el-form>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="createDialogVisible = false" :disabled="creating">取消</el-button>
        <el-button type="primary" @click="createExamPaper" :loading="creating">创建</el-button>
      </div>
    </el-dialog>

  </div>
</template>

<script>
import api from '@/pages/admin/api'
  import { mapGetters } from 'vuex'
  import PaginationComponent from '@/components/PaginationComponent.vue'
// import CategorySelector from '@/pages/admin/components/CategorySelector.vue' // 已替换为自定义ul列表

export default {
  name: 'ExamPaperList',
  components: {
    PaginationComponent
    // CategorySelector // 已替换为自定义ul列表
  },
  data() {
    return {
      loading: false,
      papers: [],
      categories: [],
      selectedPapers: [],
      isDeleting: false,
      showCategoryDropdown: false, // 控制创建对话框分类下拉菜单显示
      showEditCategoryDropdown: false, // 控制编辑对话框分类下拉菜单显示
      
      // 获取分类列表的方法已在 getCategories() 中实现
      // 打开创建对话框的方法已在模板中通过 @click="createDialogVisible = true" 实现,
      total: 0,
      currentPage: 1,
      pageSize: 20,
      
      // 筛选条件
      filterForm: {
        categoryId: '',
        paperType: '',
        orderBy: '-create_time',
        keyword: ''
      },
      
      // 编辑对话框相关
      editDialogVisible: false,
      saving: false,
      editForm: {
        id: null,
        title: '',
        description: '',
        categories: [],
        duration: 60,
        question_count: 10,
        total_score: 100
      },
      editRules: {
        title: [
          { required: true, message: '请输入试卷标题', trigger: 'blur' },
          { min: 1, max: 200, message: '标题长度在 1 到 200 个字符', trigger: 'blur' }
        ],
        categories: [
          { required: true, message: '请选择分类', trigger: 'change' }
        ],
        duration: [
          { required: true, message: '请输入考试时长', trigger: 'blur' },
          { type: 'number', min: 1, max: 300, message: '考试时长必须在 1-300 分钟之间', trigger: 'blur' }
        ],
        question_count: [
          { required: true, message: '请输入题目数量', trigger: 'blur' },
          { type: 'number', min: 1, max: 100, message: '题目数量必须在 1-100 之间', trigger: 'blur' }
        ],
        total_score: [
          { required: true, message: '请输入总分', trigger: 'blur' },
          { type: 'number', min: 1, max: 1000, message: '总分必须在 1-1000 之间', trigger: 'blur' }
        ]
      },
      
      // 创建对话框相关
      createDialogVisible: false,
      creating: false,
      createForm: {
        title: '',
        description: '',
        categories: [],
        duration: 60,
        question_count: 10,
        total_score: 100
      },
      createRules: {
        title: [
          { required: true, message: '请输入试卷标题', trigger: 'blur' },
          { min: 1, max: 200, message: '标题长度在 1 到 200 个字符', trigger: 'blur' }
        ],
        categories: [
          { required: true, message: '请选择至少一个分类', trigger: 'change' }
        ],
        duration: [
          { required: true, message: '请输入考试时长', trigger: 'blur' },
          { type: 'number', min: 1, max: 300, message: '考试时长必须在 1-300 分钟之间', trigger: 'blur' }
        ],
        question_count: [
          { required: true, message: '请输入题目数量', trigger: 'blur' },
          { type: 'number', min: 1, max: 100, message: '题目数量必须在 1-100 之间', trigger: 'blur' }
        ],
        total_score: [
          { required: true, message: '请输入总分', trigger: 'blur' },
          { type: 'number', min: 1, max: 1000, message: '总分必须在 1-1000 之间', trigger: 'blur' }
        ]
      }

    }
  },
  
  computed: {
    ...mapGetters(['user', 'isAuthenticated', 'isAdminRole']),
    
    // 扁平化分类数据，支持层级显示
    flattenedCategories() {
      if (!this.categories || this.categories.length === 0) {
        return []
      }
      
      // 递归去重处理
      const globalSeenIds = new Set()
      const deepDeduplication = (cats) => {
        const result = []
        cats.forEach(cat => {
          if (!globalSeenIds.has(cat.id)) {
            globalSeenIds.add(cat.id)
            const cleanCat = { ...cat }
            if (cleanCat.children && cleanCat.children.length > 0) {
              cleanCat.children = deepDeduplication(cleanCat.children)
            }
            result.push(cleanCat)
          }
        })
        return result
      }
      
      const deduplicatedCategories = deepDeduplication(this.categories)
      
      // 扁平化处理，使用与分类管理页面相同的排序逻辑
      const flatten = (cats, level = 0, parentName = '') => {
        let result = []
        // 按order排序
        const sortedCats = [...cats].sort((a, b) => (a.order || 0) - (b.order || 0))
        
        sortedCats.forEach(cat => {
          const displayName = level > 0 ? `${'  '.repeat(level)}${cat.name}` : cat.name
          result.push({
            ...cat,
            level,
            displayName,
            parentName
          })
          if (cat.children && cat.children.length > 0) {
            result = result.concat(flatten(cat.children, level + 1, cat.name))
          }
        })
        return result
      }
      
      return flatten(deduplicatedCategories)
    },
    
    // 获取选中分类的文本显示（创建对话框）
    selectedCategoriesText() {
      if (!this.createForm.categories || this.createForm.categories.length === 0) {
        return ''
      }
      
      const selectedNames = this.createForm.categories.map(id => {
        const category = this.flattenedCategories.find(cat => cat.id === id)
        return category ? category.name : ''
      }).filter(name => name)
      
      if (selectedNames.length <= 2) {
        return selectedNames.join(', ')
      } else {
        return `${selectedNames.slice(0, 2).join(', ')} 等${selectedNames.length}个分类`
      }
    },
    
    // 获取选中分类的文本显示（编辑对话框）
    selectedEditCategoriesText() {
      if (!this.editForm.categories || this.editForm.categories.length === 0) {
        return ''
      }
      
      const selectedNames = this.editForm.categories.map(id => {
        const category = this.flattenedCategories.find(cat => cat.id === id)
        return category ? category.name : ''
      }).filter(name => name)
      
      if (selectedNames.length <= 2) {
        return selectedNames.join(', ')
      } else {
        return `${selectedNames.slice(0, 2).join(', ')} 等${selectedNames.length}个分类`
      }
    }
  },
  
  async mounted() {
    console.log('ExamPaperList mounted')
    console.log('Current user:', this.user)
    console.log('Is authenticated:', this.isAuthenticated)
    console.log('Is admin role:', this.isAdminRole)
    
    // 确保用户已登录且有权限
    await this.checkAuth()
    
    // 初始化页面数据
    this.init()
    this.getCategories()
  },
  
  methods: {
    // 切换分类下拉菜单显示状态
    toggleCategoryDropdown() {
      this.showCategoryDropdown = !this.showCategoryDropdown
    },
    
    // 切换分类选择状态（支持多选）
    toggleCategorySelection(category) {
      const index = this.createForm.categories.indexOf(category.id)
      if (index > -1) {
        // 如果已选中，则取消选择
        this.createForm.categories.splice(index, 1)
      } else {
        // 如果未选中，则添加选择
        this.createForm.categories.push(category.id)
      }
    },
    
    // 切换编辑对话框分类下拉菜单显示状态
    toggleEditCategoryDropdown() {
      this.showEditCategoryDropdown = !this.showEditCategoryDropdown
    },
    
    // 切换编辑对话框分类选择状态（支持多选）
    toggleEditCategorySelection(category) {
      const index = this.editForm.categories.indexOf(category.id)
      if (index > -1) {
        // 如果已选中，则取消选择
        this.editForm.categories.splice(index, 1)
      } else {
        // 如果未选中，则添加选择
        this.editForm.categories.push(category.id)
      }
    },
    
    async checkAuth() {
      try {
        // 如果 store 中没有用户信息，尝试获取
        if (!this.user || !this.user.id) {
          const res = await api.getProfile()
          if (res.data.data && res.data.data.user) {
            this.$store.commit('CHANGE_PROFILE', {profile: res.data.data})
          } else {
            throw new Error('No user profile')
          }
        }
        
        // 检查管理员权限
        if (!this.isAdminRole) {
          this.$error('您没有管理员权限')
          this.$router.push('/admin/')
        }
      } catch (err) {
        console.error('Auth check failed:', err)
        this.$router.push({
          name: 'login',
          query: {redirect: this.$route.fullPath}
        })
      }
    },
    
    async init() {
      await this.getCategories()
      await this.loadPapers()
    },
    
    async getCategories() {
      try {
        const res = await api.getCategoryList()
        this.categories = res.data.data || []
      } catch (err) {
        console.error('获取分类列表失败:', err)
        this.categories = []
      }
    },
    
    async loadPapers() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          ordering: this.filterForm.orderBy
        }
        
        // 添加筛选条件
        if (this.filterForm.categoryId) {
          params.category = this.filterForm.categoryId
        }
        if (this.filterForm.paperType) {
          params.paper_type = this.filterForm.paperType
        }
        if (this.filterForm.keyword) {
          params.search = this.filterForm.keyword
        }
        
        const res = await api.getExamPaperList(params)
        const data = res.data.data || res.data
        
        this.papers = data.results || data
        this.total = data.count || data.length || 0
        
      } catch (err) {
        console.error('获取试卷列表失败:', err)
        
        // 检查是否是认证错误
        if (err.response && err.response.data && err.response.data.data && 
            err.response.data.data.includes('Please login')) {
          console.log('Authentication error, redirecting to login')
          this.$router.push({name: 'login', query: {redirect: this.$route.fullPath}})
        } else if (err.response && (err.response.status === 401 || err.response.status === 403)) {
          console.log('Authentication/Permission error, redirecting to login')
          this.$router.push({name: 'login', query: {redirect: this.$route.fullPath}})
        } else {
          this.$message.error('获取试卷列表失败: ' + (err.response && err.response.data && err.response.data.error ? err.response.data.error : err.message))
        }
        this.papers = []
        this.total = 0
      } finally {
        this.loading = false
      }
    },
    
    resetFilter() {
      this.filterForm = {
        categoryId: '',
        paperType: '',
        orderBy: '-create_time',
        keyword: ''
      }
      this.currentPage = 1
      this.loadPapers()
    },
    
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
      this.loadPapers()
    },
    
    handleCurrentChange(val) {
      this.currentPage = val
      this.loadPapers()
    },
    
    // 处理表格选择变化
    handleSelectionChange(selection) {
      this.selectedPapers = selection.map(item => item.id)
    },
    
    // 批量删除
    async batchDelete() {
      if (this.selectedPapers.length === 0) {
        this.$message.warning('请选择要删除的试卷')
        return
      }
      
      if (this.isDeleting) return
      
      try {
        await this.$confirm(
          `确定要删除选中的 ${this.selectedPapers.length} 份试卷吗？删除后可以恢复。`,
          '批量删除确认',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        this.isDeleting = true
        
        const response = await api.batchDeleteExamPapers(this.selectedPapers)
        
        if (response.data.error === null) {
          this.$message.success(response.data.data.message || '删除成功')
          this.selectedPapers = []
          await this.loadPapers()
        } else {
          this.$message.error(response.data.data || '删除失败')
        }
        
      } catch (error) {
        if (error !== 'cancel') {
          console.error('批量删除失败:', error)
          this.$message.error('删除失败: ' + (error.response && error.response.data && error.response.data.message ? error.response.data.message : error.message))
        }
      } finally {
        this.isDeleting = false
      }
    },
    
    // 单个删除
    async deleteSingle(paper) {
      try {
        await this.$confirm(
          `确定要删除试卷「${paper.title}」吗？删除后可以恢复。`,
          '删除确认',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        const response = await api.batchDeleteExamPapers([paper.id])
        
        if (response.data.error === null) {
          this.$message.success('删除成功')
          await this.loadPapers()
        } else {
          this.$message.error(response.data.data || '删除失败')
        }
        
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除失败:', error)
          this.$message.error('删除失败: ' + (error.response && error.response.data && error.response.data.message ? error.response.data.message : error.message))
        }
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    // 打开编辑对话框
    openEditDialog(paper) {
      console.log('打开编辑对话框，试卷信息:', paper)
      
      // 重置编辑对话框的分类下拉状态
      this.showEditCategoryDropdown = false
      
      // 填充表单数据
      this.editForm = {
        id: paper.id,
        title: paper.title || '',
        description: paper.description || '',
        categories: paper.category ? [paper.category.id] : [],
        duration: paper.duration || 60,
        question_count: paper.question_count || 10,
        total_score: paper.total_score || 100
      }
      
      console.log('编辑表单数据:', this.editForm)
      
      this.editDialogVisible = true
      
      // 清除表单验证状态
      this.$nextTick(() => {
        if (this.$refs.editForm) {
          this.$refs.editForm.clearValidate()
        }
      })
    },
    
    // 保存试卷信息
    async saveExamPaper() {
      try {
        // 表单验证
        const valid = await this.$refs.editForm.validate()
        if (!valid) {
          return
        }
        
        this.saving = true
        
        // 准备提交数据
        const updateData = {
          title: this.editForm.title,
          description: this.editForm.description,
          categories: this.editForm.categories || [],
          duration: this.editForm.duration,
          question_count: this.editForm.question_count,
          total_score: this.editForm.total_score
        }
        
        console.log('提交更新数据:', updateData)
        
        // 调用API更新试卷
        const response = await api.updateExamPaper(this.editForm.id, updateData)
        
        console.log('更新响应:', response)
        
        this.$message.success('试卷更新成功')
        this.editDialogVisible = false
        
        // 刷新列表
        await this.loadPapers()
        
      } catch (error) {
        console.error('更新试卷失败:', error)
        
        let errorMessage = '更新试卷失败'
        if (error.response && error.response.data) {
          errorMessage = error.response.data.error || error.response.data.message || errorMessage
        }
        
        this.$message.error(errorMessage)
      } finally {
        this.saving = false
      }
    },
    
    // 创建试卷
    async createExamPaper() {
      try {
        // 表单验证
        const valid = await this.$refs.createForm.validate()
        if (!valid) {
          return
        }
        
        this.creating = true
        
        // 准备提交数据
        const createData = {
          title: this.createForm.title,
          description: this.createForm.description,
          categories: this.createForm.categories || [],
          duration: this.createForm.duration,
          question_count: this.createForm.question_count,
          total_score: this.createForm.total_score
        }
        
        console.log('提交创建数据:', createData)
        
        // 调用API创建试卷
        const response = await api.createExamPaper(createData)
        
        console.log('创建响应:', response)
        
        this.$message({
          message: '试卷创建成功！',
          type: 'success',
          duration: 3000
        })
        
        // 关闭对话框并重置表单
        this.createDialogVisible = false
        this.resetCreateForm()
        
        // 刷新列表数据
        await this.loadPapers()
        
        // 可选：跳转到新创建的试卷详情页
        // if (response.data && response.data.data && response.data.data.id) {
        //   this.$router.push(`/admin/exam-paper/${response.data.data.id}`)
        // }
        
      } catch (error) {
        console.error('创建试卷失败:', error)
        
        let errorMessage = '创建试卷失败'
        if (error.response && error.response.data) {
          errorMessage = error.response.data.error || error.response.data.message || errorMessage
        }
        
        this.$message.error(errorMessage)
      } finally {
        this.creating = false
      }
    },
    
    // 重置创建表单
    resetCreateForm() {
      this.createForm = {
        title: '',
        description: '',
        categories: [],
        duration: 60,
        question_count: 10,
        total_score: 100
      }
      
      this.$nextTick(() => {
        if (this.$refs.createForm) {
          this.$refs.createForm.clearValidate()
        }
      })
    },
    
    // 打开创建对话框
     openCreateDialog() {
       this.resetCreateForm()
       this.createDialogVisible = true
     },
     
     // 获取分类列表
     async getCategories() {
       try {
         const response = await api.getCategoryList()
         console.log('分类列表响应:', response)
         
         if (response.data && response.data.data) {
           this.categories = response.data.data
         } else if (response.data) {
           this.categories = response.data
         } else {
           this.categories = []
         }
         
         console.log('分类列表:', this.categories)
       } catch (error) {
         console.error('获取分类列表失败:', error)
         this.categories = []
       }
     }
  }
}
</script>

<style scoped>
.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  margin-bottom: 0;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.el-descriptions {
  margin-bottom: 20px;
}

.dialog-footer {
  text-align: right;
}

/* 统一的分类选择器样式 */
.category-selector-wrapper {
  position: relative;
  width: 100%;
}

.category-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #fff;
  cursor: pointer;
  transition: border-color 0.2s;
  min-height: 32px;
}

.category-display:hover {
  border-color: #c0c4cc;
}

.category-display.active {
  border-color: #409eff;
}

.selected-text {
  flex: 1;
  color: #606266;
}

.selected-text.placeholder {
  color: #c0c4cc;
}

.el-icon-arrow-down {
  margin-left: 8px;
  transition: transform 0.3s;
  color: #c0c4cc;
}

.el-icon-arrow-down.rotate {
  transform: rotate(180deg);
}

.category-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.category-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f5f7fa;
}

.category-item:last-child {
  border-bottom: none;
}

.category-item:hover {
  background-color: #f5f7fa;
}

.category-item.selected {
  background-color: #ecf5ff;
  color: #409eff;
}

/* 层级样式 */
.category-item.level-0 {
  padding-left: 12px;
  font-weight: 500;
}

.category-item.level-1 {
  padding-left: 28px;
}

.category-item.level-2 {
  padding-left: 44px;
}

.category-item.level-3 {
  padding-left: 60px;
}

.category-indent {
  width: 16px;
  height: 1px;
}

.category-icon {
  margin-right: 6px;
  color: #909399;
}

.category-name {
  flex: 1;
}
</style>