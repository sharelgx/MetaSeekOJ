const fs = require('fs');
const path = require('path');

class AutoFixer {
  static async checkAndFixRoutes() {
    const routerPath = path.join(__dirname, '../src/pages/admin/router.js');
    
    if (!fs.existsSync(routerPath)) {
      console.log('Router file not found:', routerPath);
      return false;
    }
    
    const content = fs.readFileSync(routerPath, 'utf8');
    
    // 检查是否包含选择题路由
    if (!content.includes('choice-question')) {
      console.log('Adding missing choice question routes...');
      
      // 检查是否已导入组件
      if (!content.includes('ChoiceQuestion') || !content.includes('ChoiceQuestionList')) {
        console.log('Adding missing component imports...');
        
        const importSection = content.match(/(import.*from.*views.*\n)+/);
        if (importSection) {
          const newImports = `import ChoiceQuestion from '@/pages/admin/views/choice-question/ChoiceQuestion'
import ChoiceQuestionList from '@/pages/admin/views/choice-question/ChoiceQuestionList'
`;
          const updatedContent = content.replace(importSection[0], importSection[0] + newImports);
          fs.writeFileSync(routerPath, updatedContent);
        }
      }
      
      // 重新读取文件内容
      const updatedContent = fs.readFileSync(routerPath, 'utf8');
      
      // 添加路由配置
      const routeConfig = `        {
          path: '/choice-questions',
          name: 'choice-question-list',
          component: ChoiceQuestionList,
          meta: { title: 'Choice Question List' }
        },
        {
          path: '/choice-question/create',
          name: 'create-choice-question',
          component: ChoiceQuestion,
          meta: { title: 'Create Choice Question' }
        },
        {
          path: '/choice-question/:id/edit',
          name: 'edit-choice-question',
          component: ChoiceQuestion,
          meta: { title: 'Edit Choice Question' }
        },`;
      
      // 查找children数组并插入路由
      const childrenMatch = updatedContent.match(/(children:\s*\[)([\s\S]*?)(\]\s*}\s*\])/m);
      if (childrenMatch) {
        const newContent = updatedContent.replace(
          childrenMatch[0],
          childrenMatch[1] + '\n' + routeConfig + '\n' + childrenMatch[2] + childrenMatch[3]
        );
        fs.writeFileSync(routerPath, newContent);
        console.log('Routes added successfully');
        return true;
      }
    }
    
    return false;
  }
  
  static async checkAndFixSideMenu() {
    const menuPath = path.join(__dirname, '../src/pages/admin/components/SideMenu.vue');
    
    if (!fs.existsSync(menuPath)) {
      console.log('SideMenu file not found:', menuPath);
      return false;
    }
    
    const content = fs.readFileSync(menuPath, 'utf8');
    
    if (!content.includes('choice-question')) {
      console.log('Adding missing choice question menu item...');
      
      const menuItem = `        <el-submenu index="choice-question" v-if="user.problem_permission === 'All'">
          <template slot="title">
            <i class="el-icon-fa-list-alt"></i>
            {{ $t('m.Choice_Question') }}
          </template>
          <el-menu-item index="choice-question-list">
            <router-link :to="{name: 'choice-question-list'}">
              {{ $t('m.Choice_Question_List') }}
            </router-link>
          </el-menu-item>
          <el-menu-item index="create-choice-question">
            <router-link :to="{name: 'create-choice-question'}">
              {{ $t('m.Create_Choice_Question') }}
            </router-link>
          </el-menu-item>
        </el-submenu>`;
      
      // 在问题菜单后插入选择题菜单
      const problemMenuMatch = content.match(/(<el-submenu index="problem"[\s\S]*?<\/el-submenu>)/);
      if (problemMenuMatch) {
        const updatedContent = content.replace(
          problemMenuMatch[0],
          problemMenuMatch[0] + '\n' + menuItem
        );
        
        fs.writeFileSync(menuPath, updatedContent);
        console.log('Menu item added successfully');
        return true;
      }
    }
    
    return false;
  }
  
  static async checkAndFixAPI() {
    const apiPath = path.join(__dirname, '../src/pages/admin/api.js');
    
    if (!fs.existsSync(apiPath)) {
      console.log('API file not found:', apiPath);
      return false;
    }
    
    const content = fs.readFileSync(apiPath, 'utf8');
    
    if (!content.includes('getChoiceQuestions')) {
      console.log('Adding missing choice question API methods...');
      
      const apiMethods = `
// Choice Question API
export function getChoiceQuestions(offset, limit, keyword) {
  let params = {
    paging: true,
    offset,
    limit
  }
  if (keyword) {
    params.keyword = keyword
  }
  return ajax('choice_questions', 'get', {
    params
  })
}

export function createChoiceQuestion(data) {
  return ajax('choice_question', 'post', {
    data
  })
}

export function getChoiceQuestion(id) {
  return ajax('choice_question', 'get', {
    params: {
      id
    }
  })
}

export function editChoiceQuestion(data) {
  return ajax('choice_question', 'put', {
    data
  })
}

export function deleteChoiceQuestion(id) {
  return ajax('choice_question', 'delete', {
    params: {
      id
    }
  })
}`;
      
      // 在文件末尾添加API方法
      const updatedContent = content + apiMethods;
      fs.writeFileSync(apiPath, updatedContent);
      console.log('API methods added successfully');
      return true;
    }
    
    return false;
  }
  
  static async checkAndFixI18n() {
    const zhPath = path.join(__dirname, '../src/i18n/admin/zh-CN.js');
    const enPath = path.join(__dirname, '../src/i18n/admin/en-US.js');
    
    let fixed = false;
    
    // 检查中文翻译
    if (fs.existsSync(zhPath)) {
      const zhContent = fs.readFileSync(zhPath, 'utf8');
      if (!zhContent.includes('Choice_Question')) {
        console.log('Adding missing Chinese translations...');
        
        const translations = `  Choice_Question: '选择题',
  Choice_Question_List: '选择题列表',
  Create_Choice_Question: '创建选择题',
  Options: '选项',
  Explanation: '解释',`;
        
        // 在合适位置插入翻译
        const insertPoint = zhContent.lastIndexOf('}');
        if (insertPoint > 0) {
          const updatedContent = zhContent.slice(0, insertPoint) + '  ' + translations + '\n' + zhContent.slice(insertPoint);
          fs.writeFileSync(zhPath, updatedContent);
          fixed = true;
        }
      }
    }
    
    // 检查英文翻译
    if (fs.existsSync(enPath)) {
      const enContent = fs.readFileSync(enPath, 'utf8');
      if (!enContent.includes('Choice_Question')) {
        console.log('Adding missing English translations...');
        
        const translations = `  Choice_Question: 'Choice Question',
  Choice_Question_List: 'Choice Question List',
  Create_Choice_Question: 'Create Choice Question',
  Options: 'Options',
  Explanation: 'Explanation',`;
        
        // 在合适位置插入翻译
        const insertPoint = enContent.lastIndexOf('}');
        if (insertPoint > 0) {
          const updatedContent = enContent.slice(0, insertPoint) + '  ' + translations + '\n' + enContent.slice(insertPoint);
          fs.writeFileSync(enPath, updatedContent);
          fixed = true;
        }
      }
    }
    
    if (fixed) {
      console.log('I18n translations added successfully');
    }
    
    return fixed;
  }
  
  static async runAllFixes() {
    console.log('Starting auto-fix process...');
    
    const results = {
      routes: await this.checkAndFixRoutes(),
      sideMenu: await this.checkAndFixSideMenu(),
      api: await this.checkAndFixAPI(),
      i18n: await this.checkAndFixI18n()
    };
    
    console.log('Auto-fix results:', results);
    
    const hasChanges = Object.values(results).some(result => result === true);
    
    if (hasChanges) {
      console.log('Changes made, frontend restart recommended');
    } else {
      console.log('No changes needed');
    }
    
    return results;
  }
}

module.exports = AutoFixer;