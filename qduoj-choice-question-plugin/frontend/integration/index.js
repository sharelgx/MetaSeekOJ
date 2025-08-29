// 选择题插件前端集成主入口文件
import routeConfig from './routes.js'
import menuConfig from './menu.js'
import { CategoryAPI, QuestionAPI, TagAPI } from '../api/index.js'

// 插件信息
export const pluginInfo = {
  name: 'choice-question-plugin',
  version: '1.0.0',
  description: '选择题练习插件',
  author: 'QDUOJ Team',
  homepage: 'https://github.com/QingdaoU/OnlineJudge'
}

// 插件配置
export const pluginConfig = {
  // API基础路径
  apiBaseUrl: '/api/choice-question',
  
  // 权限配置
  permissions: {
    // 普通用户权限
    user: {
      canAnswer: true,
      canViewWrongBook: true,
      canViewStatistics: true
    },
    // 管理员权限
    admin: {
      canManageQuestions: true,
      canManageCategories: true,
      canViewAllStatistics: true,
      canImportExport: true
    }
  },
  
  // 功能开关
  features: {
    enableWrongBook: true,
    enableStatistics: true,
    enableTags: true,
    enableCategories: true,
    enableImportExport: true,
    enableBatchOperations: true
  }
}

// 插件初始化函数
export function initializePlugin(app, options = {}) {
  const config = { ...pluginConfig, ...options }
  
  // 注册API服务
  if (app.config && app.config.globalProperties) {
    app.config.globalProperties.$choiceQuestionAPI = {
      category: CategoryAPI,
      question: QuestionAPI,
      tag: TagAPI
    }
  }
  
  // 添加全局配置
  if (app.provide) {
    app.provide('choiceQuestionConfig', config)
  }
  
  console.log(`[${pluginInfo.name}] Plugin initialized successfully`)
  
  return config
}

// OJ前端集成函数
export function integrateWithOJ(router, store, i18n) {
  try {
    // 集成路由
    if (router && routeConfig.ojRoutes) {
      routeConfig.ojRoutes.forEach(route => {
        router.addRoute(route)
      })
      console.log(`[${pluginInfo.name}] OJ routes integrated successfully`)
    }
    
    // 集成国际化
    if (i18n && menuConfig.i18nTexts) {
      Object.keys(menuConfig.i18nTexts).forEach(locale => {
        if (i18n.messages[locale]) {
          Object.assign(i18n.messages[locale], menuConfig.i18nTexts[locale])
        }
      })
      console.log(`[${pluginInfo.name}] I18n texts integrated successfully`)
    }
    
    // 集成Vuex状态管理（如果需要）
    if (store) {
      store.registerModule('choiceQuestion', {
        namespaced: true,
        state: {
          currentQuestion: null,
          categories: [],
          tags: [],
          statistics: {}
        },
        mutations: {
          SET_CURRENT_QUESTION(state, question) {
            state.currentQuestion = question
          },
          SET_CATEGORIES(state, categories) {
            state.categories = categories
          },
          SET_TAGS(state, tags) {
            state.tags = tags
          },
          SET_STATISTICS(state, statistics) {
            state.statistics = statistics
          }
        },
        actions: {
          async fetchCategories({ commit }) {
            try {
              const response = await CategoryAPI.getCategories()
              commit('SET_CATEGORIES', response.data.results)
            } catch (error) {
              console.error('Failed to fetch categories:', error)
            }
          },
          async fetchTags({ commit }) {
            try {
              const response = await TagAPI.getTags()
              commit('SET_TAGS', response.data.results)
            } catch (error) {
              console.error('Failed to fetch tags:', error)
            }
          }
        }
      })
      console.log(`[${pluginInfo.name}] Vuex module registered successfully`)
    }
    
    return true
  } catch (error) {
    console.error(`[${pluginInfo.name}] Failed to integrate with OJ:`, error)
    return false
  }
}

// Admin后端集成函数
export function integrateWithAdmin(router, store, i18n) {
  try {
    // 集成路由
    if (router && routeConfig.adminRoutes) {
      // 在Admin的Home组件子路由中添加选择题管理路由
      const homeRoute = router.getRoutes().find(route => route.path === '/')
      if (homeRoute) {
        routeConfig.adminRoutes.forEach(route => {
          router.addRoute('/', route) // 添加为Home路由的子路由
        })
      }
      console.log(`[${pluginInfo.name}] Admin routes integrated successfully`)
    }
    
    // 集成国际化
    if (i18n && menuConfig.i18nTexts) {
      Object.keys(menuConfig.i18nTexts).forEach(locale => {
        if (i18n.messages[locale]) {
          Object.assign(i18n.messages[locale], menuConfig.i18nTexts[locale])
        }
      })
      console.log(`[${pluginInfo.name}] Admin I18n texts integrated successfully`)
    }
    
    return true
  } catch (error) {
    console.error(`[${pluginInfo.name}] Failed to integrate with Admin:`, error)
    return false
  }
}

// 菜单集成辅助函数
export function integrateMenus(isAdmin = false) {
  // 这个函数需要在组件挂载后调用
  if (typeof window !== 'undefined') {
    // 延迟执行，确保组件已经挂载
    setTimeout(() => {
      if (isAdmin) {
        // 查找Admin侧边栏组件并集成菜单
        const sideMenuElements = document.querySelectorAll('.vertical_menu')
        if (sideMenuElements.length > 0) {
          console.log(`[${pluginInfo.name}] Admin menu integration attempted`)
        }
      } else {
        // 查找OJ导航栏组件并集成菜单
        const navElements = document.querySelectorAll('.oj-menu')
        if (navElements.length > 0) {
          console.log(`[${pluginInfo.name}] OJ menu integration attempted`)
        }
      }
    }, 1000)
  }
}

// 导出所有配置和函数
export default {
  pluginInfo,
  pluginConfig,
  routeConfig,
  menuConfig,
  initializePlugin,
  integrateWithOJ,
  integrateWithAdmin,
  integrateMenus
}

// 导出API
export { CategoryAPI, QuestionAPI, TagAPI }