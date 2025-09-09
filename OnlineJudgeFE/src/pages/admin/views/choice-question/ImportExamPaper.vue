<template>
  <div class="view">
    <Panel title="导入试卷">
      <div class="import-container">
        <!-- 选择器区域 -->
        <div class="selector-section">
          <el-row :gutter="20">
            <!-- 分类选择 -->
            <el-col :span="8">
              <div class="form-group">
                <label class="form-label">
                  <i class="el-icon-folder"></i>
                  选择分类 *
                </label>
                <div class="category-selector-wrapper">
                  <div 
                    class="category-display" 
                    @click="toggleCategoryDropdown"
                    :class="{ 'active': showCategoryDropdown }"
                  >
                    <span class="selected-text">
                      {{ selectedCategoryName || '请选择分类' }}
                    </span>
                    <i class="el-icon-arrow-down" :class="{ 'rotate': showCategoryDropdown }"></i>
                  </div>
                  
                  <div v-if="showCategoryDropdown" class="category-dropdown">
                    <ul class="category-list">
                      <li 
                        v-for="category in flattenedCategories" 
                        :key="category.id"
                        class="category-item"
                        :class="{ 
                           'selected': selectedCategory === category.id,
                           ['level-' + category.level]: true 
                         }"
                        @click="selectCategory(category)"
                      >
                        <span class="category-indent" v-for="n in category.level" :key="n"></span>
                        <i class="el-icon-folder category-icon"></i>
                        <span class="category-name">{{ category.name }}</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </el-col>
            
            <!-- 编程语言选择 -->
            <el-col :span="8">
              <div class="form-group">
                <label class="form-label">
                  <i class="el-icon-cpu"></i>
                  编程语言
                </label>
                <el-select
                  v-model="selectedLanguage"
                  placeholder="请选择编程语言"
                  style="width: 100%"
                  clearable
                >
                  <el-option
                    v-for="lang in languageOptions"
                    :key="lang.value"
                    :label="lang.label"
                    :value="lang.value"
                  >
                  </el-option>
                </el-select>
              </div>
            </el-col>
            
            <!-- 导入选项 -->
            <el-col :span="8">
              <div class="form-group">
                <label class="form-label">
                  <i class="el-icon-sort"></i>
                  导入选项
                </label>
                <div class="import-options">
                  <el-checkbox v-model="useImportOrder">
                    按导入顺序排序题目
                  </el-checkbox>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 试卷标题设置 -->
        <div class="title-section">
          <div class="form-group">
            <label class="form-label">
              <i class="el-icon-document"></i>
              试卷标题 *
            </label>
            <el-select
              v-model="selectedExistingPaper"
              placeholder="请选择现有试卷标题"
              style="width: 100%"
              filterable
              allow-create
              default-first-option
              @change="onPaperTitleChange"
            >
              <el-option
                v-for="paper in existingPapers"
                :key="paper.id"
                :label="paper.title"
                :value="paper.title"
              >
              </el-option>
            </el-select>
            <div v-if="titleWarning" class="title-warning">
              <i class="el-icon-warning"></i>
              {{ titleWarning }}
            </div>
          </div>
        </div>

        <!-- 导入方式选择 -->
        <el-tabs v-model="activeTab" type="border-card">
          <!-- 文件上传 -->
          <el-tab-pane label="文件上传" name="file">
            <div class="upload-section">
              <el-upload
                class="upload-dragger"
                drag
                :action="uploadUrl"
                :auto-upload="false"
                :file-list="fileList"
                :on-change="handleFileChange"
                :on-remove="handleFileRemove"
                accept=".json"
                :limit="1"
              >
                <i class="el-icon-upload"></i>
                <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
                <div class="el-upload__tip" slot="tip">只能上传JSON文件，且不超过10MB</div>
              </el-upload>
            </div>
          </el-tab-pane>
          
          <!-- JSON文本输入 -->
          <el-tab-pane label="JSON文本" name="text">
            <div class="json-input-section">
              <div class="json-help">
                <p>📝 请粘贴您的JSON格式题目数据，支持以下格式：</p>
                <details class="format-example">
                  <summary>查看JSON格式示例</summary>
                  <pre class="json-example">[{
  "type": "single",
  "question": "以下不属于计算机输入设备的有( )。",
  "options": [
    "A. 键盘",
    "B. 音箱", 
    "C. 鼠标",
    "D. 传感器"
  ],
  "correct": "B",
  "explanation": "音箱属于输出设备"
}]</pre>
                </details>
              </div>
              <el-input
                v-model="jsonText"
                type="textarea"
                :rows="15"
                placeholder="请输入JSON格式的题目数据，或点击上方查看格式示例..."
                class="json-textarea"
              >
              </el-input>
              <div class="json-actions">
                <el-button size="small" type="text" @click="loadJsonExample">📋 加载示例数据</el-button>
                <el-button size="small" type="text" @click="clearJsonText">🗑️ 清空文本</el-button>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>

        <!-- 操作按钮 -->
        <div class="action-section">
          <!-- 状态检查器 -->
          <div class="import-status">
            <h4>📋 导入状态检查</h4>
            <div class="status-items">
              <div class="status-item" :class="{ 'status-success': previewData && previewData.questions && previewData.questions.length > 0 }">
                <i class="el-icon-document"></i>
                <span>数据解析</span>
                <span class="status-value">{{ previewData ? `${previewData.questions ? previewData.questions.length : 0}道题目` : '未解析' }}</span>
              </div>
              <div class="status-item" :class="{ 'status-success': examPaperTitle && examPaperTitle.trim() }">
                <i class="el-icon-edit"></i>
                <span>试卷标题</span>
                <span class="status-value">{{ examPaperTitle && examPaperTitle.trim() ? '已填写' : '请填写' }}</span>
              </div>
              <div class="status-item" :class="{ 'status-success': selectedCategory }">
                <i class="el-icon-folder"></i>
                <span>选择分类</span>
                <span class="status-value">{{ selectedCategory ? '已选择' : '请选择' }}</span>
              </div>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button
              type="primary"
              :disabled="!canParse"
              :loading="parsing"
              @click="parseData"
            >
              解析数据
            </el-button>
            <el-button
              type="success"
              :disabled="!canImport"
              :loading="importing"
              @click="importPaper"
            >
              导入试卷
            </el-button>
            <el-button @click="clearAll">清空</el-button>
          </div>
        </div>

        <!-- 预览区域 -->
        <div v-if="previewData" class="preview-section">
          <h3>📋 数据预览</h3>
          <div class="preview-info">
            <div class="preview-header">
              <p><strong>试卷标题:</strong> {{ previewData.title || '未设置' }}</p>
              <p><strong>题目数量:</strong> {{ previewData.questions ? previewData.questions.length : 0 }}</p>
              <p><strong>总分:</strong> {{ previewData.total_score || 0 }} 分</p>
              <p><strong>包含解析:</strong> {{ previewData.questions ? previewData.questions.filter(q => q.explanation).length : 0 }} 道题目有解析</p>
              <p><strong>题目类型:</strong> {{ getQuestionTypes() }}</p>
              <p><strong>排序方式:</strong> 
                <span :style="{ color: useImportOrder ? '#28a745' : '#6c757d' }">
                  {{ useImportOrder ? '✅ 按导入顺序排序' : '❌ 随机排序' }}
                </span>
              </p>
            </div>
            
            <!-- 题目样例预览 -->
            <div v-if="previewData.questions && previewData.questions.length > 0" class="question-preview">
              <h4>📝 题目样例（前3道）</h4>
              <div 
                v-for="(question, index) in previewData.questions.slice(0, 3)" 
                :key="question.id"
                class="question-item"
              >
                <div class="question-header">
                  <span class="question-number">第{{ index + 1 }}题</span>
                  <span class="question-type">[{{ question.type === 'single' ? '单选' : '多选' }}]</span>
                  <span class="question-score">({{ question.score }}分)</span>
                </div>
                <div class="question-content">{{ question.question }}</div>
                <div class="question-options">
                  <div v-for="(option, optIndex) in question.options" :key="optIndex" class="option-item">
                    {{ option }}
                  </div>
                </div>
                <div class="question-answer">
                  <strong>正确答案:</strong> <span class="correct-answer">{{ question.correct }}</span>
                </div>
                <div v-if="question.explanation" class="question-explanation">
                  <strong>解析:</strong> {{ question.explanation }}
                </div>
              </div>
              
              <div v-if="previewData.questions.length > 3" class="more-questions">
                <p>... 还有 {{ previewData.questions.length - 3 }} 道题目</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Panel>
  </div>
</template>

<script>
import api from '../../api.js'
// import CategorySelector from '../../components/CategorySelector.vue' // 已替换为自定义ul列表
// import { getApiMethod, validateApiCall } from '@/utils/api-mapping'  // 不再使用API映射
// import { createApiProxy } from '@/utils/api-validator'  // 不再使用API验证器

export default {
  name: 'ImportExamPaper',
  // components: {
  //   CategorySelector // 已替换为自定义ul列表
  // },
  data() {
    return {
      // 分类选择
      selectedCategory: null,
      showCategoryDropdown: false,
      categories: [],
      loading: false,
      
      // 编程语言选择
      selectedLanguage: '',
      languageOptions: [
        { value: '', label: '不限制' },
        { value: 'cpp', label: 'C++' },
        { value: 'c', label: 'C' },
        { value: 'java', label: 'Java' },
        { value: 'python', label: 'Python' },
        { value: 'javascript', label: 'JavaScript' }
      ],
      
      // 导入选项
      useImportOrder: true,
      
      // 试卷标题
      examPaperTitle: '',
      // 现有试卷列表
      existingPapers: [],
      selectedExistingPaper: null,
      
      // 导入方式
      activeTab: 'file',
      
      // 文件上传
      fileList: [],
      uploadUrl: '',
      
      // JSON文本
      jsonText: '',
      
      // 预览和导入
      previewData: null,
      parsing: false,
      importing: false,
      
      // 标题验证
      titleWarning: ''
    }
  },
  
  computed: {
    // 扁平化分类数据，支持层级显示
    flattenedCategories() {
      if (!this.categories || this.categories.length === 0) {
        return []
      }
      
      // 递归去重处理
      const globalSeenIds = new Set()
      const deepDeduplication = (cats) => {
        const result = []
        cats.forEach(cat => {
          if (!globalSeenIds.has(cat.id)) {
            globalSeenIds.add(cat.id)
            const cleanCat = { ...cat }
            if (cleanCat.children && cleanCat.children.length > 0) {
              cleanCat.children = deepDeduplication(cleanCat.children)
            }
            result.push(cleanCat)
          }
        })
        return result
      }
      
      const uniqueCategories = deepDeduplication(this.categories)
      
      // 扁平化处理
      const flatten = (categories, level = 0) => {
        let result = []
        const sortedCategories = [...categories].sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
        
        sortedCategories.forEach(category => {
          const flatCategory = {
            ...category,
            level: level,
            displayName: '　'.repeat(level) + category.name
          }
          result.push(flatCategory)
          
          if (category.children && category.children.length > 0) {
            result = result.concat(flatten(category.children, level + 1))
          }
        })
        
        return result
      }
      
      return flatten(uniqueCategories)
    },
    
    // 获取选中分类的名称
    selectedCategoryName() {
      if (!this.selectedCategory) return ''
      const category = this.flattenedCategories.find(cat => cat.id === this.selectedCategory)
      return category ? category.name : ''
    },
    
    canParse() {
      const hasData = (this.activeTab === 'file' && this.fileList.length > 0) || 
                     (this.activeTab === 'text' && this.jsonText.trim())
      console.log('canParse检查:', {
        activeTab: this.activeTab,
        fileCount: this.fileList.length,
        hasJsonText: !!this.jsonText.trim(),
        result: hasData
      })
      return hasData
    },
    
    canImport() {
      const hasPreviewData = this.previewData && this.previewData.questions && this.previewData.questions.length > 0
      const hasCategory = !!this.selectedCategory
      const hasTitle = !!(this.examPaperTitle && this.examPaperTitle.trim())
      
      const result = hasPreviewData && hasCategory && hasTitle
      
      console.log('canImport检查:', {
        hasPreviewData,
        hasCategory,
        hasTitle,
        selectedCategory: this.selectedCategory,
        examPaperTitle: this.examPaperTitle,
        questionsCount: this.previewData ? (this.previewData.questions ? this.previewData.questions.length : 0) : 0,
        result
      })
      
      return result
    }
  },
  
  methods: {
    // 切换分类下拉菜单
    toggleCategoryDropdown() {
      this.showCategoryDropdown = !this.showCategoryDropdown
    },
    
    // 选择分类
    selectCategory(category) {
      this.selectedCategory = category.id
      this.showCategoryDropdown = false
    },
    
    // 加载分类数据
    async loadCategories() {
      if (this.loading) return
      
      this.loading = true
      try {
        const res = await api.getChoiceQuestionCategories()
        this.categories = res.data.data || []
      } catch (error) {
        console.error('加载分类失败:', error)
        this.$message.error('加载分类失败')
      } finally {
        this.loading = false
      }
    },
    
    handleFileChange(file, fileList) {
      this.fileList = fileList
    },
    
    handleFileRemove(file, fileList) {
      this.fileList = fileList
    },
    
    async parseData() {
      this.parsing = true
      try {
        let jsonData = ''
        
        if (this.activeTab === 'file' && this.fileList.length > 0) {
          const file = this.fileList[0].raw
          jsonData = await this.readFileAsText(file)
        } else if (this.activeTab === 'text') {
          jsonData = this.jsonText
        }
        
        if (!jsonData.trim()) {
          this.$message.error('请输入JSON数据')
          return
        }
        
        console.log('开始解析JSON数据:', jsonData.substring(0, 200) + '...')
        const rawData = JSON.parse(jsonData)
        console.log('解析后的原始数据:', rawData)
        
        // 清理特殊字符的函数
        const cleanText = (text) => {
          if (!text) return ''
          // 移除后端不允许的特殊字符：< > " \\
          return String(text).replace(/[<>"\\]/g, '')
        }
        
        // 解析试卷数据结构
        let paperData = {
          title: this.examPaperTitle || '未设置标题',  // 优先使用用户输入的标题
          description: '',
          total_score: 0,
          questions: []
        }
        
        // 处理不同的数据格式
        if (rawData.title && !this.examPaperTitle) {
          // 只有在用户没有输入标题时，才使用JSON中的标题
          this.examPaperTitle = cleanText(rawData.title)
          paperData.title = cleanText(rawData.title)
        }
        
        if (rawData.description) {
          paperData.description = cleanText(rawData.description)
        }
        
        // 处理题目数据 - 支持您的实际JSON格式
        let questions = []
        if (Array.isArray(rawData.questions)) {
          questions = rawData.questions
        } else if (Array.isArray(rawData)) {
          // 如果直接是题目数组（您的格式）
          questions = rawData
        }
        
        console.log('提取到的题目数据:', questions)
        
        // 验证和标准化题目数据（完全支持您的JSON格式）
        const validQuestions = []
        let totalScore = 0
        
        questions.forEach((item, index) => {
          console.log(`处理题目 ${index + 1}:`, item)
          
          // 支持您的实际格式：question, options, correct
          if (item.question && item.options && item.correct) {
            const question = {
              id: item.id || `q_${index + 1}`,
              question: cleanText(item.question), // 清理题目内容
              options: Array.isArray(item.options) ? item.options.map(opt => cleanText(opt)) : [], // 清理所有选项
              correct: item.correct,
              type: item.type || 'single',  // 支持type字段（您的格式）
              explanation: cleanText(item.explanation || ''),  // 清理解析内容
              score: item.score || 2, // 默认2分
              difficulty: item.difficulty || 'easy', // 默认简单
              category_id: item.category_id || null,
              tag_ids: item.tag_ids || [],
              original_order: index + 1 // 保存原始导入顺序
            }
            
            validQuestions.push(question)
            totalScore += question.score
            console.log(`有效题目 ${index + 1} 处理完成:`, question)
          } else {
            console.warn(`题目 ${index + 1} 格式不正确，缺少必需字段:`, {
              hasQuestion: !!item.question,
              hasOptions: !!item.options,
              hasCorrect: !!item.correct
            })
          }
        })
        
        if (validQuestions.length === 0) {
          this.$message.error('没有找到有效的题目数据，请检查JSON格式')
          console.error('未找到有效题目，原始数据:', rawData)
          return
        }
        
        paperData.questions = validQuestions
        paperData.total_score = totalScore
        
        // 确保使用用户输入的标题（最终检查）
        if (this.examPaperTitle && this.examPaperTitle.trim()) {
          paperData.title = cleanText(this.examPaperTitle.trim())
        } else if (!paperData.title || paperData.title === '未设置标题') {
          this.$message.warning('请输入试卷标题')
          paperData.title = '未命名试卷'
        }
        
        this.previewData = paperData
        console.log('最终预览数据:', paperData)
        
        // 显示详细的成功信息
        const successInfo = [
          `找到 ${validQuestions.length} 道题目`,
          `总分 ${totalScore} 分`,
          `包含解析的题目: ${validQuestions.filter(q => q.explanation).length} 道`,
          `题目类型: ${[...new Set(validQuestions.map(q => q.type))].join(', ')}`
        ]
        
        this.$message.success(`数据解析成功！${successInfo.join('，')}`)
        
      } catch (err) {
        console.error('解析失败:', err)
        console.error('原始数据:', jsonData)
        this.$message.error('数据解析失败：' + err.message)
      } finally {
        this.parsing = false
      }
    },
    
    readFileAsText(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = e => resolve(e.target.result)
        reader.onerror = reject
        reader.readAsText(file)
      })
    },
    
    async importPaper() {
      if (!this.canImport) return
      
      this.importing = true
      try {
        // 全面清理特殊字符的函数
        const cleanText = (text) => {
          if (!text) return ''
          // 移除后端不允许的特殊字符：< > " \\
          return String(text).replace(/[<>"\\]/g, '')
        }
        
        // 验证和清理标题
        let cleanTitle = cleanText(this.examPaperTitle.trim())
        
        if (!cleanTitle) {
          this.$message.error('请输入有效的试卷标题')
          return
        }
        
        // 准备试卷导入数据 - 对所有数据进行清理
        const paperData = {
          title: cleanTitle,
          description: cleanText(this.previewData.description || ''),
          questions: this.previewData.questions.map((q, index) => ({
            question: cleanText(q.question),
            options: Array.isArray(q.options) ? q.options.map(opt => cleanText(opt)) : [],
            correct: q.correct, // 保持使用 correct 字段
            type: q.type,
            explanation: cleanText(q.explanation || ''),
            score: q.score,
            difficulty: q.difficulty,
            order: this.useImportOrder ? index + 1 : null // 明确的排序序号
          })),
          category_id: this.selectedCategory,
          language: this.selectedLanguage || 'zh-CN',
          use_import_order: this.useImportOrder,
          duration: this.previewData.duration || 60,
          total_score: this.previewData.total_score
        }
        
        console.log('准备导入的数据（已清理特殊字符）:', paperData)
        console.log('🔢 排序配置:', {
          use_import_order: this.useImportOrder,
          questions_with_order: paperData.questions.map((q, idx) => ({
            index: idx,
            order: q.order,
            title: q.question.substring(0, 30) + '...'
          }))
        })
        
        // 调用试卷导入API
        const response = await api.importExamPaper(paperData)
        console.log('导入响应:', response)
        
        if (response && response.data) {
          if (response.data.error === null) {
            const result = response.data.data
            this.$message.success(`成功导入试卷"${cleanTitle}"，包含 ${paperData.questions.length} 道题目！`)
            this.clearAll()
          } else {
            // 显示详细的错误信息
            let errorMsg = '导入失败：'
            if (typeof response.data.data === 'string') {
              errorMsg += response.data.data
            } else if (Array.isArray(response.data.data)) {
              errorMsg += response.data.data.join('; ')
            } else {
              errorMsg += JSON.stringify(response.data.data)
            }
            this.$message.error(errorMsg)
          }
        }
      } catch (err) {
        console.error('导入失败:', err)
        let errorMsg = '导入失败：'
        if (err.response && err.response.data && err.response.data.data) {
          errorMsg += err.response.data.data
        } else {
          errorMsg += (err.message || '未知错误')
        }
        this.$message.error(errorMsg)
      } finally {
        this.importing = false
      }
    },
    
    clearAll() {
      this.selectedCategory = null
      this.selectedLanguage = ''
      this.useImportOrder = true
      this.examPaperTitle = ''
      this.fileList = []
      this.jsonText = ''
      this.previewData = null
      this.activeTab = 'file'
    },
    
    getQuestionTypes() {
      if (!this.previewData || !this.previewData.questions) {
        return '无'
      }
      
      const types = this.previewData.questions.map(q => q.type || 'single')
      const typeCount = {}
      types.forEach(type => {
        typeCount[type] = (typeCount[type] || 0) + 1
      })
      
      const typeLabels = {
        'single': '单选',
        'multiple': '多选'
      }
      
      return Object.entries(typeCount)
        .map(([type, count]) => `${typeLabels[type] || type}(${count})`)
        .join(', ')
    },
    
    loadJsonExample() {
      const exampleData = `[
  {
    "type": "single",
    "question": "以下不属于计算机输入设备的有( )。",
    "options": [
      "A. 键盘",
      "B. 音箱",
      "C. 鼠标",
      "D. 传感器"
    ],
    "correct": "B",
    "explanation": "输入指外界向机器内部传递信息，输出指计算机内部信息向外界展示。音箱属于向外部播放声音，故属于输出设备。"
  },
  {
    "type": "single",
    "question": "计算机系统中存储的基本单位用B来表示，它代表的是( )。",
    "options": [
      "A. Byte",
      "B. Block",
      "C. Bulk",
      "D. Bit"
    ],
    "correct": "A",
    "explanation": "计算机中，表示存储大小的最小单位为字节，英文为Byte，用大写字母B表示。"
  },
  {
    "type": "single",
    "question": "常量7.0的数据类型是( )。",
    "options": [
      "A. double",
      "B. float",
      "C. void",
      "D. int"
    ],
    "correct": "A",
    "explanation": "C++中基本数据类型有整型int，浮点型double、float等，7.0是小数形式，属于浮点型，C++中浮点型默认是double。"
  }
]`
      this.jsonText = exampleData
      this.$message.success('示例数据已加载，您可以直接点击解析数据按钮进行测试')
    },
    
    clearJsonText() {
      this.jsonText = ''
      this.previewData = null
      this.$message.info('文本已清空')
    },
    
    validateTitle() {
      const invalidChars = /[<>"\\]/
      if (invalidChars.test(this.examPaperTitle)) {
        this.titleWarning = '标题不能包含特殊字符: < > " \\'
        // 自动移除非法字符
        this.examPaperTitle = this.examPaperTitle.replace(/[<>"\\]/g, '')
      } else {
        this.titleWarning = ''
      }
    },
    
    // 处理试卷标题选择变化
    onPaperTitleChange(value) {
      this.examPaperTitle = value
      this.validateTitle()
    },
    
    // 加载现有试卷列表
    async loadExistingPapers() {
      try {
        const response = await api.getExamPaperList({ page: 1, limit: 100 })
        console.log('API响应:', response)
        if (response && response.data) {
          // 根据实际API响应结构调整数据路径
          this.existingPapers = response.data.data || response.data || []
          console.log('加载的试卷列表:', this.existingPapers)
        }
      } catch (error) {
        console.error('加载试卷列表失败:', error)
      }
    }
  },
  
  // 组件挂载时加载数据
  async mounted() {
    await this.loadCategories()
    await this.loadExistingPapers()
  }
}
</script>

<style scoped lang="less">
.view {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.import-container {
  background: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid #ebeef5;
}

.selector-section {
  background: #ffffff;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 20px;
  border: 1px solid #ebeef5;
}

.form-group {
  margin-bottom: 0;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  line-height: 1.4;
}

.form-label i {
  margin-right: 6px;
  color: #409eff;
}

.import-options {
  padding-top: 8px;
}

.upload-section {
  padding: 20px;
}

.json-input-section {
  padding: 20px;
}

.json-help {
  background: #e7f3ff;
  border: 1px solid #b3d7ff;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.json-help p {
  margin: 0 0 10px 0;
  color: #004085;
  font-size: 14px;
}

.format-example {
  cursor: pointer;
}

.format-example summary {
  font-weight: 500;
  color: #0056b3;
  outline: none;
  user-select: none;
}

.format-example summary:hover {
  color: #004085;
}

.json-example {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 15px;
  margin: 10px 0 0 0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #495057;
  overflow-x: auto;
  white-space: pre;
}

.json-textarea {
  font-family: 'Courier New', monospace;
}

.json-actions {
  margin-top: 10px;
  text-align: right;
}

.json-actions .el-button {
  margin-left: 10px;
}

.action-section {
  margin-top: 20px;
}

.import-status {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 20px;
  margin-bottom: 20px;
}

.import-status h4 {
  margin: 0 0 15px 0;
  color: #495057;
  font-size: 16px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 8px;
}

.status-items {
  display: flex;
  justify-content: space-around;
  gap: 20px;
}

.status-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  background: white;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.status-item.status-success {
  border-color: #28a745;
  background: #d4edda;
}

.status-item i {
  font-size: 24px;
  margin-bottom: 8px;
  color: #6c757d;
}

.status-item.status-success i {
  color: #28a745;
}

.status-item span:first-of-type {
  font-weight: 500;
  color: #495057;
  margin-bottom: 5px;
}

.status-value {
  font-size: 12px;
  color: #6c757d;
  background: #e9ecef;
  padding: 2px 8px;
  border-radius: 3px;
}

.status-item.status-success .status-value {
  background: #c3e6cb;
  color: #155724;
}

.action-buttons {
  text-align: center;
}

.action-buttons .el-button {
  margin: 0 10px;
}

.preview-section {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.preview-section h3 {
  margin-top: 0;
  color: #495057;
  border-bottom: 2px solid #007bff;
  padding-bottom: 8px;
}

.preview-header {
  background: white;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid #dee2e6;
}

.preview-header p {
  margin: 8px 0;
  color: #495057;
}

.question-preview {
  background: white;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.question-preview h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #495057;
  font-size: 16px;
}

.question-item {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.question-item:last-child {
  margin-bottom: 0;
}

.question-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  font-size: 14px;
}

.question-number {
  background: #007bff;
  color: white;
  padding: 2px 8px;
  border-radius: 3px;
  font-weight: 500;
  margin-right: 8px;
}

.question-type {
  background: #28a745;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  margin-right: 8px;
}

.question-score {
  background: #ffc107;
  color: #212529;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 500;
}

.question-content {
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 10px;
  color: #212529;
  font-weight: 500;
}

.question-options {
  margin: 10px 0;
}

.option-item {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 3px;
  padding: 6px 10px;
  margin: 4px 0;
  font-size: 13px;
  color: #495057;
}

.question-answer {
  margin: 8px 0;
  font-size: 13px;
}

.correct-answer {
  background: #d4edda;
  color: #155724;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 500;
}

.question-explanation {
  background: #e2e3e5;
  border-left: 4px solid #6c757d;
  padding: 8px 12px;
  margin-top: 10px;
  font-size: 13px;
  font-style: italic;
  color: #495057;
  border-radius: 0 3px 3px 0;
}

.more-questions {
  text-align: center;
  margin-top: 15px;
  padding: 10px;
  background: #e9ecef;
  border-radius: 4px;
  color: #6c757d;
  font-style: italic;
}

.more-questions p {
  margin: 0;
}

.preview-info p {
  margin: 8px 0;
  color: #666;
}

.title-warning {
  margin-top: 5px;
  padding: 8px 12px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  color: #856404;
  font-size: 13px;
}

.title-warning i {
  margin-right: 5px;
}

.title-warning {
  color: #f39c12;
}

.question-options {
  margin: 10px 0;
}

.option-item {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 3px;
  padding: 6px 10px;
  margin: 4px 0;
  font-size: 13px;
  color: #495057;
}

.question-answer {
  margin: 8px 0;
  font-size: 13px;
}

.correct-answer {
  background: #d4edda;
  color: #155724;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 500;
}

.question-explanation {
  background: #e2e3e5;
  border-left: 4px solid #6c757d;
  padding: 8px 12px;
  margin-top: 10px;
  font-size: 13px;
  font-style: italic;
  color: #495057;
  border-radius: 0 3px 3px 0;
}

.more-questions {
  text-align: center;
  margin-top: 15px;
  padding: 10px;
  background: #e9ecef;
  border-radius: 4px;
  color: #6c757d;
  font-style: italic;
}

.more-questions p {
  margin: 0;
}

.preview-info p {
  margin: 8px 0;
  color: #666;
}

/* 分类选择器样式 */
.category-selector-wrapper {
  position: relative;
  width: 100%;
}

.category-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.2s;
}

.category-display:hover {
  border-color: #c0c4cc;
}

.category-display.active {
  border-color: #409eff;
}

.selected-text {
  flex: 1;
  color: #606266;
  font-size: 14px;
}

.category-display .el-icon-arrow-down {
  color: #c0c4cc;
  transition: transform 0.3s;
}

.category-display .el-icon-arrow-down.rotate {
  transform: rotate(180deg);
}

.category-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1000;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  max-height: 300px;
  overflow-y: auto;
}

.category-list {
  list-style: none;
  margin: 0;
  padding: 6px 0;
}

.category-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: background-color 0.2s;
}

.category-item:hover {
  background-color: #f5f7fa;
}

.category-item.selected {
  background-color: #409eff;
  color: #fff;
}

.category-indent {
  width: 16px;
  display: inline-block;
}

.category-icon {
  margin-right: 6px;
  color: #909399;
  font-size: 14px;
}

.category-item.selected .category-icon {
  color: #fff;
}

.category-name {
  flex: 1;
}

/* 层级样式 */
.category-item.level-0 {
  font-weight: 500;
}

.category-item.level-1 {
  padding-left: 28px;
}

.category-item.level-2 {
  padding-left: 44px;
}

.category-item.level-3 {
  padding-left: 60px;
}
</style>