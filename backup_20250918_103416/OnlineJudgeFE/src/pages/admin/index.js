import 'babel-polyfill'
import Vue from 'vue'
import App from './App.vue'
import store from '@/store'
import i18n from '@/i18n'
import Element from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

import filters from '@/utils/filters'
import router from './router'
import { GOOGLE_ANALYTICS_ID } from '@/utils/constants'
import VueAnalytics from 'vue-analytics'
import katex from '@/plugins/katex'
import api from './api'
import { types } from '@/store'

import Panel from './components/Panel.vue'
import IconBtn from './components/btn/IconBtn.vue'
import Save from './components/btn/Save.vue'
import Cancel from './components/btn/Cancel.vue'
import './style.less'

// register global utility filters.
Object.keys(filters).forEach(key => {
  Vue.filter(key, filters[key])
})

Vue.use(VueAnalytics, {
  id: GOOGLE_ANALYTICS_ID,
  router
})
Vue.use(katex)
Vue.component(IconBtn.name, IconBtn)
Vue.component(Panel.name, Panel)
Vue.component(Save.name, Save)
Vue.component(Cancel.name, Cancel)

// 添加全局路由守卫
router.beforeEach(async (to, from, next) => {
  console.log('Global route guard triggered, target:', to.path, 'name:', to.name)
  
  // 如果访问的是登录页面，直接放行
  if (to.name === 'login') {
    console.log('Accessing login page, allowing access')
    next()
    return
  }
  
  // 检查用户登录状态
  console.log('Checking user profile...')
  try {
    const res = await api.getProfile()
    console.log('Profile API response:', res.data)
    
    if (!res.data.data || !res.data.data.user) {
      // 未登录，重定向到登录页面并携带redirect参数
      console.log('No profile data, redirecting to login with redirect:', to.fullPath)
      store.dispatch('clearProfile')
      next({name: 'login', query: {redirect: to.fullPath}})
    } else {
      // 已登录，更新store并继续
      console.log('Profile data found, updating store and proceeding')
      store.commit(types.CHANGE_PROFILE, {profile: res.data.data})
      
      // 检查是否有管理员权限 - 修复权限检查逻辑
      const user = res.data.data.user
      console.log('User admin_type:', user.admin_type)
      console.log('Admin type check:', user.admin_type === 'Admin' || user.admin_type === 'Super Admin')
      
      // 使用正确的权限检查逻辑
      const isAdmin = user.admin_type === 'Admin' || user.admin_type === 'Super Admin'
      
      if (!isAdmin) {
        console.log('User does not have admin privileges, admin_type:', user.admin_type)
        Vue.prototype.$error('您没有管理员权限')
        next({name: 'login'}) // 重定向到登录页面
      } else {
        console.log('User has admin privileges, proceeding')
        next()
      }
    }
  } catch (err) {
    // API调用失败，重定向到登录页面
    console.error('Profile API error:', err)
    
    // 清除可能过期的认证信息
    store.dispatch('clearProfile')
    
    next({name: 'login', query: {redirect: to.fullPath}})
  }
})

Vue.use(Element, {
  i18n: (key, value) => i18n.t(key, value)
})

Vue.prototype.$error = (msg) => {
  Vue.prototype.$message({'message': msg, 'type': 'error'})
}

Vue.prototype.$warning = (msg) => {
  Vue.prototype.$message({'message': msg, 'type': 'warning'})
}

Vue.prototype.$success = (msg) => {
  if (!msg) {
    Vue.prototype.$message({'message': 'Succeeded', 'type': 'success'})
  } else {
    Vue.prototype.$message({'message': msg, 'type': 'success'})
  }
}

new Vue(Vue.util.extend({router, store, i18n}, App)).$mount('#app')
