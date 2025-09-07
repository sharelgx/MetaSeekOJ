<template>
  <div class="topic-practice-detail">
    <div class="header">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/topics' }">专题练习</el-breadcrumb-item>
        <el-breadcrumb-item>{{ categoryName }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    
    <div class="content">
      <el-card>
        <div slot="header">
          <span>{{ categoryName }}</span>
          <el-button style="float: right; padding: 3px 0" type="text" @click="startPractice">开始练习</el-button>
        </div>
        
        <div class="category-info">
          <p>题目数量: {{ questionCount }}</p>
          <p>练习次数: {{ practiceCount }}</p>
          <p>正确率: {{ accuracy }}%</p>
        </div>
        
        <div class="practice-options">
          <el-button type="primary" @click="startPractice">开始练习</el-button>
          <el-button @click="viewWrongQuestions">查看错题</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TopicPracticeDetail',
  data() {
    return {
      categoryId: null,
      categoryName: '加载中...',
      questionCount: 0,
      practiceCount: 0,
      accuracy: 0
    }
  },
  created() {
    this.categoryId = this.$route.params.categoryId
    this.loadCategoryInfo()
  },
  methods: {
    loadCategoryInfo() {
      // 模拟加载分类信息
      this.categoryName = '专题分类 ' + this.categoryId
      this.questionCount = 50
      this.practiceCount = 10
      this.accuracy = 85
    },
    startPractice() {
      this.$router.push({
        name: 'choice-question-practice',
        query: { category: this.categoryId }
      })
    },
    viewWrongQuestions() {
      this.$router.push({
        name: 'wrong-question-book',
        query: { category: this.categoryId }
      })
    }
  }
}
</script>

<style scoped>
.topic-practice-detail {
  padding: 20px;
}

.header {
  margin-bottom: 20px;
}

.category-info {
  margin-bottom: 20px;
}

.category-info p {
  margin: 10px 0;
  font-size: 14px;
  color: #666;
}

.practice-options {
  text-align: center;
}

.practice-options .el-button {
  margin: 0 10px;
}
</style>