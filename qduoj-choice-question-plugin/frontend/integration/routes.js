// 选择题插件路由配置
import QuestionManagement from '../views/QuestionManagement.vue'
import CategoryManagement from '../views/CategoryManagement.vue'
import QuestionAnswering from '../components/QuestionAnswering.vue'
import WrongQuestionBook from '../views/WrongQuestionBook.vue'
import QuestionStatistics from '../views/QuestionStatistics.vue'

// 普通用户路由（OJ前端）
export const ojRoutes = [
  {
    name: 'choice-question-list',
    path: '/choice-question',
    meta: { title: '选择题练习' },
    component: QuestionManagement
  },
  {
    name: 'choice-question-answering',
    path: '/choice-question/:questionId/answer',
    meta: { title: '答题', requiresAuth: true },
    component: QuestionAnswering
  },
  {
    name: 'choice-question-wrong-book',
    path: '/choice-question/wrong-book',
    meta: { title: '错题本', requiresAuth: true },
    component: WrongQuestionBook
  },
  {
    name: 'choice-question-statistics',
    path: '/choice-question/statistics',
    meta: { title: '练习统计', requiresAuth: true },
    component: QuestionStatistics
  }
]

// 管理员路由（Admin后端）
export const adminRoutes = [
  {
    path: '/choice-question',
    name: 'choice-question-management',
    component: QuestionManagement
  },
  {
    path: '/choice-question/create',
    name: 'create-choice-question',
    component: () => import('../components/QuestionEditor.vue')
  },
  {
    path: '/choice-question/edit/:questionId',
    name: 'edit-choice-question',
    component: () => import('../components/QuestionEditor.vue')
  },
  {
    path: '/choice-question/category',
    name: 'choice-question-category',
    component: CategoryManagement
  },
  {
    path: '/choice-question/statistics',
    name: 'choice-question-admin-statistics',
    component: QuestionStatistics
  }
]

// 路由集成函数
export function integrateRoutes(router, isAdmin = false) {
  const routes = isAdmin ? adminRoutes : ojRoutes
  
  routes.forEach(route => {
    router.addRoute(route)
  })
}

// 导出默认配置
export default {
  ojRoutes,
  adminRoutes,
  integrateRoutes
}