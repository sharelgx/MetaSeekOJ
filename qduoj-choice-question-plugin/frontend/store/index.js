// 选择题模块 Vuex Store

import api from '../api'

const state = {
  // 选择题相关状态
  questions: [],
  currentQuestion: null,
  categories: [],
  tags: [],
  submissions: [],
  wrongQuestions: [],
  stats: null,
  
  // 分页和筛选状态
  pagination: {
    page: 1,
    limit: 20,
    total: 0
  },
  filters: {
    keyword: '',
    category: null,
    tags: [],
    difficulty: null,
    questionType: null
  },
  
  // 加载状态
  loading: {
    questions: false,
    categories: false,
    tags: false,
    submissions: false,
    wrongQuestions: false,
    stats: false
  }
}

const mutations = {
  // 设置题目列表
  SET_QUESTIONS(state, { data, total }) {
    state.questions = data
    state.pagination.total = total
  },
  
  // 设置当前题目
  SET_CURRENT_QUESTION(state, question) {
    state.currentQuestion = question
  },
  
  // 设置分类列表
  SET_CATEGORIES(state, categories) {
    state.categories = categories
  },
  
  // 设置标签列表
  SET_TAGS(state, tags) {
    state.tags = tags
  },
  
  // 设置提交记录
  SET_SUBMISSIONS(state, { data, total }) {
    state.submissions = data
    state.pagination.total = total
  },
  
  // 设置错题列表
  SET_WRONG_QUESTIONS(state, { data, total }) {
    state.wrongQuestions = data
    state.pagination.total = total
  },
  
  // 设置统计信息
  SET_STATS(state, stats) {
    state.stats = stats
  },
  
  // 更新分页信息
  UPDATE_PAGINATION(state, pagination) {
    state.pagination = { ...state.pagination, ...pagination }
  },
  
  // 更新筛选条件
  UPDATE_FILTERS(state, filters) {
    state.filters = { ...state.filters, ...filters }
  },
  
  // 设置加载状态
  SET_LOADING(state, { type, loading }) {
    state.loading[type] = loading
  }
}

const actions = {
  // 获取题目列表
  async getQuestions({ commit, state }) {
    commit('SET_LOADING', { type: 'questions', loading: true })
    try {
      const params = {
        page: state.pagination.page,
        limit: state.pagination.limit,
        ...state.filters
      }
      const response = await api.getQuestions(params)
      commit('SET_QUESTIONS', response.data)
      return response
    } finally {
      commit('SET_LOADING', { type: 'questions', loading: false })
    }
  },
  
  // 获取题目详情
  async getQuestionDetail({ commit }, id) {
    const response = await api.getQuestionDetail(id)
    commit('SET_CURRENT_QUESTION', response.data)
    return response
  },
  
  // 获取分类列表
  async getCategories({ commit }) {
    commit('SET_LOADING', { type: 'categories', loading: true })
    try {
      const response = await api.getCategories()
      commit('SET_CATEGORIES', response.data.results || response.data)
      return response
    } finally {
      commit('SET_LOADING', { type: 'categories', loading: false })
    }
  },
  
  // 获取标签列表
  async getTags({ commit }) {
    commit('SET_LOADING', { type: 'tags', loading: true })
    try {
      const response = await api.getTags()
      commit('SET_TAGS', response.data.results || response.data)
      return response
    } finally {
      commit('SET_LOADING', { type: 'tags', loading: false })
    }
  },
  
  // 提交答案
  async submitAnswer({ dispatch }, { questionId, selectedAnswer }) {
    const response = await api.submitAnswer({ questionId, selectedAnswer })
    // 提交后重新获取题目详情以更新状态
    await dispatch('getQuestionDetail', questionId)
    return response
  },
  
  // 获取提交记录
  async getSubmissions({ commit, state }) {
    commit('SET_LOADING', { type: 'submissions', loading: true })
    try {
      const params = {
        page: state.pagination.page,
        limit: state.pagination.limit
      }
      const response = await api.getSubmissions(params)
      commit('SET_SUBMISSIONS', response.data)
      return response
    } finally {
      commit('SET_LOADING', { type: 'submissions', loading: false })
    }
  },
  
  // 获取错题列表
  async getWrongQuestions({ commit, state }) {
    commit('SET_LOADING', { type: 'wrongQuestions', loading: true })
    try {
      const params = {
        page: state.pagination.page,
        limit: state.pagination.limit,
        ...state.filters
      }
      const response = await api.getWrongQuestions(params)
      commit('SET_WRONG_QUESTIONS', response.data)
      return response
    } finally {
      commit('SET_LOADING', { type: 'wrongQuestions', loading: false })
    }
  },
  
  // 添加错题
  async addWrongQuestion({ dispatch }, questionId) {
    const response = await api.addWrongQuestion({ questionId })
    // 添加后重新获取错题列表
    await dispatch('getWrongQuestions')
    return response
  },
  
  // 移除错题
  async removeWrongQuestion({ dispatch }, id) {
    const response = await api.removeWrongQuestion(id)
    // 移除后重新获取错题列表
    await dispatch('getWrongQuestions')
    return response
  },
  
  // 获取统计信息
  async getStats({ commit }) {
    commit('SET_LOADING', { type: 'stats', loading: true })
    try {
      const response = await api.getStats()
      commit('SET_STATS', response.data)
      return response
    } finally {
      commit('SET_LOADING', { type: 'stats', loading: false })
    }
  },
  
  // 更新分页
  updatePagination({ commit }, pagination) {
    commit('UPDATE_PAGINATION', pagination)
  },
  
  // 更新筛选条件
  updateFilters({ commit }, filters) {
    commit('UPDATE_FILTERS', filters)
  },
  
  // 重置筛选条件
  resetFilters({ commit }) {
    commit('UPDATE_FILTERS', {
      keyword: '',
      category: null,
      tags: [],
      difficulty: null,
      questionType: null
    })
  }
}

const getters = {
  // 获取当前页题目列表
  currentQuestions: state => state.questions,
  
  // 获取当前题目
  currentQuestion: state => state.currentQuestion,
  
  // 获取分类选项
  categoryOptions: state => state.categories.map(cat => ({
    label: cat.name,
    value: cat.id
  })),
  
  // 获取标签选项
  tagOptions: state => state.tags.map(tag => ({
    label: tag.name,
    value: tag.id,
    color: tag.color
  })),
  
  // 获取加载状态
  isLoading: state => type => state.loading[type] || false,
  
  // 获取分页信息
  pagination: state => state.pagination,
  
  // 获取筛选条件
  filters: state => state.filters
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}