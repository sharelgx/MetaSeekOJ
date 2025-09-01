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
              <el-select v-model="choiceQuestion.category" placeholder="Select Category" clearable>
                <el-option
                  v-for="category in categories"
                  :key="category.id"
                  :label="category.name"
                  :value="category.id">
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item prop="question_type" :label="题目类型" required>
              <el-select v-model="choiceQuestion.question_type" placeholder="选择题目类型">
                <el-option label="单选题" value="single"></el-option>
                <el-option label="多选题" value="multiple"></el-option>
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
                placeholder="Select or create tags">
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
              <Simditor v-model="choiceQuestion.description"></Simditor>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 选项部分 -->
        <el-row>
          <el-col :span="24">
            <el-form-item :label="$t('m.Options')" required>
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
              <el-button v-if="choiceQuestion.options.length < 6" @click="addOption" type="primary" icon="el-icon-plus" size="small">Add Option</el-button>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item prop="explanation" :label="解析">
              <Simditor v-model="choiceQuestion.explanation" placeholder="请输入答案解析（可选）"></Simditor>
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
        title: 'Create Choice Question',
        submitting: false,
        categories: [],
        tags: [],
        choiceQuestion: {
          title: '',
          description: '',
          difficulty: 'Easy',
          question_type: 'single',
          category: null,
          tags: [],
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
            {required: true, message: 'Title is required', trigger: 'blur'}
          ],
          description: [
            {required: true, message: 'Description is required', trigger: 'blur'}
          ],
          difficulty: [
            {required: true, message: 'Difficulty is required', trigger: 'change'}
          ]
        }
      }
    },
    mounted () {
      this.getCategories()
      this.getTags()
      if (this.$route.name === 'edit-choice-question') {
        this.title = 'Edit Choice Question'
        this.getChoiceQuestion(this.$route.params.choiceQuestionId)
      } else {
        this.title = 'Create Choice Question'
      }
    },
    methods: {
      submitChoiceQuestion () {
        this.$refs['formValidate'].validate((valid) => {
          if (!valid) {
            this.$error('Please check the error fields')
            return
          }
          
          // 验证选项
          const validOptions = this.choiceQuestion.options.filter(option => option.text.trim() !== '')
          if (validOptions.length < 2) {
            this.$error('At least 2 options are required')
            return
          }
          
          // 验证正确答案
          if (this.choiceQuestion.question_type === 'single') {
            const correctIndex = this.choiceQuestion.correct_answer.charCodeAt(0) - 65
            if (correctIndex >= validOptions.length || !validOptions[correctIndex].text.trim()) {
              this.$error('Please select a valid correct answer')
              return
            }
          } else {
            // 多选题验证
            const hasCorrectAnswer = validOptions.some(option => option.is_correct)
            if (!hasCorrectAnswer) {
              this.$error('Please select at least one correct answer for multiple choice question')
              return
            }
          }

          this.submitting = true
          const funcName = this.$route.name === 'edit-choice-question' ? 'editChoiceQuestion' : 'createChoiceQuestion'
          
          // 处理数据
          let processedData = { ...this.choiceQuestion }
          processedData.options = validOptions
          
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
            this.$success('Saved successfully')
            this.$router.push({name: 'choice-question-list'})
          }).catch(() => {
            this.submitting = false
          })
        })
      },
      getChoiceQuestion (choiceQuestionId) {
        api.getChoiceQuestion(choiceQuestionId).then(res => {
          let data = res.data.data
          this.choiceQuestion = {
            id: data.id,
            title: data.title,
            description: data.description,
            difficulty: data.difficulty,
            question_type: data.question_type || 'single',
            category: data.category ? data.category.id : null,
            tags: data.tags ? data.tags.map(tag => tag.name) : [],
            options: data.options || [
              { text: '', is_correct: false },
              { text: '', is_correct: false },
              { text: '', is_correct: false },
              { text: '', is_correct: false }
            ],
            correct_answer: data.correct_answer || 'A',
            explanation: data.explanation || '',
            visible: data.visible
          }
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
      }
    },
    watch: {
      '$route' (newVal, oldVal) {
        if (newVal !== oldVal) {
          if (newVal.name === 'edit-choice-question') {
            this.title = 'Edit Choice Question'
            this.getChoiceQuestion(newVal.params.choiceQuestionId)
          } else {
            this.title = 'Create Choice Question'
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
</style>