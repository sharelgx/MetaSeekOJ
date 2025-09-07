<template>
  <div class="topic-management-simple">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">专题管理</h1>
          <p class="page-subtitle">管理专题分类和试卷的层级结构</p>
        </div>
        <div class="action-section">
          <el-button type="primary" @click="createTopic">
            <i class="el-icon-plus"></i> 创建专题
          </el-button>
          <el-button @click="refreshData">
            <i class="el-icon-refresh"></i> 刷新
          </el-button>
        </div>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <div class="search-section">
      <el-card>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-input 
              v-model="searchKeyword" 
              placeholder="搜索专题名称或描述"
              @keyup.enter.native="searchTopics">
              <el-button slot="append" @click="searchTopics">搜索</el-button>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-button @click="resetSearch">重置</el-button>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 专题列表 -->
    <div class="main-content">
      <el-card>
        <!-- 专题表格 -->
        <el-table 
          :data="topics" 
          v-loading="loading"
          class="topics-table">
          <el-table-column prop="id" label="ID" width="80"></el-table-column>
          <el-table-column prop="title" label="专题名称" min-width="200">
            <template slot-scope="scope">
              <div class="topic-title-cell">
                <span class="topic-name">{{ scope.row.title }}</span>
                <el-tag 
                  :type="getDifficultyType(scope.row.difficulty_level)" 
                  size="mini">
                  {{ getDifficultyText(scope.row.difficulty_level) }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200">
            <template slot-scope="scope">
              <div class="description-cell">
                {{ scope.row.description || '-' }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="结构统计" width="150">
            <template slot-scope="scope">
              <div class="stats-cell">
                <div class="stat-item">
                  <span class="stat-number">{{ scope.row.categories_count || 0 }}</span>
                  <span class="stat-label">分类</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ scope.row.papers_count || 0 }}</span>
                  <span class="stat-label">试卷</span>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="练习统计" width="120">
            <template slot-scope="scope">
              <div class="stats-cell">
                <div class="stat-item">
                  <span class="stat-number">{{ scope.row.practice_count || 0 }}</span>
                  <span class="stat-label">次数</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ scope.row.user_count || 0 }}</span>
                  <span class="stat-label">用户</span>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template slot-scope="scope">
              <div class="status-cell">
                <el-tag 
                  :type="scope.row.is_active ? 'success' : 'info'" 
                  size="small">
                  {{ scope.row.is_active ? '启用' : '禁用' }}
                </el-tag>
                <el-tag 
                  :type="scope.row.is_public ? 'success' : 'warning'" 
                  size="mini"
                  style="margin-top: 5px;">
                  {{ scope.row.is_public ? '公开' : '私有' }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="created_by" label="创建者" width="100"></el-table-column>
          <el-table-column prop="create_time" label="创建时间" width="150">
            <template slot-scope="scope">
              {{ scope.row.create_time | localtime }}
            </template>
          </el-table-column>
          <el-table-column fixed="right" label="操作" width="200">
            <template slot-scope="scope">
              <el-button type="text" @click="editTopic(scope.row)">
                <i class="el-icon-edit"></i> 编辑
              </el-button>
              <el-button type="text" @click="viewStructure(scope.row)">
                <i class="el-icon-s-grid"></i> 结构
              </el-button>
              <el-button type="text" @click="deleteTopic(scope.row)">
                <i class="el-icon-delete"></i> 删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            @current-change="handleCurrentChange"
            @size-change="handleSizeChange"
            :current-page="pagination.page"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pagination.pageSize"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper">
          </el-pagination>
        </div>

        <!-- 空状态 -->
        <div v-if="topics.length === 0 && !loading" class="empty-state">
          <i class="el-icon-folder-opened"></i>
          <h3>暂无专题</h3>
          <p>创建您的第一个专题，开始组织考试内容</p>
          <el-button type="primary" @click="createTopic">创建专题</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import api from '@admin/api'

export default {
  name: 'TopicManagementSimple',
  data () {
    return {
      loading: false,
      topics: [],
      searchKeyword: '',
      
      // 分页
      pagination: {
        page: 1,
        pageSize: 20,
        total: 0
      }
    }
  },

  created () {
    this.loadTopics()
  },

  methods: {
    async loadTopics () {
      this.loading = true
      try {
        // 尝试加载真实数据
        if (api.getTopicsManage) {
          const params = {
            page: this.pagination.page,
            page_size: this.pagination.pageSize,
            keyword: this.searchKeyword
          }
          
          const res = await api.getTopicsManage(params)
          if (res && res.data && res.data.data) {
            const data = res.data.data
            this.topics = data.results || []
            this.pagination.total = data.total || 0
          }
        } else {
          // 使用演示数据
          this.loadDemoData()
        }
      } catch (err) {
        console.error('加载专题失败:', err)
        // 加载演示数据作为回退
        this.loadDemoData()
      } finally {
        this.loading = false
      }
    },

    loadDemoData () {
      // 演示数据
      this.topics = [
        {
          id: 1,
          title: 'GESP等级考试',
          description: '青少年软件编程等级考试专题练习',
          difficulty_level: 2,
          categories_count: 5,
          papers_count: 12,
          practice_count: 156,
          user_count: 45,
          is_active: true,
          is_public: true,
          created_by: 'admin',
          create_time: '2025-09-01T10:00:00Z'
        },
        {
          id: 2,
          title: '算法竞赛',
          description: '各类算法竞赛题目集合',
          difficulty_level: 4,
          categories_count: 8,
          papers_count: 25,
          practice_count: 89,
          user_count: 23,
          is_active: true,
          is_public: true,
          created_by: 'admin',
          create_time: '2025-08-25T14:30:00Z'
        }
      ]
      this.pagination.total = this.topics.length
      this.$message.info('正在显示演示数据，请检查后端服务连接')
    },

    // 搜索相关
    searchTopics () {
      this.pagination.page = 1
      this.loadTopics()
    },

    resetSearch () {
      this.searchKeyword = ''
      this.searchTopics()
    },

    refreshData () {
      this.loadTopics()
    },

    // 分页相关
    handleCurrentChange (page) {
      this.pagination.page = page
      this.loadTopics()
    },

    handleSizeChange (pageSize) {
      this.pagination.pageSize = pageSize
      this.pagination.page = 1
      this.loadTopics()
    },

    // 操作相关
    createTopic () {
      this.$router.push('/topic/create')
    },

    editTopic (topic) {
      this.$router.push(`/topic/edit/${topic.id}`)
    },

    viewStructure (topic) {
      this.$message.info(`查看专题"${topic.title}"的结构 - 功能开发中`)
    },

    async deleteTopic (topic) {
      try {
        await this.$confirm(`确定要删除专题"${topic.title}"吗？删除后将无法恢复。`, '确认删除', {
          type: 'warning',
          confirmButtonText: '删除',
          confirmButtonClass: 'el-button--danger'
        })
        
        if (api.deleteTopic) {
          await api.deleteTopic(topic.id)
          this.$message.success('专题删除成功')
          this.loadTopics()
        } else {
          this.$message.warning('删除功能暂不可用，请检查后端服务')
        }
      } catch (err) {
        if (err !== 'cancel') {
          this.$message.error('删除失败: ' + (err.message || err))
        }
      }
    },

    // 辅助方法
    getDifficultyType (level) {
      const types = ['', 'success', 'primary', 'warning', 'danger', 'info']
      return types[level] || 'info'
    },

    getDifficultyText (level) {
      const texts = ['', '简单', '中等', '困难', '专家', '大师']
      return texts[level] || '未知'
    }
  }
}
</script>

<style lang="less" scoped>
.topic-management-simple {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;
    
    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .title-section {
        .page-title {
          font-size: 28px;
          color: #2c3e50;
          margin-bottom: 8px;
        }
        
        .page-subtitle {
          color: #7f8c8d;
          font-size: 14px;
          margin: 0;
        }
      }
      
      .action-section {
        .el-button {
          margin-left: 10px;
        }
      }
    }
  }

  .search-section {
    margin-bottom: 20px;
  }

  .main-content {
    .topics-table {
      .topic-title-cell {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .topic-name {
          font-weight: 500;
        }
      }

      .description-cell {
        max-width: 200px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .stats-cell {
        .stat-item {
          display: flex;
          align-items: center;
          margin-bottom: 4px;
          
          .stat-number {
            font-weight: 600;
            color: #2c3e50;
            margin-right: 4px;
          }
          
          .stat-label {
            font-size: 12px;
            color: #909399;
          }
        }
      }

      .status-cell {
        display: flex;
        flex-direction: column;
        gap: 5px;
      }
    }

    .pagination-wrapper {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }

    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: #909399;
      
      i {
        font-size: 64px;
        margin-bottom: 20px;
        display: block;
      }
      
      h3 {
        margin-bottom: 12px;
        color: #606266;
      }
      
      p {
        margin-bottom: 20px;
      }
    }
  }
}
</style>
