<template>
  <div class="view">
    <Panel title="导入选择题">
      <div class="import-container">
        <!-- 分类选择 -->
        <el-row style="margin-bottom: 20px;">
          <el-col :span="24">
            <el-card shadow="hover">
              <div slot="header">
                <i class="el-icon-folder"></i>
                <span>选择分类</span>
              </div>
              <div class="card-content">
                <el-select 
                  v-model="selectedCategory" 
                  placeholder="请选择题目分类（可选）" 
                  clearable 
                  style="width: 100%;"
                >
                  <el-option
                    v-for="category in categories"
                    :key="category.id"
                    :label="getCategoryDisplayName(category)"
                    :value="category.id"
                  >
                  </el-option>
                </el-select>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 导入方式选择 -->
        <el-tabs v-model="activeTab" @tab-click="handleTabClick">
          <!-- JSON文件上传 -->
          <el-tab-pane label="上传JSON文件" name="file">
            <div class="upload-section">
              <el-upload
                class="upload-demo"
                drag
                :action="''"
                :auto-upload="false"
                :on-change="handleFileChange"
                :file-list="fileList"
                accept=".json">
                <i class="el-icon-upload"></i>
                <div class="el-upload__text">点击或拖拽文件到此处上传</div>
                <div class="el-upload__tip" slot="tip">只能上传JSON文件</div>
              </el-upload>
            </div>
          </el-tab-pane>

          <!-- JSON文本输入 -->
          <el-tab-pane label="JSON文本输入" name="text">
            <div class="json-input-section">
              <el-input
                type="textarea"
                :rows="15"
                placeholder="在此粘贴JSON内容"
                v-model="jsonText"
                class="json-textarea">
              </el-input>
            </div>
          </el-tab-pane>

          <!-- 格式说明 -->
          <el-tab-pane label="格式说明" name="guide">
            <div class="format-guide">
              <h4>JSON格式示例</h4>
              <div class="json-example">{{ JSON.stringify(formatGuide.example, null, 2) }}</div>
              
              <div class="field-descriptions">
                <h4>字段说明</h4>
                <ul>
                  <li><strong>id</strong>: 题目ID（可选，导入时会自动生成）</li>
                  <li><strong>type</strong>: 题型，"single"（单选）或"multiple"（多选）</li>
                  <li><strong>question</strong>: 题目描述，支持HTML格式</li>
                  <li><strong>options</strong>: 选项数组，每个选项为字符串</li>
                  <li><strong>correct</strong>: 正确答案，单选为字母（如"A"），多选为字母数组（如["A","B"]）</li>
                  <li><strong>explanation</strong>: 答案解释（可选）</li>
                </ul>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>

        <!-- 预览区域 -->
        <div v-if="previewData.length > 0" class="preview-section">
          <h4>导入预览</h4>
          <p>将导入 {{ previewData.length }} 道题目到分类：{{ getCategoryName(selectedCategory) }}</p>
          <el-table :data="previewData.slice(0, 5)" style="width: 100%" size="small">
            <el-table-column prop="title" label="标题" width="200" show-overflow-tooltip></el-table-column>
            <el-table-column prop="question_type" label="题型" width="80">
              <template slot-scope="scope">
                {{ scope.row.question_type === 0 ? '单选' : '多选' }}
              </template>
            </el-table-column>
            <el-table-column prop="options" label="选项数量" width="80">
              <template slot-scope="scope">
                {{ scope.row.options.length }}
              </template>
            </el-table-column>
            <el-table-column prop="difficulty" label="难度" width="80"></el-table-column>
            <el-table-column prop="score" label="分数" width="80"></el-table-column>
          </el-table>
          <div v-if="previewData.length > 5" class="more-info">
            还有 {{ previewData.length - 5 }} 道题目...
          </div>
        </div>

        <!-- 错误信息 -->
        <div v-if="importErrors.length > 0" class="error-section">
          <h4>导入错误</h4>
          <el-alert
            v-for="(error, index) in importErrors"
            :key="index"
            :title="error"
            type="error"
            class="error-item"
            show-icon>
          </el-alert>
        </div>

        <!-- 操作按钮 -->
        <div style="margin-top: 20px; text-align: center;">
          <el-button @click="goBack">返回</el-button>
          <el-button 
            type="primary" 
            @click="validateJSON" 
            :disabled="!canValidate">
            验证JSON
          </el-button>
          <el-button 
            type="success" 
            @click="importQuestions" 
            :disabled="!canImport"
            :loading="importing">
            {{ importing ? '导入中...' : '导入' }}
          </el-button>
        </div>
      </div>
    </Panel>
  </div>
</template>

<script>
import api from '../../api.js'

export default {
  name: 'ImportChoiceQuestion',
  data() {
    return {
      activeTab: 'file',
      fileList: [],
      jsonText: '',
      previewData: [],
      importErrors: [],
      importing: false,
      selectedCategory: null,
      categories: [],
      selectedCategoryId: null,

      formatGuide: {
        example: [
          {
            "id": "GESP_2_2024_3_1",
            "type": "single",
            "question": "下列关于C++语言变量的叙述，正确的是( )。",
            "options": [
              "A. 变量可以没有定义",
              "B. 对一个没有定义的变量赋值，相当于定义了一个新变量", 
              "C. 执行赋值语句后，变量的类型可能会变化",
              "D. 执行赋值语句后，变量的值可能不会变化"
            ],
            "correct": "D",
            "explanation": "变量需先定义后使用（排除A、B），赋值不改变类型（排除C）。若赋值前后值相同，值不变（如a=5; a=5;），故D正确。"
          }
        ],
        fields: [
          { name: 'id', desc: '题目ID（可选）', required: false },
          { name: 'question', desc: '题目内容', required: true },
          { name: 'type', desc: '题目类型 (single/multiple)', required: true },
          { name: 'options', desc: '选项数组', required: true },
          { name: 'correct', desc: '正确答案', required: true },
          { name: 'explanation', desc: '题目解析（可选）', required: false }
        ]
      }
    }
  },
  computed: {
    canValidate() {
      if (this.activeTab === 'file') {
        return this.fileList.length > 0
      } else if (this.activeTab === 'text') {
        return this.jsonText.trim() !== ''
      }
      return false
    },
    canImport() {
      return this.previewData.length > 0 && this.importErrors.length === 0
    }
  },
  mounted() {
    this.getCategories()
  },
  methods: {
    async getCategories() {
       try {
         const res = await api.getChoiceQuestionCategories()
         this.categories = res.data.data || []
       } catch (err) {
         this.$error('获取分类失败')
       }
     },
    getCategoryName(categoryId) {
      const category = this.categories.find(c => c.id === categoryId)
      return category ? this.getCategoryDisplayName(category) : ''
    },
    getCategoryDisplayName(category) {
      if (!category) return ''
      
      // 如果有父分类，显示 "父分类 > 子分类" 的格式
      if (category.parent) {
        const parentCategory = this.categories.find(c => c.id === category.parent)
        if (parentCategory) {
          return `${parentCategory.name} > ${category.name}`
        }
      }
      
      return category.name
    },
    handleTabClick() {
      this.resetImportState()
    },
    handleFileChange(file) {
      this.resetImportState()
      const reader = new FileReader()
      reader.onload = (e) => {
        this.jsonText = e.target.result
      }
      reader.readAsText(file.raw)
    },
    resetImportState() {
      this.previewData = []
      this.importErrors = []
    },
    validateJSON() {
      this.resetImportState()
      
      try {
        const data = JSON.parse(this.jsonText)
        
        let questionsArray = []
        let categoryId = null
        
        // 支持两种格式：数组格式和对象格式
        if (Array.isArray(data)) {
          // 数组格式：直接是题目数组
          questionsArray = data
        } else if (data && typeof data === 'object') {
          // 对象格式：包含questions数组和category_id
          if (Array.isArray(data.questions)) {
            questionsArray = data.questions
            categoryId = data.category_id
          } else {
            this.importErrors.push('JSON数据格式错误：对象格式必须包含questions数组')
            return
          }
        } else {
          this.importErrors.push('JSON数据必须是数组格式或包含questions数组的对象格式')
          return
        }
        
        // 如果JSON中指定了分类，自动选择该分类
        if (categoryId && this.categories.length > 0) {
          const category = this.categories.find(cat => cat.id === categoryId)
          if (category) {
            this.selectedCategory = categoryId
          }
        }
        
        const validatedData = []
        questionsArray.forEach((item, index) => {
          const errors = this.validateQuestionItem(item, index)
          if (errors.length === 0) {
            // 转换为系统格式
            const convertedItem = this.convertToSystemFormat(item)
            validatedData.push(convertedItem)
          } else {
            this.importErrors.push(...errors)
          }
        })
        
        this.previewData = validatedData
        
        if (this.importErrors.length === 0) {
          if (!this.selectedCategory) {
            this.$success(`JSON验证成功！共 ${validatedData.length} 道题目。请选择分类后即可导入。`)
          } else {
            this.$success(`验证成功！共 ${validatedData.length} 道题目`)
          }
        }
      } catch (error) {
        this.importErrors.push('JSON格式错误：' + error.message)
      }
    },
    validateQuestionItem(item, index) {
      const errors = []
      
      // 验证必填字段
      if (!item.question || typeof item.question !== 'string') {
        errors.push(`第${index + 1}题: question字段必填且必须为字符串`)
      }
      
      if (!item.type || !['single', 'multiple'].includes(item.type)) {
        errors.push(`第${index + 1}题: type字段必须为'single'或'multiple'`)
      }
      
      if (!Array.isArray(item.options) || item.options.length === 0) {
        errors.push(`第${index + 1}题: options字段必须为非空数组`)
      }
      
      if (!item.correct || typeof item.correct !== 'string') {
        errors.push(`第${index + 1}题: correct字段必填且必须为字符串`)
      }
      
      return errors
    },
    convertToSystemFormat(item) {
      // 从question字段提取标题（前50个字符）
      const tempDiv = document.createElement('div')
      tempDiv.innerHTML = item.question
      const plainText = tempDiv.textContent || tempDiv.innerText || ''
      const title = plainText.trim().substring(0, 50) + (plainText.length > 50 ? '...' : '')
      
      return {
        title: title,
        description: item.question,
        question_type: item.type === 'single' ? 0 : 1, // 0-单选，1-多选
        difficulty: 'Mid', // 默认中等难度
        score: 2, // 默认2分
        options: item.options.map((option, index) => {
          const optionLetter = String.fromCharCode(65 + index) // A, B, C, D...
          return {
            content: option,
            is_correct: item.type === 'single' 
              ? item.correct === optionLetter
              : item.correct.includes(optionLetter)
          }
        }),
        categories: this.selectedCategory ? [this.selectedCategory] : [],
        tags: [],
        explanation: item.explanation || '' // 添加解析字段
      }
    },
    async importQuestions() {
      if (!this.selectedCategory) {
        this.$error('请先选择分类')
        return
      }
      
      if (!this.canImport) return
      
      this.importing = true
      try {
        const importData = {
          questions: this.previewData,
          category_id: this.selectedCategory
        }
        
        // 添加调试信息
        console.log('=== 导入调试信息 ===')
        console.log('发送的数据:', JSON.stringify(importData, null, 2))
        console.log('预览数据长度:', this.previewData.length)
        console.log('选择的分类ID:', this.selectedCategory)
        
        const res = await this.$http.post('/plugin/choice/questions/import/', importData)
        
        console.log('服务器响应:', res)
        console.log('响应状态:', res.status)
        console.log('响应数据:', JSON.stringify(res.data, null, 2))
        
        const result = res.data.data
        
        if (result && result.success_count > 0) {
          this.$success(`成功导入 ${result.success_count} 道题目`)
          
          if (result.error_list && result.error_list.length > 0) {
            let errorMsg = '部分题目导入失败：\n'
            result.error_list.forEach(error => {
              errorMsg += `第${error.index}题: ${JSON.stringify(error.errors)}\n`
            })
            this.$error(errorMsg)
          }
          
          // 重置表单状态
          this.resetImportState()
          this.jsonText = ''
          this.selectedCategory = null
          
        } else {
          console.error('导入失败，服务器返回:', result)
          this.$error('导入失败，请检查数据格式。详细信息请查看浏览器控制台。')
        }
        
        // 移除自动跳转，让用户留在当前页面
        // this.$router.push({ name: 'choice-question-list' })
        
      } catch (err) {
        console.error('=== 导入错误详情 ===')
        console.error('错误对象:', err)
        console.error('错误消息:', err.message)
        
        if (err.response) {
          console.error('响应状态:', err.response.status)
          console.error('响应头:', err.response.headers)
          console.error('响应数据:', err.response.data)
          
          let errorMsg = '导入失败: '
          if (err.response.data) {
            if (err.response.data.data) {
              errorMsg += err.response.data.data
            } else if (err.response.data.error) {
              errorMsg += err.response.data.error
            } else if (err.response.data.message) {
              errorMsg += err.response.data.message
            } else {
              errorMsg += JSON.stringify(err.response.data)
            }
          } else {
            errorMsg += `HTTP ${err.response.status} 错误`
          }
          
          this.$error(errorMsg + '。详细信息请查看浏览器控制台。')
        } else {
          this.$error('网络错误: ' + err.message + '。详细信息请查看浏览器控制台。')
        }
      } finally {
        this.importing = false
      }
    },
    simulateImport() {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve()
        }, 2000)
      })
    },
    goBack() {
      this.$router.push({ name: 'choice-question-list' })
    }
  }
}
</script>

<style scoped lang="less">
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