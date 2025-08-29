// 选择题模块路由配置

const ChoiceQuestionList = () => import('../views/ChoiceQuestionList.vue')
const ChoiceQuestionDetail = () => import('../views/ChoiceQuestionDetail.vue')
const WrongQuestionBook = () => import('../views/WrongQuestionBook.vue')

export const choiceQuestionRoutes = [
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

// 导出路由配置，供主应用集成使用
export default {
  routes: choiceQuestionRoutes,
  // 菜单配置
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
  }
}