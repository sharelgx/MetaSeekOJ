<template>
  <div class="view">
    <Panel title="试卷管理">
      <div slot="header">
        <el-button 
          type="primary" 
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
            <el-select 
              v-model="filterForm.categoryId" 
              @change="loadPapers" 
              clearable 
              placeholder="选择分类"
              style="width: 150px;"
            >
              <el-option label="全部分类" value=""></el-option>
              <el-option 
                v-for="category in categories" 
                :key="category.id" 
                :label="category.name" 
                :value="category.id"
              >
              </el-option>
            </el-select>
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
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- 试卷列表 -->
      <el-table 
        :data="papers" 
        :loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        
        <el-table-column prop="title" label="试卷标题" min-width="200">
          <template slot-scope="scope">
            <el-link type="primary" @click="viewPaper(scope.row)">
              {{ scope.row.title }}
            </el-link>
          </template>
        </el-table-column>
        
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip>
          <template slot-scope="scope">
            {{ scope.row.description || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="category" label="分类" width="120">
          <template slot-scope="scope">
            {{ scope.row.category ? scope.row.category.name : '-' }}
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
        
        <el-table-column label="操作" width="200" align="center">
          <template slot-scope="scope">
            <el-button 
              type="primary" 
              size="mini" 
              @click="viewPaper(scope.row)"
            >
              查看
            </el-button>
            <el-button 
              type="success" 
              size="mini" 
              @click="startExam(scope.row)"
            >
              开始考试
            </el-button>
            <el-button 
              type="danger" 
              size="mini" 
              @click="deletePaper(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
        >
        </el-pagination>
      </div>
    </Panel>
    
    <!-- 试卷详情对话框 -->
    <el-dialog
      title="试卷详情"
      :visible.sync="detailDialogVisible"
      width="60%"
      :close-on-click-modal="false"
    >
      <div v-if="selectedPaper">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="试卷标题">{{ selectedPaper.title }}</el-descriptions-item>
          <el-descriptions-item label="试卷类型">
            <el-tag :type="selectedPaper.paper_type === 'fixed' ? 'success' : 'info'" size="small">
              {{ selectedPaper.paper_type === 'fixed' ? '固定题目' : '动态生成' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="分类">{{ selectedPaper.category ? selectedPaper.category.name : '-' }}</el-descriptions-item>
          <el-descriptions-item label="题目数量">{{ selectedPaper.question_count }}题</el-descriptions-item>
          <el-descriptions-item label="考试时长">{{ selectedPaper.duration }}分钟</el-descriptions-item>
          <el-descriptions-item label="总分">{{ selectedPaper.total_score }}分</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ formatDate(selectedPaper.create_time) }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ selectedPaper.description || '-' }}</el-descriptions-item>
        </el-descriptions>
        
        <!-- 标签 -->
        <div v-if="selectedPaper.tags && selectedPaper.tags.length > 0" style="margin-top: 20px;">
          <h4>标签：</h4>
          <el-tag 
            v-for="tag in selectedPaper.tags" 
            :key="tag.id" 
            style="margin-right: 8px; margin-bottom: 8px;"
            :color="tag.color"
          >
            {{ tag.name }}
          </el-tag>
        </div>
        
        <!-- 题目列表（仅固定题目类型显示） -->
        <div v-if="selectedPaper.paper_type === 'fixed' && selectedPaper.questions && selectedPaper.questions.length > 0" style="margin-top: 20px;">
          <h4>题目列表：</h4>
          <el-table :data="selectedPaper.questions" size="small" max-height="300">
            <el-table-column prop="order" label="序号" width="60" align="center"></el-table-column>
            <el-table-column prop="question.title" label="题目" min-width="200" show-overflow-tooltip></el-table-column>
            <el-table-column prop="question.question_type" label="类型" width="80" align="center">
              <template slot-scope="scope">
                {{ scope.row.question.question_type === 'single' ? '单选' : '多选' }}
              </template>
            </el-table-column>
            <el-table-column prop="score" label="分值" width="60" align="center"></el-table-column>
          </el-table>
        </div>
      </div>
      
      <span slot="footer" class="dialog-footer">
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="startExam(selectedPaper)">开始考试</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import api from '@/pages/oj/api'

export default {
  name: 'ExamPaperList',
  data() {
    return {
      loading: false,
      papers: [],
      categories: [],
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
      
      // 对话框
      detailDialogVisible: false,
      selectedPaper: null
    }
  },
  
  mounted() {
    this.init()
  },
  
  methods: {
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
        this.$message.error('获取试卷列表失败')
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
    
    viewPaper(paper) {
      this.selectedPaper = paper
      this.detailDialogVisible = true
    },
    
    startExam(paper) {
      // 跳转到考试页面
      const routeData = this.$router.resolve({
        name: 'exam-paper',
        params: { paperId: paper.id }
      })
      window.open(routeData.href, '_blank')
    },
    
    async deletePaper(paper) {
      try {
        await this.$confirm(`确定要删除试卷「${paper.title}」吗？`, '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        // 调用删除API
        await api.deleteExamPaper(paper.id)
        this.$message.success('删除成功')
        
        // 重新加载列表
        await this.loadPapers()
        
      } catch (err) {
        if (err !== 'cancel') {
          console.error('删除试卷失败:', err)
          this.$message.error('删除失败')
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
</style>