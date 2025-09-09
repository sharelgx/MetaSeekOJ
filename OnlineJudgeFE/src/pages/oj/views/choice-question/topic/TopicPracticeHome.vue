<template>
  <div class="topic-practice-home">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">
        <i class="el-icon-collection"></i>
        专题练习
      </h1>
      <p class="page-description">选择专题分类，开始你的学习之旅</p>
    </div>

    <!-- 测试按钮 -->
    <div style="margin-bottom: 20px; text-align: center;">
      <el-button type="primary" @click="testClick">测试点击事件</el-button>
    </div>
    
    <!-- 分类网格 -->
    <div class="category-grid" v-loading="loading">
      <el-card 
        v-for="topic in categories" 
        :key="topic.id"
        class="category-card"
        shadow="hover"
        style="cursor: pointer;"
        @click="navigateToCategory(topic.id)"
      >
        <div class="category-content">
          <div class="category-icon">
            <i class="el-icon-collection"></i>
          </div>
          <h3 class="category-title">{{ topic.name }}</h3>
          <p class="category-description">{{ topic.description }}</p>
          <div class="category-stats">
            <span class="problem-count">
              <i class="el-icon-document"></i>
              {{ topic.question_count || 0 }} 道题
            </span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 最近练习记录 -->
    <div v-if="recentRecords.length > 0" class="recent-section">
      <h2 class="section-title">
        <i class="el-icon-time"></i>
        最近练习
      </h2>
      <el-table 
        :data="recentRecords" 
        stripe
        style="width: 100%"
      >
        <el-table-column prop="title" label="专题" min-width="200"/>
        <el-table-column prop="score" label="得分" width="80" align="center">
          <template slot-scope="scope">
            <span v-if="scope.row.score !== null">{{ scope.row.score }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="correct_count" label="正确率" width="100" align="center">
          <template slot-scope="scope">
            <span v-if="scope.row.total_count > 0">
              {{ Math.round(scope.row.correct_count / scope.row.total_count * 100) }}%
            </span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="时间" width="150" align="center"/>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template slot-scope="scope">
            <el-tag 
              :type="getStatusType(scope.row.status)"
              size="small"
            >
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template slot-scope="scope">
            <el-button 
              v-if="scope.row.can_continue"
              type="primary" 
              size="mini"
              @click="continueRecord(scope.row)"
            >
              继续
            </el-button>
            <el-button 
              v-else
              type="text" 
              size="mini"
              @click="viewResult(scope.row)"
            >
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
import api from '@oj/api'

export default {
  name: 'TopicPracticeHome',
  data() {
    return {
      loading: false,
      categories: [],
      recentRecords: []
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        // 获取专题练习首页数据（包含分类和最近记录）
        const res = await api.getTopicPracticeHome()
        this.categories = res.data.data.categories || []
        this.recentRecords = res.data.data.recent_records || []
      } catch (error) {
        console.error('加载专题数据失败:', error)
        this.$error('加载数据失败')
        // 确保即使出错也有默认值
        this.categories = []
        this.recentRecords = []
      } finally {
        this.loading = false
      }
    },
    testClick() {
      console.log('测试按钮被点击了！')
      alert('测试按钮被点击了！')
    },
    navigateToCategory(topicId) {
      // 跳转到专题练习页面
      console.log('点击了分类，ID:', topicId)
      console.log('即将跳转到:', `/topics/${topicId}/practice`)
      alert(`点击了分类 ID: ${topicId}`)
      this.$router.push({
        path: `/topics/${topicId}/practice`
      })
    },
    
    getDifficultyText(level) {
      const difficultyMap = {
        1: '入门',
        2: '简单', 
        3: '中等',
        4: '困难',
        5: '专家'
      }
      return difficultyMap[level] || '未知'
    },
    getStatusType(status) {
      const typeMap = {
        'created': 'info',
        'started': 'warning', 
        'submitted': 'success',
        'timeout': 'danger'
      }
      return typeMap[status] || 'info'
    },
    getStatusText(status) {
      const textMap = {
        'created': '已创建',
        'started': '进行中',
        'submitted': '已完成',
        'timeout': '超时'
      }
      return textMap[status] || status
    },
    continueRecord(record) {
      this.$router.push(`/exam/session/${record.id}/`)
    },
    viewResult(record) {
      this.$router.push(`/exam/result/${record.id}/`)
    }
  }
}
</script>

<style scoped>
.topic-practice-home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-title {
  font-size: 32px;
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-title i {
  margin-right: 10px;
  color: #409eff;
}

.page-description {
  font-size: 16px;
  color: #606266;
  margin: 0;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.category-card {
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 180px;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.category-content {
  text-align: center;
  padding: 10px;
}

.category-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 15px;
}

.category-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
}

.category-description {
  color: #606266;
  font-size: 14px;
  margin-bottom: 15px;
  min-height: 40px;
  line-height: 1.4;
}

.category-stats {
  display: flex;
  justify-content: center;
  align-items: center;
}

.problem-count {
  color: #909399;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.problem-count i {
  margin-right: 5px;
}

.recent-section {
  margin-top: 40px;
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

.text-muted {
  color: #c0c4cc;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .topic-practice-home {
    padding: 15px;
  }
  
  .category-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .page-title {
    font-size: 24px;
  }
}
</style>