// 选择题插件菜单集成配置

// OJ前端导航栏菜单项
export const ojNavMenuItems = [
  {
    name: '/choice-question',
    icon: 'ios-list-box',
    title: '选择题练习',
    order: 15 // 在问题和竞赛之间
  }
]

// OJ前端子菜单项
export const ojSubMenuItems = [
  {
    name: 'choice-question-practice',
    title: '选择题练习',
    icon: 'ios-list-box',
    children: [
      {
        name: '/choice-question',
        title: '题目练习'
      },
      {
        name: '/choice-question/wrong-book',
        title: '错题本',
        requiresAuth: true
      },
      {
        name: '/choice-question/statistics',
        title: '练习统计',
        requiresAuth: true
      }
    ]
  }
]

// Admin后端侧边栏菜单项
export const adminSideMenuItems = [
  {
    index: 'choice-question',
    title: '选择题管理',
    icon: 'el-icon-fa-list-alt',
    order: 25, // 在问题管理之后
    children: [
      {
        index: '/choice-question',
        title: '题目管理'
      },
      {
        index: '/choice-question/create',
        title: '创建题目'
      },
      {
        index: '/choice-question/category',
        title: '分类管理'
      },
      {
        index: '/choice-question/statistics',
        title: '统计分析'
      }
    ]
  }
]

// 菜单集成函数
export function integrateOJMenu(menuComponent) {
  // 在NavBar组件中添加选择题菜单项
  if (menuComponent && menuComponent.$options && menuComponent.$options.template) {
    // 动态添加菜单项到模板中
    const menuItemHtml = `
      <Menu-item name="/choice-question">
        <Icon type="ios-list-box"></Icon>
        选择题练习
      </Menu-item>
    `
    
    // 在问题菜单项后插入
    const template = menuComponent.$options.template
    const problemMenuIndex = template.indexOf('{{$t(\'m.NavProblems\')}}')
    if (problemMenuIndex !== -1) {
      const insertIndex = template.indexOf('</Menu-item>', problemMenuIndex) + '</Menu-item>'.length
      menuComponent.$options.template = template.slice(0, insertIndex) + menuItemHtml + template.slice(insertIndex)
    }
  }
}

export function integrateAdminMenu(sideMenuComponent) {
  // 在SideMenu组件中添加选择题管理菜单
  if (sideMenuComponent && sideMenuComponent.$options && sideMenuComponent.$options.template) {
    const submenuHtml = `
      <el-submenu index="choice-question" v-if="hasProblemPermission">
        <template slot="title"><i class="el-icon-fa-list-alt"></i>选择题管理</template>
        <el-menu-item index="/choice-question">题目管理</el-menu-item>
        <el-menu-item index="/choice-question/create">创建题目</el-menu-item>
        <el-menu-item index="/choice-question/category">分类管理</el-menu-item>
        <el-menu-item index="/choice-question/statistics">统计分析</el-menu-item>
      </el-submenu>
    `
    
    // 在问题管理菜单后插入
    const template = sideMenuComponent.$options.template
    const problemSubmenuIndex = template.indexOf('</el-submenu>')
    if (problemSubmenuIndex !== -1) {
      const insertIndex = problemSubmenuIndex + '</el-submenu>'.length
      sideMenuComponent.$options.template = template.slice(0, insertIndex) + submenuHtml + template.slice(insertIndex)
    }
  }
}

// 国际化文本
export const i18nTexts = {
  'zh-CN': {
    'Choice_Question_Practice': '选择题练习',
    'Choice_Question_Management': '选择题管理',
    'Question_Practice': '题目练习',
    'Wrong_Question_Book': '错题本',
    'Practice_Statistics': '练习统计',
    'Question_Management': '题目管理',
    'Create_Question': '创建题目',
    'Category_Management': '分类管理',
    'Statistics_Analysis': '统计分析'
  },
  'en-US': {
    'Choice_Question_Practice': 'Choice Question Practice',
    'Choice_Question_Management': 'Choice Question Management',
    'Question_Practice': 'Question Practice',
    'Wrong_Question_Book': 'Wrong Question Book',
    'Practice_Statistics': 'Practice Statistics',
    'Question_Management': 'Question Management',
    'Create_Question': 'Create Question',
    'Category_Management': 'Category Management',
    'Statistics_Analysis': 'Statistics Analysis'
  }
}

// 导出默认配置
export default {
  ojNavMenuItems,
  ojSubMenuItems,
  adminSideMenuItems,
  integrateOJMenu,
  integrateAdminMenu,
  i18nTexts
}