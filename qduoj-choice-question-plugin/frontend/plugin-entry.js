/**
 * 青岛OJ选择题插件前端入口文件
 * 负责插件的动态注册、路由配置和菜单集成
 */

// 插件元信息
const PLUGIN_INFO = {
  name: 'qduoj-choice-question-plugin',
  version: '1.0.0',
  description: '青岛OJ选择题功能插件',
  author: 'QDU OJ Team'
}

// 插件配置
const PLUGIN_CONFIG = {
  namespace: 'choiceQuestion',
  routePrefix: '/choice-question',
  apiPrefix: '/api/plugin/choice',
  storeName: 'choiceQuestion'
}

/**
 * 插件主类
 */
class ChoiceQuestionPlugin {
  constructor() {
    this.installed = false
    this.router = null
    this.store = null
    this.components = new Map()
    this.routes = []
    this.menuItems = []
  }

  /**
   * 获取插件信息
   */
  getPluginInfo() {
    return PLUGIN_INFO
  }

  /**
   * 获取插件配置
   */
  getPluginConfig() {
    return PLUGIN_CONFIG
  }

  /**
   * 动态导入组件
   */
  async loadComponents() {
    try {
      // 导入页面组件
      const ChoiceQuestionList = await import('./views/ChoiceQuestionList.vue')
      const ChoiceQuestionDetail = await import('./views/ChoiceQuestionDetail.vue')
      const WrongQuestionBook = await import('./views/WrongQuestionBook.vue')
      const QuestionPractice = await import('./views/QuestionPractice.vue')
      const QuestionStatistics = await import('./views/QuestionStatistics.vue')
      
      // 导入通用组件
      const QuestionCard = await import('./components/QuestionCard.vue')
      const CategoryTree = await import('./components/CategoryTree.vue')
      const TagSelector = await import('./components/TagSelector.vue')
      const AnswerAnalysis = await import('./components/AnswerAnalysis.vue')
      
      // 注册组件
      this.components.set('ChoiceQuestionList', ChoiceQuestionList.default)
      this.components.set('ChoiceQuestionDetail', ChoiceQuestionDetail.default)
      this.components.set('WrongQuestionBook', WrongQuestionBook.default)
      this.components.set('QuestionPractice', QuestionPractice.default)
      this.components.set('QuestionStatistics', QuestionStatistics.default)
      this.components.set('QuestionCard', QuestionCard.default)
      this.components.set('CategoryTree', CategoryTree.default)
      this.components.set('TagSelector', TagSelector.default)
      this.components.set('AnswerAnalysis', AnswerAnalysis.default)
      
      return true
    } catch (error) {
      console.error('选择题插件组件加载失败:', error)
      return false
    }
  }

  /**
   * 配置路由
   */
  setupRoutes() {
    this.routes = [
      {
        path: `${PLUGIN_CONFIG.routePrefix}`,
        name: 'ChoiceQuestionIndex',
        component: this.components.get('ChoiceQuestionList'),
        meta: {
          title: '选择题练习',
          requireAuth: true,
          plugin: PLUGIN_INFO.name
        }
      },
      {
        path: `${PLUGIN_CONFIG.routePrefix}/list`,
        name: 'ChoiceQuestionList',
        component: this.components.get('ChoiceQuestionList'),
        meta: {
          title: '题目列表',
          requireAuth: true,
          plugin: PLUGIN_INFO.name
        }
      },
      {
        path: `${PLUGIN_CONFIG.routePrefix}/detail/:id`,
        name: 'ChoiceQuestionDetail',
        component: this.components.get('ChoiceQuestionDetail'),
        meta: {
          title: '题目详情',
          requireAuth: true,
          plugin: PLUGIN_INFO.name
        }
      },
      {
        path: `${PLUGIN_CONFIG.routePrefix}/practice`,
        name: 'QuestionPractice',
        component: this.components.get('QuestionPractice'),
        meta: {
          title: '题目练习',
          requireAuth: true,
          plugin: PLUGIN_INFO.name
        }
      },
      {
        path: `${PLUGIN_CONFIG.routePrefix}/wrong-questions`,
        name: 'WrongQuestionBook',
        component: this.components.get('WrongQuestionBook'),
        meta: {
          title: '错题本',
          requireAuth: true,
          plugin: PLUGIN_INFO.name
        }
      },
      {
        path: `${PLUGIN_CONFIG.routePrefix}/statistics`,
        name: 'QuestionStatistics',
        component: this.components.get('QuestionStatistics'),
        meta: {
          title: '答题统计',
          requireAuth: true,
          plugin: PLUGIN_INFO.name
        }
      }
    ]
  }

  /**
   * 配置菜单项
   */
  setupMenuItems() {
    this.menuItems = [
      {
        name: 'choice-question',
        title: '选择题练习',
        icon: 'el-icon-edit-outline',
        path: `${PLUGIN_CONFIG.routePrefix}`,
        children: [
          {
            name: 'choice-question-list',
            title: '题目练习',
            icon: 'el-icon-document',
            path: `${PLUGIN_CONFIG.routePrefix}/practice`
          },
          {
            name: 'wrong-question-book',
            title: '错题本',
            icon: 'el-icon-warning-outline',
            path: `${PLUGIN_CONFIG.routePrefix}/wrong-questions`
          },
          {
            name: 'question-statistics',
            title: '答题统计',
            icon: 'el-icon-data-analysis',
            path: `${PLUGIN_CONFIG.routePrefix}/statistics`
          }
        ]
      }
    ]
  }

  /**
   * 注册Vuex Store模块
   */
  async setupStore(store) {
    try {
      // 动态导入store模块
      const choiceQuestionStore = await import('./store/index.js')
      
      // 注册store模块
      store.registerModule(PLUGIN_CONFIG.storeName, choiceQuestionStore.default)
      
      this.store = store
      return true
    } catch (error) {
      console.error('选择题插件Store注册失败:', error)
      return false
    }
  }

  /**
   * 注册全局组件
   */
  registerGlobalComponents(Vue) {
    // 注册常用组件为全局组件
    Vue.component('QuestionCard', this.components.get('QuestionCard'))
    Vue.component('CategoryTree', this.components.get('CategoryTree'))
    Vue.component('TagSelector', this.components.get('TagSelector'))
    Vue.component('AnswerAnalysis', this.components.get('AnswerAnalysis'))
  }

  /**
   * 安装插件
   */
  async install(Vue, { router, store }) {
    if (this.installed) {
      console.warn('选择题插件已经安装')
      return false
    }

    try {
      console.log('开始安装选择题插件...')
      
      // 1. 加载组件
      const componentsLoaded = await this.loadComponents()
      if (!componentsLoaded) {
        throw new Error('组件加载失败')
      }
      
      // 2. 配置路由
      this.setupRoutes()
      
      // 3. 注册路由
      if (router) {
        this.routes.forEach(route => {
          router.addRoute(route)
        })
        this.router = router
      }
      
      // 4. 注册Store模块
      if (store) {
        const storeRegistered = await this.setupStore(store)
        if (!storeRegistered) {
          throw new Error('Store模块注册失败')
        }
      }
      
      // 5. 配置菜单
      this.setupMenuItems()
      
      // 6. 注册全局组件
      this.registerGlobalComponents(Vue)
      
      // 7. 添加插件特定的全局方法
      Vue.prototype.$choiceQuestion = {
        config: PLUGIN_CONFIG,
        info: PLUGIN_INFO,
        utils: {
          // 这里可以添加插件工具方法
        }
      }
      
      this.installed = true
      console.log('选择题插件安装成功')
      
      // 触发插件安装完成事件
      if (typeof window !== 'undefined' && window.dispatchEvent) {
        window.dispatchEvent(new CustomEvent('plugin:choice-question:installed', {
          detail: { plugin: this }
        }))
      }
      
      return true
    } catch (error) {
      console.error('选择题插件安装失败:', error)
      return false
    }
  }

  /**
   * 卸载插件
   */
  uninstall() {
    if (!this.installed) {
      return false
    }

    try {
      // 移除路由
      if (this.router) {
        this.routes.forEach(route => {
          this.router.removeRoute(route.name)
        })
      }
      
      // 注销Store模块
      if (this.store) {
        this.store.unregisterModule(PLUGIN_CONFIG.storeName)
      }
      
      // 清理组件
      this.components.clear()
      
      this.installed = false
      console.log('选择题插件卸载成功')
      
      // 触发插件卸载完成事件
      if (typeof window !== 'undefined' && window.dispatchEvent) {
        window.dispatchEvent(new CustomEvent('plugin:choice-question:uninstalled', {
          detail: { plugin: this }
        }))
      }
      
      return true
    } catch (error) {
      console.error('选择题插件卸载失败:', error)
      return false
    }
  }

  /**
   * 获取菜单项
   */
  getMenuItems() {
    return this.menuItems
  }

  /**
   * 获取路由配置
   */
  getRoutes() {
    return this.routes
  }

  /**
   * 检查插件是否已安装
   */
  isInstalled() {
    return this.installed
  }
}

// 创建插件实例
const choiceQuestionPlugin = new ChoiceQuestionPlugin()

// 导出插件实例和安装函数
export default choiceQuestionPlugin

// 兼容不同的模块系统
if (typeof module !== 'undefined' && module.exports) {
  module.exports = choiceQuestionPlugin
}

// 全局注册（如果在浏览器环境中直接引入）
if (typeof window !== 'undefined') {
  window.ChoiceQuestionPlugin = choiceQuestionPlugin
}