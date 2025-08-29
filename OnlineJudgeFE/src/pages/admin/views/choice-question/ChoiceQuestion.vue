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
          <el-col :span="12">
            <el-form-item prop="difficulty" :label="$t('m.Difficulty')" required>
              <el-select v-model="choiceQuestion.difficulty" class="difficulty-select">
                <el-option label="Easy" value="Easy"></el-option>
                <el-option label="Medium" value="Medium"></el-option>
                <el-option label="Hard" value="Hard"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="visible" :label="$t('m.Visible')">
              <el-switch v-model="choiceQuestion.visible"></el-switch>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item prop="description" :label="$t('m.Description')" required>
              <el-input
                type="textarea"
                :autosize="{minRows: 4, maxRows: 10}"
                :placeholder="$t('m.Description')"
                v-model="choiceQuestion.description">
              </el-input>
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
                    <el-radio v-model="choiceQuestion.correct_answer" :label="String.fromCharCode(65 + index)">{{ String.fromCharCode(65 + index) }}</el-radio>
                  </el-col>
                  <el-col :span="20">
                    <el-input v-model="option.text" :placeholder="'Option ' + String.fromCharCode(65 + index)"></el-input>
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
            <el-form-item prop="explanation" :label="$t('m.Explanation')">
              <el-input
                type="textarea"
                :autosize="{minRows: 3, maxRows: 8}"
                placeholder="Explanation for the correct answer (optional)"
                v-model="choiceQuestion.explanation">
              </el-input>
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

  export default {
    name: 'ChoiceQuestion',
    data () {
      return {
        title: 'Create Choice Question',
        submitting: false,
        choiceQuestion: {
          title: '',
          description: '',
          difficulty: 'Easy',
          options: [
            { text: '' },
            { text: '' },
            { text: '' },
            { text: '' }
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
          const correctIndex = this.choiceQuestion.correct_answer.charCodeAt(0) - 65
          if (correctIndex >= validOptions.length || !validOptions[correctIndex].text.trim()) {
            this.$error('Please select a valid correct answer')
            return
          }

          this.submitting = true
          const funcName = this.$route.name === 'edit-choice-question' ? 'editChoiceQuestion' : 'createChoiceQuestion'
          const data = {
            ...this.choiceQuestion,
            options: validOptions
          }
          
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
            options: data.options || [
              { text: '' },
              { text: '' },
              { text: '' },
              { text: '' }
            ],
            correct_answer: data.correct_answer || 'A',
            explanation: data.explanation || '',
            visible: data.visible
          }
        })
      },
      addOption () {
        if (this.choiceQuestion.options.length < 6) {
          this.choiceQuestion.options.push({ text: '' })
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