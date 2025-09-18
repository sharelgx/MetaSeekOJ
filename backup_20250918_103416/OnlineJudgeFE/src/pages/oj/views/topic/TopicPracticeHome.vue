<template>
  <div class="topic-practice-home">
    <div class="content-wrapper">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">专题练习</h1>
        <p class="page-description">按分类系统化学习，提升您的专业技能</p>
      </div>

      <!-- 分类导航 -->
      <div class="category-navigation">
        <h2 class="section-title">选择分类</h2>
        <div class="category-grid">
          <div 
            v-for="category in rootCategories" 
            :key="category.id" 
            class="category-card"
            @click="enterCategory(category)">
            <div class="category-icon">
              <i class="el-icon-folder-opened"></i>
            </div>
            <div class="category-info">
              <h3 class="category-title">{{ category.name }}</h3>
              <p class="category-description">{{ category.description || '暂无描述' }}</p>
              <div class="category-stats">
                <span class="stat-item">
                  <i class="el-icon-document"></i>
                  {{ category.topic_count || 0 }} 个专题
                </span>
                <span class="stat-item">
                  <i class="el-icon-edit-outline"></i>
                  {{ category.question_count || 0 }} 道题目
                </span>
              </div>
            </div>
            <div class="category-arrow">
              <i class="el-icon-arrow-right"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- 热门专题 -->
      <div class="popular-topics" v-if="popularTopics.length > 0">
        <h2 class="section-title">热门专题</h2>
        <div class="topic-grid">
          <div 
            v-for="topic in popularTopics" 
            :key="topic.id" 
            class="topic-card"
            @click="startTopic(topic)">
            <div class="topic-header">
              <div class="topic-title">{{ topic.title }}</div>
              <div class="topic-difficulty">
                <el-tag 
                  :type="getDifficultyType(topic.difficulty_level)" 
                  size="small">
                  {{ getDifficultyText(topic.difficulty_level) }}
                </el-tag>
              </div>
            </div>
            <div class="topic-description">{{ topic.description }}</div>
            <div class="topic-stats">
              <span class="stat">{{ topic.total_questions }} 道题目</span>
              <span class="stat">{{ topic.practice_count }} 次练习</span>
            </div>
            <div class="topic-footer">
              <el-button type="primary" size="small">开始练习</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近练习记录 -->
      <div class="recent-practice" v-if="recentPractices.length > 0">
        <h2 class="section-title">最近练习</h2>
        <el-table :data="recentPractices" style="width: 100%">
          <el-table-column prop="topic_title" label="专题名称" min-width="200"></el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template slot-scope="scope">
              <el-tag :type="getStatusType(scope.row.status)" size="small">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="得分" width="100">
            <template slot-scope="scope">
              <span v-if="scope.row.status === 'completed'">{{ scope.row.score }}%</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="start_time" label="开始时间" width="150">
            <template slot-scope="scope">
              {{ scope.row.start_time | localtime }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template slot-scope="scope">
              <el-button 
                v-if="scope.row.status === 'in_progress'"
                type="primary" 
                size="mini"
                @click="continuePractice(scope.row)">
                继续练习
              </el-button>
              <el-button 
                v-else
                type="info" 
                size="mini"
                @click="viewResult(scope.row)">
                查看结果
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@oj/api'

export default {
  name: 'TopicPracticeHome',
  data () {
    return {
      rootCategories: [],
      popularTopics: [],
      recentPractices: [],
      loading: false
    }
  },
  
  mounted () {
    this.init()
  },
  
  methods: {
    async init () {
      this.loading = true
      try {
        await Promise.all([
          this.loadCategories(),
          this.loadPopularTopics(),
          this.loadRecentPractices()
        ])
      } catch (err) {
        console.error('初始化失败:', err)
      } finally {
        this.loading = false
      }
    },
    
    async loadCategories () {
      try {
        // 使用模拟数据，因为前台API还没有完全实现
        this.rootCategories = [
          {
            id: 1,
            name: 'GESP等级考试',
            description: 'GESP等级考试相关专题练习',
            topic_count: 12,
            question_count: 256
          },
          {
            id: 2,
            name: '算法基础',
            description: '基础算法与数据结构专题',
            topic_count: 8,
            question_count: 189
          },
          {
            id: 3,
            name: '数学竞赛',
            description: '数学竞赛相关专题练习',
            topic_count: 15,
            question_count: 324
          }
        ]
      } catch (err) {
        console.error('加载分类失败:', err)
      }
    },
    
    async loadPopularTopics () {
      try {
        // 使用模拟数据
        this.popularTopics = [
          {
            id: 1,
            title: 'GESP三级算法基础',
            description: 'GESP三级考试中的基础算法题目练习',
            difficulty_level: 2,
            total_questions: 25,
            practice_count: 156
          },
          {
            id: 2,
            title: '排序算法专项',
            description: '各种排序算法的原理与实现',
            difficulty_level: 3,
            total_questions: 18,
            practice_count: 89
          },
          {
            id: 3,
            title: '数学基础知识',
            description: '编程竞赛中常用的数学知识',
            difficulty_level: 1,
            total_questions: 32,
            practice_count: 234
          }
        ]
      } catch (err) {
        console.error('加载热门专题失败:', err)
      }
    },
    
    async loadRecentPractices () {
      if (!this.$store.getters.isAuthenticated) {
        return
      }
      
      try {
        // 使用模拟数据
        this.recentPractices = [
          {
            id: 1,
            topic: 1,
            topic_title: 'GESP三级算法基础',
            status: 'completed',
            score: 85.5,
            start_time: new Date().toISOString()
          },
          {
            id: 2,
            topic: 2,
            topic_title: '排序算法专项',
            status: 'in_progress',
            score: null,
            start_time: new Date(Date.now() - 24*60*60*1000).toISOString()
          }
        ]
      } catch (err) {
        console.error('加载最近练习失败:', err)
      }
    },
    
    // 导航操作
    enterCategory (category) {
      this.$router.push({
        name: 'topic-category',
        params: { categoryId: category.id }
      })
    },
    
    startTopic (topic) {
      if (!this.$store.getters.isAuthenticated) {
        this.$warning('请先登录')
        this.$router.push({ name: 'login' })
        return
      }
      
      this.$router.push({
        name: 'topic-practice',
        params: { topicId: topic.id }
      })
    },
    
    continuePractice (practice) {
      this.$router.push({
        name: 'topic-practice',
        params: { topicId: practice.topic },
        query: { practiceId: practice.id }
      })
    },
    
    viewResult (practice) {
      this.$router.push({
        name: 'topic-result',
        params: { practiceId: practice.id }
      })
    },
    
    // 辅助方法
    getDifficultyType (level) {
      const types = ['', 'success', 'primary', 'warning', 'danger', 'info']
      return types[level] || 'info'
    },
    
    getDifficultyText (level) {
      const texts = ['', '简单', '中等', '困难', '专家', '大师']
      return texts[level] || '未知'
    },
    
    getStatusType (status) {
      const types = {
        'in_progress': 'warning',
        'completed': 'success',
        'paused': 'info'
      }
      return types[status] || 'info'
    },
    
    getStatusText (status) {
      const texts = {
        'in_progress': '进行中',
        'completed': '已完成',
        'paused': '已暂停'
      }
      return texts[status] || status
    }
  }
}
</script>

<style lang="less" scoped>
.topic-practice-home {
  min-height: 100vh;
  background: #f5f7fa;
  
  .content-wrapper {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .page-header {
    text-align: center;
    margin-bottom: 40px;
    
    .page-title {
      font-size: 2.5em;
      color: #2c3e50;
      margin-bottom: 10px;
    }
    
    .page-description {
      font-size: 1.2em;
      color: #7f8c8d;
      margin: 0;
    }
  }
  
  .section-title {
    font-size: 1.8em;
    color: #2c3e50;
    margin-bottom: 20px;
    border-left: 4px solid #3498db;
    padding-left: 15px;
  }
  
  .category-navigation {
    margin-bottom: 50px;
  }
  
  .category-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
  }
  
  .category-card {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 20px;
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .category-icon {
      font-size: 2.5em;
      color: #3498db;
      flex-shrink: 0;
    }
    
    .category-info {
      flex: 1;
      
      .category-title {
        font-size: 1.3em;
        color: #2c3e50;
        margin-bottom: 8px;
      }
      
      .category-description {
        color: #7f8c8d;
        margin-bottom: 12px;
        line-height: 1.5;
      }
      
      .category-stats {
        display: flex;
        gap: 15px;
        
        .stat-item {
          display: flex;
          align-items: center;
          gap: 5px;
          color: #95a5a6;
          font-size: 0.9em;
          
          i {
            color: #3498db;
          }
        }
      }
    }
    
    .category-arrow {
      font-size: 1.5em;
      color: #bdc3c7;
      flex-shrink: 0;
    }
  }
  
  .popular-topics {
    margin-bottom: 50px;
  }
  
  .topic-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }
  
  .topic-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    
    .topic-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      
      .topic-title {
        font-size: 1.2em;
        font-weight: 600;
        color: #2c3e50;
        flex: 1;
        margin-right: 10px;
      }
    }
    
    .topic-description {
      color: #7f8c8d;
      line-height: 1.5;
      margin-bottom: 15px;
      height: 3em;
      overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
    }
    
    .topic-stats {
      display: flex;
      justify-content: space-between;
      margin-bottom: 15px;
      
      .stat {
        color: #95a5a6;
        font-size: 0.9em;
      }
    }
    
    .topic-footer {
      text-align: center;
    }
  }
  
  .recent-practice {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  }
}

@media (max-width: 768px) {
  .topic-practice-home {
    .content-wrapper {
      padding: 15px;
    }
    
    .category-grid {
      grid-template-columns: 1fr;
    }
    
    .topic-grid {
      grid-template-columns: 1fr;
    }
    
    .category-card {
      padding: 20px;
      
      .category-info {
        .category-title {
          font-size: 1.1em;
        }
      }
    }
  }
}
</style>
