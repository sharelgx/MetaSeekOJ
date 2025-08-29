import Vue from 'vue'
import ElementUI from 'element-ui'
import VueRouter from 'vue-router'
import Vuex from 'vuex'

// 配置Vue以避免生产提示
Vue.config.productionTip = false

// 全局安装插件
Vue.use(ElementUI)
Vue.use(VueRouter)
Vue.use(Vuex)

// 模拟全局对象
Object.defineProperty(window, 'localStorage', {
  value: {
    store: {},
    getItem: function(key) {
      return this.store[key] || null
    },
    setItem: function(key, value) {
      this.store[key] = String(value)
    },
    removeItem: function(key) {
      delete this.store[key]
    },
    clear: function() {
      this.store = {}
    }
  },
  writable: true
})

Object.defineProperty(window, 'sessionStorage', {
  value: {
    store: {},
    getItem: function(key) {
      return this.store[key] || null
    },
    setItem: function(key, value) {
      this.store[key] = String(value)
    },
    removeItem: function(key) {
      delete this.store[key]
    },
    clear: function() {
      this.store = {}
    }
  },
  writable: true
})

// 模拟window.location
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000',
    origin: 'http://localhost:3000',
    protocol: 'http:',
    host: 'localhost:3000',
    hostname: 'localhost',
    port: '3000',
    pathname: '/',
    search: '',
    hash: '',
    reload: jest.fn(),
    assign: jest.fn(),
    replace: jest.fn()
  },
  writable: true
})

// 模拟console方法以避免测试输出污染
global.console = {
  ...console,
  // 保留error和warn用于调试
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn()
}

// 模拟IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

// 模拟ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

// 模拟matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn()
  }))
})

// 模拟requestAnimationFrame
global.requestAnimationFrame = callback => {
  setTimeout(callback, 0)
}

global.cancelAnimationFrame = id => {
  clearTimeout(id)
}

// 模拟URL构造函数
global.URL = class URL {
  constructor(url, base) {
    this.href = url
    this.origin = base || 'http://localhost:3000'
    this.protocol = 'http:'
    this.host = 'localhost:3000'
    this.hostname = 'localhost'
    this.port = '3000'
    this.pathname = '/'
    this.search = ''
    this.hash = ''
  }
  
  toString() {
    return this.href
  }
}

// 模拟File和FileReader
global.File = class File {
  constructor(chunks, filename, options = {}) {
    this.chunks = chunks
    this.name = filename
    this.size = chunks.reduce((acc, chunk) => acc + chunk.length, 0)
    this.type = options.type || ''
    this.lastModified = options.lastModified || Date.now()
  }
}

global.FileReader = class FileReader {
  constructor() {
    this.readyState = 0
    this.result = null
    this.error = null
    this.onload = null
    this.onerror = null
    this.onabort = null
  }
  
  readAsText(file) {
    setTimeout(() => {
      this.readyState = 2
      this.result = file.chunks.join('')
      if (this.onload) {
        this.onload({ target: this })
      }
    }, 0)
  }
  
  readAsDataURL(file) {
    setTimeout(() => {
      this.readyState = 2
      this.result = `data:${file.type};base64,${btoa(file.chunks.join(''))}`
      if (this.onload) {
        this.onload({ target: this })
      }
    }, 0)
  }
  
  abort() {
    this.readyState = 2
    if (this.onabort) {
      this.onabort({ target: this })
    }
  }
}

// 模拟Blob
global.Blob = class Blob {
  constructor(chunks = [], options = {}) {
    this.size = chunks.reduce((acc, chunk) => acc + chunk.length, 0)
    this.type = options.type || ''
    this.chunks = chunks
  }
  
  text() {
    return Promise.resolve(this.chunks.join(''))
  }
  
  arrayBuffer() {
    const buffer = new ArrayBuffer(this.size)
    const view = new Uint8Array(buffer)
    let offset = 0
    
    this.chunks.forEach(chunk => {
      for (let i = 0; i < chunk.length; i++) {
        view[offset + i] = chunk.charCodeAt(i)
      }
      offset += chunk.length
    })
    
    return Promise.resolve(buffer)
  }
}

// 设置默认的测试超时时间
jest.setTimeout(10000)

// 全局错误处理
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason)
})

// 清理函数
beforeEach(() => {
  // 清理localStorage和sessionStorage
  localStorage.clear()
  sessionStorage.clear()
  
  // 清理所有模拟
  jest.clearAllMocks()
})

afterEach(() => {
  // 清理DOM
  document.body.innerHTML = ''
  
  // 清理定时器
  jest.clearAllTimers()
})

// 导出常用的测试工具
export const createMockStore = (modules = {}) => {
  return new Vuex.Store({
    modules: {
      choiceQuestion: {
        namespaced: true,
        state: {
          questions: [],
          categories: [],
          tags: [],
          loading: false,
          error: null
        },
        mutations: {
          SET_QUESTIONS: (state, questions) => {
            state.questions = questions
          },
          SET_CATEGORIES: (state, categories) => {
            state.categories = categories
          },
          SET_TAGS: (state, tags) => {
            state.tags = tags
          },
          SET_LOADING: (state, loading) => {
            state.loading = loading
          },
          SET_ERROR: (state, error) => {
            state.error = error
          }
        },
        actions: {
          getQuestions: jest.fn(),
          getCategories: jest.fn(),
          getTags: jest.fn(),
          submitAnswer: jest.fn()
        },
        getters: {
          questions: state => state.questions,
          categories: state => state.categories,
          tags: state => state.tags,
          loading: state => state.loading,
          error: state => state.error
        },
        ...modules.choiceQuestion
      },
      ...modules
    }
  })
}

export const createMockRouter = (routes = []) => {
  return new VueRouter({
    mode: 'abstract',
    routes: [
      { path: '/', name: 'Home' },
      { path: '/practice', name: 'Practice' },
      { path: '/wrong-questions', name: 'WrongQuestions' },
      { path: '/statistics', name: 'Statistics' },
      { path: '/admin/questions', name: 'AdminQuestions' },
      { path: '/admin/categories', name: 'AdminCategories' },
      ...routes
    ]
  })
}