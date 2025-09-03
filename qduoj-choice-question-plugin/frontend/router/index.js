// 选择题模块路由配置

const ChoiceQuestionList = () => import('../views/ChoiceQuestionList.vue')
const ChoiceQuestionDetail = () => import('../views/ChoiceQuestionDetail.vue')
const WrongQuestionBook = () => import('../views/WrongQuestionBook.vue')
const QuestionManagement = () => import('../views/QuestionManagement.vue')
const CategoryManagement = () => import('../views/CategoryManagement.vue')
const TagManagement = () => import('../views/TagManagement.vue')
const StatisticsAnalysis = () => import('../views/StatisticsAnalysis.vue')

export const choiceQuestionRoutes = [
  // 用户端路由
  {
    name: 'choice-question-list',
    path: '/choice-questions',
    component: ChoiceQuestionList,
    meta: {
      title: '选择题练习',
      requiresAuth: true
    }
  },
  {
    name: 'choice-question-detail',
    path: '/choice-questions/:id',
    component: ChoiceQuestionDetail,
    meta: {
      title: '选择题详情',
      requiresAuth: true
    }
  },
  {
    name: 'wrong-question-book',
    path: '/wrong-questions',
    component: WrongQuestionBook,
    meta: {
      title: '错题本',
      requiresAuth: true
    }
  }
]

// 管理端路由
export const adminChoiceQuestionRoutes = [
  {
    name: 'question-management',
    path: '/admin/choice-questions',
    component: QuestionManagement,
    meta: {
      title: '选择题管理',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    name: 'category-management',
    path: '/admin/choice-questions/categories',
    component: CategoryManagement,
    meta: {
      title: '分类管理',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    name: 'tag-management',
    path: '/admin/choice-questions/tags',
    component: TagManagement,
    meta: {
      title: '标签管理',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    name: 'choice-question-statistics',
    path: '/admin/choice-questions/statistics',
    component: StatisticsAnalysis,
    meta: {
      title: '统计分析',
      requiresAuth: true,
      requiresAdmin: true
    }
  }
]

// 导出路由配置，供主应用集成使用
export default {
  routes: choiceQuestionRoutes,
  adminRoutes: adminChoiceQuestionRoutes,
  // 用户端菜单配置
  menu: {
    name: '选择题练习',
    icon: 'el-icon-edit-outline',
    children: [
      {
        name: '题目练习',
        route: 'choice-question-list'
      },
      {
        name: '错题本',
        route: 'wrong-question-book'
      }
    ]
  },
  // 管理端菜单配置
  adminMenu: {
    name: '选择题管理',
    icon: 'el-icon-s-management',
    children: [
      {
        name: '题目管理',
        route: 'question-management'
      },
      {
        name: '分类管理',
        route: 'category-management'
      },
      {
        name: '标签管理',
        route: 'tag-management'
      },
      {
        name: '统计分析',
        route: 'choice-question-statistics'
      }
    ]
  }
}