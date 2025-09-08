import Vue from 'vue'
import VueRouter from 'vue-router'
// 引入 view 组件
import { Announcement, Conf, Contest, ContestList, Home, JudgeServer, Login,
  Problem, ProblemList, User, PruneTestCase, Dashboard, ProblemImportOrExport,
  ChoiceQuestion, ChoiceQuestionList, CategoryManagement, TagManagement, ImportChoiceQuestion, ImportExamPaper, TopicPracticeManagement, TopicManagement, CreateTopic, ExamPaperList, ExamStatistics } from './views'
Vue.use(VueRouter)

export default new VueRouter({
  mode: 'history',
  base: '/admin/',
  scrollBehavior: () => ({y: 0}),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/',
      component: Home,
      children: [
        {
          path: '',
          name: 'dashboard',
          component: Dashboard
        },
        {
          path: '/announcement',
          name: 'announcement',
          component: Announcement
        },
        {
          path: '/user',
          name: 'user',
          component: User
        },
        {
          path: '/conf',
          name: 'conf',
          component: Conf
        },
        {
          path: '/judge-server',
          name: 'judge-server',
          component: JudgeServer
        },
        {
          path: '/prune-test-case',
          name: 'prune-test-case',
          component: PruneTestCase
        },
        {
          path: '/problems',
          name: 'problem-list',
          component: ProblemList
        },
        {
          path: '/problem/create',
          name: 'create-problem',
          component: Problem
        },
        {
          path: '/problem/edit/:problemId',
          name: 'edit-problem',
          component: Problem
        },
        {
          path: '/problem/batch_ops',
          name: 'problem_batch_ops',
          component: ProblemImportOrExport
        },
        {
          path: '/choice-questions',
          name: 'choice-question-list',
          component: ChoiceQuestionList
        },
        {
          path: '/choice-question/create',
          name: 'create-choice-question',
          component: ChoiceQuestion
        },
        {
          path: '/choice-question/edit/:choiceQuestionId',
          name: 'edit-choice-question',
          component: ChoiceQuestion
        },
        {
          path: '/choice-question/category',
          name: 'choice-question-category',
          component: CategoryManagement
        },
        {
          path: '/choice-question/tag',
          name: 'choice-question-tag',
          component: TagManagement
        },
        {
          path: '/choice-question/import',
          name: 'import-choice-question',
          component: ImportChoiceQuestion
        },
        {
          path: '/exam-paper/import',
          name: 'import-exam-paper',
          component: ImportExamPaper
        },
        {
          path: '/topic-practice/management',
          name: 'topic-practice-management',
          component: TopicPracticeManagement
        },
        {
          path: '/topic/management',
          name: 'topic-management',
          component: TopicManagement
        },
        {
          path: '/topic/create',
          name: 'create-topic',
          component: CreateTopic
        },
        {
          path: '/topic/edit/:topicId',
          name: 'edit-topic',
          component: CreateTopic
        },

        {
          path: '/exam-papers',
          name: 'exam-paper-list',
          component: ExamPaperList
        },
        {
          path: '/exam-statistics',
          name: 'exam-statistics',
          component: ExamStatistics
        },
        {
          path: '/contest/create',
          name: 'create-contest',
          component: Contest
        },
        {
          path: '/contest',
          name: 'contest-list',
          component: ContestList
        },
        {
          path: '/contest/:contestId/edit',
          name: 'edit-contest',
          component: Contest
        },
        {
          path: '/contest/:contestId/announcement',
          name: 'contest-announcement',
          component: Announcement
        },
        {
          path: '/contest/:contestId/problems',
          name: 'contest-problem-list',
          component: ProblemList
        },
        {
          path: '/contest/:contestId/problem/create',
          name: 'create-contest-problem',
          component: Problem
        },
        {
          path: '/contest/:contestId/problem/:problemId/edit',
          name: 'edit-contest-problem',
          component: Problem
        }
      ]
    },
    {
      path: '*', redirect: '/login'
    }
  ]
})
