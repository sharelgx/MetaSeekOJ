import ajax from '@oj/api'

export default {
  // 分类相关API
  getCategoryList() {
    return ajax('choice-question/categories/', 'get')
  },
  createCategory(data) {
    return ajax('choice-question/categories/', 'post', {
      data
    })
  },
  updateCategory(id, data) {
    return ajax(`choice-question/categories/${id}/`, 'put', {
      data
    })
  },
  deleteCategory(id) {
    return ajax(`choice-question/categories/${id}/`, 'delete')
  },

  // 标签相关API
  getTagList() {
    return ajax('choice-question/tags/', 'get')
  },
  createTag(data) {
    return ajax('choice-question/tags/', 'post', {
      data
    })
  },
  updateTag(id, data) {
    return ajax(`choice-question/tags/${id}/`, 'put', {
      data
    })
  },
  deleteTag(id) {
    return ajax(`choice-question/tags/${id}/`, 'delete')
  },

  // 选择题相关API
  getQuestionList(params) {
    return ajax('choice-question/questions/', 'get', {
      params
    })
  },
  getQuestionDetail(id) {
    return ajax(`choice-question/questions/${id}/`, 'get')
  },
  createQuestion(data) {
    return ajax('choice-question/questions/', 'post', {
      data
    })
  },
  updateQuestion(id, data) {
    return ajax(`choice-question/questions/${id}/`, 'put', {
      data
    })
  },
  deleteQuestion(id) {
    return ajax(`choice-question/questions/${id}/`, 'delete')
  },

  // 提交相关API
  submitAnswer(data) {
    return ajax('choice-question/submissions/', 'post', {
      data
    })
  },
  getSubmissionList(params) {
    return ajax('choice-question/submissions/', 'get', {
      params
    })
  },

  // 错题本相关API
  getWrongQuestionList(params) {
    return ajax('choice-question/wrong-questions/', 'get', {
      params
    })
  },
  addToWrongQuestions(data) {
    return ajax('choice-question/wrong-questions/', 'post', {
      data
    })
  },
  removeFromWrongQuestions(id) {
    return ajax(`choice-question/wrong-questions/${id}/`, 'delete')
  },
  updateWrongQuestionNote(id, data) {
    return ajax(`choice-question/wrong-questions/${id}/`, 'put', {
      data
    })
  },

  // 统计相关API
  getQuestionStats() {
    return ajax('choice-question/stats/', 'get')
  }
}