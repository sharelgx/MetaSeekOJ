<template>
  <div class="topic-management-list">
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
              v-model="searchForm.keyword" 
              placeholder="搜索专题名称或描述"
              @keyup.enter.native="searchTopics">
              <el-button slot="append" @click="searchTopics">搜索</el-button>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-select v-model="searchForm.difficulty" placeholder="选择难度" clearable>
              <el-option label="简单" :value="1"></el-option>
              <el-option label="中等" :value="2"></el-option>
              <el-option label="困难" :value="3"></el-option>
              <el-option label="专家" :value="4"></el-option>
              <el-option label="大师" :value="5"></el-option>
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select v-model="searchForm.status" placeholder="选择状态" clearable>
              <el-option label="启用" :value="true"></el-option>
              <el-option label="禁用" :value="false"></el-option>
            </el-select>
          </el-col>
          <el-col :span="4">
            <el-select v-model="searchForm.visibility" placeholder="可见性" clearable>
              <el-option label="公开" :value="true"></el-option>
              <el-option label="私有" :value="false"></el-option>
            </el-select>
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
        <!-- 批量操作 -->
        <div class="batch-actions" v-if="selectedTopics.length > 0">
          <span>已选择 {{ selectedTopics.length }} 个专题</span>
          <el-button type="primary" size="small" @click="batchEnable">批量启用</el-button>
          <el-button type="info" size="small" @click="batchDisable">批量禁用</el-button>
          <el-button type="danger" size="small" @click="batchDelete">批量删除</el-button>
        </div>

        <!-- 专题表格 -->
        <el-table 
          :data="topics" 
          v-loading="loading"
          @selection-change="handleSelectionChange"
          class="topics-table">
          <el-table-column type="selection" width="55"></el-table-column>
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
              <el-button type="text" @click="viewStatistics(scope.row)">
                <i class="el-icon-data-line"></i> 统计
              </el-button>
              <el-dropdown trigger="click">
                <el-button type="text">
                  更多<i class="el-icon-arrow-down el-icon--right"></i>
                </el-button>
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item @click.native="duplicateTopic(scope.row)">
                    <i class="el-icon-copy-document"></i> 复制专题
                  </el-dropdown-item>
                  <el-dropdown-item @click.native="exportTopic(scope.row)">
                    <i class="el-icon-download"></i> 导出数据
                  </el-dropdown-item>
                  <el-dropdown-item 
                    @click.native="toggleStatus(scope.row)"
                    :divided="true">
                    <i :class="scope.row.is_active ? 'el-icon-close' : 'el-icon-check'"></i>
                    {{ scope.row.is_active ? '禁用' : '启用' }}
                  </el-dropdown-item>
                  <el-dropdown-item @click.native="deleteTopic(scope.row)">
                    <i class="el-icon-delete" style="color: #f56c6c;"></i> 
                    <span style="color: #f56c6c;">删除</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </el-dropdown>
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

    <!-- 专题结构查看对话框 -->
    <el-dialog 
      :title="currentTopic ? `${currentTopic.title} - 专题结构` : '专题结构'"
      :visible.sync="showStructureDialog"
      width="80%"
      class="structure-dialog">
      <div v-if="currentTopic">
        <div class="structure-overview">
          <el-card>
            <div slot="header">
              <span>结构概览</span>
            </div>
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="overview-item">
                  <div class="overview-number">{{ topicStructure.categories_count }}</div>
                  <div class="overview-label">分类数量</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="overview-item">
                  <div class="overview-number">{{ topicStructure.papers_count }}</div>
                  <div class="overview-label">试卷数量</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="overview-item">
                  <div class="overview-number">{{ topicStructure.questions_count }}</div>
                  <div class="overview-label">题目数量</div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </div>

        <div class="structure-tree" style="margin-top: 20px;">
          <el-card>
            <div slot="header">
              <span>层级结构</span>
            </div>
            <div class="tree-container">
              <div class="tree-node root-node">
                <div class="node-content">
                  <i class="el-icon-folder-opened"></i>
                  <span class="node-title">{{ currentTopic.title }}</span>
                  <el-tag size="mini">专题</el-tag>
                </div>
                
                <div class="children-nodes" v-if="topicStructure.categories && topicStructure.categories.length > 0">
                  <div 
                    v-for="category in topicStructure.categories" 
                    :key="category.id"
                    class="tree-node category-node">
                    <div class="node-content">
                      <i class="el-icon-folder"></i>
                      <span class="node-title">{{ category.name }}</span>
                      <el-tag size="mini" type="primary">分类</el-tag>
                      <span class="node-stats">{{ (category.papers && category.papers.length) || 0 }} 试卷</span>
                    </div>
                    
                    <div class="children-nodes" v-if="category.papers && category.papers.length > 0">
                      <div 
                        v-for="paper in category.papers" 
                        :key="paper.id"
                        class="tree-node paper-node">
                        <div class="node-content">
                          <i class="el-icon-document"></i>
                          <span class="node-title">{{ paper.title }}</span>
                          <el-tag size="mini" type="success">试卷</el-tag>
                          <span class="node-stats">{{ paper.question_count }} 题</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div v-else class="empty-categories">
                  <p>暂无分类</p>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import api from '@admin/api'

export default {
  name: 'TopicManagement',
  data () {
    return {
      loading: false,
      topics: [],
      selectedTopics: [],
      
      // 搜索表单
      searchForm: {
        keyword: '',
        difficulty: null,
        status: null,
        visibility: null
      },
      
      // 分页
      pagination: {
        page: 1,
        pageSize: 20,
        total: 0
      },

      // 专题结构查看
      showStructureDialog: false,
      currentTopic: null,
      topicStructure: {}
    }
  },

  created () {
    console.log('TopicManagement component created')
    console.log('API object:', api)
    this.loadTopics()
  },

  methods: {
    async loadTopics () {
      this.loading = true
      try {
        // 检查API方法是否存在
        if (!api.getTopicsManage) {
          console.error('API method getTopicsManage not found')
          this.$message.error('未找到专题管理API方法，请检查后端接口配置')
          return
        }
        
        const params = {
          page: this.pagination.page,
          page_size: this.pagination.pageSize,
          keyword: this.searchForm.keyword,
          difficulty: this.searchForm.difficulty,
          is_active: this.searchForm.status,
          is_public: this.searchForm.visibility
        }
        
        console.log('Loading topics with params:', params)
        const res = await api.getTopicsManage(params)
        console.log('API response:', res)
        
        if (res && res.data && res.data.data) {
          const data = res.data.data
          this.topics = data.results || []
          this.pagination.total = data.total || 0
        } else {
          console.error('Invalid API response structure:', res)
          this.topics = []
          this.pagination.total = 0
          this.$message.warning('服务器返回的数据格式不正确')
        }
      } catch (err) {
        console.error('Failed to load topics:', err)
        
        // 更详细的错误处理
        let errorMessage = '加载专题列表失败'
        if (err.isAuthError) {
          errorMessage = '用户未登录或权限不足'
        } else if (err.response) {
          if (err.response.status === 404) {
            errorMessage = '专题管理API接口不存在，请检查后端服务配置'
          } else if (err.response.data && err.response.data.error) {
            errorMessage += ': ' + err.response.data.error
          } else {
            errorMessage += ': HTTP ' + err.response.status
          }
        } else if (err.message) {
          errorMessage += ': ' + err.message
        }
        
        this.$message.error(errorMessage)
        this.topics = []
        this.pagination.total = 0
      } finally {
        this.loading = false
      }
    },

    // 搜索相关
    searchTopics () {
      this.pagination.page = 1
      this.loadTopics()
    },

    resetSearch () {
      this.searchForm = {
        keyword: '',
        difficulty: null,
        status: null,
        visibility: null
      }
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

    // 选择相关
    handleSelectionChange (selection) {
      this.selectedTopics = selection
    },

    // 操作相关
    createTopic () {
      this.$router.push('/topic/create')
    },

    editTopic (topic) {
      this.$router.push(`/topic/edit/${topic.id}`)
    },

    async viewStructure (topic) {
      this.currentTopic = topic
      this.showStructureDialog = true
      await this.loadTopicStructure(topic.id)
    },

    async loadTopicStructure (topicId) {
      try {
        const res = await api.getTopicStructure(topicId)
        this.topicStructure = res.data.data
      } catch (err) {
        console.error('加载专题结构失败:', err)
        this.topicStructure = {
          categories_count: 0,
          papers_count: 0,
          questions_count: 0,
          categories: []
        }
      }
    },

    viewStatistics (topic) {
      this.$router.push(`/topic/statistics/${topic.id}`)
    },

    async toggleStatus (topic) {
      try {
        await api.updateTopic(topic.id, {
          is_active: !topic.is_active
        })
        this.$message.success(`专题已${topic.is_active ? '禁用' : '启用'}`)
        this.loadTopics()
      } catch (err) {
        this.$message.error('操作失败: ' + (err.response && err.response.data && err.response.data.error || err.message))
      }
    },

    async deleteTopic (topic) {
      try {
        await this.$confirm(`确定要删除专题"${topic.title}"吗？删除后将无法恢复。`, '确认删除', {
          type: 'warning',
          confirmButtonText: '删除',
          confirmButtonClass: 'el-button--danger'
        })
        
        await api.deleteTopic(topic.id)
        this.$message.success('专题删除成功')
        this.loadTopics()
      } catch (err) {
        if (err !== 'cancel') {
          this.$message.error('删除失败: ' + (err.response && err.response.data && err.response.data.error || err.message))
        }
      }
    },

    async duplicateTopic (topic) {
      try {
        await this.$confirm(`确定要复制专题"${topic.title}"吗？`, '确认复制', {
          type: 'info'
        })
        
        await api.duplicateTopic(topic.id)
        this.$message.success('专题复制成功')
        this.loadTopics()
      } catch (err) {
        if (err !== 'cancel') {
          this.$message.error('复制失败: ' + (err.response && err.response.data && err.response.data.error || err.message))
        }
      }
    },

    async exportTopic (topic) {
      try {
        const res = await api.exportTopic(topic.id)
        // 处理文件下载
        const blob = new Blob([res.data], { type: 'application/json' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${topic.title}_export.json`
        link.click()
        window.URL.revokeObjectURL(url)
        
        this.$message.success('导出成功')
      } catch (err) {
        this.$message.error('导出失败: ' + (err.response && err.response.data && err.response.data.error || err.message))
      }
    },

    // 批量操作
    async batchEnable () {
      await this.batchOperation('enable', '启用')
    },

    async batchDisable () {
      await this.batchOperation('disable', '禁用')
    },

    async batchDelete () {
      await this.batchOperation('delete', '删除', true)
    },

    async batchOperation (action, actionName, needConfirm = false) {
      if (this.selectedTopics.length === 0) {
        this.$message.warning('请选择要操作的专题')
        return
      }

      try {
        if (needConfirm) {
          await this.$confirm(`确定要${actionName} ${this.selectedTopics.length} 个专题吗？`, '确认操作', {
            type: 'warning'
          })
        }

        const topicIds = this.selectedTopics.map(t => t.id)
        await api.batchOperateTopics({
          action: action,
          topic_ids: topicIds
        })

        this.$message.success(`批量${actionName}成功`)
        this.loadTopics()
        this.selectedTopics = []
      } catch (err) {
        if (err !== 'cancel') {
          this.$message.error(`批量${actionName}失败: ` + (err.response && err.response.data && err.response.data.error || err.message))
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
.topic-management-list {
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
    .batch-actions {
      padding: 10px;
      background-color: #f5f7fa;
      border-radius: 4px;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 10px;
    }

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

.structure-dialog {
  .structure-overview {
    .overview-item {
      text-align: center;
      
      .overview-number {
        font-size: 32px;
        font-weight: 600;
        color: #409eff;
        margin-bottom: 8px;
      }
      
      .overview-label {
        color: #606266;
        font-size: 14px;
      }
    }
  }

  .structure-tree {
    .tree-container {
      .tree-node {
        margin-bottom: 12px;
        
        .node-content {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 12px;
          border-radius: 4px;
          
          .node-title {
            font-weight: 500;
          }
          
          .node-stats {
            margin-left: auto;
            font-size: 12px;
            color: #909399;
          }
        }
        
        &.root-node > .node-content {
          background-color: #e3f2fd;
          border-left: 4px solid #2196f3;
        }
        
        &.category-node > .node-content {
          background-color: #f3e5f5;
          border-left: 4px solid #9c27b0;
          margin-left: 20px;
        }
        
        &.paper-node > .node-content {
          background-color: #e8f5e8;
          border-left: 4px solid #4caf50;
          margin-left: 40px;
        }
        
        .children-nodes {
          margin-top: 8px;
        }
        
        .empty-categories {
          margin-left: 20px;
          padding: 20px;
          text-align: center;
          color: #909399;
        }
      }
    }
  }
}
</style>
