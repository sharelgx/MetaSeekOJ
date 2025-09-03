import Vue from 'vue'
import store from '@/store'
import axios from 'axios'

Vue.prototype.$http = axios
axios.defaults.baseURL = '/api'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.xsrfCookieName = 'csrftoken'

export default {
  getWebsiteConf (params) {
    return ajax('website', 'get', {
      params
    })
  },
  getAnnouncementList (offset, limit) {
    let params = {
      offset: offset,
      limit: limit
    }
    return ajax('announcement', 'get', {
      params
    })
  },
  login (data) {
    return ajax('login', 'post', {
      data
    })
  },
  checkUsernameOrEmail (username, email) {
    return ajax('check_username_or_email', 'post', {
      data: {
        username,
        email
      }
    })
  },
  // 注册
  register (data) {
    return ajax('register', 'post', {
      data
    })
  },
  logout () {
    return ajax('logout', 'get')
  },
  getCaptcha () {
    return ajax('captcha', 'get')
  },
  getUserInfo (username = undefined) {
    return ajax('profile', 'get', {
      params: {
        username
      }
    })
  },
  updateProfile (profile) {
    return ajax('profile', 'put', {
      data: profile
    })
  },
  freshDisplayID (userID) {
    return ajax('profile/fresh_display_id', 'get', {
      params: {
        user_id: userID
      }
    })
  },
  twoFactorAuth (method, data) {
    return ajax('two_factor_auth', method, {
      data
    })
  },
  tfaRequiredCheck (username) {
    return ajax('tfa_required', 'post', {
      data: {
        username
      }
    })
  },
  getSessions () {
    return ajax('sessions', 'get')
  },
  deleteSession (sessionKey) {
    return ajax('sessions', 'delete', {
      params: {
        session_key: sessionKey
      }
    })
  },
  applyResetPassword (data) {
    return ajax('apply_reset_password', 'post', {
      data
    })
  },
  resetPassword (data) {
    return ajax('reset_password', 'post', {
      data
    })
  },
  changePassword (data) {
    return ajax('change_password', 'post', {
      data
    })
  },
  changeEmail (data) {
    return ajax('change_email', 'post', {
      data
    })
  },
  getLanguages () {
    return ajax('languages', 'get')
  },
  getProblemTagList () {
    return ajax('problem/tags', 'get')
  },
  getProblemList (offset, limit, searchParams) {
    let params = {
      paging: true,
      offset,
      limit
    }
    Object.keys(searchParams).forEach((element) => {
      if (searchParams[element]) {
        params[element] = searchParams[element]
      }
    })
    return ajax('problem', 'get', {
      params: params
    })
  },
  pickone () {
    return ajax('pickone', 'get')
  },
  getProblem (problemID) {
    return ajax('problem', 'get', {
      params: {
        problem_id: problemID
      }
    })
  },
  getContestList (offset, limit, searchParams) {
    let params = {
      offset,
      limit
    }
    if (searchParams !== undefined) {
      Object.keys(searchParams).forEach((element) => {
        if (searchParams[element]) {
          params[element] = searchParams[element]
        }
      })
    }
    return ajax('contests', 'get', {
      params
    })
  },
  getContest (id) {
    return ajax('contest', 'get', {
      params: {
        id
      }
    })
  },
  getContestAccess (contestID) {
    return ajax('contest/access', 'get', {
      params: {
        contest_id: contestID
      }
    })
  },
  checkContestPassword (contestID, password) {
    return ajax('contest/password', 'post', {
      data: {
        contest_id: contestID,
        password
      }
    })
  },
  getContestAnnouncementList (contestId) {
    return ajax('contest/announcement', 'get', {
      params: {
        contest_id: contestId
      }
    })
  },
  getContestProblemList (contestId) {
    return ajax('contest/problem', 'get', {
      params: {
        contest_id: contestId
      }
    })
  },
  getContestProblem (problemID, contestID) {
    return ajax('contest/problem', 'get', {
      params: {
        contest_id: contestID,
        problem_id: problemID
      }
    })
  },
  submitCode (data) {
    return ajax('submission', 'post', {
      data
    })
  },
  getSubmissionList (offset, limit, params) {
    params.limit = limit
    params.offset = offset
    return ajax('submissions', 'get', {
      params
    })
  },
  getContestSubmissionList (offset, limit, params) {
    params.limit = limit
    params.offset = offset
    return ajax('contest_submissions', 'get', {
      params
    })
  },
  getSubmission (id) {
    return ajax('submission', 'get', {
      params: {
        id
      }
    })
  },
  submissionExists (problemID) {
    return ajax('submission_exists', 'get', {
      params: {
        problem_id: problemID
      }
    })
  },
  submissionRejudge (id) {
    return ajax('admin/submission/rejudge', 'get', {
      params: {
        id
      }
    })
  },
  updateSubmission (data) {
    return ajax('submission', 'put', {
      data
    })
  },
  getUserRank (offset, limit, rule = 'acm') {
    let params = {
      offset,
      limit,
      rule
    }
    return ajax('user_rank', 'get', {
      params
    })
  },
  getContestRank (params) {
    return ajax('contest_rank', 'get', {
      params
    })
  },
  getACMACInfo (params) {
    return ajax('admin/contest/acm_helper', 'get', {
      params
    })
  },
  updateACInfoCheckedStatus (data) {
    return ajax('admin/contest/acm_helper/', 'put', {
      data
    })
  },
  
  // 统一提交系统API
  getUnifiedSubmissions (offset, limit, params) {
    params.limit = limit
    params.offset = offset
    return ajax('judge/submissions', 'get', {
      params
    })
  },
  
  submitUnified (data) {
    return ajax('judge/submit', 'post', {
      data
    })
  },
  
  getUnifiedSubmissionDetail (id) {
    return ajax('judge/submission/detail', 'get', {
      params: {
        id
      }
    })
  },
  
  getUserStatistics (userId) {
    return ajax('judge/statistics', 'get', {
      params: {
        user_id: userId
      }
    })
  },

  // 选择题相关API
  getChoiceQuestionList (offset, limit, params) {
    // 构建查询参数
    let query = {
      offset: offset,
      limit: limit,
      ...params
    }
    
    // 移除空值参数
    Object.keys(query).forEach(key => {
      if (query[key] === '' || query[key] === null || query[key] === undefined) {
        delete query[key]
      }
    })
    
    return ajax('plugin/choice/questions/', 'get', {
      params: query
    })
  },

  getChoiceQuestionDetail (id) {
    return ajax('plugin/choice/questions/' + id + '/', 'get')
  },

  // 试卷管理API
  createExamPaper (data) {
    return ajax('plugin/choice/exam-papers/', 'post', {
      data
    })
  },

  getExamPaperDetail (paperId) {
    if (!paperId) {
      return Promise.reject(new Error('试卷ID不能为空'))
    }
    return ajax('plugin/choice/exam-papers/' + paperId + '/', 'get')
  },

  // 考试会话API
  createExamSession (paperId) {
    if (!paperId) {
      return Promise.reject(new Error('试卷ID不能为空'))
    }
    return ajax('plugin/choice/exam-sessions/create/', 'post', {
      data: {
        paper_id: paperId
      }
    })
  },

  startExamSession (sessionId) {
    if (!sessionId) {
      return Promise.reject(new Error('会话ID不能为空'))
    }
    return ajax('plugin/choice/exam-sessions/' + sessionId + '/start/', 'post')
  },

  submitExamSession (sessionId) {
    if (!sessionId) {
      return Promise.reject(new Error('会话ID不能为空'))
    }
    return ajax('plugin/choice/exam-sessions/' + sessionId + '/submit/', 'post')
  },

  submitAnswer (sessionId, questionId, answer) {
    if (!sessionId) {
      return Promise.reject(new Error('会话ID不能为空'))
    }
    return ajax('plugin/choice/exam-sessions/' + sessionId + '/answer/', 'post', {
      data: {
        question_id: questionId,
        answer: answer
      }
    })
  },

  // 提交考试答案（兼容方法）
  submitExamAnswer (sessionId, data) {
    if (!sessionId) {
      return Promise.reject(new Error('会话ID不能为空'))
    }
    return ajax('plugin/choice/exam-sessions/' + sessionId + '/answer/', 'post', {
      data: data
    })
  },

  // 获取考试会话详情
  getExamSessionDetail (sessionId) {
    if (!sessionId) {
      return Promise.reject(new Error('会话ID不能为空'))
    }
    return ajax('plugin/choice/exam-sessions/' + sessionId + '/', 'get')
  },

  // 获取题目详情
  getQuestionDetail (questionId) {
    if (!questionId) {
      return Promise.reject(new Error('题目ID不能为空'))
    }
    return ajax('plugin/choice/questions/' + questionId + '/', 'get')
  },

  // 获取题目列表（用于练习模式）
  getQuestionList (params) {
    // 构建查询参数（用于练习模式，不需要分页）
    let query = params || {}
    
    // 移除空值参数
    Object.keys(query).forEach(key => {
      if (query[key] === '' || query[key] === null || query[key] === undefined) {
        delete query[key]
      }
    })
    
    return ajax('plugin/choice/questions/', 'get', {
      params: query
    })
  },

  // 错题本相关API
  addToWrongQuestions (data) {
    return ajax('plugin/choice/wrong-questions/', 'post', {
      data
    })
  },

  getWrongQuestionList (params) {
    return ajax('plugin/choice/wrong-questions/', 'get', {
      params: params || {}
    })
  },

  removeFromWrongQuestions (wrongQuestionId) {
    return ajax('plugin/choice/wrong-questions/' + wrongQuestionId + '/', 'delete')
  },

  updateWrongQuestionNote (wrongQuestionId, data) {
    return ajax('plugin/choice/wrong-questions/' + wrongQuestionId + '/', 'put', {
      data
    })
  },

  // 获取分类列表
  getCategoryList () {
    return ajax('plugin/choice/categories/', 'get')
  },

  // 获取标签列表
  getTagList () {
    return ajax('plugin/choice/tags/', 'get')
  },

  // 获取考试历史记录列表
  getExamHistoryList (params) {
    return ajax('plugin/choice/exam-sessions/', 'get', {
      params: params || {}
    })
  },

  // 提交选择题答案（练习模式）
  submitChoiceQuestion (questionId, data) {
    if (!questionId) {
      return Promise.reject(new Error('题目ID不能为空'))
    }
    return ajax('plugin/choice/questions/' + questionId + '/submit/', 'post', {
      data: data
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
  return new Promise((resolve, reject) => {
    axios({
      url,
      method,
      params,
      data
    }).then(res => {
      // API正常返回(status=20x), 是否错误通过有无error判断
      if (res.data.error !== null) {
        Vue.prototype.$error(res.data.data)
        reject(res)
        // 若后端返回为登录，则为session失效，应退出当前登录用户
        if (res.data.data.startsWith('Please login')) {
          store.dispatch('changeModalStatus', {'mode': 'login', 'visible': true})
        }
      } else {
        resolve(res)
        // if (method !== 'get') {
        //   Vue.prototype.$success('Succeeded')
        // }
      }
    }, res => {
      // API请求异常，一般为Server error 或 network error
      reject(res)
      Vue.prototype.$error(res.data.data)
    })
  })
}
