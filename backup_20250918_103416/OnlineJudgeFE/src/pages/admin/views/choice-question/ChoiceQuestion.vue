<template>
  <div class="view">
    <Panel :title="title">
      <el-form :model="choiceQuestion" :rules="ruleValidate" ref="formValidate">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item prop="title" :label="$t('m.Title')" required>
              <el-input
                v-model="choiceQuestion.title"
                :placeholder="$t('m.Title')"
                class="title-input">
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item prop="difficulty" :label="$t('m.Difficulty')" required>
              <el-select v-model="choiceQuestion.difficulty" class="difficulty-select">
                <el-option label="Easy" value="Easy"></el-option>
                <el-option label="Medium" value="Medium"></el-option>
                <el-option label="Hard" value="Hard"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item prop="category" :label="$t('m.Category')">
              <div class="category-selector-wrapper">
                <div 
                  class="category-display" 
                  @click="toggleCategoryDropdown"
                  :class="{ 'active': showCategoryDropdown }"
                >
                  <span class="selected-text">
                    {{ selectedCategoryName || $t('m.Select_Category') }}
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
                         'selected': choiceQuestion.category === category.id,
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
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item prop="question_type" :label="$t('m.Question_Type')" required>
              <el-select v-model="choiceQuestion.question_type" :placeholder="$t('m.Select_Question_Type')">
                <el-option :label="$t('m.Single_Choice')" value="single"></el-option>
                <el-option :label="$t('m.Multiple_Choice')" value="multiple"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item prop="visible" :label="$t('m.Visible')">
              <el-switch v-model="choiceQuestion.visible"></el-switch>
            </el-form-item>
          </el-col>

          <el-col :span="24">
            <el-form-item prop="tags" :label="$t('m.Tags')">
              <el-select
                v-model="choiceQuestion.tags"
                multiple
                filterable
                allow-create
                default-first-option
                :placeholder="$t('m.Select_or_create_tags')">
                <el-option
                  v-for="tag in tags"
                  :key="tag.id"
                  :label="tag.name"
                  :value="tag.name">
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item prop="description" :label="$t('m.Description')" required>
              <!-- 添加调试信息 -->
              <div v-if="!choiceQuestion.description" class="debug-info">
                <el-alert
                  title="题目描述为空"
                  type="warning"
                  :closable="false"
                  show-icon>
                  <div slot="default">
                    <p>如果您看到这个警告，说明题目数据没有正确加载。</p>
                    <p>请检查浏览器控制台查看详细错误信息。</p>
                  </div>
                </el-alert>
              </div>
              <Simditor v-model="choiceQuestion.description" v-if="choiceQuestion.description || true"></Simditor>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 选项部分 -->
        <el-row>
          <el-col :span="24">
            <el-form-item :label="$t('m.Options')" required>
              <!-- 添加选项调试信息 -->
              <div v-if="choiceQuestion.options.every(opt => !opt.text)" class="debug-info">
                <el-alert
                  title="所有选项都为空"
                  type="warning"
                  :closable="false"
                  show-icon>
                  <div slot="default">
                    <p>选项数据没有正确加载。原始选项数据可能格式不正确。</p>
                    <p>请查看浏览器控制台的调试信息。</p>
                  </div>
                </el-alert>
              </div>
              
              <div v-for="(option, index) in choiceQuestion.options" :key="index" class="option-item">
                <el-row :gutter="10">
                  <el-col :span="2">
                    <!-- 单选题显示单选按钮 -->
                    <el-radio v-if="choiceQuestion.question_type === 'single'" v-model="choiceQuestion.correct_answer" :label="String.fromCharCode(65 + index)">{{ String.fromCharCode(65 + index) }}</el-radio>
                    <!-- 多选题显示复选框 -->
                    <el-checkbox v-else v-model="option.is_correct">{{ String.fromCharCode(65 + index) }}</el-checkbox>
                  </el-col>
                  <el-col :span="20">
                    <div class="option-editor">
                      <label>选项 {{ String.fromCharCode(65 + index) }}:</label>
                      <Simditor v-model="option.text" :placeholder="'Option ' + String.fromCharCode(65 + index)"></Simditor>
                    </div>
                  </el-col>
                  <el-col :span="2">
                    <el-button v-if="choiceQuestion.options.length > 2" @click="removeOption(index)" type="danger" icon="el-icon-delete" size="small" circle></el-button>
                  </el-col>
                </el-row>
              </div>
              <el-button v-if="choiceQuestion.options.length < 6" @click="addOption" type="primary" icon="el-icon-plus" size="small">{{$t('m.Add_Option')}}</el-button>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item prop="explanation" :label="$t('m.Explanation')">
              <Simditor v-model="choiceQuestion.explanation" :placeholder="$t('m.Enter_explanation_optional')"></Simditor>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <div class="save-button">
            <el-button type="primary" @click="submitChoiceQuestion" :loading="submitting">{{$t('m.Save')}}</el-button>
          </div>
        </el-form-item>
      </el-form>
    </Panel>
  </div>
</template>

<script>
  import api from '../../api.js'
  import Simditor from '../../components/Simditor.vue'

  export default {
    name: 'ChoiceQuestion',
    components: {
      Simditor
    },
    data () {
      return {
        title: this.$t('m.Create_Choice_Question'),
        submitting: false,
        categories: [],
        tags: [],
        showCategoryDropdown: false,
        choiceQuestion: {
          title: '',
          description: '',
          difficulty: 'Easy',
          question_type: 'single',
          category: null,
          tags: [],
          language: 'text',
          options: [
            { text: '', is_correct: false },
            { text: '', is_correct: false },
            { text: '', is_correct: false },
            { text: '', is_correct: false }
          ],
          correct_answer: 'A',
          explanation: '',
          visible: true
        },
        ruleValidate: {
          title: [
            {required: true, message: this.$t('m.Title_is_required'), trigger: 'blur'}
          ],
          description: [
            {required: true, message: this.$t('m.Description_is_required'), trigger: 'blur'}
          ],
          difficulty: [
            {required: true, message: this.$t('m.Difficulty_is_required'), trigger: 'change'}
          ]
        }
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
        
        const cleanCategories = deepDeduplication(this.categories)
        
        // 扁平化处理
        const flatten = (categories, level = 0) => {
          let result = []
          categories.forEach(category => {
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
        if (!this.choiceQuestion.category) return ''
        const category = this.flattenedCategories.find(cat => cat.id === this.choiceQuestion.category)
        return category ? category.name : ''
      }
    },
    mounted () {
      this.getCategories()
      this.getTags()
      if (this.$route.name === 'edit-choice-question') {
        this.title = this.$t('m.Edit_Choice_Question')
        this.getChoiceQuestion(this.$route.params.choiceQuestionId)
      } else {
        this.title = this.$t('m.Create_Choice_Question')
      }
    },
    methods: {
      submitChoiceQuestion () {
        this.$refs['formValidate'].validate((valid) => {
          if (!valid) {
            this.$error(this.$t('m.Please_check_the_error_fields'))
            return
          }
          
          // 验证选项
          const validOptions = this.choiceQuestion.options.filter(option => option.text.trim() !== '')
          if (validOptions.length < 2) {
            this.$error(this.$t('m.At_least_2_options_are_required'))
            return
          }
          
          // 验证正确答案
          if (this.choiceQuestion.question_type === 'single') {
            const correctIndex = this.choiceQuestion.correct_answer.charCodeAt(0) - 65
            if (correctIndex >= validOptions.length || !validOptions[correctIndex].text.trim()) {
              this.$error(this.$t('m.Please_select_a_valid_correct_answer'))
              return
            }
          } else {
            // 多选题验证
            const hasCorrectAnswer = validOptions.some(option => option.is_correct)
            if (!hasCorrectAnswer) {
              this.$error(this.$t('m.Please_select_at_least_one_correct_answer'))
              return
            }
          }

          this.submitting = true
          const funcName = this.$route.name === 'edit-choice-question' ? 'editChoiceQuestion' : 'createChoiceQuestion'
          
          // 处理数据
          let processedData = { ...this.choiceQuestion }
          processedData.options = validOptions
          
          // 根据选项的is_correct状态生成正确答案
          if (this.choiceQuestion.question_type === 'multiple') {
            const correctAnswers = []
            validOptions.forEach((option, index) => {
              if (option.is_correct) {
                correctAnswers.push(String.fromCharCode(65 + index)) // A, B, C, D...
              }
            })
            processedData.correct_answer = correctAnswers.join(',')
          }
          
          // 处理标签ID
          if (processedData.tags && processedData.tags.length > 0) {
            processedData.tag_ids = this.tags.filter(tag => 
              processedData.tags.includes(tag.name)
            ).map(tag => tag.id)
          }
          
          // 处理分类ID
          if (processedData.category) {
            processedData.category_id = processedData.category
            delete processedData.category
          }
          
          delete processedData.tags
          
          const data = processedData
          
          api[funcName](data).then(res => {
            this.submitting = false
            this.$success(this.$t('m.Saved_successfully'))
            this.$router.push({name: 'choice-question-list'})
          }).catch(() => {
            this.submitting = false
          })
        })
      },
      getChoiceQuestion (choiceQuestionId) {
        console.log('📝 开始加载选择题数据, ID:', choiceQuestionId)
        
        api.getChoiceQuestion(choiceQuestionId).then(res => {
          console.log('📊 API响应数据:', res)
          let data = res.data.data
          console.log('📄 题目原始数据:', data)
          
          if (!data) {
            console.error('❌ 没有获取到题目数据')
            this.$message.error('无法获取题目数据')
            return
          }
          
          // 处理选项和正确答案 - 更强的容错性
          let options = []
          
          // 尝试多种可能的选项数据格式
          if (data.options && Array.isArray(data.options)) {
            console.log('📅 处理选项数据:', data.options)
            
            options = data.options.map(option => {
              // 支持多种选项格式
              if (typeof option === 'string') {
                // 字符串格式: "A. 选项内容"
                return { text: option, is_correct: false }
              } else if (option.key && option.text) {
                // key-text 格式: {key: 'A', text: 'A. 正确'}
                return { text: option.text, is_correct: option.is_correct || false }
              } else if (option.content) {
                // content 字段格式
                return { text: option.content, is_correct: option.is_correct || false }
              } else if (option.text) {
                // text 字段格式
                return { text: option.text, is_correct: option.is_correct || false }
              } else {
                // 其他格式，尝试直接使用
                return { text: String(option), is_correct: false }
              }
            })
          } else {
            // 如果没有选项数据，创建默认选项
            console.log('⚠️ 没有找到选项数据，使用默认选项')
            options = [
              { text: '', is_correct: false },
              { text: '', is_correct: false },
              { text: '', is_correct: false },
              { text: '', is_correct: false }
            ]
          }
          
          // 根据correct_answer设置选项的is_correct状态
          if (data.correct_answer) {
            console.log('🎯 处理正确答案:', data.correct_answer, '题目类型:', data.question_type)
            
            if (data.question_type === 'multiple') {
              // 多选题：支持多种格式
              let correctAnswers = []
              if (typeof data.correct_answer === 'string') {
                // 字符串格式："A,B" 或 "AB"
                if (data.correct_answer.includes(',')) {
                  correctAnswers = data.correct_answer.split(',')
                } else {
                  correctAnswers = data.correct_answer.split('')
                }
              } else if (Array.isArray(data.correct_answer)) {
                // 数组格式：["A", "B"]
                correctAnswers = data.correct_answer
              }
              
              options.forEach((option, index) => {
                const optionKey = String.fromCharCode(65 + index) // A, B, C, D...
                option.is_correct = correctAnswers.includes(optionKey)
              })
            } else {
              // 单选题
              const correctAnswer = String(data.correct_answer).charAt(0) // 取第一个字符
              const correctIndex = correctAnswer.charCodeAt(0) - 65 // A=0, B=1, C=2...
              
              options.forEach((option, index) => {
                option.is_correct = index === correctIndex
              })
            }
          }
          
          console.log('📋 处理后的选项数据:', options)
          
          // 构建choiceQuestion对象 - 支持多种字段名
          this.choiceQuestion = {
            id: data.id,
            title: data.title || '',
            description: data.description || data.content || '', // 支持description或content字段
            difficulty: data.difficulty || 'Easy',
            question_type: data.question_type || 'single',
            category: data.category ? (data.category.id || data.category) : null,
            tags: data.tags ? data.tags.map(tag => tag.name || tag) : [],
            options: options,
            correct_answer: data.correct_answer || 'A',
            explanation: data.explanation || '',
            visible: data.visible !== undefined ? data.visible : true
          }
          
          console.log('✅ 最终的choiceQuestion数据:', this.choiceQuestion)
          
          // 检查数据完整性
          if (!this.choiceQuestion.title) {
            console.warn('⚠️ 题目标题为空')
          }
          if (!this.choiceQuestion.description) {
            console.warn('⚠️ 题目描述为空')
          }
          if (options.every(opt => !opt.text)) {
            console.warn('⚠️ 所有选项都为空')
          }
          
        }).catch(error => {
          console.error('❌ 获取选择题数据失败:', error)
          this.$message.error('获取题目数据失败: ' + (error.message || '未知错误'))
        })
      },
      getCategories () {
        api.getChoiceQuestionCategories().then(res => {
          this.categories = res.data.data || []
        }).catch(() => {
          this.categories = []
        })
      },
      getTags () {
        api.getChoiceQuestionTags().then(res => {
          this.tags = res.data.data || []
        }).catch(() => {
          this.tags = []
        })
      },
      addOption () {
        if (this.choiceQuestion.options.length < 6) {
          this.choiceQuestion.options.push({ text: '', is_correct: false })
        }
      },
      removeOption (index) {
        if (this.choiceQuestion.options.length > 2) {
          this.choiceQuestion.options.splice(index, 1)
          // 调整正确答案如果需要
          const correctIndex = this.choiceQuestion.correct_answer.charCodeAt(0) - 65
          if (correctIndex >= this.choiceQuestion.options.length) {
            this.choiceQuestion.correct_answer = 'A'
          }
        }
      },
      onQuestionTypeChange () {
        // 当题目类型改变时，重置选项的正确答案状态
        this.choiceQuestion.options.forEach(option => {
          option.is_correct = false
        })
        this.choiceQuestion.correct_answer = 'A'
      },
      // 分类选择器相关方法
      toggleCategoryDropdown() {
        this.showCategoryDropdown = !this.showCategoryDropdown
      },
      selectCategory(category) {
        this.choiceQuestion.category = category.id
        this.showCategoryDropdown = false
      }
    },
    watch: {
      '$route' (newVal, oldVal) {
        if (newVal !== oldVal) {
          if (newVal.name === 'edit-choice-question') {
            this.title = this.$t('m.Edit_Choice_Question')
            this.getChoiceQuestion(newVal.params.choiceQuestionId)
          } else {
            this.title = this.$t('m.Create_Choice_Question')
          }
        }
      },
      // 监听描述变化，自动生成标题
      'choiceQuestion.description' (newVal) {
        if (newVal && newVal.trim()) {
          // 从HTML内容中提取纯文本
          const tempDiv = document.createElement('div')
          tempDiv.innerHTML = newVal
          const plainText = tempDiv.textContent || tempDiv.innerText || ''
          
          // 截取前12个字符作为标题
          const autoTitle = plainText.trim().substring(0, 12)
          if (autoTitle) {
            this.choiceQuestion.title = autoTitle + (plainText.trim().length > 12 ? '...' : '')
          }
        }
      }
    }
  }
</script>

<style scoped lang="less">
  .title-input, .difficulty-select {
    width: 100%;
  }
  
  .option-item {
    margin-bottom: 10px;
  }
  
  .save-button {
    text-align: center;
  }
  
  // 调试信息样式
  .debug-info {
    margin-bottom: 15px;
    
    .el-alert {
      border-radius: 6px;
      
      p {
        margin: 5px 0;
        font-size: 14px;
        line-height: 1.5;
      }
    }
  }
  
  // 选项编辑器样式
  .option-editor {
    label {
      display: block;
      margin-bottom: 5px;
      font-size: 14px;
      font-weight: 500;
      color: #606266;
    }
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

    &:hover {
      border-color: #c0c4cc;
    }

    &.active {
      border-color: #409eff;
    }
  }

  .selected-text {
    flex: 1;
    color: #606266;
    
    &.placeholder {
      color: #c0c4cc;
    }
  }

  .el-icon-arrow-down {
    margin-left: 8px;
    transition: transform 0.3s;
    color: #c0c4cc;
    
    &.rotate {
      transform: rotate(180deg);
    }
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

    &:last-child {
      border-bottom: none;
    }

    &:hover {
      background-color: #f5f7fa;
    }

    &.selected {
      background-color: #ecf5ff;
      color: #409eff;
    }

    /* 层级样式 */
    &.level-0 {
      padding-left: 12px;
      font-weight: 500;
    }

    &.level-1 {
      padding-left: 28px;
    }

    &.level-2 {
      padding-left: 44px;
    }

    &.level-3 {
      padding-left: 60px;
    }
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