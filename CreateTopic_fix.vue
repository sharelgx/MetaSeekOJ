<template>
  <div class="app-container">
    <!-- 页面导航 -->
    <div class="page-header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/admin/topic/management' }">专题管理</el-breadcrumb-item>
        <el-breadcrumb-item>{{ isEdit ? '编辑专题' : '创建专题' }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- 头部 -->
    <div class="page-title">
      <h2>{{ isEdit ? '编辑专题' : '创建专题' }}</h2>
      <p class="subtitle">{{ isEdit ? '修改专题信息和关联的分类' : '选择一级分类作为专题，二级分类下的试卷将自动关联' }}</p>
    </div>

    <!-- 调试信息 -->
    <el-card v-if="showDebugInfo" style="margin-bottom: 20px;">
      <div slot="header">调试信息</div>
      <p>当前路由: {{ $route.path }}</p>
      <p>路由参数: {{ JSON.stringify($route.params) }}</p>
      <p>专题ID: {{ topicId }}</p>
      <p>是否编辑模式: {{ isEdit }}</p>
      <p>表单数据: {{ JSON.stringify(topicForm) }}</p>
      <el-button size="mini" @click="showDebugInfo = false">隐藏调试信息</el-button>
    </el-card>

    <!-- 表单 -->
    <el-form ref="topicForm" :model="topicForm" :rules="rules" label-width="120px" class="topic-form">
      <!-- 分类选择 -->
      <el-card class="form-section">
        <div slot="header" class="section-header">
          <span>选择分类</span>
        </div>
        
        <el-form-item label="一级分类" prop="category_id">
          <el-select v-model="topicForm.category_id" placeholder="请选择一级分类作为专题" @change="onCategoryChange">
            <el-option 
              v-for="category in rootCategories" 
              :key="category.id" 
              :label="category.name" 
              :value="category.id">
            </el-option>
          </el-select>
        </el-form-item>
        
        <!-- 显示选中分类的信息 -->
        <div v-if="selectedCategory" class="category-info">
          <h4>{{ selectedCategory.name }}</h4>
          <p v-if="selectedCategory.description">{{ selectedCategory.description }}</p>
          <div class="subcategories-preview">
            <h5>包含的二级分类：</h5>
            <el-tag v-for="sub in subcategories" :key="sub.id" class="subcategory-tag">
              {{ sub.name }} ({{ sub.paper_count || 0 }}套试卷)
            </el-tag>
          </div>
        </div>
      </el-card>

      <!-- 基本信息 -->
      <el-card class="form-section">
        <div slot="header" class="section-header">
          <span>基本信息</span>
        </div>
        
        <el-form-item label="专题名称" prop="name">
          <el-input v-model="topicForm.name" placeholder="专题名称" :readonly="!isEdit && topicForm.category_id"></el-input>
        </el-form-item>
        
        <el-form-item label="难度等级" prop="difficulty">
          <el-select v-model="topicForm.difficulty" placeholder="请选择难度等级">
            <el-option label="简单" value="Easy"></el-option>
            <el-option label="中等" value="Medium"></el-option>
            <el-option label="困难" value="Hard"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="专题描述" prop="description">
          <el-input type="textarea" v-model="topicForm.description" placeholder="请输入专题描述" :rows="4" maxlength="500" show-word-limit></el-input>
        </el-form-item>
        
        <el-form-item label="及格分数" prop="pass_score">
          <el-input-number v-model="topicForm.pass_score" :min="0" :max="100" placeholder="请输入及格分数"></el-input-number>
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="topicForm.is_active" active-text="启用" inactive-text="禁用"></el-switch>
        </el-form-item>
      </el-card>

      <!-- 操作按钮 -->
      <div class="form-actions">
        <el-button @click="goBack">取消</el-button>
        <el-button type="primary" @click="saveTopic" :loading="saving" :disabled="!topicForm.category_id">
          {{ isEdit ? '更新专题' : '创建专题' }}
        </el-button>
        <el-button type="info" @click="showDebugInfo = true" size="mini">显示调试信息</el-button>
      </div>
    </el-form>
  </div>
</template>

<script>
import api from '@admin/api'

export default {
  name: 'CreateTopic',
  data () {
    return {
      saving: false,
      showDebugInfo: false,
      
      // 专题表单
      topicForm: {
        category_id: null,
        name: '',
        description: '',
        difficulty: 'Medium',
        pass_score: 60,
        cover_image: '',
        is_active: true
      },
      rules: {
        category_id: [
          { required: true, message: '请选择一级分类', trigger: 'change' }
        ],
        name: [
          { required: true, message: '专题名称不能为空', trigger: 'blur' }
        ],
        difficulty: [
          { required: true, message: '请选择难度等级', trigger: 'change' }
        ]
      },

      // 分类数据
      rootCategories: [], // 一级分类列表
      selectedCategory: null, // 选中的分类
      subcategories: [] // 二级分类列表
    }
  },

  computed: {
    // 获取专题ID，支持多种参数名
    topicId() {
      return this.$route.params.topicId || this.$route.params.id
    },
    
    // 判断是否为编辑模式
    isEdit() {
      return !!this.topicId
    }
  },

  created () {
    console.log('CreateTopic 组件创建')
    console.log('当前路由:', this.$route.path)
    console.log('路由参数:', this.$route.params)
    console.log('专题ID:', this.topicId)
    console.log('是否编辑模式:', this.isEdit)
    
    this.loadRootCategories()
  },

  mounted () {
    // 检查是否为编辑模式
    if (this.isEdit) {
      console.log('编辑模式，加载专题数据，ID:', this.topicId)
      this.loadTopicForEdit(this.topicId)
    }
  },

  methods: {
    // 加载一级分类
    async loadRootCategories () {
      try {
        console.log('开始加载根分类')
        const res = await api.getChoiceQuestionCategories({ parent: 'null' })
        console.log('根分类 API 响应:', res)
        
        this.rootCategories = res.data.data || []
        console.log('加载的根分类:', this.rootCategories)
        
        if (this.rootCategories.length === 0) {
          this.$message.warning('暂无可用的分类，请先创建分类')
        }
      } catch (err) {
        console.error('加载分类失败:', err)
        this.$message.error('加载分类失败: ' + (err.response?.data?.error || err.message))
        this.rootCategories = []
      }
    },

    // 加载专题数据用于编辑
    async loadTopicForEdit (topicId) {
      try {
        console.log('加载专题数据，ID:', topicId)
        
        const res = await api.getTopicManageDetail(topicId)
        console.log('API 响应:', res)
        
        const topic = res.data.data
        console.log('获取到的专题数据:', topic)
        
        // 处理数据为空的情况
        if (!topic) {
          throw new Error('专题数据为空')
        }
        
        // 更安全的数据映射
        this.topicForm = {
          // 处理分类ID - 支持多种数据结构
          category_id: this.getCategoryId(topic),
          
          // 专题名称
          name: topic.title || topic.name || '',
          
          // 描述
          description: topic.description || '',
          
          // 难度级别转换
          difficulty: this.convertDifficultyLevel(topic.difficulty_level),
          
          // 及格分数
          pass_score: topic.pass_score || 60,
          
          // 封面图片
          cover_image: topic.cover_image || '',
          
          // 状态
          is_active: topic.is_active !== undefined ? !!topic.is_active : true
        }
        
        console.log('映射后的表单数据:', this.topicForm)
        
        // 加载分类信息
        if (this.topicForm.category_id) {
          await this.$nextTick() // 等待组件更新
          await this.loadCategoryInfo()
        }
        
      } catch (err) {
        console.error('加载专题数据失败:', err)
        this.$message.error('加载专题数据失败: ' + (err.response?.data?.error || err.message))
        
        // 加载失败时返回列表页
        setTimeout(() => {
          this.$router.push('/admin/topic/management')
        }, 2000)
      }
    },

    // 获取分类ID的辅助方法
    getCategoryId(topic) {
      // 支持多种数据结构
      if (topic.category_ids && Array.isArray(topic.category_ids) && topic.category_ids.length > 0) {
        return topic.category_ids[0]
      }
      if (topic.category_id) {
        return topic.category_id
      }
      if (topic.categories && Array.isArray(topic.categories) && topic.categories.length > 0) {
        return topic.categories[0].id
      }
      return null
    },

    // 难度级别转换
    convertDifficultyLevel(level) {
      if (typeof level === 'string') {
        return level // 如果已经是字符串，直接返回
      }
      
      // 数字转字符串
      switch (level) {
        case 1: return 'Easy'
        case 2: return 'Medium'
        case 3: return 'Hard'
        default: return 'Medium'
      }
    },

    // 加载分类信息
    async loadCategoryInfo() {
      try {
        // 等待根分类加载完成
        if (this.rootCategories.length === 0) {
          await this.loadRootCategories()
        }
        
        // 查找选中的分类
        this.selectedCategory = this.rootCategories.find(cat => cat.id === this.topicForm.category_id)
        
        if (this.selectedCategory) {
          console.log('找到选中的分类:', this.selectedCategory)
          // 加载子分类
          await this.loadSubcategories(this.topicForm.category_id)
        } else {
          console.warn('未找到ID为', this.topicForm.category_id, '的分类')
        }
      } catch (err) {
        console.error('加载分类信息失败:', err)
      }
    },

    // 分类选择变化
    async onCategoryChange (categoryId) {
      try {
        this.selectedCategory = this.rootCategories.find(cat => cat.id === categoryId)
        
        if (this.selectedCategory) {
          this.topicForm.category_id = categoryId
          
          // 如果不是编辑模式，自动填充名称
          if (!this.isEdit) {
            this.topicForm.name = this.selectedCategory.name
          }
          
          // 手动触发name字段的验证
          this.$nextTick(() => {
            if (this.$refs.topicForm) {
              this.$refs.topicForm.validateField('name')
            }
          })
          
          await this.loadSubcategories(categoryId)
        }
      } catch (err) {
        console.error('分类选择失败:', err)
        this.$message.error('加载分类信息失败')
      }
    },

    // 加载二级分类和试卷统计
    async loadSubcategories (parentId) {
      try {
        const res = await api.getChoiceQuestionCategories({ parent: parentId })
        this.subcategories = res.data.data || []
        
        // 为每个二级分类加载试卷数量
        for (let sub of this.subcategories) {
          try {
            const paperRes = await api.getChoiceQuestionPapers({ category: sub.id })
            sub.paper_count = paperRes.data.data.length
          } catch (err) {
            sub.paper_count = 0
          }
        }
      } catch (err) {
        this.$message.error('加载子分类失败')
        this.subcategories = []
      }
    },

    // 保存专题
    async saveTopic () {
      if (!this.$refs.topicForm) return
      
      this.$refs.topicForm.validate(async (valid) => {
        if (!valid) return
        
        this.saving = true
        try {
          const isEdit = this.isEdit
          
          console.log(isEdit ? '编辑专题' : '创建专题', '- 表单数据:', this.topicForm)
          
          const topicData = {
            title: this.topicForm.name,
            description: this.topicForm.description,
            difficulty_level: this.topicForm.difficulty === 'Easy' ? 1 : this.topicForm.difficulty === 'Medium' ? 2 : this.topicForm.difficulty === 'Hard' ? 3 : 2,
            pass_score: this.topicForm.pass_score,
            cover_image: this.topicForm.cover_image,
            is_active: this.topicForm.is_active,
            category_ids: this.topicForm.category_id ? [this.topicForm.category_id] : []
          }
          
          console.log('发送到API的数据:', topicData)
          
          if (isEdit) {
            await api.updateTopic(this.topicId, topicData)
            this.$message.success('专题更新成功')
          } else {
            await api.createTopic(topicData)
            this.$message.success('专题创建成功')
          }
          
          this.$router.push('/admin/topic/management')
        } catch (err) {
          const action = this.isEdit ? '更新' : '创建'
          this.$message.error(`${action}失败: ` + (err.response?.data?.error || err.message))
        } finally {
          this.saving = false
        }
      })
    },

    goBack () {
      this.$router.push('/admin/topic/management')
    }
  }
}
</script>

<style lang="less" scoped>
.app-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;

  .page-header {
    margin-bottom: 20px;
  }

  .page-title {
    margin-bottom: 30px;
    
    h2 {
      font-size: 28px;
      color: #2c3e50;
      margin-bottom: 8px;
    }
    
    .subtitle {
      color: #7f8c8d;
      font-size: 14px;
      margin: 0;
    }
  }

  .topic-form {
    .form-section {
      margin-bottom: 20px;
      
      .section-header {
        font-weight: 600;
      }
    }

    .category-info {
      margin-top: 15px;
      padding: 15px;
      background-color: #f8f9fa;
      border-radius: 4px;
      
      h4 {
        margin: 0 0 8px 0;
        color: #2c3e50;
      }
      
      p {
        margin: 0 0 12px 0;
        color: #666;
      }
      
      .subcategories-preview {
        h5 {
          margin: 0 0 8px 0;
          font-size: 14px;
          color: #2c3e50;
        }
        
        .subcategory-tag {
          margin-right: 8px;
          margin-bottom: 5px;
        }
      }
    }

    .form-actions {
      text-align: center;
      padding: 30px 0;
      border-top: 1px solid #e4e7ed;
      margin-top: 30px;

      .el-button {
        margin: 0 10px;
      }
    }
  }
}
</style>
