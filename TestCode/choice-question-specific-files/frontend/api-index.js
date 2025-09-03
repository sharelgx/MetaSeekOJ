import api from '@oj/api'
import Vue from 'vue'
import store from '@/store'
import axios from 'axios'

// 配置axios默认设置
axios.defaults.baseURL = '/api'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.xsrfCookieName = 'csrftoken'

// 创建一个内部的 ajax 函数来处理选择题相关的 API 请求
function ajax (url, method, options) {
  if (options !== undefined) {
    var {params = {}, data = {}} = options
  } else {
    params = data = {}
  }
  return new Promise((resolve, reject) => {
    axios({
      url: url,
      method,
      params,
      data
    }).then(res => {
      // API正常返回(status=20x), 是否错误通过有无error判断
      if (res.data.error !== null) {
        Vue.prototype.$error(res.data.data)
        reject(res)
        // 若后端返回为登录，则为session失效，应退出当前登录用户
        if (res.data.data && res.data.data.startsWith && res.data.data.startsWith('Please login')) {
          store.dispatch('changeModalStatus', {'mode': 'login', 'visible': true})
        }
      } else {
        resolve(res)
      }
    }, res => {
      // API请求异常，一般为Server error 或 network error
      reject(res)
      if (res.data && res.data.data) {
        Vue.prototype.$error(res.data.data)
      } else {
        Vue.prototype.$error('Network error or server error')
      }
    })
  })
}

export default {
  // 分类相关API - 修正路径
  getCategoryList() {
    return ajax('choice_question/categories/', 'get')
  },
  createCategory(data) {
    return ajax('choice_question/categories/', 'post', {
      data
    })
  },
  updateCategory(id, data) {
    return ajax(`choice_question/categories/${id}/`, 'put', {
      data
    })
  },
  deleteCategory(id) {
    return ajax(`choice_question/categories/${id}/`, 'delete')
  },

  // 标签相关API - 修正路径
  getTagList() {
    return ajax('choice_question/tags/', 'get')
  },
  createTag(data) {
    return ajax('choice_question/tags/', 'post', {
      data
    })
  },
  updateTag(id, data) {
    return ajax(`choice_question/tags/${id}/`, 'put', {
      data
    })
  },
  deleteTag(id) {
    return ajax(`choice_question/tags/${id}/`, 'delete')
  },

  // 选择题相关API - 修正路径
  getQuestionList(params) {
    return ajax('choice_question/questions/', 'get', {
      params
    })
  },
  getQuestionDetail(id) {
    return ajax(`choice_question/questions/${id}/`, 'get')
  },
  getChoiceQuestionDetail(id) {
    // 别名，兼容性
    return ajax(`choice_question/questions/${id}/`, 'get')
  },
  createQuestion(data) {
    return ajax('choice_question/questions/', 'post', {
      data
    })
  },
  updateQuestion(id, data) {
    return ajax(`choice_question/questions/${id}/`, 'put', {
      data
    })
  },
  deleteQuestion(id) {
    return ajax(`choice_question/questions/${id}/`, 'delete')
  },

  // 提交相关API - 修正路径
  submitAnswer(questionId, data) {
    return ajax(`choice_question/questions/${questionId}/submit/`, 'post', {
      data
    })
  },
  getSubmissionList(params) {
    return ajax('choice_question/submissions/', 'get', {
      params
    })
  },

  // 错题本相关API - 修正路径
  getWrongQuestionList(params) {
    return ajax('choice_question/wrong-questions/', 'get', {
      params
    })
  },
  addToWrongQuestions(data) {
    return ajax('choice_question/wrong-questions/', 'post', {
      data
    })
  },
  removeFromWrongQuestions(id) {
    return ajax(`choice_question/wrong-questions/${id}/`, 'delete')
  },
  updateWrongQuestionNote(id, data) {
    return ajax(`choice_question/wrong-questions/${id}/`, 'put', {
      data
    })
  },

  // 统计相关API - 修正路径
  getQuestionStats() {
    return ajax('choice_question/statistics/', 'get')
  },

  // 考试相关API - 修正路径
  // 试卷管理
  getExamPaperList(params) {
    return ajax('choice_question/exam-papers/', 'get', {
      params
    })
  },
  getExamPaperDetail(id) {
    return ajax(`choice_question/exam-papers/${id}/`, 'get')
  },
  createExamPaper(data) {
    return ajax('choice_question/exam-papers/', 'post', {
      data
    })
  },
  getExamPaperGeneratePreview(params) {
    return ajax('choice_question/exam-papers/generate-preview/', 'get', {
      params
    })
  },

  // 考试会话管理 - 修正路径
  getExamSessionList(params) {
    return ajax('choice_question/exam-sessions/', 'get', {
      params
    })
  },
  createExamSession(paperId) {
    // 修正：直接传paper_id
    return ajax('choice_question/exam-sessions/', 'post', {
      data: {
        paper_id: paperId
      }
    })
  },
  startExamSession(sessionId) {
    return ajax(`choice_question/exam-sessions/${sessionId}/start/`, 'post')
  },
  getExamSessionDetail(sessionId) {
    return ajax(`choice_question/exam-sessions/${sessionId}/`, 'get')
  },
  submitExamAnswer(sessionId, data) {
    return ajax(`choice_question/exam-sessions/${sessionId}/answer/`, 'post', {
      data
    })
  },
  submitExamSession(sessionId, data) {
    return ajax(`choice_question/exam-sessions/${sessionId}/submit/`, 'post', {
      data
    })
  }
}