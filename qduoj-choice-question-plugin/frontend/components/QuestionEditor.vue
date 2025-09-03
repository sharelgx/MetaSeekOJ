<template>
  <div class="question-editor">
    <Form ref="questionForm" :model="form" :rules="rules" :label-width="100">
      <!-- 基本信息 -->
      <Card>
        <div slot="title">
          <Icon type="ios-information-circle" />
          基本信息
        </div>
        
        <Row :gutter="16">
          <Col :span="12">
            <FormItem label="题目标题" prop="title">
              <Input v-model="form.title" placeholder="请输入题目标题" />
            </FormItem>
          </Col>
          <Col :span="12">
            <FormItem label="题目类型" prop="question_type">
              <Select v-model="form.question_type" @on-change="onQuestionTypeChange">
                <Option value="single">单选题</Option>
                <Option value="multiple">多选题</Option>
              </Select>
            </FormItem>
          </Col>
        </Row>
        
        <Row :gutter="16">
          <Col :span="8">
            <FormItem label="分类" prop="category">
              <Cascader
                v-model="form.category"
                :data="categoryOptions"
                placeholder="选择分类"
                clearable
              />
            </FormItem>
          </Col>
          <Col :span="8">
            <FormItem label="难度" prop="difficulty">
              <Select v-model="form.difficulty">
                <Option value="easy">简单</Option>
                <Option value="medium">中等</Option>
                <Option value="hard">困难</Option>
              </Select>
            </FormItem>
          </Col>
          <Col :span="8">
            <FormItem label="分值" prop="score">
              <InputNumber 
                v-model="form.score" 
                :min="1" 
                :max="100"
                placeholder="题目分值"
              />
            </FormItem>
          </Col>
        </Row>
        
        <Row :gutter="16">
          <Col :span="12">
            <FormItem label="标签">
              <Select 
                v-model="form.tags" 
                multiple 
                filterable 
                allow-create
                placeholder="选择或创建标签"
              >
                <Option 
                  v-for="tag in tagOptions" 
                  :key="tag.id" 
                  :value="tag.id"
                >
                  {{ tag.name }}
                </Option>
              </Select>
            </FormItem>
          </Col>
          <Col :span="12">
            <FormItem label="状态">
              <RadioGroup v-model="form.visible">
                <Radio :label="true">公开</Radio>
                <Radio :label="false">私有</Radio>
              </RadioGroup>
            </FormItem>
          </Col>
        </Row>
      </Card>
      
      <!-- 题目内容 -->
      <Card style="margin-top: 16px;">
        <div slot="title">
          <Icon type="ios-document" />
          题目内容
        </div>
        <div slot="extra">
          <ButtonGroup>
            <Button 
              :type="contentMode === 'rich' ? 'primary' : 'default'"
              @click="contentMode = 'rich'"
              size="small"
            >
              富文本
            </Button>
            <Button 
              :type="contentMode === 'markdown' ? 'primary' : 'default'"
              @click="contentMode = 'markdown'"
              size="small"
            >
              Markdown
            </Button>
          </ButtonGroup>
        </div>
        
        <FormItem prop="content">
          <!-- 富文本编辑器 -->
          <div v-if="contentMode === 'rich'" class="rich-editor">
            <Simditor 
              ref="simditor"
              v-model="form.content"
              :height="300"
            />
          </div>
          
          <!-- Markdown编辑器 -->
          <div v-else class="markdown-editor">
            <Row :gutter="16">
              <Col :span="12">
                <div class="editor-header">Markdown 编辑</div>
                <Input 
                  v-model="form.content"
                  type="textarea"
                  :rows="15"
                  placeholder="请输入题目内容（支持Markdown语法）"
                  @on-change="updateMarkdownPreview"
                />
              </Col>
              <Col :span="12">
                <div class="editor-header">预览</div>
                <div class="markdown-preview" v-html="markdownPreview"></div>
              </Col>
            </Row>
          </div>
        </FormItem>
      </Card>
      
      <!-- 选项设置 -->
      <Card style="margin-top: 16px;">
        <div slot="title">
          <Icon type="ios-list" />
          选项设置
        </div>
        <div slot="extra">
          <Button type="primary" size="small" @click="addOption">
            <Icon type="ios-add" />
            添加选项
          </Button>
        </div>
        
        <div class="options-container">
          <div 
            v-for="(option, index) in form.options" 
            :key="index"
            class="option-item"
          >
            <div class="option-header">
              <span class="option-label">选项 {{ String.fromCharCode(65 + index) }}</span>
              <div class="option-actions">
                <Checkbox 
                  v-model="option.is_correct"
                  @on-change="onCorrectChange(index)"
                >
                  正确答案
                </Checkbox>
                <Button 
                  type="error" 
                  size="small" 
                  @click="removeOption(index)"
                  :disabled="form.options.length <= 2"
                >
                  删除
                </Button>
              </div>
            </div>
            
            <div class="option-content">
              <Input 
                v-model="option.content"
                type="textarea"
                :rows="3"
                :placeholder="`请输入选项${String.fromCharCode(65 + index)}的内容`"
              />
            </div>
            
            <div class="option-explanation" v-if="option.is_correct">
              <Input 
                v-model="option.explanation"
                type="textarea"
                :rows="2"
                placeholder="请输入该选项的解释说明（可选）"
              />
            </div>
          </div>
        </div>
      </Card>
      
      <!-- 解析说明 -->
      <Card style="margin-top: 16px;">
        <div slot="title">
          <Icon type="ios-help-circle" />
          解析说明
        </div>
        
        <FormItem>
          <Input 
            v-model="form.explanation"
            type="textarea"
            :rows="4"
            placeholder="请输入题目解析说明（可选）"
          />
        </FormItem>
      </Card>
      
      <!-- 高级设置 -->
      <Card style="margin-top: 16px;">
        <div slot="title">
          <Icon type="ios-settings" />
          高级设置
        </div>
        
        <Row :gutter="16">
          <Col :span="8">
            <FormItem label="时间限制">
              <InputNumber 
                v-model="form.time_limit"
                :min="0"
                :max="3600"
                placeholder="秒（0表示无限制）"
              />
            </FormItem>
          </Col>
          <Col :span="8">
            <FormItem label="提示次数">
              <InputNumber 
                v-model="form.hint_count"
                :min="0"
                :max="5"
                placeholder="允许的提示次数"
              />
            </FormItem>
          </Col>
          <Col :span="8">
            <FormItem label="排序权重">
              <InputNumber 
                v-model="form.sort_order"
                :min="0"
                :max="9999"
                placeholder="数字越小越靠前"
              />
            </FormItem>
          </Col>
        </Row>
        
        <Row :gutter="16">
          <Col :span="12">
            <FormItem label="来源">
              <Input v-model="form.source" placeholder="题目来源（可选）" />
            </FormItem>
          </Col>
          <Col :span="12">
            <FormItem label="作者">
              <Input v-model="form.author" placeholder="题目作者（可选）" />
            </FormItem>
          </Col>
        </Row>
        
        <FormItem label="备注">
          <Input 
            v-model="form.note"
            type="textarea"
            :rows="3"
            placeholder="内部备注信息（不会显示给用户）"
          />
        </FormItem>
      </Card>
    </Form>
    
    <!-- 预览模态框 -->
    <Modal
      v-model="previewModal"
      title="题目预览"
      width="800"
      :footer-hide="true"
    >
      <div class="question-preview">
        <div class="preview-header">
          <h3>{{ form.title }}</h3>
          <div class="preview-meta">
            <Tag color="blue">{{ form.difficulty }}</Tag>
            <Tag color="green">{{ form.question_type === 'single' ? '单选题' : '多选题' }}</Tag>
            <Tag color="orange">{{ form.score }}分</Tag>
          </div>
        </div>
        
        <div class="preview-content" v-html="getPreviewContent()"></div>
        
        <div class="preview-options">
          <div 
            v-for="(option, index) in form.options"
            :key="index"
            class="preview-option"
            :class="{ 'correct-option': option.is_correct }"
          >
            <span class="option-prefix">{{ String.fromCharCode(65 + index) }}.</span>
            <span class="option-text">{{ option.content }}</span>
            <Icon v-if="option.is_correct" type="ios-checkmark-circle" color="#19be6b" />
          </div>
        </div>
        
        <div class="preview-explanation" v-if="form.explanation">
          <h4>解析：</h4>
          <p>{{ form.explanation }}</p>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import api from '../api'
import { marked } from 'marked'
import Simditor from './Simditor.vue'

export default {
  name: 'QuestionEditor',
  components: {
    Simditor
  },
  props: {
    question: {
      type: Object,
      default: null
    },
    visible: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      form: {
        title: '',
        content: '',
        question_type: 'single',
        difficulty: 'easy',
        score: 5,
        category: null,
        tags: [],
        visible: true,
        options: [
          { content: '', is_correct: false, explanation: '' },
          { content: '', is_correct: false, explanation: '' }
        ],
        explanation: '',
        time_limit: 0,
        hint_count: 0,
        sort_order: 0,
        source: '',
        author: '',
        note: ''
      },
      
      contentMode: 'rich', // rich | markdown
      markdownPreview: '',
      previewModal: false,
      
      // 选项数据
      categoryOptions: [],
      tagOptions: [],
      
      // 表单验证规则
      rules: {
        title: [
          { required: true, message: '请输入题目标题', trigger: 'blur' },
          { min: 5, max: 200, message: '标题长度在5到200个字符', trigger: 'blur' }
        ],
        content: [
          { required: true, message: '请输入题目内容', trigger: 'blur' }
        ],
        question_type: [
          { required: true, message: '请选择题目类型', trigger: 'change' }
        ],
        difficulty: [
          { required: true, message: '请选择难度', trigger: 'change' }
        ],
        score: [
          { required: true, type: 'number', min: 1, message: '请输入有效的分值', trigger: 'blur' }
        ]
      }
    }
  },
  watch: {
    question: {
      handler(newVal) {
        if (newVal) {
          this.loadQuestion(newVal)
        } else {
          this.resetForm()
        }
      },
      immediate: true
    },
    
    visible(newVal) {
      if (newVal) {
        this.$nextTick(() => {
          this.initRichEditor()
        })
      }
    }
  },
  mounted() {
    this.init()
  },
  beforeDestroy() {
    // Simditor组件会自动处理销毁
  },
  methods: {
    async init() {
      await Promise.all([
        this.loadCategories(),
        this.loadTags()
      ])
    },
    
    async loadCategories() {
      try {
        const res = await api.getCategories()
        this.categoryOptions = this.buildCascaderOptions(res.data.results || res.data)
      } catch (error) {
        console.error('加载分类失败:', error)
      }
    },
    
    buildCascaderOptions(categories) {
      const categoryMap = {}
      const rootOptions = []
      
      categories.forEach(category => {
        categoryMap[category.id] = {
          value: category.id,
          label: category.name,
          children: []
        }
      })
      
      categories.forEach(category => {
        if (category.parent) {
          const parent = categoryMap[category.parent]
          if (parent) {
            parent.children.push(categoryMap[category.id])
          }
        } else {
          rootOptions.push(categoryMap[category.id])
        }
      })
      
      return rootOptions
    },
    
    async loadTags() {
      try {
        const res = await api.getTags()
        this.tagOptions = res.data.results || res.data
      } catch (error) {
        console.error('加载标签失败:', error)
      }
    },
    
    loadQuestion(question) {
      this.form = {
        ...question,
        tags: question.tags ? question.tags.map(tag => tag.id) : [],
        options: question.options || [
          { content: '', is_correct: false, explanation: '' },
          { content: '', is_correct: false, explanation: '' }
        ]
      }
      
      // Simditor组件通过v-model自动同步内容
      
      this.updateMarkdownPreview()
    },
    
    resetForm() {
      this.form = {
        title: '',
        content: '',
        question_type: 'single',
        difficulty: 'easy',
        score: 5,
        category: null,
        tags: [],
        visible: true,
        options: [
          { content: '', is_correct: false, explanation: '' },
          { content: '', is_correct: false, explanation: '' }
        ],
        explanation: '',
        time_limit: 0,
        hint_count: 0,
        sort_order: 0,
        source: '',
        author: '',
        note: ''
      }
      
      // Simditor组件通过v-model自动同步内容
      
      this.markdownPreview = ''
    },
    
    initRichEditor() {
      // Simditor组件会自动初始化，无需手动处理
    },
    
    onQuestionTypeChange(type) {
      // 单选题只能有一个正确答案，多选题可以有多个
      if (type === 'single') {
        const correctCount = this.form.options.filter(opt => opt.is_correct).length
        if (correctCount > 1) {
          // 只保留第一个正确答案
          let foundFirst = false
          this.form.options.forEach(opt => {
            if (opt.is_correct && !foundFirst) {
              foundFirst = true
            } else if (opt.is_correct) {
              opt.is_correct = false
            }
          })
        }
      }
    },
    
    onCorrectChange(index) {
      if (this.form.question_type === 'single') {
        // 单选题：取消其他选项的正确状态
        this.form.options.forEach((opt, i) => {
          if (i !== index) {
            opt.is_correct = false
          }
        })
      }
    },
    
    addOption() {
      if (this.form.options.length < 8) {
        this.form.options.push({
          content: '',
          is_correct: false,
          explanation: ''
        })
      } else {
        this.$Message.warning('最多只能添加8个选项')
      }
    },
    
    removeOption(index) {
      if (this.form.options.length > 2) {
        this.form.options.splice(index, 1)
      } else {
        this.$Message.warning('至少需要保留2个选项')
      }
    },
    
    updateMarkdownPreview() {
      if (this.contentMode === 'markdown' && this.form.content) {
        try {
          this.markdownPreview = marked(this.form.content)
        } catch (error) {
          this.markdownPreview = this.form.content
        }
      }
    },
    
    getPreviewContent() {
      if (this.contentMode === 'markdown') {
        return this.markdownPreview
      } else {
        return this.form.content
      }
    },
    
    async validate() {
      try {
        await this.$refs.questionForm.validate()
        
        // 验证选项
        if (this.form.options.length < 2) {
          throw new Error('至少需要2个选项')
        }
        
        const hasCorrect = this.form.options.some(opt => opt.is_correct)
        if (!hasCorrect) {
          throw new Error('至少需要设置一个正确答案')
        }
        
        const emptyOptions = this.form.options.filter(opt => !opt.content.trim())
        if (emptyOptions.length > 0) {
          throw new Error('所有选项都必须填写内容')
        }
        
        return true
      } catch (error) {
        if (typeof error === 'string') {
          this.$Message.error(error)
        } else if (error.message) {
          this.$Message.error(error.message)
        }
        return false
      }
    },
    
    getData() {
      const data = { ...this.form }
      
      // 富文本内容已通过v-model同步到form.content中
      
      // 提取正确答案
      const correctAnswers = []
      data.options.forEach((option, index) => {
        if (option.is_correct) {
          correctAnswers.push(String.fromCharCode(65 + index)) // A, B, C, D...
        }
      })
      
      // 设置正确答案字段
      if (correctAnswers.length > 0) {
        data.correct_answer = correctAnswers.join(',')
      }
      
      return data
    },
    
    preview() {
      this.previewModal = true
    }
  }
}
</script>

<style scoped>
.question-editor {
  max-width: 1200px;
  margin: 0 auto;
}

.rich-editor {
  border: 1px solid #dcdee2;
  border-radius: 4px;
}

.editor-container {
  min-height: 200px;
}

.markdown-editor {
  border: 1px solid #dcdee2;
  border-radius: 4px;
}

.editor-header {
  padding: 8px 12px;
  background: #f8f8f9;
  border-bottom: 1px solid #dcdee2;
  font-weight: bold;
  color: #666;
}

.markdown-preview {
  min-height: 300px;
  padding: 12px;
  background: #fff;
  overflow-y: auto;
}

.options-container {
  margin-top: 16px;
}

.option-item {
  margin-bottom: 16px;
  padding: 16px;
  border: 1px solid #dcdee2;
  border-radius: 4px;
  background: #fafafa;
}

.option-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.option-label {
  font-weight: bold;
  color: #333;
}

.option-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.option-content {
  margin-bottom: 8px;
}

.option-explanation {
  margin-top: 8px;
}

.question-preview {
  padding: 20px;
}

.preview-header {
  margin-bottom: 20px;
}

.preview-header h3 {
  margin: 0 0 8px 0;
  color: #333;
}

.preview-meta {
  display: flex;
  gap: 8px;
}

.preview-content {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f8f9;
  border-radius: 4px;
  line-height: 1.6;
}

/* 富文本内容中的图片尺寸控制 */
.preview-content img {
  max-width: 400px;
  width: auto;
  height: auto;
}

.preview-options {
  margin-bottom: 20px;
}

.preview-option {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  border: 1px solid #dcdee2;
  border-radius: 4px;
  background: #fff;
}

.preview-option.correct-option {
  background: #f6ffed;
  border-color: #b7eb8f;
}

.option-prefix {
  font-weight: bold;
  margin-right: 8px;
  color: #666;
}

.option-text {
  flex: 1;
}

/* 选项预览中的图片尺寸控制 */
.option-text img {
  max-width: 400px;
  width: auto;
  height: auto;
}

.preview-explanation {
  padding: 16px;
  background: #f0f9ff;
  border-radius: 4px;
  border-left: 4px solid #2d8cf0;
}

.preview-explanation h4 {
  margin: 0 0 8px 0;
  color: #2d8cf0;
}

.preview-explanation p {
  margin: 0;
  line-height: 1.6;
  color: #666;
}

/* 解析预览中的图片尺寸控制 */
.preview-explanation img {
  max-width: 400px;
  width: auto;
  height: auto;
}
</style>