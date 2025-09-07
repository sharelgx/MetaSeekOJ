<template>
  <div class="topic-practice-detail">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb-nav">
      <el-breadcrumb-item :to="{ name: 'TopicPracticeHome' }">
        专题练习
      </el-breadcrumb-item>
      <el-breadcrumb-item 
        v-for="(item, index) in breadcrumb" 
        :key="item.id"
        :to="index < breadcrumb.length - 1 ? { name: 'TopicPracticeDetail', params: { categoryId: item.id } } : null"
      >
        {{ item.name }}
      </el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 分类信息 -->
    <div class="category-info" v-loading="loading">
      <h1 class="category-title">
        <i class="el-icon-collection"></i>
        {{ currentCategory.name }}
      </h1>
      <p class="category-description">{{ currentCategory.description }}</p>
      <div class="category-meta">
        <span class="meta-item">
          <i class="el-icon-document"></i>
          共 {{ currentCategory.question_count }} 道题
        </span>
      </div>
    </div>

    <!-- 子分类列表 -->
    <div v-if="childCategories.length > 0" class="subcategories-section">
      <h2 class="section-title">
        <i class="el-icon-folder"></i>
        子分类
      </h2>
      <div class="subcategory-grid">
        <el-card 
          v-for="child in childCategories" 
          :key="child.id"
          class="subcategory-card"
          shadow="hover"
          @click.native="navigateToCategory(child.id)"
        >
          <div class="subcategory-content">
            <h3 class="subcategory-title">{{ child.name }}</h3>
            <p class="subcategory-description">{{ child.description }}</p>
            <div class="subcategory-stats">
              <span class="question-count">
                <i class="el-icon-document"></i>
                {{ child.question_count }} 道题
              </span>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 题目列表 -->
    <div v-if="questions.length > 0" class="questions-section">
      <div class="section-header">
        <h2 class="section-title">
          <i class="el-icon-edit-outline"></i>
          练习题目
        </h2>
        <el-button 
          type="primary" 
          size="medium"
          @click="startPractice"
          :loading="startLoading"
        >
          <i class="el-icon-caret-right"></i>
          开始练习
        </el-button>
      </div>
      
      <!-- 题目表格 -->
      <el-table 
        :data="questions" 
        stripe
        style="width: 100%"
        class="questions-table"
      >
        <el-table-column prop="order" label="序号" width="80" align="center"/>
        <el-table-column prop="title" label="题目标题" min-width="300">
          <template slot-scope="scope">
            <span class="question-title">{{ scope.row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="question_type" label="类型" width="100" align="center">
          <template slot-scope="scope">
            <el-tag 
              :type="scope.row.question_type === 'single' ? 'primary' : 'success'"
              size="small"
            >
              {{ scope.row.question_type === 'single' ? '单选' : '多选' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="难度" width="100" align="center">
          <template slot-scope="scope">
            <el-tag 
              :type="getDifficultyType(scope.row.difficulty)"
              size="small"
            >
              {{ getDifficultyText(scope.row.difficulty) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && childCategories.length === 0 && questions.length === 0" class="empty-state">
      <i class="el-icon-document-remove"></i>
      <p>该分类下暂无内容</p>
      <el-button @click="$router.go(-1)">返回上级</el-button>
    </div>
  </div>
</template>

<script>
import api from '@oj/api'

export default {
  name: 'TopicPracticeDetail',
  data() {
    return {
      loading: false,
      startLoading: false,
      currentCategory: {},
      childCategories: [],
      questions: [],
      breadcrumb: []
    }
  },
  mounted() {
    this.loadCategoryData()
  },
  watch: {
    '$route'() {
      this.loadCategoryData()
    }
  },
  methods: {
    async loadCategoryData() {
      const categoryId = this.$route.params.categoryId
      if (!categoryId) {
        this.$error('分类ID无效')
        return
      }
      
      this.loading = true
      try {
        const res = await api.getTopicPracticeDetail(categoryId)
        this.currentCategory = res.data.category || {}
        this.childCategories = res.data.child_categories || []
        this.questions = res.data.questions || []
        this.breadcrumb = res.data.breadcrumb || []
      } catch (error) {
        console.error('加载分类数据失败:', error)
        this.$error('加载分类数据失败')
        // 确保即使出错也有默认值
        this.currentCategory = {}
        this.childCategories = []
        this.questions = []
        this.breadcrumb = []
        this.$router.back()
      } finally {
        this.loading = false
      }
    },
    
    navigateToCategory(categoryId) {
      this.$router.push({
        name: 'TopicPracticeDetail',
        params: { categoryId }
      })
    },
    
    async startPractice() {
      if (!this.$store.getters.isAuthenticated) {
        this.$warning('请先登录')
        this.$store.dispatch('changeModalStatus', { mode: 'login', visible: true })
        return
      }
      
      if (this.questions.length === 0) {
        this.$warning('该分类下没有题目，无法开始练习')
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
        this.$error('开始练习失败')
      } finally {
        this.startLoading = false
      }
    },
    
    getDifficultyType(difficulty) {
      const typeMap = {
        'easy': 'success',
        'medium': 'warning',
        'hard': 'danger'
      }
      return typeMap[difficulty] || 'info'
    },
    
    getDifficultyText(difficulty) {
      const textMap = {
        'easy': '简单',
        'medium': '中等', 
        'hard': '困难'
      }
      return textMap[difficulty] || difficulty
    }
  }
}
</script>

<style scoped>
.topic-practice-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.breadcrumb-nav {
  margin-bottom: 20px;
}

.category-info {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.category-title {
  font-size: 28px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.category-title i {
  margin-right: 10px;
}

.category-description {
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 15px;
  opacity: 0.9;
}

.category-meta {
  display: flex;
  gap: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  opacity: 0.9;
}

.meta-item i {
  margin-right: 5px;
}

.subcategories-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 20px;
  color: #2c3e50;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.section-title i {
  margin-right: 8px;
  color: #409eff;
}

.subcategory-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.subcategory-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.subcategory-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.subcategory-content {
  padding: 10px;
  text-align: center;
}

.subcategory-title {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.subcategory-description {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
  min-height: 40px;
  line-height: 1.4;
}

.subcategory-stats {
  display: flex;
  justify-content: center;
}

.question-count {
  color: #909399;
  font-size: 13px;
  display: flex;
  align-items: center;
}

.question-count i {
  margin-right: 4px;
}

.questions-section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.questions-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.question-title {
  color: #2c3e50;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-state i {
  font-size: 64px;
  margin-bottom: 20px;
  display: block;
}

.empty-state p {
  font-size: 16px;
  margin-bottom: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .topic-practice-detail {
    padding: 15px;
  }
  
  .category-info {
    padding: 20px;
  }
  
  .category-title {
    font-size: 22px;
  }
  
  .subcategory-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
}
</style>