<template>
  <div class="view">
    <Panel :title="$t('m.Choice_Question_List')">
      <div slot="header">
        <el-row :gutter="20">
          <el-col :span="4">
            <el-button type="primary" size="small" @click="goCreateChoiceQuestion" icon="el-icon-plus">{{$t('m.Create')}}</el-button>
          </el-col>
          <el-col :span="4">
          </el-col>
          <el-col :span="6">
            <el-input v-model="keyword" prefix-icon="el-icon-search" placeholder="Keywords"></el-input>
          </el-col>
          <el-col :span="6">
            <el-button type="primary" size="small" @click="filterByKeyword">{{$t('m.Search')}}</el-button>
          </el-col>
        </el-row>
      </div>
      <!-- 批量操作工具栏 -->
      <div v-if="selectedQuestions.length > 0" class="batch-toolbar">
        <el-alert
          :title="`已选择 ${selectedQuestions.length} 道题目`"
          type="info"
          :closable="false"
          show-icon>
          <div slot="default">
            <el-button-group>
              <el-button size="small" @click="clearSelection">取消选择</el-button>
              <el-button size="small" type="primary" @click="showBatchOperationDialog">批量操作</el-button>
            </el-button-group>
          </div>
        </el-alert>
      </div>
      
      <el-table
        v-loading="loadingTable"
        element-loading-text="loading"
        ref="table"
        :data="choiceQuestionList"
        @selection-change="handleSelectionChange"
        style="width: 100%">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column width="100" prop="id" label="ID"></el-table-column>
        <el-table-column prop="title" label="Title">
          <template slot-scope="{row}">
            <a @click="goEdit(row.id)" class="entry">{{ row.title }}</a>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="Difficulty" width="150">
          <template slot-scope="scope">
            <el-tag :type="scope.row.difficulty === 'Easy' ? 'success' : scope.row.difficulty === 'Medium' ? 'warning' : 'danger'" size="small">
              {{ scope.row.difficulty }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_by.username" label="Author" width="150"></el-table-column>
        <el-table-column prop="create_time" label="Create Time" width="200">
          <template slot-scope="scope">
            {{ scope.row.create_time | localtime }}
          </template>
        </el-table-column>
        <el-table-column prop="visible" label="Visible" width="100">
          <template slot-scope="scope">
            <el-switch v-model="scope.row.visible" @change="updateChoiceQuestion(scope.row)"></el-switch>
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="Operation" width="200">
          <template slot-scope="scope">
            <icon-btn name="Edit" icon="edit" @click.native="goEdit(scope.row.id)"></icon-btn>
            <icon-btn name="Delete" icon="trash" @click.native="deleteChoiceQuestion(scope.row.id)"></icon-btn>
          </template>
        </el-table-column>
      </el-table>
      <div class="panel-options">
        <el-pagination
          class="page"
          layout="prev, pager, next"
          @current-change="currentChange"
          :page-size="pageSize"
          :total="total">
        </el-pagination>
      </div>
    </Panel>
    
    <!-- 导入选择题对话框 -->
    <el-dialog
      :title="$t('m.Import_Choice_Questions')"
      :visible.sync="importDialogVisible"
      width="60%"
      :close-on-click-modal="false">
      <div class="import-container">
        <!-- 编程语言选择 -->
        <div class="language-selection" style="margin-bottom: 20px;">
          <el-row :gutter="20">
            <el-col :span="8">
              <label style="display: block; margin-bottom: 8px; font-weight: bold;">{{$t('m.Programming_Language')}}:</label>
              <el-select v-model="selectedLanguage" :placeholder="$t('m.Select_Programming_Language')" style="width: 100%;">
                <el-option value="text" label="Plain Text"></el-option>
                <el-option value="c" label="C"></el-option>
                <el-option value="cpp" label="C++"></el-option>
                <el-option value="java" label="Java"></el-option>
                <el-option value="python" label="Python"></el-option>
                <el-option value="javascript" label="JavaScript"></el-option>
                <el-option value="go" label="Go"></el-option>
                <el-option value="rust" label="Rust"></el-option>
                <el-option value="php" label="PHP"></el-option>
                <el-option value="csharp" label="C#"></el-option>
                <el-option value="kotlin" label="Kotlin"></el-option>
                <el-option value="swift" label="Swift"></el-option>
                <el-option value="ruby" label="Ruby"></el-option>
                <el-option value="scala" label="Scala"></el-option>
                <el-option value="perl" label="Perl"></el-option>
                <el-option value="lua" label="Lua"></el-option>
                <el-option value="bash" label="Bash"></el-option>
                <el-option value="sql" label="SQL"></el-option>
                <el-option value="html" label="HTML"></el-option>
                <el-option value="css" label="CSS"></el-option>
                <el-option value="xml" label="XML"></el-option>
                <el-option value="json" label="JSON"></el-option>
                <el-option value="yaml" label="YAML"></el-option>
                <el-option value="markdown" label="Markdown"></el-option>
              </el-select>
            </el-col>
            <el-col :span="16">
              <div style="padding-top: 28px; color: #666; font-size: 14px;">
                <i class="el-icon-info"></i>
                {{$t('m.Language_Selection_Help')}}
              </div>
            </el-col>
          </el-row>
        </div>
        
        <el-tabs v-model="activeTab" type="border-card">
          <!-- JSON文件上传 -->
          <el-tab-pane :label="$t('m.Upload_JSON_File')" name="file">
            <div class="upload-section">
              <el-upload
                class="upload-demo"
                drag
                action=""
                :auto-upload="false"
                :on-change="handleFileChange"
                :file-list="fileList"
                accept=".json">
                <i class="el-icon-upload"></i>
                <div class="el-upload__text">{{$t('m.Drop_JSON_File_Here_Or_Click_To_Upload')}}</div>
                <div class="el-upload__tip" slot="tip">{{$t('m.Only_JSON_Files_Are_Supported')}}</div>
              </el-upload>
            </div>
          </el-tab-pane>
          
          <!-- JSON文本输入 -->
          <el-tab-pane :label="$t('m.Paste_JSON_Text')" name="text">
            <div class="json-input-section">
              <el-input
                type="textarea"
                :rows="15"
                v-model="jsonText"
                :placeholder="$t('m.Paste_JSON_Content_Here')"
                class="json-textarea">
              </el-input>
            </div>
          </el-tab-pane>
          
          <!-- JSON格式说明 -->
          <el-tab-pane :label="$t('m.JSON_Format_Guide')" name="guide">
            <div class="format-guide">
              <h4>{{$t('m.JSON_Format_Example')}}</h4>
              <pre class="json-example">{{ jsonFormatExample }}</pre>
              <div class="field-descriptions">
                <h4>{{$t('m.Field_Descriptions')}}</h4>
                <ul>
                  <li><strong>title:</strong> {{$t('m.Question_Title_Required')}}</li>
                  <li><strong>description:</strong> {{$t('m.Question_Description_Optional')}}</li>
                  <li><strong>question_type:</strong> {{$t('m.Question_Type_Single_Or_Multiple')}}</li>
                  <li><strong>options:</strong> {{$t('m.Options_Array_With_Key_And_Text')}}</li>
                  <li><strong>correct_answer:</strong> {{$t('m.Correct_Answer_Format')}}</li>
                  <li><strong>difficulty:</strong> {{$t('m.Difficulty_Easy_Medium_Hard')}}</li>
                  <li><strong>score:</strong> {{$t('m.Question_Score_1_To_100')}}</li>
                  <li><strong>explanation:</strong> {{$t('m.Answer_Explanation_Optional')}}</li>
                  <li><strong>category_name:</strong> {{$t('m.Category_Name_Optional')}}</li>
                  <li><strong>tags:</strong> {{$t('m.Tags_Array_Optional')}}</li>
                </ul>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
        
        <!-- 预览区域 -->
        <div v-if="previewData.length > 0" class="preview-section">
          <h4>{{$t('m.Import_Preview')}} ({{previewData.length}} {{$t('m.Questions')}})</h4>
          <el-table :data="previewData.slice(0, 5)" size="small" max-height="300">
            <el-table-column prop="title" :label="$t('m.Title')" width="200" show-overflow-tooltip></el-table-column>
            <el-table-column prop="question_type" :label="$t('m.Type')" width="80"></el-table-column>
            <el-table-column prop="difficulty" :label="$t('m.Difficulty')" width="80"></el-table-column>
            <el-table-column prop="score" :label="$t('m.Score')" width="60"></el-table-column>
            <el-table-column :label="$t('m.Options')" width="150">
              <template slot-scope="scope">
                {{ scope.row.options ? scope.row.options.length : 0 }} {{$t('m.Options')}}
              </template>
            </el-table-column>
          </el-table>
          <div v-if="previewData.length > 5" class="more-info">
            {{$t('m.And_More_Questions', {count: previewData.length - 5})}}
          </div>
        </div>
        
        <!-- 错误信息 -->
        <div v-if="importErrors.length > 0" class="error-section">
          <h4>{{$t('m.Import_Errors')}}</h4>
          <el-alert
            v-for="(error, index) in importErrors"
            :key="index"
            :title="error"
            type="error"
            :closable="false"
            class="error-item">
          </el-alert>
        </div>
      </div>
      
      <span slot="footer" class="dialog-footer">
        <el-button @click="importDialogVisible = false">{{$t('m.Cancel')}}</el-button>
        <el-button @click="validateJSON" type="primary" :disabled="!canValidate">{{$t('m.Validate')}}</el-button>
        <el-button @click="importQuestions" type="success" :disabled="!canImport" :loading="importing">{{$t('m.Import')}}</el-button>
      </span>
    </el-dialog>
    
    <!-- 批量操作对话框 -->
    <el-dialog
      title="批量操作"
      :visible.sync="batchDialogVisible"
      width="500px"
      :close-on-click-modal="false">
      <div class="batch-operation-content">
        <p>已选择 <strong>{{ selectedQuestions.length }}</strong> 道题目</p>
        <el-form :model="batchForm" label-width="120px">
          <el-form-item label="操作类型：">
            <el-select v-model="batchForm.action" placeholder="请选择操作类型" style="width: 100%;">
              <el-option value="delete" label="删除题目"></el-option>
              <el-option value="set_visible" label="设为可见"></el-option>
              <el-option value="set_hidden" label="设为隐藏"></el-option>
              <el-option value="update_difficulty" label="修改难度"></el-option>
              <el-option value="update_language" label="修改编程语言"></el-option>
            </el-select>
          </el-form-item>
          
          <!-- 难度选择 -->
          <el-form-item v-if="batchForm.action === 'update_difficulty'" label="难度：">
            <el-select v-model="batchForm.difficulty" placeholder="请选择难度" style="width: 100%;">
              <el-option value="Easy" label="简单"></el-option>
              <el-option value="Medium" label="中等"></el-option>
              <el-option value="Hard" label="困难"></el-option>
            </el-select>
          </el-form-item>
          
          <!-- 编程语言选择 -->
          <el-form-item v-if="batchForm.action === 'update_language'" label="编程语言：">
            <el-select v-model="batchForm.language" placeholder="请选择编程语言" style="width: 100%;">
              <el-option value="text" label="Plain Text"></el-option>
              <el-option value="c" label="C"></el-option>
              <el-option value="cpp" label="C++"></el-option>
              <el-option value="java" label="Java"></el-option>
              <el-option value="python" label="Python"></el-option>
              <el-option value="javascript" label="JavaScript"></el-option>
              <el-option value="go" label="Go"></el-option>
              <el-option value="rust" label="Rust"></el-option>
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      
      <span slot="footer" class="dialog-footer">
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="executeBatchOperation" :loading="batchOperating">确认操作</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
  import api from '../../api.js'

  export default {
    name: 'ChoiceQuestionList',
    data () {
      return {
        pageSize: 10,
        total: 0,
        choiceQuestionList: [],
        keyword: '',
        loadingTable: false,
        currentPage: 1,
        // 批量操作相关数据
        selectedQuestions: [],
        batchDialogVisible: false,
        batchOperating: false,
        batchForm: {
          action: '',
          difficulty: '',
          language: ''
        },
        // 导入相关数据
        importDialogVisible: false,
        activeTab: 'file',
        fileList: [],
        jsonText: '',
        previewData: [],
        importErrors: [],
        importing: false,
        selectedLanguage: 'cpp', // 默认选择C++
        jsonFormatExample: `[
  {
    "title": "1+1等于多少？",
    "description": "请选择正确答案",
    "question_type": "single",
    "options": [
      {"key": "A", "text": "1"},
      {"key": "B", "text": "2"},
      {"key": "C", "text": "3"},
      {"key": "D", "text": "4"}
    ],
    "correct_answer": "B",
    "difficulty": "easy",
    "score": 10,
    "explanation": "1+1=2，这是基础数学运算",
    "category_name": "数学",
    "tags": ["基础运算", "数学"]
  }
]`
      }
    },
    mounted () {
      this.getChoiceQuestionList(1)
    },
    computed: {
      canValidate () {
        return (this.activeTab === 'file' && this.fileList.length > 0) || 
               (this.activeTab === 'text' && this.jsonText.trim())
      },
      canImport () {
        return this.previewData.length > 0 && this.importErrors.length === 0
      }
    },
    methods: {
      // 切换页码回调
      currentChange (page) {
        this.currentPage = page
        this.getChoiceQuestionList(page)
      },
      getChoiceQuestionList (page) {
        this.loadingTable = true
        api.getChoiceQuestionList((page - 1) * this.pageSize, this.pageSize, this.keyword).then(res => {
          this.loadingTable = false
          this.total = res.data.data.total
          this.choiceQuestionList = res.data.data.results
        }, res => {
          this.loadingTable = false
        })
      },
      goEdit (choiceQuestionId) {
        this.$router.push({name: 'edit-choice-question', params: {choiceQuestionId}})
      },
      goCreateChoiceQuestion () {
        this.$router.push({name: 'create-choice-question'})
      },

      deleteChoiceQuestion (id) {
        this.$confirm('Sure to delete this choice question? The associated submissions will be deleted as well.', 'Delete Choice Question', {
          type: 'warning'
        }).then(() => {
          api.deleteChoiceQuestion(id).then(() => [
            this.getChoiceQuestionList(this.currentPage)
          ]).catch(() => {
          })
        }, () => {
        })
      },
      filterByKeyword () {
        this.currentPage = 1
        this.getChoiceQuestionList(1)
      },
      updateChoiceQuestion (row) {
        api.editChoiceQuestion(row).then(res => {
          this.$success('Updated successfully')
        }).catch(() => {
        })
      },
      // 导入相关方法
      showImportDialog () {
        this.importDialogVisible = true
        this.resetImportData()
      },
      resetImportData () {
        this.activeTab = 'file'
        this.fileList = []
        this.jsonText = ''
        this.previewData = []
        this.importErrors = []
        this.importing = false
      },
      handleFileChange (file, fileList) {
        this.fileList = fileList
        if (file.raw) {
          const reader = new FileReader()
          reader.onload = (e) => {
            this.jsonText = e.target.result
          }
          reader.readAsText(file.raw)
        }
      },
      validateJSON () {
        this.importErrors = []
        this.previewData = []
        
        let jsonData
        try {
          jsonData = JSON.parse(this.jsonText)
        } catch (error) {
          this.importErrors.push(this.$t('m.Invalid_JSON_Format') + ': ' + error.message)
          return
        }
        
        if (!Array.isArray(jsonData)) {
          this.importErrors.push(this.$t('m.JSON_Must_Be_Array'))
          return
        }
        
        // 验证每个题目的格式
        const validatedData = []
        jsonData.forEach((item, index) => {
          const errors = this.validateQuestionItem(item, index + 1)
          if (errors.length > 0) {
            this.importErrors.push(...errors)
          } else {
            validatedData.push(item)
          }
        })
        
        if (this.importErrors.length === 0) {
          this.previewData = validatedData
          this.$message.success(this.$t('m.Validation_Successful', {count: validatedData.length}))
        }
      },
      validateQuestionItem (item, index) {
        const errors = []
        const prefix = `${this.$t('m.Question')} ${index}: `
        
        // 必填字段验证
        if (!item.title || !item.title.trim()) {
          errors.push(prefix + this.$t('m.Title_Is_Required'))
        }
        
        if (!item.question_type || !['single', 'multiple'].includes(item.question_type)) {
          errors.push(prefix + this.$t('m.Question_Type_Must_Be_Single_Or_Multiple'))
        }
        
        if (!item.options || !Array.isArray(item.options) || item.options.length < 2) {
          errors.push(prefix + this.$t('m.At_Least_Two_Options_Required'))
        } else {
          // 验证选项格式
          item.options.forEach((option, optIndex) => {
            if (!option.key || !option.text) {
              errors.push(prefix + this.$t('m.Option_Must_Have_Key_And_Text', {index: optIndex + 1}))
            }
          })
        }
        
        if (!item.correct_answer) {
          errors.push(prefix + this.$t('m.Correct_Answer_Is_Required'))
        }
        
        if (item.difficulty && !['easy', 'medium', 'hard'].includes(item.difficulty)) {
          errors.push(prefix + this.$t('m.Difficulty_Must_Be_Easy_Medium_Or_Hard'))
        }
        
        if (item.score && (item.score < 1 || item.score > 100)) {
          errors.push(prefix + this.$t('m.Score_Must_Be_Between_1_And_100'))
        }
        
        return errors
      },
      async importQuestions () {
        if (!this.canImport) return
        
        this.importing = true
        try {
          // 为每个题目添加选择的编程语言
          const questionsWithLanguage = this.previewData.map(question => ({
            ...question,
            language: this.selectedLanguage
          }))
          
          // 调用后端API进行导入
          const response = await this.$http.post('/api/admin/choice_question/import', {
            questions: questionsWithLanguage
          })
          
          if (response.data.error) {
            throw new Error(response.data.data || this.$t('m.Import_Failed'))
          }
          
          this.$message.success(this.$t('m.Import_Successful', {count: this.previewData.length}))
          this.importDialogVisible = false
          this.getChoiceQuestionList(1) // 刷新列表
        } catch (error) {
          console.error('Import error:', error)
          const errorMessage = (error.response && error.response.data && error.response.data.data) || error.message || this.$t('m.Import_Failed')
          this.$message.error(this.$t('m.Import_Failed') + ': ' + errorMessage)
        } finally {
          this.importing = false
        }
      },
      
      // 批量操作相关方法
      handleSelectionChange (selection) {
        this.selectedQuestions = selection
      },
      
      clearSelection () {
        this.$refs.table.clearSelection()
        this.selectedQuestions = []
      },
      
      showBatchOperationDialog () {
        this.batchDialogVisible = true
        this.batchForm = {
          action: '',
          difficulty: '',
          language: ''
        }
      },
      
      async executeBatchOperation () {
        if (!this.batchForm.action) {
          this.$message.warning('请选择操作类型')
          return
        }
        
        if (this.selectedQuestions.length === 0) {
          this.$message.warning('请选择要操作的题目')
          return
        }
        
        // 构建请求参数
        const questionIds = this.selectedQuestions.map(q => q.id)
        let requestData = {
          action: this.batchForm.action,
          question_ids: questionIds
        }
        
        // 根据操作类型添加额外参数
        if (this.batchForm.action === 'update_difficulty') {
          if (!this.batchForm.difficulty) {
            this.$message.warning('请选择难度')
            return
          }
          requestData.params = { difficulty: this.batchForm.difficulty }
        } else if (this.batchForm.action === 'update_language') {
          if (!this.batchForm.language) {
            this.$message.warning('请选择编程语言')
            return
          }
          requestData.params = { language: this.batchForm.language }
        }
        
        // 确认操作
        const actionNames = {
          'delete': '删除',
          'set_visible': '设为可见',
          'set_hidden': '设为隐藏',
          'update_difficulty': '修改难度',
          'update_language': '修改编程语言'
        }
        
        const actionName = actionNames[this.batchForm.action] || this.batchForm.action
        
        try {
          await this.$confirm(`确定要${actionName} ${questionIds.length} 道题目吗？`, '批量操作确认', {
            type: 'warning'
          })
          
          this.batchOperating = true
          
          // 调用批量操作API
          const response = await this.$http.patch('/admin/choice_question/batch_operation', requestData)
          
          if (response.data.error) {
            throw new Error(response.data.data || '批量操作失败')
          }
          
          this.$message.success(`成功${actionName} ${response.data.data.affected_count} 道题目`)
          this.batchDialogVisible = false
          this.clearSelection()
          this.getChoiceQuestionList(this.currentPage) // 刷新列表
          
        } catch (error) {
          if (error !== 'cancel') {
            console.error('=== 批量操作错误详情 ===', {
              error: error,
              response: error.response,
              responseData: error.response && error.response.data,
              message: error.message,
              stack: error.stack
            })
            
            let errorMessage = '批量操作失败'
            
            if (error.response) {
              // HTTP错误响应
              const status = error.response.status
              const responseData = error.response.data
              
              console.error('HTTP错误状态:', status)
              console.error('响应数据:', responseData)
              
              if (status === 404) {
                errorMessage = '批量操作接口未找到 (404)，请检查后端路由配置'
              } else if (status === 403) {
                errorMessage = '权限不足，无法执行批量操作'
              } else if (status === 500) {
                errorMessage = '服务器内部错误，请查看后端日志'
              } else if (responseData) {
                if (responseData.data) {
                  errorMessage = responseData.data
                } else if (responseData.error) {
                  errorMessage = responseData.error
                } else {
                  errorMessage = `HTTP ${status} 错误`
                }
              }
            } else if (error.message) {
              errorMessage = error.message
            }
            
            // 在页面上显示错误
            this.$message.error({
              message: errorMessage,
              duration: 10000, // 显示10秒
              showClose: true
            })
            
            // 在控制台输出详细错误信息
            console.error('批量操作失败:', errorMessage)
          }
        } finally {
          this.batchOperating = false
        }
      }
    }
  }
</script>

<style scoped lang="less">
  .entry {
    color: #495060;
    &:hover {
      color: #2d8cf0;
      border-bottom: 1px solid #2d8cf0;
    }
  }
  
  // 批量操作工具栏样式
  .batch-toolbar {
    margin-bottom: 20px;
    
    .el-alert {
      .el-button-group {
        margin-left: 15px;
      }
    }
  }
  
  // 批量操作对话框样式
  .batch-operation-content {
    p {
      margin-bottom: 20px;
      font-size: 14px;
      color: #606266;
    }
  }
  
  // 导入对话框样式
  .import-container {
    .upload-section {
      padding: 20px;
      text-align: center;
    }
    
    .json-input-section {
      padding: 20px;
      
      .json-textarea {
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 12px;
      }
    }
    
    .format-guide {
      padding: 20px;
      
      .json-example {
        background: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 15px;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 12px;
        overflow-x: auto;
        white-space: pre;
      }
      
      .field-descriptions {
        margin-top: 20px;
        
        ul {
          list-style-type: disc;
          padding-left: 20px;
          
          li {
            margin-bottom: 8px;
            line-height: 1.5;
          }
        }
      }
    }
    
    .preview-section {
      margin-top: 20px;
      padding: 15px;
      background: #f9f9f9;
      border-radius: 4px;
      
      h4 {
        margin-bottom: 15px;
        color: #333;
      }
      
      .more-info {
        margin-top: 10px;
        color: #666;
        font-size: 14px;
        text-align: center;
      }
    }
    
    .error-section {
      margin-top: 20px;
      
      h4 {
        margin-bottom: 15px;
        color: #f56c6c;
      }
      
      .error-item {
        margin-bottom: 10px;
      }
    }
  }
</style>