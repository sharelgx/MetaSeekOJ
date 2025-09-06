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
  getChoiceQuestionCategories () {
    return ajax('admin/choice_question/categories', 'get')
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
        // // 若后端返回为登录，则为session失效，应退出当前登录用户
        if (res.data.data.startsWith('Please login')) {
          router.push({name: 'login'})
        }
      } else {
        resolve(res)
        if (method !== 'get') {
          Vue.prototype.$success('Succeeded')
        }
      }
    }, res => {
      // API请求异常，一般为Server error 或 network error
      reject(res)
      // 检查res.data是否存在，避免undefined错误
      if (res.data && res.data.data) {
        Vue.prototype.$error(res.data.data)
      } else {
        Vue.prototype.$error('Network error or server error')
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