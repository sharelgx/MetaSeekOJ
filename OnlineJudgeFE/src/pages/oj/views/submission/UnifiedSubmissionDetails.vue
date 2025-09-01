<template>
  <div class="flex-container">
    <div id="main">
      <Panel shadow>
        <div slot="title">{{ $t('m.Submission_Details') }}</div>
        <template v-if="!loading">
          <div class="submission-info">
            <Row :gutter="20">
              <Col :span="12">
                <div class="info-item">
                  <span class="label">{{ $t('m.Problem') }}:</span>
                  <a @click="goToProblem" class="problem-link">
                    {{ submission.problem.title }}
                  </a>
                </div>
                <div class="info-item">
                  <span class="label">{{ $t('m.Author') }}:</span>
                  <a @click="goToUser" class="user-link">
                    {{ submission.user.username }}
                  </a>
                </div>
                <div class="info-item">
                  <span class="label">{{ $t('m.Submit_Time') }}:</span>
                  <span>{{ submission.create_time | localtime }}</span>
                </div>
                <div class="info-item">
                  <span class="label">{{ $t('m.Type') }}:</span>
                  <Tag :color="submission.question_type === 'programming' ? 'blue' : 'green'">
                    {{ submission.question_type === 'programming' ? $t('m.Programming') : $t('m.Choice_Question') }}
                  </Tag>
                </div>
              </Col>
              <Col :span="12">
                <div class="info-item">
                  <span class="label">{{ $t('m.Status') }}:</span>
                  <Tag :color="getStatusColor(submission.result)">
                    {{ getStatusText(submission.result) }}
                  </Tag>
                </div>
                <div class="info-item" v-if="submission.question_type === 'programming'">
                  <span class="label">{{ $t('m.Time') }}:</span>
                  <span>{{ submission.statistic_info ? utils.submissionTimeFormat(submission.statistic_info.time_cost) : '-' }}</span>
                </div>
                <div class="info-item" v-if="submission.question_type === 'programming'">
                  <span class="label">{{ $t('m.Memory') }}:</span>
                  <span>{{ submission.statistic_info ? utils.submissionMemoryFormat(submission.statistic_info.memory_cost) : '-' }}</span>
                </div>
                <div class="info-item" v-if="submission.question_type === 'choice'">
                  <span class="label">{{ $t('m.Score') }}:</span>
                  <span>{{ submission.score || 0 }}</span>
                </div>
                <div class="info-item">
                  <span class="label">{{ $t('m.Language') }}:</span>
                  <span>{{ submission.question_type === 'choice' ? $t('m.Choice_Question') : submission.language }}</span>
                </div>
              </Col>
            </Row>
          </div>

          <!-- 编程题代码显示 -->
          <div v-if="submission.question_type === 'programming'" class="code-section">
            <div class="section-title">{{ $t('m.Code') }}</div>
            <div class="code-container">
              <pre><code class="hljs" v-html="highlightedCode"></code></pre>
            </div>
          </div>

          <!-- 选择题答案显示 -->
          <div v-if="submission.question_type === 'choice'" class="answer-section">
            <div class="section-title">{{ $t('m.Answer_Details') }}</div>
            <div class="answer-container">
              <div class="answer-item">
                <span class="answer-label">{{ $t('m.Selected_Answer') }}:</span>
                <Tag v-for="option in getSelectedOptions(submission.selected_answer)" 
                     :key="option" 
                     :color="isCorrectOption(option) ? 'success' : 'error'"
                     class="option-tag">
                  {{ option }}
                </Tag>
              </div>
              <div class="answer-item" v-if="submission.correct_answer">
                <span class="answer-label">{{ $t('m.Correct_Answer') }}:</span>
                <Tag v-for="option in getSelectedOptions(submission.correct_answer)" 
                     :key="option" 
                     color="success"
                     class="option-tag">
                  {{ option }}
                </Tag>
              </div>
              <div class="answer-item" v-if="submission.time_spent">
                <span class="answer-label">{{ $t('m.Time_Spent') }}:</span>
                <span>{{ submission.time_spent }}s</span>
              </div>
            </div>
          </div>

          <!-- 编程题判题详情 -->
          <div v-if="submission.question_type === 'programming' && submission.info && submission.info.data" class="judge-details">
            <div class="section-title">{{ $t('m.Judge_Details') }}</div>
            <Table :columns="judgeColumns" :data="submission.info.data" size="small"></Table>
          </div>

          <!-- 编译错误信息 -->
          <div v-if="submission.question_type === 'programming' && isCE" class="compile-error">
            <div class="section-title">{{ $t('m.Compile_Error') }}</div>
            <pre class="error-content">{{ submission.info.data }}</pre>
          </div>

          <!-- 管理员信息 -->
          <div v-if="isAdminRole" class="admin-info">
            <div class="section-title">{{ $t('m.Admin_Info') }}</div>
            <div class="admin-info-content">
              <p><strong>IP:</strong> {{ submission.ip || submission.ip_address }}</p>
              <p v-if="submission.user_agent"><strong>User Agent:</strong> {{ submission.user_agent }}</p>
              <p v-if="submission.contest_id"><strong>Contest ID:</strong> {{ submission.contest_id }}</p>
            </div>
          </div>

          <!-- 分享按钮 -->
          <div v-if="submission.question_type === 'programming' && canShare" id="share-btn">
            <Button v-if="!submission.shared" 
                    type="success" 
                    @click="shareSubmission(true)"
                    :loading="shareLoading">
              {{ $t('m.Share') }}
            </Button>
            <Button v-else 
                    type="warning" 
                    @click="shareSubmission(false)"
                    :loading="shareLoading">
              {{ $t('m.Unshare') }}
            </Button>
          </div>
        </template>
        
        <div v-else class="loading-container">
          <Spin size="large"></Spin>
        </div>
      </Panel>
    </div>
  </div>
</template>

<script>
  import { mapGetters } from 'vuex'
  import api from '@oj/api'
  import { JUDGE_STATUS, USER_TYPE } from '@/utils/constants'
  import utils from '@/utils/utils'
  import time from '@/utils/time'
  import hljs from 'highlight.js'

  export default {
    name: 'UnifiedSubmissionDetails',
    data () {
      return {
        submission: {
          result: '0',
          code: '',
          info: {
            data: []
          },
          statistic_info: {
            time_cost: '',
            memory_cost: ''
          },
          problem: {},
          user: {}
        },
        loading: false,
        shareLoading: false,
        judgeColumns: [
          {
            title: '#',
            key: 'test_case',
            width: 80
          },
          {
            title: this.$i18n.t('m.Status'),
            render: (h, params) => {
              const status = JUDGE_STATUS[params.row.result]
              return h('Tag', {
                props: {
                  color: status ? status.color : 'default'
                }
              }, status ? this.$i18n.t('m.' + status.name.replace(/ /g, '_')) : params.row.result)
            }
          },
          {
            title: this.$i18n.t('m.Time'),
            render: (h, params) => {
              return h('span', utils.submissionTimeFormat(params.row.cpu_time))
            }
          },
          {
            title: this.$i18n.t('m.Memory'),
            render: (h, params) => {
              return h('span', utils.submissionMemoryFormat(params.row.memory))
            }
          }
        ],
        utils: utils
      }
    },
    mounted () {
      this.getSubmission()
    },
    methods: {
      getSubmission () {
        this.loading = true
        api.getUnifiedSubmissionDetail(this.$route.params.id).then(res => {
          this.loading = false
          this.submission = res.data.data
          
          // 为编程题添加判题详情列
          if (this.submission.question_type === 'programming' && 
              this.submission.info && 
              this.submission.info.data && 
              this.submission.info.data.length > 0) {
            
            // 检查是否有分数列
            if (this.submission.info.data[0].score !== undefined) {
              const scoreColumn = {
                title: this.$i18n.t('m.Score'),
                align: 'center',
                key: 'score'
              }
              this.judgeColumns.push(scoreColumn)
            }
            
            // 管理员额外列
            if (this.isAdminRole) {
              const adminColumns = [
                {
                  title: this.$i18n.t('m.Real_Time'),
                  align: 'center',
                  render: (h, params) => {
                    return h('span', utils.submissionTimeFormat(params.row.real_time))
                  }
                },
                {
                  title: this.$i18n.t('m.Signal'),
                  align: 'center',
                  key: 'signal'
                }
              ]
              this.judgeColumns = this.judgeColumns.concat(adminColumns)
            }
          }
        }).catch(() => {
          this.loading = false
        })
      },
      
      shareSubmission (shared) {
        if (this.submission.question_type !== 'programming') {
          return
        }
        
        this.shareLoading = true
        let data = { id: this.submission.id, shared: shared }
        api.updateSubmission(data).then(res => {
          this.shareLoading = false
          this.submission.shared = shared
          this.$success(this.$i18n.t('m.Succeeded'))
        }).catch(() => {
          this.shareLoading = false
        })
      },
      
      goToProblem () {
        if (this.submission.question_type === 'choice') {
          this.$router.push({
            name: 'choice-question-detail',
            params: { questionId: this.submission.problem.id }
          })
        } else {
          this.$router.push({
            name: 'problem-details',
            params: { problemID: this.submission.problem.display_id }
          })
        }
      },
      
      goToUser () {
        this.$router.push({
          name: 'user-home',
          query: { username: this.submission.user.username }
        })
      },
      
      getStatusColor (result) {
        const status = JUDGE_STATUS[result]
        return status ? status.color : 'default'
      },
      
      getStatusText (result) {
        const status = JUDGE_STATUS[result]
        return status ? this.$i18n.t('m.' + status.name.replace(/ /g, '_')) : result
      },
      
      getSelectedOptions (answer) {
        if (!answer) return []
        if (typeof answer === 'string') {
          try {
            const parsed = JSON.parse(answer)
            return Array.isArray(parsed) ? parsed : [answer]
          } catch (e) {
            return [answer]
          }
        }
        return Array.isArray(answer) ? answer : [answer]
      },
      
      isCorrectOption (option) {
        if (!this.submission.correct_answer) return false
        const correctOptions = this.getSelectedOptions(this.submission.correct_answer)
        return correctOptions.includes(option)
      }
    },
    computed: {
      ...mapGetters(['isAuthenticated', 'user']),
      
      highlightedCode () {
        if (!this.submission.code) return ''
        return hljs.highlightAuto(this.submission.code).value
      },
      
      isCE () {
        return this.submission.result === -2
      },
      
      isAdminRole () {
        return this.user && this.user.admin_type === USER_TYPE.SUPER_ADMIN
      },
      
      canShare () {
        return this.isAuthenticated && 
               this.submission.user && 
               this.submission.user.id === this.user.id
      }
    },
    filters: {
      localtime: time.utcToLocal
    }
  }
</script>

<style scoped lang="less">
  .flex-container {
    #main {
      flex: auto;
      margin-right: 18px;
    }
  }

  .submission-info {
    margin-bottom: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 4px;
    
    .info-item {
      margin-bottom: 10px;
      
      .label {
        font-weight: 600;
        margin-right: 8px;
        color: #495057;
      }
      
      .problem-link, .user-link {
        color: #007bff;
        cursor: pointer;
        text-decoration: none;
        
        &:hover {
          text-decoration: underline;
        }
      }
    }
  }

  .section-title {
    font-size: 16px;
    font-weight: 600;
    margin: 20px 0 10px 0;
    color: #343a40;
    border-bottom: 2px solid #007bff;
    padding-bottom: 5px;
  }

  .code-section {
    margin-bottom: 20px;
    
    .code-container {
      background: #f8f9fa;
      border: 1px solid #dee2e6;
      border-radius: 4px;
      overflow-x: auto;
      
      pre {
        margin: 0;
        padding: 15px;
        background: none;
        border: none;
        white-space: pre-wrap;
        word-wrap: break-word;
        word-break: break-all;
      }
    }
  }

  .answer-section {
    margin-bottom: 20px;
    
    .answer-container {
      background: #f8f9fa;
      border: 1px solid #dee2e6;
      border-radius: 4px;
      padding: 15px;
      
      .answer-item {
        margin-bottom: 10px;
        
        .answer-label {
          font-weight: 600;
          margin-right: 8px;
          color: #495057;
        }
        
        .option-tag {
          margin-right: 5px;
        }
      }
    }
  }

  .judge-details {
    margin-bottom: 20px;
  }

  .compile-error {
    margin-bottom: 20px;
    
    .error-content {
      background: #f8d7da;
      border: 1px solid #f5c6cb;
      border-radius: 4px;
      padding: 15px;
      color: #721c24;
      white-space: pre-wrap;
      word-wrap: break-word;
      word-break: break-all;
    }
  }

  .admin-info {
    margin-bottom: 20px;
    
    .admin-info-content {
      background: #d1ecf1;
      border: 1px solid #bee5eb;
      border-radius: 4px;
      padding: 15px;
      
      p {
        margin: 5px 0;
      }
    }
  }

  #share-btn {
    float: right;
    margin-top: 5px;
    margin-right: 10px;
  }

  .loading-container {
    text-align: center;
    padding: 50px;
  }
</style>