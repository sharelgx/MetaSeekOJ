<template>
  <div class="view">
    <Panel title="导入选择题">
      <div class="import-container">
        <!-- 选择器区域 -->
        <div class="selector-section">
          <el-row :gutter="16" style="margin-bottom: 20px;">
            <!-- 分类选择 -->
            <el-col :span="8">
              <div class="form-group">
                <label class="form-label">
                  <i class="el-icon-folder"></i>
                  选择分类
                </label>
                <!-- 自定义分类选择器 -->
                <div class="category-selector-wrapper">
                  <div 
                    class="category-display" 
                    :class="{ active: showCategoryDropdown }"
                    @click="toggleCategoryDropdown"
                  >
                    <span 
                      class="selected-text" 
                      :class="{ placeholder: !selectedCategoryName }"
                    >
                      {{ selectedCategoryName || '请选择分类' }}
                    </span>
                    <i 
                      class="el-icon-arrow-down" 
                      :class="{ rotate: showCategoryDropdown }"
                    ></i>
                  </div>
                  
                  <div v-if="showCategoryDropdown" class="category-dropdown">
                    <ul class="category-list">
                      <li 
                        v-for="category in flattenedCategories" 
                        :key="category.id"
                        class="category-item"
                        :class="[
                          `level-${category.level}`,
                          { selected: selectedCategory === category.id }
                        ]"
                        @click="selectCategory(category)"
                      >
                        <span class="category-indent" v-for="i in category.level" :key="i"></span>
                        <i class="category-icon el-icon-folder"></i>
                        <span class="category-name">{{ category.name }}</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </el-col>
            
            <!-- 标签选择 -->
            <el-col :span="8">
              <div class="form-group">
                <label class="form-label">
                  <i class="el-icon-price-tag"></i>
                  选择标签
                </label>
                <el-select 
                  v-model="selectedTags" 
                  multiple
                  filterable
                  placeholder="选择标签" 
                  style="width: 100%;"
                  @change="handleTagChange"
                >
                  <el-option
                    v-for="tag in tags"
                    :key="tag.id"
                    :label="tag.name"
                    :value="tag.id"
                  >
                    <span style="float: left">{{ tag.name }}</span>
                    <span style="float: right; color: #8492a6; font-size: 12px">{{ tag.tag_type }}</span>
                  </el-option>
                </el-select>
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
                  placeholder="请选择语言" 
                  clearable 
                  style="width: 100%;"
                >
                  <el-option label="C" value="C"></el-option>
                  <el-option label="C++" value="C++"></el-option>
                  <el-option label="Java" value="Java"></el-option>
                  <el-option label="Python" value="Python"></el-option>
                  <el-option label="JavaScript" value="JavaScript"></el-option>
                </el-select>
              </div>
            </el-col>
          </el-row>
        </div>

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
              <div class="json-help">
                <p>📝 请粘贴您的JSON格式题目数据，支持以下格式：</p>
                <details class="format-example">
                  <summary>查看JSON格式示例</summary>
                  <pre class="json-example">{{ JSON.stringify(formatGuide.example, null, 2) }}</pre>
                </details>
              </div>
              <el-input
                type="textarea"
                :rows="10"
                placeholder="在此粘贴JSON内容"
                v-model="jsonText"
                class="json-textarea">
              </el-input>
              <div class="json-actions">
                <el-button size="small" type="text" @click="loadJsonExample">📋 加载示例数据</el-button>
                <el-button size="small" type="text" @click="clearJsonText">🗑️ 清空文本</el-button>
              </div>
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
                  <li><strong>type</strong>: 题型，"single"（单选题）</li>
                  <li><strong>question</strong>: 题目描述，支持HTML格式</li>
                  <li><strong>options</strong>: 选项数组，每个选项为字符串，格式如"A. 选项内容"</li>
                  <li><strong>answer</strong>: 正确答案，使用字母表示（如"A"、"B"、"C"、"D"）</li>
                  <li><strong>explanation</strong>: 答案解释，详细说明正确答案的原因</li>
                </ul>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>

        <!-- 预览区域 -->
        <div v-if="previewData.length > 0" class="preview-section">
          <h4>导入预览</h4>
          <div class="question-preview" v-for="(question, index) in previewData" :key="index">
            <h5>{{ index + 1 }}. {{ question.title }}</h5>
            <div class="question-content" v-html="question.description"></div>
            <div class="options">
              <div class="option" v-for="(option, optIndex) in question.options" :key="optIndex">
                {{ String.fromCharCode(65 + optIndex) }}. {{ option.content }}
                <span v-if="option.is_correct" class="correct-mark">✓</span>
              </div>
            </div>
            <div class="correct-answer">
              <strong>正确答案:</strong> {{ question.correct_answer }}
              <span v-if="question.explanation"> | <strong>解释:</strong> {{ question.explanation }}</span>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div style="text-align: center; margin-top: 20px;">
          <el-button @click="parseJSON" :disabled="!canParse" type="primary">解析JSON</el-button>
          <el-button @click="importQuestions" :disabled="previewData.length === 0" type="success">确认导入</el-button>
          <el-button @click="clearAll">清空</el-button>
        </div>
      </div>
    </Panel>
  </div>
</template>

<script>
import Panel from '@admin/components/Panel.vue'
import api from '@admin/api'

export default {
  name: 'ImportChoiceQuestion',
  components: {
    Panel
  },
  data() {
    return {
      categories: [],
      tags: [],
      selectedCategory: null,
      selectedTags: [],
      selectedLanguage: null,
      newTagName: '',
      newTagType: 'knowledge',
      activeTab: 'file',
      fileList: [],
      jsonText: '',
      previewData: [],
      showCategoryDropdown: false,
      formatGuide: {
        example: [
          {
            "type": "single",
            "question": "以下不属于计算机输入设备的有( )。",
            "options": [
              "A. 键盘",
              "B. 音箱",
              "C. 鼠标",
              "D. 传感器"
            ],
            "answer": "B",
            "explanation": "输入指外界向机器内部传递信息，输出指计算机内部信息向外界展示。音箱属于向外部播放声音，故属于输出设备。"
          }
        ]
      }
    }
  },
  computed: {
    canParse() {
      return (this.activeTab === 'file' && this.fileList.length > 0) || 
             (this.activeTab === 'text' && this.jsonText.trim())
    },
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
      
      const cleanCategories = deepDeduplication(this.categories)
      
      // 扁平化处理
      const flatten = (categories, level = 0) => {
        let result = []
        // 按order排序
        const sortedCategories = [...categories].sort((a, b) => (a.order || 0) - (b.order || 0))
        
        sortedCategories.forEach(category => {
          result.push({
            ...category,
            level: level
          })
          if (category.children && category.children.length > 0) {
            result = result.concat(flatten(category.children, level + 1))
          }
        })
        return result
      }
      
      return flatten(cleanCategories)
    },
    // 获取选中分类的名称
    selectedCategoryName() {
      if (!this.selectedCategory) return ''
      const category = this.flattenedCategories.find(cat => cat.id === this.selectedCategory)
      return category ? category.name : ''
    }
  },
  mounted() {
    this.getCategories()
    this.getTags()
  },
  methods: {
    async getCategories() {
      try {
        const res = await api.getChoiceQuestionCategories()
        this.categories = res.data.data || []
        console.log('分类数据加载成功:', this.categories)
      } catch (err) {
        console.error('获取分类失败:', err)
        this.categories = []
      }
    },
    async getTags() {
      try {
        const res = await api.getChoiceQuestionTags()
        this.tags = res.data.data || []
        console.log('标签数据加载成功:', this.tags)
      } catch (err) {
        console.error('获取标签失败:', err)
        this.tags = []
      }
    },
    getCategoryDisplayName(category) {
      if (!category) return ''
      if (category.parent) {
        if (typeof category.parent === 'number') {
          const parentCategory = this.categories.find(c => c.id === category.parent)
          return parentCategory ? `${parentCategory.name} > ${category.name}` : category.name
        }
        else if (category.parent.name) {
          return `${category.parent.name} > ${category.name}`
        }
        return category.name
      }
      return category.name
    },
    getCategoryById(id) {
      return this.categories.find(c => c.id === id)
    },
    getTagById(id) {
      return this.tags.find(t => t.id === id)
    },
    getTagName(id) {
      const tag = this.getTagById(id)
      return tag ? tag.name : ''
    },
    handleTagChange(value) {
      this.selectedTags = value
    },
    removeTag(tagId) {
      this.selectedTags = this.selectedTags.filter(id => id !== tagId)
    },
    // 分类选择器相关方法
    toggleCategoryDropdown() {
      this.showCategoryDropdown = !this.showCategoryDropdown
    },
    selectCategory(category) {
      this.selectedCategory = category.id
      this.showCategoryDropdown = false
    },
    handleTabClick(tab) {
      this.activeTab = tab.name
    },
    handleFileChange(file, fileList) {
      this.fileList = fileList
    },
    loadJsonExample() {
      this.jsonText = JSON.stringify(this.formatGuide.example, null, 2)
      this.$message.success('示例数据已加载')
    },
    clearJsonText() {
      this.jsonText = ''
      this.previewData = []
      this.$message.info('文本已清空')
    },
    parseJSON() {
      let jsonData = ''
      
      if (this.activeTab === 'file' && this.fileList.length > 0) {
        const file = this.fileList[0].raw
        const reader = new FileReader()
        reader.onload = (e) => {
          try {
            jsonData = JSON.parse(e.target.result)
            this.processJSONData(jsonData)
          } catch (err) {
            this.$message.error('JSON文件格式错误')
            console.error('JSON解析错误:', err)
          }
        }
        reader.readAsText(file)
      } else if (this.activeTab === 'text' && this.jsonText.trim()) {
        try {
          jsonData = JSON.parse(this.jsonText)
          this.processJSONData(jsonData)
        } catch (err) {
          this.$message.error('JSON格式错误')
          console.error('JSON解析错误:', err)
        }
      }
    },
    processJSONData(data) {
      if (!Array.isArray(data)) {
        this.$message.error('JSON数据必须是数组格式')
        return
      }
      
      // 清理特殊字符的函数
      const cleanText = (text) => {
        if (!text) return ''
        // 移除后端不允许的特殊字符：< > " \\
        return text.replace(/[<>"\\]/g, '')
      }
      
      // 验证数据格式并转换为后端期望的格式
      const validData = data.filter(item => {
        return item.question && item.options && Array.isArray(item.options) && (item.answer || item.correct)
      }).map(item => {
        // 自动生成标题：从题目内容中提取前20个字符
        let title = item.title
        if (!title) {
          const tempDiv = document.createElement('div')
          tempDiv.innerHTML = item.question
          const plainText = tempDiv.textContent || tempDiv.innerText || ''
          
          const autoTitle = plainText.trim().substring(0, 20)
          if (autoTitle) {
            title = autoTitle + (plainText.trim().length > 20 ? '...' : '')
          } else {
            title = '未命名题目'
          }
        }
        
        // 清理标题中的特殊字符
        title = cleanText(title)
        
        // 转换选项格式：从字符串数组转换为对象数组
        const options = item.options.map((optionText, index) => {
          let isCorrect = false
          
          // 处理正确答案格式
          const answer = item.answer || item.correct
          if (Array.isArray(answer)) {
            // 多选题：answer是数组，如["A", "B"]
            isCorrect = answer.includes(String.fromCharCode(65 + index))
          } else if (typeof answer === 'string') {
            // 单选题：answer是字符串，如"A"
            isCorrect = answer === String.fromCharCode(65 + index)
          }
          
          return {
            content: cleanText(optionText), // 清理选项内容
            is_correct: isCorrect
          }
        })
        
        // 转换题目类型为整数
        let questionType = 0 // 默认单选
        if (item.type === 'multiple') {
          questionType = 1 // 多选
        }
        
        // 转换为后端期望的格式
        return {
          title: title || '未命名题目',
          description: cleanText(item.question), // 清理题目描述
          question_type: questionType,
          options: options,
          correct_answer: item.answer || item.correct,
          explanation: cleanText(item.explanation || ''), // 清理解析内容
          difficulty: 'Easy',
          visible: true
        }
      })
      
      if (validData.length === 0) {
        this.$message.error('没有找到有效的题目数据')
        return
      }
      
      this.previewData = validData
      this.$message.success(`成功解析 ${validData.length} 道题目`)
    },
    async importQuestions() {
      if (this.previewData.length === 0) {
        this.$message.error('没有可导入的题目')
        return
      }
      
      try {
        const importData = {
          questions: this.previewData,
          category_id: this.selectedCategory,
          tag_ids: this.selectedTags,
          language: this.selectedLanguage
        }
        
        console.log('准备导入的数据:', importData)
        
        const res = await api.importChoiceQuestions(importData)
        console.log('导入响应:', res)
        
        if (res.data.error === null) {
          this.$message.success(`成功导入 ${this.previewData.length} 道题目`)
          this.clearAll()
        } else {
          // 显示详细的错误信息
          let errorMsg = '导入失败：'
          if (typeof res.data.data === 'string') {
            errorMsg += res.data.data
          } else if (Array.isArray(res.data.data)) {
            errorMsg += res.data.data.join('; ')
          } else {
            errorMsg += JSON.stringify(res.data.data)
          }
          this.$message.error(errorMsg)
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
      }
    },
    clearAll() {
      this.selectedCategory = null
      this.selectedTags = []
      this.selectedLanguage = null
      this.fileList = []
      this.jsonText = ''
      this.previewData = []
      this.activeTab = 'file'
    }
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

.upload-section {
  padding: 20px;
  background: #fafbfc;
  border-radius: 6px;
  border: 1px solid #ebeef5;
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

.json-textarea .el-textarea__inner {
  border-radius: 6px;
  border: 1px solid #dcdfe6;
  background: #ffffff;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.json-actions {
  margin-top: 10px;
  text-align: right;
}

.json-actions .el-button {
  margin-left: 10px;
}

.format-guide {
  padding: 20px;
  background: #fafbfc;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

.field-descriptions {
  margin-top: 20px;
}

.field-descriptions ul {
  padding-left: 20px;
}

.field-descriptions li {
  margin-bottom: 8px;
  line-height: 1.6;
}

.preview-section {
  margin-top: 20px;
  padding: 20px;
  background: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 6px;
}

.question-preview {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 16px;
  background: #fafbfc;
}

.question-preview h5 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

.question-preview .question-content {
  margin: 12px 0;
  padding: 12px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.6;
}

.question-preview .options {
  margin: 12px 0;
}

.question-preview .option {
  margin: 6px 0;
  padding: 8px 12px;
  font-size: 13px;
  line-height: 1.5;
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-preview .correct-mark {
  color: #67c23a;
  font-weight: bold;
  font-size: 14px;
}

.question-preview .correct-answer {
  margin-top: 12px;
  padding: 8px;
  background: #f0f9ff;
  border: 1px solid #e1f5fe;
  border-radius: 4px;
  font-size: 12px;
  color: #0277bd;
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
  background-color: #fff;
  cursor: pointer;
  transition: border-color 0.2s;
  min-height: 32px;
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
}

.selected-text.placeholder {
  color: #c0c4cc;
}

.el-icon-arrow-down {
  margin-left: 8px;
  transition: transform 0.3s;
  color: #c0c4cc;
}

.el-icon-arrow-down.rotate {
  transform: rotate(180deg);
}

.category-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.category-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f5f7fa;
}

.category-item:last-child {
  border-bottom: none;
}

.category-item:hover {
  background-color: #f5f7fa;
}

.category-item.selected {
  background-color: #ecf5ff;
  color: #409eff;
}

/* 层级样式 */
.category-item.level-0 {
  padding-left: 12px;
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

.category-indent {
  width: 16px;
  height: 1px;
}

.category-icon {
  margin-right: 6px;
  color: #909399;
}

.category-name {
  flex: 1;
}
</style>
