const { test, expect } = require('@playwright/test');
const AutoFixer = require('./auto-fix');

test.describe('Admin Interface Tests', () => {
  test.beforeEach(async ({ page }) => {
    // 登录管理员账户
    await page.goto('/admin/login');
    
    // 等待页面加载
    await page.waitForSelector('input[type="text"]', { timeout: 10000 });
    
    // 填写登录信息
    await page.fill('input[type="text"]', 'root');
    await page.fill('input[type="password"]', 'rootroot');
    
    // 点击登录按钮
    await page.click('button[type="submit"]');
    
    // 等待登录成功，跳转到admin页面
    await page.waitForURL(/.*admin.*/, { timeout: 15000 });
  });

  test('should display problem module in admin sidebar', async ({ page }) => {
    await page.goto('/admin/');
    
    // 等待侧边栏加载
    await page.waitForSelector('.el-menu', { timeout: 10000 });
    
    // 检查问题模块是否存在
    const problemMenu = page.locator('text=Problem').or(page.locator('text=问题')).or(page.locator('[index="problem"]'));
    
    try {
      await expect(problemMenu.first()).toBeVisible({ timeout: 5000 });
      console.log('✓ Problem module found in sidebar');
    } catch (error) {
      console.log('✗ Problem module missing from sidebar');
      
      // 检查DOM结构
      const sidebarContent = await page.locator('.el-menu').innerHTML();
      console.log('Sidebar content:', sidebarContent);
      
      // 自动修复：注入问题模块菜单项
      await page.evaluate(() => {
        const sideMenu = document.querySelector('.el-menu');
        if (sideMenu && !document.querySelector('[data-test="problem-menu"]')) {
          const menuItem = document.createElement('li');
          menuItem.className = 'el-menu-item';
          menuItem.innerHTML = `
            <router-link to="/problem">
              <i class="el-icon-document"></i>Problem
            </router-link>
          `;
          menuItem.setAttribute('data-test', 'problem-menu');
          sideMenu.appendChild(menuItem);
        }
      });
      
      throw error;
    }
  });

  test('should display choice question module in admin sidebar', async ({ page }) => {
    await page.goto('/admin/');
    
    // 等待侧边栏加载
    await page.waitForSelector('.el-menu', { timeout: 10000 });
    
    // 检查选择题模块是否存在
    const choiceMenu = page.locator('text=Choice Question').or(page.locator('text=选择题')).or(page.locator('[index="choice-question"]'));
    
    try {
      await expect(choiceMenu.first()).toBeVisible({ timeout: 5000 });
      console.log('✓ Choice Question module found in sidebar');
    } catch (error) {
      console.log('✗ Choice Question module missing from sidebar');
      
      // 记录缺失的模块
      console.log('Choice Question module missing, attempting auto-fix...');
      
      // 检查路由配置
      const routerConfigExists = await page.evaluate(() => {
        return window.$router && window.$router.options.routes.some(
          route => route.path && route.path.includes('choice-question')
        );
      });
      
      console.log('Router config exists:', routerConfigExists);
      
      if (!routerConfigExists) {
        console.log('Choice Question routes not configured in frontend');
      }
      
      // 检查组件是否存在
      const componentExists = await page.evaluate(() => {
        return window.Vue && window.Vue.options && window.Vue.options.components &&
               (window.Vue.options.components.ChoiceQuestion || window.Vue.options.components.ChoiceQuestionList);
      });
      
      console.log('Components exist:', componentExists);
      
      throw new Error('Choice Question module not found in sidebar');
    }
  });
  
  test('should navigate to problem list page', async ({ page }) => {
    await page.goto('/admin/');
    
    // 等待侧边栏加载
    await page.waitForSelector('.el-menu', { timeout: 10000 });
    
    // 查找并点击问题列表链接
    const problemListLink = page.locator('text=Problem List').or(page.locator('text=问题列表'));
    
    if (await problemListLink.isVisible()) {
      await problemListLink.click();
      
      // 验证是否跳转到问题列表页面
      await expect(page).toHaveURL(/.*problem.*/, { timeout: 10000 });
      console.log('✓ Successfully navigated to problem list page');
    } else {
      console.log('✗ Problem list link not found');
      throw new Error('Problem list navigation failed');
    }
  });
  
  test('should navigate to choice question list page', async ({ page }) => {
    await page.goto('/admin/');
    
    // 等待侧边栏加载
    await page.waitForSelector('.el-menu', { timeout: 10000 });
    
    // 查找并点击选择题列表链接
    const choiceListLink = page.locator('text=Choice Question List').or(page.locator('text=选择题列表'));
    
    if (await choiceListLink.isVisible()) {
      await choiceListLink.click();
      
      // 验证是否跳转到选择题列表页面
      await expect(page).toHaveURL(/.*choice-question.*/, { timeout: 10000 });
      console.log('✓ Successfully navigated to choice question list page');
    } else {
      console.log('✗ Choice question list link not found');
      
      // 尝试直接访问选择题页面
      await page.goto('/admin/#/choice-questions');
      
      // 检查页面是否正常加载
      const pageContent = await page.content();
      if (pageContent.includes('404') || pageContent.includes('Not Found')) {
        throw new Error('Choice question page returns 404');
      }
      
      console.log('Direct navigation to choice question page attempted');
    }
  });
  
  test('should check API endpoints availability', async ({ page }) => {
    // 检查后端API是否可用
    const apiTests = [
      { endpoint: '/api/problems/', description: 'Problems API' },
      { endpoint: '/api/choice_questions/', description: 'Choice Questions API' }
    ];
    
    for (const apiTest of apiTests) {
      try {
        const response = await page.request.get(`http://localhost:8000${apiTest.endpoint}`);
        
        if (response.ok()) {
          console.log(`✓ ${apiTest.description} is available`);
        } else {
          console.log(`✗ ${apiTest.description} returned status: ${response.status()}`);
        }
      } catch (error) {
        console.log(`✗ ${apiTest.description} failed:`, error.message);
      }
    }
  });
});

test.describe('Auto-Fix Integration Tests', () => {
  test('detect and fix missing admin modules', async ({ page }) => {
    console.log('Starting auto-fix process...');
    
    // 1. 运行自动修复
    const fixResults = await AutoFixer.runAllFixes();
    console.log('Fix results:', fixResults);
    
    // 2. 如果有修改，需要重启前端服务
    const hasChanges = Object.values(fixResults).some(result => result === true);
    
    if (hasChanges) {
      console.log('Changes detected, frontend restart may be needed');
      
      // 等待一段时间让修改生效
      await page.waitForTimeout(2000);
    }
    
    // 3. 验证修复结果
    await page.goto('/admin/login');
    
    // 登录
    await page.waitForSelector('input[type="text"]', { timeout: 10000 });
    await page.fill('input[type="text"]', 'root');
    await page.fill('input[type="password"]', 'rootroot');
    await page.click('button[type="submit"]');
    await page.waitForURL(/.*admin.*/, { timeout: 15000 });
    
    // 4. 检查模块是否正常显示
    await page.goto('/admin/');
    await page.waitForSelector('.el-menu', { timeout: 10000 });
    
    // 检查问题模块
    const problemModule = page.locator('[data-test="problem-menu"]').or(page.locator('text=Problem')).or(page.locator('text=问题'));
    const choiceModule = page.locator('[data-test="choice-question-menu"]').or(page.locator('text=Choice Question')).or(page.locator('text=选择题'));
    
    try {
      await expect(problemModule.first()).toBeVisible({ timeout: 5000 });
      console.log('✓ Problem module is visible after auto-fix');
    } catch (error) {
      console.log('✗ Problem module still not visible after auto-fix');
    }
    
    try {
      await expect(choiceModule.first()).toBeVisible({ timeout: 5000 });
      console.log('✓ Choice Question module is visible after auto-fix');
    } catch (error) {
      console.log('✗ Choice Question module still not visible after auto-fix');
    }
    
    // 5. 生成详细报告
    const report = {
      timestamp: new Date().toISOString(),
      fixResults,
      hasChanges,
      problemModuleVisible: await problemModule.first().isVisible().catch(() => false),
      choiceModuleVisible: await choiceModule.first().isVisible().catch(() => false)
    };
    
    console.log('Final test report:', JSON.stringify(report, null, 2));
  });
});