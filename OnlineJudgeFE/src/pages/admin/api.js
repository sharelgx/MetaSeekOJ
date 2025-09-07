import Vue from 'vue'
import router from './router'
import axios from 'axios'
import utils from '@/utils/utils'

Vue.prototype.$http = axios
axios.defaults.baseURL = '/api'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.xsrfCookieName = 'csrftoken'

export default {
  // 登录
  login (username, password) {
    return ajax('login', 'post', {
      data: {
        username,
        password
      }
    })
  },
  logout () {
    return ajax('logout', 'get')
  },
  getProfile () {
    return ajax('profile', 'get')
  },
  // 获取公告列表
  getAnnouncementList (offset, limit) {
    return ajax('admin/announcement', 'get', {
      params: {
        paging: true,
        offset,
        limit
      }
    })
  },
  // 删除公告
  deleteAnnouncement (id) {
    return ajax('admin/announcement', 'delete', {
      params: {
        id
      }
    })
  },
  // 修改公告
  updateAnnouncement (data) {
    return ajax('admin/announcement', 'put', {
      data
    })
  },
  // 添加公告
  createAnnouncement (data) {
    return ajax('admin/announcement', 'post', {
      data
    })
  },
  // 获取用户列表
  getUserList (offset, limit, keyword) {
    let params = {paging: true, offset, limit}
    if (keyword) {
      params.keyword = keyword
    }
    return ajax('admin/user', 'get', {
      params: params
    })
  },
  // 获取单个用户信息
  getUser (id) {
    return ajax('admin/user', 'get', {
      params: {
        id
      }
    })
  },
  // 编辑用户
  editUser (data) {
    return ajax('admin/user', 'put', {
      data
    })
  },
  deleteUsers (id) {
    return ajax('admin/user', 'delete', {
      params: {
        id
      }
    })
  },
  importUsers (users) {
    return ajax('admin/user', 'post', {
      data: {
        users
      }
    })
  },
  generateUser (data) {
    return ajax('admin/generate_user', 'post', {
      data
    })
  },
  getLanguages () {
    return ajax('languages', 'get')
  },
  getSMTPConfig () {
    return ajax('admin/smtp', 'get')
  },
  createSMTPConfig (data) {
    return ajax('admin/smtp', 'post', {
      data
    })
  },
  editSMTPConfig (data) {
    return ajax('admin/smtp', 'put', {
      data
    })
  },
  testSMTPConfig (email) {
    return ajax('admin/smtp_test', 'post', {
      data: {
        email
      }
    })
  },
  getWebsiteConfig () {
    return ajax('admin/website', 'get')
  },
  editWebsiteConfig (data) {
    return ajax('admin/website', 'post', {
      data
    })
  },
  getJudgeServer () {
    return ajax('admin/judge_server', 'get')
  },
  deleteJudgeServer (hostname) {
    return ajax('admin/judge_server', 'delete', {
      params: {
        hostname: hostname
      }
    })
  },
  updateJudgeServer (data) {
    return ajax('admin/judge_server', 'put', {
      data
    })
  },
  getInvalidTestCaseList () {
    return ajax('admin/prune_test_case', 'get')
  },
  pruneTestCase (id) {
    return ajax('admin/prune_test_case', 'delete', {
      params: {
        id
      }
    })
  },
  createContest (data) {
    return ajax('admin/contest', 'post', {
      data
    })
  },
  getContest (id) {
    return ajax('admin/contest', 'get', {
      params: {
        id
      }
    })
  },
  editContest (data) {
    return ajax('admin/contest', 'put', {
      data
    })
  },
  getContestList (offset, limit, keyword) {
    let params = {paging: true, offset, limit}
    if (keyword) {
      params.keyword = keyword
    }
    return ajax('admin/contest', 'get', {
      params: params
    })
  },
  getContestAnnouncementList (contestID) {
    return ajax('admin/contest/announcement', 'get', {
      params: {
        contest_id: contestID
      }
    })
  },
  createContestAnnouncement (data) {
    return ajax('admin/contest/announcement', 'post', {
      data
    })
  },
  deleteContestAnnouncement (id) {
    return ajax('admin/contest/announcement', 'delete', {
      params: {
        id
      }
    })
  },
  updateContestAnnouncement (data) {
    return ajax('admin/contest/announcement', 'put', {
      data
    })
  },
  getProblemTagList (params) {
    return ajax('problem/tags', 'get', {
      params
    })
  },
  compileSPJ (data) {
    return ajax('admin/compile_spj', 'post', {
      data
    })
  },
  createProblem (data) {
    return ajax('admin/problem', 'post', {
      data
    })
  },
  editProblem (data) {
    return ajax('admin/problem', 'put', {
      data
    })
  },
  deleteProblem (id) {
    return ajax('admin/problem', 'delete', {
      params: {
        id
      }
    })
  },
  getProblem (id) {
    return ajax('admin/problem', 'get', {
      params: {
        id
      }
    })
  },
  getProblemList (params) {
    params = utils.filterEmptyValue(params)
    return ajax('admin/problem', 'get', {
      params
    })
  },
  getContestProblemList (params) {
    params = utils.filterEmptyValue(params)
    return ajax('admin/contest/problem', 'get', {
      params
    })
  },
  getContestProblem (id) {
    return ajax('admin/contest/problem', 'get', {
      params: {
        id
      }
    })
  },
  createContestProblem (data) {
    return ajax('admin/contest/problem', 'post', {
      data
    })
  },
  editContestProblem (data) {
    return ajax('admin/contest/problem', 'put', {
      data
    })
  },
  deleteContestProblem (id) {
    return ajax('admin/contest/problem', 'delete', {
      params: {
        id
      }
    })
  },
  makeContestProblemPublic (data) {
    return ajax('admin/contest_problem/make_public', 'post', {
      data
    })
  },
  addProblemFromPublic (data) {
    return ajax('admin/contest/add_problem_from_public', 'post', {
      data
    })
  },
  getReleaseNotes () {
    return ajax('admin/versions', 'get')
  },
  getDashboardInfo () {
    return ajax('admin/dashboard_info', 'get')
  },
  getSessions () {
    return ajax('sessions', 'get')
  },
  exportProblems (data) {
    return ajax('export_problem', 'post', {
      data
    })
  },
  // Choice Question APIs
  getChoiceQuestionList (offset, limit, keyword) {
    let params = {
      paging: true,
      offset,
      limit
    }
    if (keyword) {
      params.keyword = keyword
    }
    return ajax('admin/choice_question', 'get', {
      params
    })
  },
  
  // 分类管理 API
  createChoiceQuestionCategory (data) {
    return ajax('admin/choice_question/categories', 'post', {
      data
    })
  },
  
  updateChoiceQuestionCategory (id, data) {
    return ajax('admin/choice_question/categories', 'put', {
      params: { id },
      data
    })
  },
  
  deleteChoiceQuestionCategory (id) {
    return ajax('admin/choice_question/categories', 'delete', {
      params: { id }
    })
  },
  
  // 标签管理 API
  createChoiceQuestionTag (data) {
    return ajax('admin/choice_question/tags', 'post', {
      data
    })
  },
  
  updateChoiceQuestionTag (id, data) {
    return ajax('admin/choice_question/tags', 'put', {
      params: { id },
      data
    })
  },
  
  deleteChoiceQuestionTag (id) {
    return ajax('admin/choice_question/tags', 'delete', {
      params: { id }
    })
  },
  createChoiceQuestion (data) {
    return ajax('admin/choice_question', 'post', {
      data
    })
  },
  getChoiceQuestion (id) {
    return ajax('admin/choice_question', 'get', {
      params: {
        id
      }
    })
  },
  editChoiceQuestion (data) {
    return ajax('admin/choice_question', 'put', {
      data
    })
  },
  deleteChoiceQuestion (id) {
    return ajax('admin/choice_question', 'delete', {
      params: {
        id
      }
    })
  },
  // Choice Question Categories
  getChoiceQuestionCategories (params) {
    return ajax('admin/choice_question/categories', 'get', {
      params
    })
  },
  createChoiceQuestionCategory (data) {
    return ajax('admin/choice_question/categories', 'post', {
      data
    })
  },
  updateChoiceQuestionCategory (id, data) {
    return ajax('admin/choice_question/categories', 'put', {
      params: { id },
      data
    })
  },
  deleteChoiceQuestionCategory (id) {
    return ajax('admin/choice_question/categories', 'delete', {
      params: { id }
    })
  },
  updateChoiceQuestionCategory (id, data) {
    return ajax('admin/choice_question/categories', 'put', {
      params: { id },
      data
    })
  },
  // Choice Question Tags
  getChoiceQuestionTags () {
    return ajax('admin/choice_question/tags', 'get')
  },
  createChoiceQuestionTag (data) {
    return ajax('admin/choice_question/tags', 'post', {
      data
    })
  },
  updateChoiceQuestionTag (id, data) {
    return ajax('admin/choice_question/tags', 'put', {
      params: { id },
      data
    })
  },
  deleteChoiceQuestionTag (id) {
    return ajax('admin/choice_question/tags', 'delete', {
      params: { id }
    })
  },
  // Choice Question Import// 导入选择题
  importChoiceQuestions (data) {
    return ajax('admin/choice_question/import', 'post', {
      data
    })
  },

  // 试卷管理相关API
  // 获取试卷列表
  getExamPaperList (params) {
    return ajax('plugin/choice/exam-papers/', 'get', {
      params
    })
  },
  // 创建试卷
  createExamPaper (data) {
    return ajax('plugin/choice/exam-papers/', 'post', {
      data
    })
  },
  // 获取单个试卷
  getExamPaper (id) {
    return ajax(`plugin/choice/exam-papers/${id}/`, 'get')
  },
  // 更新试卷
  updateExamPaper (id, data) {
    return ajax(`plugin/choice/exam-papers/${id}/`, 'put', {
      data
    })
  },
  // 删除试卷
  deleteExamPaper (id) {
    return ajax(`plugin/choice/exam-papers/${id}/`, 'delete')
  },
  // 批量更新试卷
  batchUpdateExamPapers (ids, data) {
    return ajax('plugin/choice/exam-papers/batch-update/', 'post', {
      data: {
        ids,
        ...data
      }
    })
  },
  // 批量删除试卷
  batchDeleteExamPapers (ids) {
    return ajax('plugin/choice/exam-papers/batch-delete/', 'post', {
      data: {
        ids
      }
    })
  },
  // 导入试卷
  importExamPapers (data) {
    // 注意：后端没有直接的试卷导入API
    // 需要分两步：1. 导入题目 2. 创建试卷
    // 这里先导入题目
    return ajax('admin/choice_question/import', 'post', {
      data: {
        questions: data.questions,
        category_id: data.category_id,
        tag_ids: data.tag_ids || [],  // 注意：后端期望tag_ids
        language: data.language || 'zh-CN'
      }
    })
  },

  // 试卷导入API - 直接导入完整试卷
  importExamPaper (data) {
    return ajax('admin/exam_paper/import', 'post', {
      data: {
        title: data.title,
        description: data.description || '',
        questions: data.questions,
        category_id: data.category_id,
        language: data.language || 'zh-CN',
        use_import_order: data.use_import_order || false,
        duration: data.duration || 60,
        total_score: data.total_score
      }
    })
  },

  // 考试统计相关API
  getExamStatistics () {
    return ajax('admin/exam_statistics', 'get')
  },

  // 试卷统计相关API
  getPaperStatistics (params) {
    return ajax('admin/paper_statistics', 'get', {
      params
    })
  },

  // 分类和标签相关API
  getCategoryList () {
    return ajax('admin/choice_question/categories', 'get')
  },

  getTagList () {
    return ajax('admin/choice_question/tags', 'get')
  },

  // 专题试做管理API
  getTopicPracticeRecords (params) {
    return ajax('admin/topic_practice/records', 'get', {
      params
    })
  },

  getTopicPracticeRecordDetail (recordId) {
    return ajax(`admin/topic_practice/records/${recordId}`, 'get')
  },

  deleteTopicPracticeRecord (recordId) {
    return ajax(`admin/topic_practice/records/${recordId}`, 'delete')
  },

  getTopicPracticeStatistics () {
    return ajax('admin/topic_practice/statistics', 'get')
  },

  exportTopicPracticeRecords (params) {
    return ajax('admin/topic_practice/export', 'get', {
      params,
      responseType: 'blob'
    })
  },

  // 专题管理相关API - 增强版
  getTopicsManage (params) {
    console.log('API: getTopicsManage called with params:', params)
    
    // 临时Mock数据，避免前端报错
    if (!params) {
      console.warn('API: getTopicsManage - 使用Mock数据，因为后端接口可能不可用')
      return Promise.resolve({
        data: {
          error: null,
          data: {
            results: [],
            total: 0,
            page: 1,
            page_size: 20
          }
        }
      })
    }
    
    return ajax('admin/topics/manage', 'get', {
      params: params || {}
    }).catch(err => {
      console.error('API: getTopicsManage failed:', err)
      
      // 如果是404错误，说明后端接口不存在，返回空数据
      if (err.response && err.response.status === 404) {
        console.warn('API: 专题管理接口不存在，返回空数据')
        return {
          data: {
            error: null,
            data: {
              results: [],
              total: 0,
              page: params.page || 1,
              page_size: params.page_size || 20
            }
          }
        }
      }
      
      throw err
    })
  },

  createTopic (data) {
    console.log('API: createTopic called with data:', data)
    return ajax('admin/topics/manage', 'post', {
      data
    }).catch(err => {
      console.error('API: createTopic failed:', err)
      if (err.response && err.response.status === 404) {
        throw new Error('专题创建接口不存在，请检查后端配置')
      }
      throw err
    })
  },

  getTopicManageDetail (topicId) {
    console.log('API: getTopicManageDetail called with topicId:', topicId)
    return ajax(`admin/topics/manage/${topicId}`, 'get').catch(err => {
      console.error('API: getTopicManageDetail failed:', err)
      throw err
    })
  },

  updateTopic (topicId, data) {
    console.log('API: updateTopic called with topicId:', topicId, 'data:', data)
    return ajax(`admin/topics/manage/${topicId}`, 'put', {
      data
    }).catch(err => {
      console.error('API: updateTopic failed:', err)
      throw err
    })
  },

  deleteTopic (topicId) {
    console.log('API: deleteTopic called with topicId:', topicId)
    return ajax(`admin/topics/manage/${topicId}`, 'delete').catch(err => {
      console.error('API: deleteTopic failed:', err)
      throw err
    })
  },

  // 专题题目管理
  getTopicQuestions (topicId, params) {
    return ajax(`admin/topics/${topicId}/questions`, 'get', {
      params: params || {}
    })
  },

  addTopicQuestions (topicId, data) {
    return ajax(`admin/topics/${topicId}/questions`, 'post', {
      data
    })
  },

  updateTopicQuestionOrder (topicId, data) {
    return ajax(`admin/topics/${topicId}/questions`, 'put', {
      data
    })
  },

  removeTopicQuestions (topicId, data) {
    return ajax(`admin/topics/${topicId}/questions`, 'delete', {
      data
    })
  },

  // 题目选择器
  getQuestionSelector (params) {
    return ajax('admin/topics/questions/selector', 'get', {
      params: params || {}
    })
  },

  // 专题批量操作
  batchOperateTopics (data) {
    return ajax('admin/topics/batch', 'post', {
      data
    })
  },

  // 专题分类管理
  getTopicCategories (params) {
    return ajax('admin/topic_categories', 'get', {
      params: params || {}
    })
  },

  createTopicCategory (data) {
    return ajax('admin/topic_categories', 'post', {
      data
    })
  },

  getTopicCategoryDetail (categoryId) {
    return ajax(`admin/topic_categories/${categoryId}`, 'get')
  },

  updateTopicCategory (categoryId, data) {
    return ajax(`admin/topic_categories/${categoryId}`, 'put', {
      data
    })
  },

  deleteTopicCategory (categoryId) {
    return ajax(`admin/topic_categories/${categoryId}`, 'delete')
  },

  getTopicCategoryTree (params) {
    return ajax('admin/topic_categories/tree', 'get', {
      params: params || {}
    })
  },

  moveTopicCategory (data) {
    return ajax('admin/topic_categories/move', 'post', {
      data
    })
  },

  batchOperateTopicCategories (data) {
    return ajax('admin/topic_categories/batch', 'post', {
      data
    })
  },

  getTopicCategoryTopics (categoryId, params) {
    return ajax(`admin/topic_categories/${categoryId}/topics`, 'get', {
      params: params || {}
    })
  },

  addTopicsToCategory (categoryId, data) {
    return ajax(`admin/topic_categories/${categoryId}/topics`, 'post', {
      data
    })
  },

  removeTopicsFromCategory (categoryId, data) {
    return ajax(`admin/topic_categories/${categoryId}/topics`, 'delete', {
      data
    })
  },

  // 获取标签列表
  getQuestionTags (params) {
    return ajax('admin/choice_question/tags', 'get', {
      params: params || {}
    })
  },

  getTopicStructure (topicId) {
    return ajax(`admin/topics/${topicId}/structure`, 'get').catch(err => {
      console.error('API: getTopicStructure failed:', err)
      if (err.response && err.response.status === 404) {
        // 返回空的结构数据
        return {
          data: {
            error: null,
            data: {
              categories_count: 0,
              papers_count: 0,
              questions_count: 0,
              categories: []
            }
          }
        }
      }
      throw err
    })
  },

  // 分类试卷管理API
  getCategoryPapers (categoryId) {
    return ajax(`admin/topic_categories/${categoryId}/papers`, 'get')
  },

  addPapersToCategory (categoryId, data) {
    return ajax(`admin/topic_categories/${categoryId}/papers`, 'post', {
      data
    })
  },

  removePaperFromCategory (categoryId, data) {
    return ajax(`admin/topic_categories/${categoryId}/papers`, 'delete', {
      data
    })
  },

  // 专题操作API
  duplicateTopic (topicId) {
    return ajax(`admin/topics/${topicId}/duplicate`, 'post')
  },

  exportTopic (topicId) {
    return ajax(`admin/topics/${topicId}/export`, 'get', {
      responseType: 'blob'
    })
  },
  
  // 选择题分类管理 API - 已删除重复定义，使用第377行的版本
  
  // 选择题标签管理 API  
  getChoiceQuestionTags () {
    return ajax('admin/choice_question/tags', 'get')
  },
  
  // 选择题列表 API
  getChoiceQuestionList (offset, limit, keyword) {
    let params = {
      paging: true,
      offset,
      limit
    }
    if (keyword) {
      params.keyword = keyword
    }
    return ajax('admin/choice_question', 'get', {
      params
    })
  }
}

/**
 * @param url
 * @param method get|post|put|delete...
 * @param params like queryString. if a url is index?a=1&b=2, params = {a: '1', b: '2'}
 * @param data post data, use for method put|post
 * @returns {Promise}
 */
function ajax (url, method, options) {
  if (options !== undefined) {
    var {params = {}, data = {}} = options
  } else {
    params = data = {}
  }
  
  console.log(`API: ${method.toUpperCase()} ${url}`, {params, data})
  
  return new Promise((resolve, reject) => {
    axios({
      url,
      method,
      params,
      data,
      timeout: 30000 // 增加超时时间到30秒
    }).then(res => {
      console.log(`API: ${method.toUpperCase()} ${url} - Success:`, res.data)
      
      // API正常返回(status=20x), 是否错误通过有无error判断
      if (res.data.error !== null) {
        console.error(`API: ${method.toUpperCase()} ${url} - Error:`, res.data.data)
        
        // 检查是否是登录相关错误
        if (res.data.data && typeof res.data.data === 'string' && 
            res.data.data.startsWith('Please login')) {
          console.log('API: Authentication error detected')
          // 不在这里直接跳转，而是抛出特殊错误让组件处理
          const authError = new Error('Authentication required')
          authError.isAuthError = true
          authError.originalData = res.data.data
          reject(authError)
        } else {
          Vue.prototype.$error(res.data.data)
          reject(res)
        }
      } else {
        resolve(res)
        if (method !== 'get') {
          Vue.prototype.$success('操作成功')
        }
      }
    }).catch(err => {
      console.error(`API: ${method.toUpperCase()} ${url} - Network/Server Error:`, err)
      
      // API请求异常，一般为Server error 或 network error
      if (err.response) {
        // 服务器响应了错误状态码
        console.error('API: Error response:', err.response.status, err.response.data)
        
        if (err.response.status === 401 || err.response.status === 403) {
          // 认证或权限错误
          const authError = new Error('Authentication or permission error')
          authError.isAuthError = true
          authError.status = err.response.status
          reject(authError)
        } else {
          if (err.response.data && err.response.data.data) {
            Vue.prototype.$error(err.response.data.data)
          } else {
            Vue.prototype.$error(`服务器错误 (${err.response.status})`)
          }
          reject(err)
        }
      } else if (err.request) {
        // 请求发出了但没有收到响应
        console.error('API: No response received:', err.request)
        Vue.prototype.$error('网络连接失败，请检查网络设置')
        reject(err)
      } else {
        // 请求配置错误
        console.error('API: Request setup error:', err.message)
        Vue.prototype.$error('请求配置错误: ' + err.message)
        reject(err)
      }
    })
  })
}

// Choice Question API
export function getChoiceQuestions(offset, limit, keyword) {
  let params = {
    paging: true,
    offset,
    limit
  }
  if (keyword) {
    params.keyword = keyword
  }
  return ajax('choice_questions', 'get', {
    params
  })
}

export function createChoiceQuestion(data) {
  return ajax('choice_question', 'post', {
    data
  })
}

export function getChoiceQuestion(id) {
  return ajax('choice_question', 'get', {
    params: {
      id
    }
  })
}

export function editChoiceQuestion(data) {
  return ajax('choice_question', 'put', {
    data
  })
}

export function deleteChoiceQuestion(id) {
  return ajax('choice_question', 'delete', {
    params: {
      id
    }
  })
}