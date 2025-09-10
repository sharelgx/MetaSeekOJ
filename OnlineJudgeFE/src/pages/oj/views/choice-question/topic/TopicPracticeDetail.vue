<template>
  <div class="topic-practice-detail">

    


    <!-- 面包屑导航 -->
    <div class="breadcrumb-section">
      <el-breadcrumb separator="/" class="breadcrumb-nav">
        <el-breadcrumb-item style="cursor: pointer;">
          <i class="fa fa-home"></i>
          专题练习
        </el-breadcrumb-item>
        <el-breadcrumb-item style="cursor: pointer;">
          <i class="fa fa-graduation-cap"></i>
          GESP等级考试
        </el-breadcrumb-item>
        <el-breadcrumb-item style="cursor: pointer;">
          <i class="fa fa-folder"></i>
          {{ currentCategory.name || '分类详情' }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 页面标题区 -->
    <div class="page-header">
      <div class="page-title">{{ parentCategoryName || currentCategory.name || '专题练习' }}</div>
      <div class="page-desc">{{ currentCategory.description }}</div>
    </div>

    <!-- 等级选择区（如果有子分类） -->
    <div v-if="childCategories.length > 0" class="level-section">
      <div class="section-title">
        <i class="fa fa-list"></i>
        选择分类
      </div>
      <div class="level-buttons">
        <div 
          v-for="child in childCategories" 
          :key="child.id"
          class="level-btn"
          @click="navigateToCategory(child.id)"
        >
          {{ child.name }}
        </div>
      </div>
    </div>

    <!-- 试卷列表区域 -->
    <div v-if="examPapers.length > 0" class="question-section">
      <div class="section-title">
        <i class="fa fa-file-text"></i>
        试卷列表
      </div>
      <table class="question-table">
        <thead>
          <tr>
            <th>试卷编号</th>
            <th>试卷名称</th>
            <th>题目数量</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="paper in examPapers" :key="paper.id" @click="startExam(paper.id)">
            <td class="question-id">{{ paper.id }}</td>
            <td>
              <a href="#" class="question-title">{{ paper.title }}</a>
            </td>
            <td>{{ paper.question_count || 0 }}题</td>
            <td>
              <span class="difficulty" :class="getPaperStatusClass(paper.status)">
                {{ getPaperStatusText(paper.status) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 题目列表区域 -->
    <div v-if="questions.length > 0" class="question-section">
      <div class="section-header">
        <div class="section-title">
          <i class="fa fa-edit"></i>
          练习题目
        </div>
        <el-button 
          type="primary" 
          size="medium"
          @click="startPractice"
          :loading="startLoading"
          class="start-practice-btn"
        >
          <i class="fa fa-play"></i>
          开始练习
        </el-button>
      </div>
      
      <table class="question-table">
        <thead>
          <tr>
            <th>题号</th>
            <th>题目标题</th>
            <th>类型</th>
            <th>难度</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(question, index) in questions" :key="question.id">
            <td class="question-id">{{ String(index + 1).padStart(3, '0') }}</td>
            <td>
              <a href="#" class="question-title">{{ question.title }}</a>
            </td>
            <td>
              <span class="difficulty" :class="getQuestionTypeClass(question.question_type)">
                {{ getQuestionTypeText(question.question_type) }}
              </span>
            </td>
            <td>
              <span class="difficulty" :class="getDifficultyClass(question.difficulty)">
                {{ getDifficultyText(question.difficulty) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 统一分页组件 -->
    <UnifiedPagination
      v-if="(examPapers.length > 0 || questions.length > 0) && pagination.total > pagination.pageSize"
      :current-page="pagination.page"
      :total="pagination.total"
      :page-size="pagination.pageSize"
      mode="frontend"
      @page-change="handlePageChange"
    />

    <!-- 空状态 -->
    <div v-if="!loading && childCategories.length === 0 && examPapers.length === 0 && questions.length === 0" class="empty-state">
      <i class="fa fa-folder-open"></i>
      <p>该分类下暂无内容</p>
      <el-button @click="$router.go(-1)">返回上级</el-button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <i class="fa fa-spinner fa-spin"></i>
      <p>正在加载...</p>
    </div>
  </div>
</template>

<script>
import api from '@oj/api'
import UnifiedPagination from '@/components/UnifiedPagination.vue'

export default {
  name: 'TopicPracticeDetail',
  components: {
    UnifiedPagination
  },
  data() {
    return {
      loading: false,
      startLoading: false,
      currentCategory: {},
      parentCategoryName: '', // 保存父级分类名称用于页面标题显示
      childCategories: [],
      examPapers: [],
      questions: [],
      breadcrumb: [],
      pagination: {
        page: 1,
        pageSize: 20,
        total: 0
      }
    }
  },
  computed: {
    // 移除了不再需要的分页计算属性，由统一分页组件处理
  },
  mounted() {
    console.log('TopicPracticeDetail mounted, route params:', this.$route.params)
    console.log('Current route path:', this.$route.path)
    this.loadCategoryData()
  },
  watch: {
    '$route'() {
      this.loadCategoryData()
    }
  },
  methods: {
    async loadCategoryData() {
      const categoryId = this.$route.params.categoryId || this.$route.params.id
      console.log('loadCategoryData called, categoryId:', categoryId)
      
      if (!categoryId) {
        console.error('Category ID is invalid')
        this.$message.error('分类ID无效')
        return
      }
      
      this.loading = true
      try {
        console.log('Calling API getTopicPracticeDetail with categoryId:', categoryId)
        const res = await api.getTopicPracticeDetail(categoryId)
        console.log('API response:', res)
        
        if (res.data && res.data.data) {
          this.currentCategory = res.data.data.category || {}
          this.childCategories = res.data.data.child_categories || []
          this.examPapers = res.data.data.exam_papers || []
          this.questions = res.data.data.questions || []
          this.breadcrumb = res.data.data.breadcrumb || []
          
          // 初始化时设置父级分类名称（从面包屑或固定值获取）
          if (!this.parentCategoryName) {
            // 如果面包屑有数据，取倒数第二个作为父级分类
            if (this.breadcrumb.length >= 2) {
              this.parentCategoryName = this.breadcrumb[this.breadcrumb.length - 2].name
            } else {
              // 否则使用固定的父级分类名称
              this.parentCategoryName = 'GESP等级考试'
            }
          }
          
          // 设置分页信息
          this.pagination.total = (res.data.data.exam_papers || []).length + (res.data.data.questions || []).length
        } else {
          console.error('API响应数据结构异常:', res.data)
        }
      } catch (error) {
        console.error('加载分类数据失败:', error)
        this.$message.error('加载分类数据失败')
        // 确保即使出错也有默认值
        this.currentCategory = {}
        this.childCategories = []
        this.examPapers = []
        this.questions = []
        this.breadcrumb = []
      } finally {
        this.loading = false
      }
    },
    
    async navigateToCategory(categoryId) {
      // 保存当前的子分类列表，以防新分类没有子分类时能保持显示
      const originalChildCategories = [...this.childCategories]
      
      // 只更新列表数据，不改变页面标题和路由
      this.loading = true
      try {
        const res = await api.getTopicPracticeDetail(categoryId)
        
        if (res.data && res.data.data) {
          // 更新所有数据，包括面包屑导航
          this.currentCategory = res.data.data.category || {}
          const newChildCategories = res.data.data.child_categories || []
          
          // 如果新分类没有子分类，保持原来的子分类显示（同级分类）
          if (newChildCategories.length === 0) {
            this.childCategories = originalChildCategories
          } else {
            this.childCategories = newChildCategories
          }
          
          this.examPapers = res.data.data.exam_papers || []
          this.questions = res.data.data.questions || []
          this.breadcrumb = res.data.data.breadcrumb || []
          
          // 重置分页
          this.pagination.page = 1
          this.pagination.total = (res.data.data.exam_papers || []).length + (res.data.data.questions || []).length
        } else {
          console.error('API响应数据结构异常:', res.data)
        }
      } catch (error) {
        console.error('加载分类数据失败:', error)
        this.$message.error('加载分类数据失败')
        // 确保即使出错也有默认值，但保持原有分类按钮
        this.childCategories = originalChildCategories
        this.examPapers = []
        this.questions = []
      } finally {
        this.loading = false
      }
    },
    

    
    async startPractice() {
      if (!this.$store.getters.isAuthenticated) {
        this.$message.warning('请先登录')
        this.$store.dispatch('changeModalStatus', { mode: 'login', visible: true })
        return
      }
      
      if (this.questions.length === 0) {
        this.$message.warning('该分类下没有题目，无法开始练习')
        return
      }
      
      this.startLoading = true
      try {
        const res = await api.startTopicPractice({
          category_id: this.currentCategory.id
        })
        
        // 重定向到考试页面（复用现有的考试系统）
        const redirectUrl = res.data.redirect_url
        this.$router.push(redirectUrl)
        
      } catch (error) {
        console.error('开始练习失败:', error)
        this.$message.error('开始练习失败')
      } finally {
        this.startLoading = false
      }
    },
    
    startExam(paperId) {
      // 跳转到考试页面，复用现有的考试系统
      this.$router.push(`/exam/${paperId}`)
    },
    
    handlePageChange(page) {
      this.pagination.page = page
      // 这里可以添加重新加载数据的逻辑
      // 例如：this.loadCategoryData()
    },
    
    getDifficultyClass(difficulty) {
      const classMap = {
        'easy': 'difficulty-easy',
        'medium': 'difficulty-medium',
        'hard': 'difficulty-hard'
      }
      return classMap[difficulty] || 'difficulty-medium'
    },
    
    getDifficultyText(difficulty) {
      const textMap = {
        'easy': '简单',
        'medium': '中等', 
        'hard': '困难'
      }
      return textMap[difficulty] || difficulty
    },
    
    getQuestionTypeClass(type) {
      const classMap = {
        'single': 'difficulty-easy',
        'multiple': 'difficulty-medium'
      }
      return classMap[type] || 'difficulty-easy'
    },
    
    getQuestionTypeText(type) {
      const textMap = {
        'single': '单选',
        'multiple': '多选'
      }
      return textMap[type] || type
    },
    
    getPaperStatusClass(status) {
      const classMap = {
        'available': 'difficulty-easy',
        'completed': 'difficulty-medium',
        'locked': 'difficulty-hard',
        'expired': 'difficulty-hard'
      }
      return classMap[status] || 'difficulty-easy'
    },
    
    getPaperStatusText(status) {
      const textMap = {
        'available': '可考试',
        'completed': '已完成',
        'locked': '未解锁',
        'expired': '已过期'
      }
      return textMap[status] || status
    }
  }
}
</script>

<style scoped>
/* 基础样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "Helvetica Neue", "Microsoft Yahei", sans-serif;
}

/* FontAwesome图标样式 */
.fa {
  font-family: 'FontAwesome' !important;
  font-style: normal;
  font-weight: normal;
  display: inline-block;
}

.topic-practice-detail {
  background-color: #f5f7fa;
  color: #333;
  line-height: 1.6;
  min-height: 100vh;
}



/* 面包屑导航 */
.breadcrumb-section {
  padding: 0 20px;
  margin-bottom: 20px;
}

.breadcrumb-nav {
  background-color: #fff;
  padding: 12px 16px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  font-size: 14px;
  color: #666;
}

.breadcrumb-nav .el-breadcrumb__item {
  font-weight: 500;
}

.breadcrumb-nav .el-breadcrumb__item a {
  color: #409EFF;
  text-decoration: none;
  transition: color 0.3s ease;
}

.breadcrumb-nav .el-breadcrumb__item a:hover {
  color: #66b1ff;
}

.breadcrumb-nav .el-breadcrumb__item i {
  margin-right: 6px;
  font-size: 12px;
  font-family: 'FontAwesome' !important;
  font-style: normal;
  font-weight: normal;
  display: inline-block;
}

.breadcrumb-nav .el-breadcrumb__item:last-child {
  color: #303133;
  font-weight: 600;
}

/* 页面标题区 */
.page-header {
  background-color: #fff;
  border-radius: 4px;
  padding: 16px 20px;
  margin: 0 20px 20px 20px;
  border-left: 4px solid #1890ff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2329;
}

.page-desc {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

/* 等级选择区 */
.level-section {
  background-color: #fff;
  border-radius: 4px;
  padding: 16px 20px;
  margin: 0 20px 20px 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #1f2329;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title i {
  color: #1890ff;
  font-family: 'FontAwesome' !important;
  font-style: normal;
  font-weight: normal;
}

.level-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.level-btn {
  padding: 8px 16px;
  background-color: #f5f7fa;
  border: 1px solid #e5e6eb;
  border-radius: 4px;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.level-btn:hover {
  background-color: #e6f7ff;
  border-color: #91d5ff;
}

.level-btn.active {
  background-color: #1890ff;
  color: #fff;
  border-color: #1890ff;
}

/* 试题列表区域 */
.question-section {
  background-color: #fff;
  border-radius: 4px;
  margin: 0 20px 20px 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e6eb;
}

.start-practice-btn {
  display: flex;
  align-items: center;
  gap: 8px;
}

.question-table {
  width: 100%;
  border-collapse: collapse;
}

.question-table th, 
.question-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e5e6eb;
  font-size: 14px;
}

.question-table th {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #666;
}

.question-table tbody tr {
  cursor: pointer;
  transition: background-color 0.2s;
}

.question-table tbody tr:hover {
  background-color: #f5f7fa;
}

.question-id {
  color: #1890ff;
  font-weight: 600;
  width: 80px;
}

.question-title {
  color: #1f2329;
  text-decoration: none;
  transition: color 0.2s;
}

.question-title:hover {
  color: #1890ff;
  text-decoration: underline;
}

.difficulty {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.difficulty-easy {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.difficulty-medium {
  background-color: #fffbe6;
  color: #faad14;
  border: 1px solid #ffe58f;
}

.difficulty-hard {
  background-color: #fff2f3;
  color: #f5222d;
  border: 1px solid #ffccc7;
}

/* 分页样式已移至统一分页组件 */

/* 空状态和加载状态 */
.empty-state, .loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
  margin: 0 20px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.empty-state i, .loading-state i {
  font-size: 64px;
  margin-bottom: 20px;
  display: block;
}

.empty-state p, .loading-state p {
  font-size: 16px;
  margin-bottom: 20px;
}

.loading-state i {
  color: #1890ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .topic-practice-detail {
    padding: 0;
  }
  

  
  .page-header, .level-section, .question-section, .breadcrumb-section {
    margin: 0 10px 10px 10px;
  }
  
  .question-table th:nth-child(4),
  .question-table td:nth-child(4) {
    display: none;
  }
  
  .level-btn {
    padding: 6px 12px;
    font-size: 13px;
  }
  
  /* 分页样式已移至统一分页组件 */
  
  .section-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
}
</style>