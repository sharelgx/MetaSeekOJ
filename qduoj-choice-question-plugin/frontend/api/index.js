// 简单的ajax函数，用于插件环境
const ajax = (url, method = 'get', options = {}) => {
  const baseURL = '/api/'
  const fullURL = baseURL + url
  
  const config = {
    method: method.toUpperCase(),
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
    }
  }
  
  if (options.params) {
    const searchParams = new URLSearchParams(options.params)
    const separator = fullURL.includes('?') ? '&' : '?'
    config.url = fullURL + separator + searchParams.toString()
  } else {
    config.url = fullURL
  }
  
  if (options.data && ['POST', 'PUT', 'PATCH'].includes(config.method)) {
    config.body = JSON.stringify(options.data)
  }
  
  return fetch(config.url, config).then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json().then(data => ({ data }))
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
  getCategoryStatistics(params) {
    return ajax('plugin/choice/categories/statistics/', 'get', {
      params
    })
  },
  getCategoryStats(categoryId) {
    return ajax(`plugin/choice/categories/${categoryId}/stats/`, 'get')
  },
  batchUpdateCategories(data) {
    return ajax('plugin/choice/categories/batch-update/', 'post', {
      data
    })
  },
  batchDeleteCategories(data) {
    return ajax('plugin/choice/categories/batch-delete/', 'post', {
      data
    })
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
  submitAnswer(data) {
    return ajax('plugin/choice/submissions/', 'post', {
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
  },

  // 导入导出相关API
  importQuestions(formData) {
    return ajax('plugin/choice/import/', 'post', {
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  exportQuestions(params) {
    return ajax('plugin/choice/export/', 'get', {
      params,
      responseType: 'blob'
    })
  },
  downloadTemplate(format) {
    return ajax('plugin/choice/template/', 'get', {
      params: { format },
      responseType: 'blob'
    })
  },
  batchOperation(data) {
    return ajax('plugin/choice/batch/', 'post', {
      data
    })
  },

  // 批量删除标签
  batchDeleteTags(data) {
    return ajax('plugin/choice/tags/batch-delete/', 'post', {
      data: {
        action: 'delete',
        tag_ids: data.tag_ids || data
      }
    })
  },
  
  // 标签统计
  getTagStatistics() {
    return ajax('plugin/choice/tags/statistics/', 'get')
  },
  
  // 分类移动
  moveCategory(id, data) {
    return ajax(`plugin/choice/categories/${id}/move/`, 'post', {
      data
    })
  },
  
  // 分类统计
  getCategoryStatistics(id) {
    return ajax(`plugin/choice/categories/${id}/statistics/`, 'get')
  },
  getImportHistory(params) {
    return ajax('plugin/choice/import-history/', 'get', {
      params
    })
  }
}