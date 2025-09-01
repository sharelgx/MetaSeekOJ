<template>
  <div class="flex-container">
    <div id="main">
      <Panel shadow>
        <div slot="title">{{ title }}</div>
        <div slot="extra">
          <ul class="filter">
            <li>
              <Dropdown @on-click="handleResultChange" placement="bottom-start">
                <span>{{ status }}
                  <Icon type="md-arrow-dropdown"></Icon>
                </span>
                <DropdownMenu slot="list">
                  <DropdownItem name="">{{ $t('m.All') }}</DropdownItem>
                  <DropdownItem v-for="status in Object.keys(JUDGE_STATUS)" :key="status" :name="status">
                    {{ $t('m.' + JUDGE_STATUS[status].name.replace(/ /g, '_')) }}
                  </DropdownItem>
                </DropdownMenu>
              </Dropdown>
            </li>
            
            <li>
              <Dropdown @on-click="handleTypeChange" placement="bottom-start">
                <span>{{ questionType }}
                  <Icon type="md-arrow-dropdown"></Icon>
                </span>
                <DropdownMenu slot="list">
                  <DropdownItem name="all">{{ $t('m.All_Types') }}</DropdownItem>
                  <DropdownItem name="programming">{{ $t('m.Programming') }}</DropdownItem>
                  <DropdownItem name="choice">{{ $t('m.Choice_Question') }}</DropdownItem>
                </DropdownMenu>
              </Dropdown>
            </li>

            <li>
              <i-switch size="large" v-model="formFilter.myself" @on-change="handleQueryChange">
                <span slot="open">{{ $t('m.Mine') }}</span>
                <span slot="close">{{ $t('m.All') }}</span>
              </i-switch>
            </li>
            <li>
              <Input v-model="formFilter.username" :placeholder="$t('m.Search_Author')" @on-enter="handleQueryChange"/>
            </li>
            <li>
              <Button type="info" icon="md-refresh" @click="getSubmissions">{{ $t('m.Refresh') }}</Button>
            </li>
          </ul>
        </div>
        <Table stripe :disabled-hover="true" :columns="columns" :data="submissions" :loading="loadingTable"></Table>
        <Pagination :total="total" :page-size="limit" @on-change="changeRoute" :current.sync="page"></Pagination>
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
  import Pagination from '@/pages/oj/components/Pagination'

  export default {
    name: 'UnifiedSubmissionList',
    components: {
      Pagination
    },
    data () {
      return {
        formFilter: {
          myself: false,
          result: '',
          username: '',
          question_type: 'all'
        },
        columns: [
          {
            title: this.$i18n.t('m.When'),
            align: 'center',
            width: 150,
            render: (h, params) => {
              return h('span', time.utcToLocal(params.row.submit_time))
            }
          },
          {
            title: this.$i18n.t('m.ID'),
            align: 'center',
            width: 100,
            render: (h, params) => {
              if (params.row.show_link) {
                return h('span', {
                  style: {
                    color: '#57a3f3',
                    cursor: 'pointer'
                  },
                  on: {
                    click: () => {
                      this.$router.push('/status/' + params.row.id)
                    }
                  }
                }, params.row.id.toString().slice(0, 12))
              } else {
                return h('span', params.row.id.toString().slice(0, 12))
              }
            }
          },
          {
            title: this.$i18n.t('m.Problem'),
            align: 'center',
            render: (h, params) => {
              return h('span', {
                style: {
                  color: '#495060',
                  cursor: 'pointer'
                },
                on: {
                  click: () => {
                    if (params.row.question_type === 'choice') {
                      this.$router.push({
                        name: 'choice-question-detail',
                        params: { questionId: params.row.question_id }
                      })
                    } else {
                      this.$router.push({
                        name: 'problem-details',
                        params: { problemID: params.row.question_display_id }
                      })
                    }
                  }
                }
              }, params.row.question_title)
            }
          },
          {
            title: this.$i18n.t('m.Type'),
            align: 'center',
            width: 100,
            render: (h, params) => {
              const typeMap = {
                'programming': this.$i18n.t('m.Programming'),
                'choice': this.$i18n.t('m.Choice_Question')
              }
              return h('Tag', {
                props: {
                  color: params.row.question_type === 'programming' ? 'blue' : 'green'
                }
              }, typeMap[params.row.question_type] || params.row.question_type)
            }
          },
          {
            title: this.$i18n.t('m.Status'),
            align: 'center',
            width: 150,
            render: (h, params) => {
              const status = JUDGE_STATUS[params.row.result]
              if (!status) {
                return h('span', params.row.result)
              }
              return h('Tag', {
                props: {
                  color: status.color
                }
              }, this.$i18n.t('m.' + status.name.replace(/ /g, '_')))
            }
          },
          {
            title: this.$i18n.t('m.Score'),
            align: 'center',
            width: 80,
            render: (h, params) => {
              return h('span', params.row.score || 0)
            }
          },
          {
            title: this.$i18n.t('m.Time'),
            align: 'center',
            width: 100,
            render: (h, params) => {
              if (params.row.question_type === 'choice') {
                return h('span', params.row.time_spent ? `${params.row.time_spent}s` : '-')
              } else {
                return h('span', utils.submissionTimeFormat(params.row.time_cost))
              }
            }
          },
          {
            title: this.$i18n.t('m.Memory'),
            align: 'center',
            width: 100,
            render: (h, params) => {
              if (params.row.question_type === 'choice') {
                return h('span', '-')
              } else {
                return h('span', utils.submissionMemoryFormat(params.row.memory_cost))
              }
            }
          },
          {
            title: this.$i18n.t('m.Language'),
            align: 'center',
            width: 120,
            render: (h, params) => {
              if (params.row.question_type === 'choice') {
                return h('span', this.$i18n.t('m.Choice_Question'))
              } else {
                return h('span', params.row.language)
              }
            }
          },
          {
            title: this.$i18n.t('m.Author'),
            align: 'center',
            width: 120,
            render: (h, params) => {
              return h('a', {
                style: {
                  'display': 'inline-block',
                  'max-width': '150px'
                },
                on: {
                  click: () => {
                    this.$router.push({
                      name: 'user-home',
                      query: { username: params.row.username }
                    })
                  }
                }
              }, params.row.username)
            }
          }
        ],
        loadingTable: false,
        submissions: [],
        total: 30,
        limit: 12,
        page: 1,
        contestID: '',
        problemID: '',
        routeName: '',
        JUDGE_STATUS: '',
        rejudge_column: false
      }
    },
    mounted () {
      this.init()
      this.JUDGE_STATUS = Object.assign({}, JUDGE_STATUS)
      // 为选择题添加特殊状态
      this.JUDGE_STATUS['Correct'] = { color: 'success', type: 'success', name: 'Correct' }
      this.JUDGE_STATUS['Wrong'] = { color: 'error', type: 'error', name: 'Wrong Answer' }
    },
    methods: {
      init () {
        this.contestID = this.$route.params.contestID
        this.problemID = this.$route.params.problemID
        this.routeName = this.$route.name
        let query = this.$route.query
        this.page = parseInt(query.page) || 1
        if (this.page < 1) {
          this.page = 1
        }
        this.formFilter.result = query.result || ''
        this.formFilter.myself = query.myself === '1'
        this.formFilter.username = query.username || ''
        this.formFilter.question_type = query.question_type || 'all'
        this.getSubmissions()
      },
      buildQuery () {
        return {
          result: this.formFilter.result,
          myself: this.formFilter.myself === true ? '1' : '0',
          username: this.formFilter.username,
          question_type: this.formFilter.question_type,
          page: this.page
        }
      },
      getSubmissions () {
        let params = this.buildQuery()
        params.contest_id = this.contestID
        params.problem_id = this.problemID
        let offset = (this.page - 1) * this.limit
        this.loadingTable = true
        
        // 调用统一提交记录API
        this.getUnifiedSubmissions(offset, this.limit, params).then(res => {
          let data = res.data.data
          this.loadingTable = false
          this.submissions = data.submissions.map(submission => {
            // 统一数据格式
            return {
              ...submission,
              show_link: this.isAuthenticated && (submission.user_id === this.user.id || this.user.admin_type === USER_TYPE.SUPER_ADMIN)
            }
          })
          this.total = data.total
        }).catch(() => {
          this.loadingTable = false
        })
      },
      
      // 统一提交记录API调用
      getUnifiedSubmissions (offset, limit, params) {
        return api.getUnifiedSubmissions(offset, limit, params)
      },
      
      // 改变route， 通过监听route变化请求数据，这样可以产生route history， 用户返回时就会保存之前的状态
      changeRoute () {
        let query = utils.filterEmptyValue(this.buildQuery())
        query.contestID = this.contestID
        query.problemID = this.problemID
        let routeName = 'unified-submission-list'
        this.$router.push({
          name: routeName,
          query: utils.filterEmptyValue(query)
        })
      },
      
      handleResultChange (status) {
        this.page = 1
        this.formFilter.result = status
        this.changeRoute()
      },
      
      handleTypeChange (type) {
        this.page = 1
        this.formFilter.question_type = type
        this.changeRoute()
      },
      
      handleQueryChange () {
        this.page = 1
        this.changeRoute()
      }
    },
    computed: {
      ...mapGetters(['isAuthenticated', 'user']),
      title () {
        return this.$i18n.t('m.Unified_Submissions')
      },
      status () {
        if (this.formFilter.result === '') {
          return this.$i18n.t('m.Status')
        }
        const status = this.JUDGE_STATUS[this.formFilter.result]
        return status ? this.$i18n.t('m.' + status.name.replace(/ /g, '_')) : this.formFilter.result
      },
      questionType () {
        const typeMap = {
          'all': this.$i18n.t('m.All_Types'),
          'programming': this.$i18n.t('m.Programming'),
          'choice': this.$i18n.t('m.Choice_Question')
        }
        return typeMap[this.formFilter.question_type] || this.$i18n.t('m.All_Types')
      }
    },
    watch: {
      '$route' (newVal, oldVal) {
        if (newVal !== oldVal) {
          this.init()
        }
      }
    }
  }
</script>

<style scoped lang="less">
  .flex-container {
    #main {
      flex: auto;
      margin-right: 18px;
      .filter {
        margin-right: -10px;
        margin-top: -10px;
        li {
          display: inline-block;
          margin-right: 10px;
          margin-top: 10px;
        }
      }
    }
    #contest-menu {
      flex: none;
      width: 210px;
    }
  }
</style>