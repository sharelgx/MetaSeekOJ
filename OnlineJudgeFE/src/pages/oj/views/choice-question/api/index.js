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
  // 分类相关API
  getCategoryList() {
    return ajax('plugin/choice/categories/', 'get')
  },
  createCategory(data) {
    return ajax('plugin/choice/categories/', 'post', {
      data
    })
  },
  updateCategory(id, data) {
    return ajax(`plugin/choice/categories/${id}/`, 'put', {
      data
    })
  },
  deleteCategory(id) {
    return ajax(`plugin/choice/categories/${id}/`, 'delete')
  },

  // 标签相关API
  getTagList() {
    return ajax('plugin/choice/tags/', 'get')
  },
  createTag(data) {
    return ajax('plugin/choice/tags/', 'post', {
      data
    })
  },
  updateTag(id, data) {
    return ajax(`plugin/choice/tags/${id}/`, 'put', {
      data
    })
  },
  deleteTag(id) {
    return ajax(`plugin/choice/tags/${id}/`, 'delete')
  },

  // 选择题相关API
  getQuestionList(params) {
    return ajax('plugin/choice/questions/', 'get', {
      params
    })
  },
  getQuestionDetail(id) {
    return ajax(`plugin/choice/questions/${id}/`, 'get')
  },
  createQuestion(data) {
    return ajax('plugin/choice/questions/', 'post', {
      data
    })
  },
  updateQuestion(id, data) {
    return ajax(`plugin/choice/questions/${id}/`, 'put', {
      data
    })
  },
  deleteQuestion(id) {
    return ajax(`plugin/choice/questions/${id}/`, 'delete')
  },

  // 提交相关API
  submitAnswer(questionId, data) {
    return ajax(`plugin/choice/questions/${questionId}/submit/`, 'post', {
      data
    })
  },
  getSubmissionList(params) {
    return ajax('plugin/choice/submissions/', 'get', {
      params
    })
  },

  // 错题本相关API
  getWrongQuestionList(params) {
    return ajax('plugin/choice/wrong-questions/', 'get', {
      params
    })
  },
  addToWrongQuestions(data) {
    return ajax('plugin/choice/wrong-questions/', 'post', {
      data
    })
  },
  removeFromWrongQuestions(id) {
    return ajax(`plugin/choice/wrong-questions/${id}/`, 'delete')
  },
  updateWrongQuestionNote(id, data) {
    return ajax(`plugin/choice/wrong-questions/${id}/`, 'put', {
      data
    })
  },

  // 统计相关API
  getQuestionStats() {
    return ajax('plugin/choice/statistics/', 'get')
  }
}