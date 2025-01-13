<template>
  <div class="view">
    <Panel title="导入选择题">
      <div class="import-container">
        <!-- 选择器区域 - 扁平化布局 -->
        <div class="selector-section">
          <el-row :gutter="16" style="margin-bottom: 20px;">
            <!-- 分类选择 -->
            <el-col :span="8">
              <div class="form-group">
                <label class="form-label">
                  <i class="el-icon-folder"></i>
                  选择分类
                </label>
                <el-select 
                  v-model="selectedCategory" 
                  placeholder="请选择分类" 
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
            </el-col>
            
            <!-- 标签选择和添加 -->
            <el-col :span="8">
              <div class="form-group">
                <label class="form-label">
                  <i class="el-icon-price-tag"></i>
                  标签管理
                </label>
                <div class="tag-management">
                  <el-select 
                    v-model="selectedTags" 
                    multiple
                    filterable
                    placeholder="选择或搜索标签" 
                    style="width: 100%; margin-bottom: 8px;"
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
                  
                  <!-- 添加新标签 -->
                  <div class="add-tag-section">
                    <el-input
                      v-model="newTagName"
                      placeholder="新标签名称"
                      size="small"
                      style="margin-bottom: 4px;"
                      @keyup.enter.native="addNewTag"
                    ></el-input>
                    <div style="display: flex; gap: 8px;">
                      <el-select v-model="newTagType" placeholder="类型" size="small" style="flex: 1;">
                        <el-option label="知识点" value="knowledge"></el-option>
                        <el-option label="难度" value="difficulty"></el-option>
                        <el-option label="学科" value="subject"></el-option>
                        <el-option label="自定义" value="custom"></el-option>
                      </el-select>
                      <el-button type="primary" size="small" @click="addNewTag" :disabled="!newTagName.trim()">添加</el-button>
                    </div>
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
                  placeholder="请选择语言" 
                  clearable 
                  style="width: 100%;"
                >
                  <el-option label="C" value="C"></el-option>
                  <el-option label="C++" value="C++"></el-option>
                  <el-option label="Java" value="Java"></el-option>
                  <el-option label="Python" value="Python"></el-option>
                  <el-option label="Python3" value="Python3"></el-option>
                  <el-option label="JavaScript" value="JavaScript"></el-option>
                  <el-option label="Go" value="Go"></el-option>
                  <el-option label="C#" value="C#"></el-option>
                  <el-option label="PHP" value="PHP"></el-option>
                  <el-option label="Ruby" value="Ruby"></el-option>
                  <el-option label="Kotlin" value="Kotlin"></el-option>
                  <el-option label="Swift" value="Swift"></el-option>
                  <el-option label="Rust" value="Rust"></el-option>
                  <el-option label="Scala" value="Scala"></el-option>
                </el-select>
              </div>
            </el-col>
          </el-row>
        </div>
        
        <!-- 已选项显示 -->
        <div class="selection-summary" v-if="selectedTags.length > 0 || selectedLanguage || selectedCategory" style="margin-bottom: 12px;">
          <div class="summary-header" style="margin-bottom: 8px; color: #606266; font-size: 14px; font-weight: 500;">
            <i class="el-icon-check"></i> 当前选择
          </div>
          <div class="summary-content" style="display: flex; flex-wrap: wrap; gap: 8px;">
            <!-- 已选分类 -->
            <el-tag v-if="selectedCategory" type="success" size="small">
              分类: {{ getCategoryDisplayName(categories.find(c => c.id === selectedCategory)) }}
            </el-tag>
            
            <!-- 已选标签 -->
            <el-tag
              v-for="tagId in selectedTags"
              :key="'tag-' + tagId"
              closable
              size="small"
              @close="removeTag(tagId)"
            >
              {{ getTagName(tagId) }}
            </el-tag>
            
            <!-- 已选编程语言 -->
            <el-tag v-if="selectedLanguage" type="info" size="small">
              语言: {{ selectedLanguage }}
            </el-tag>
          </div>
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
              <el-input
                type="textarea"
                :rows="10"
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
      formatGuide: {
        example: [
          {
            "id": 1,
            "type": "single",
            "question": "以下哪个是JavaScript的数据类型？",
            "options": ["String", "Integer", "Float", "Character"],
            "correct": "A",
            "explanation": "JavaScript中有String类型，但没有Integer、Float、Character类型"
          },
          {
            "id": 2,
            "type": "multiple",
            "question": "以下哪些是前端框架？",
            "options": ["Vue.js", "React", "Django", "Angular"],
            "correct": ["A", "B", "D"],
            "explanation": "Vue.js、React、Angular都是前端框架，Django是后端框架"
          }
        ]
      }
    }
  },
  computed: {
    canParse() {
      return (this.activeTab === 'file' && this.fileList.length > 0) || 
             (this.activeTab === 'text' && this.jsonText.trim())
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
      } catch (err) {
        console.error('获取分类失败:', err)
        this.categories = []
      }
    },
    async getTags() {
      try {
        const res = await api.getChoiceQuestionTags()
        this.tags = res.data.data || []
      } catch (err) {
        console.error('获取标签失败:', err)
        this.tags = []
      }
    },
    getCategoryDisplayName(category) {
      if (!category) return ''
      if (category.parent) {
        // 如果parent是ID，需要查找对应的分类对象
        if (typeof category.parent === 'number') {
          const parentCategory = this.categories.find(c => c.id === category.parent)
          return parentCategory ? `${parentCategory.name} > ${category.name}` : category.name
        }
        // 如果parent是对象且有name属性
        else if (category.parent.name) {
          return `${category.parent.name} > ${category.name}`
        }
        // 其他情况直接返回分类名
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
    async addNewTag() {
      if (!this.newTagName.trim()) return
      
      try {
        const res = await api.createChoiceQuestionTag({
          name: this.newTagName.trim(),
          tag_type: this.newTagType
        })
        
        if (res.data.error === null) {
          this.$message.success('标签添加成功')
          this.tags.push(res.data.data)
          this.selectedTags.push(res.data.data.id)
          this.newTagName = ''
          this.newTagType = 'knowledge'
        } else {
          this.$message.error(res.data.data || '添加标签失败')
        }
      } catch (err) {
        this.$message.error('添加标签失败')
        console.error('添加标签失败:', err)
      }
    },
    handleTabClick(tab) {
      this.activeTab = tab.name
    },
    handleFileChange(file, fileList) {
      this.fileList = fileList
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
      
      // 验证数据格式并转换为后端期望的格式
      const validData = data.filter(item => {
        return item.question && item.options && Array.isArray(item.options) && item.correct
      }).map(item => {
        // 自动生成标题：从题目内容中提取前12个字符
        let title = item.title
        if (!title) {
          // 从HTML内容中提取纯文本
          const tempDiv = document.createElement('div')
          tempDiv.innerHTML = item.question
          const plainText = tempDiv.textContent || tempDiv.innerText || ''
          
          // 截取前12个字符作为标题
          const autoTitle = plainText.trim().substring(0, 12)
          if (autoTitle) {
            title = autoTitle + (plainText.trim().length > 12 ? '...' : '')
          } else {
            title = '未命名题目'
          }
        }
        
        // 转换选项格式：从字符串数组转换为对象数组
        const options = item.options.map((optionText, index) => {
          const isCorrect = Array.isArray(item.correct) 
            ? item.correct.includes(String.fromCharCode(65 + index))
            : item.correct === String.fromCharCode(65 + index)
          
          return {
            content: optionText, // 使用content字段而不是text
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
          title: title,
          description: item.question, // question 字段映射为 description
          question_type: questionType, // 转换为整数类型
          options: options,
          correct_answer: item.correct,
          explanation: item.explanation || '',
          difficulty: 'Easy', // 默认难度
          visible: true // 默认可见
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
        
        const res = await api.importChoiceQuestions(importData)
        
        if (res.data.error === null) {
          this.$message.success(`成功导入 ${this.previewData.length} 道题目`)
          this.clearAll()
        } else {
          this.$message.error(res.data.data || '导入失败')
        }
      } catch (err) {
        this.$message.error('导入失败')
        console.error('导入失败:', err)
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
/* 整体页面样式 */
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

/* 选择器区域样式 */
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

/* 标签管理区域 */
.tag-management {
  width: 100%;
}

.add-tag-section {
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px dashed #dcdfe6;
}

/* 已选项显示样式 */
.selection-summary {
  background: #f8f9fa;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 16px;
}

.summary-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.summary-header i {
  margin-right: 6px;
  color: #67c23a;
}

.summary-content {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 上传区域样式 */
.upload-section {
  padding: 20px;
  background: #fafbfc;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

/* JSON输入区域样式 */
.json-input-section {
  padding: 20px;
}

.json-textarea .el-textarea__inner {
  border-radius: 6px;
  border: 1px solid #dcdfe6;
  background: #ffffff;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
}

/* 格式说明区域样式 */
.format-guide {
  padding: 20px;
  background: #fafbfc;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

.json-example {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 16px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  overflow-x: auto;
  margin: 12px 0;
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

/* 预览区域样式 */
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

/* 响应式设计 */
@media (max-width: 768px) {
  .view {
    padding: 12px;
  }
  
  .import-container {
    padding: 16px;
  }
  
  .selector-section {
    padding: 12px;
  }
  
  .el-col {
    margin-bottom: 16px;
  }
}
</style>