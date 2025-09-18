// Main entry point for the application
import Vue from 'vue'
import App from './pages/oj/App.vue'
import router from './pages/oj/router'
import store from './store'
import i18n from './i18n'

// Import global styles
import 'iview/dist/styles/iview.css'
import './styles/index.less'

Vue.config.productionTip = false

new Vue({
  el: '#app',
  router,
  store,
  i18n,
  render: h => h(App)
})