const { test, expect } = require('@playwright/test');

test.describe('Localization Verification Tests', () => {
  test.beforeEach(async ({ page }) => {
    // 设置中文语言环境
    await page.goto('http://localhost:8080/admin/login');
    // 等待页面加载完成
    await page.waitForLoadState('networkidle');
  });

  test('Admin Problem List Page - Should display Chinese text', async ({ page }) => {
    // 登录管理员账户
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin');
    await page.click('button[type="submit"]');
    
    // 等待登录成功并跳转
    await page.waitForURL('**/admin/dashboard');
    
    // 导航到问题列表页面
    await page.goto('http://localhost:8080/admin/problems');
    await page.waitForLoadState('networkidle');
    
    // 验证页面标题和表头是否为中文
    await expect(page.locator('text=问题列表')).toBeVisible();
    await expect(page.locator('text=ID')).toBeVisible();
    await expect(page.locator('text=标题')).toBeVisible();
    await expect(page.locator('text=作者')).toBeVisible();
    await expect(page.locator('text=创建时间')).toBeVisible();
    await expect(page.locator('text=可见')).toBeVisible();
    await expect(page.locator('text=操作')).toBeVisible();
    
    // 验证操作按钮是否为中文
    await expect(page.locator('text=编辑')).toBeVisible();
    await expect(page.locator('text=删除问题')).toBeVisible();
    
    // 验证创建按钮是否为中文
    await expect(page.locator('text=创建')).toBeVisible();
  });

  test('Admin Choice Question List Page - Should display Chinese text', async ({ page }) => {
    // 登录管理员账户
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin');
    await page.click('button[type="submit"]');
    
    // 等待登录成功并跳转
    await page.waitForURL('**/admin/dashboard');
    
    // 导航到选择题列表页面
    await page.goto('http://localhost:8080/admin/choice-questions');
    await page.waitForLoadState('networkidle');
    
    // 验证页面标题和表头是否为中文
    await expect(page.locator('text=选择题管理')).toBeVisible();
    await expect(page.locator('text=ID')).toBeVisible();
    await expect(page.locator('text=标题')).toBeVisible();
    await expect(page.locator('text=作者')).toBeVisible();
    await expect(page.locator('text=创建时间')).toBeVisible();
    await expect(page.locator('text=可见')).toBeVisible();
    await expect(page.locator('text=操作')).toBeVisible();
    
    // 验证操作按钮是否为中文
    await expect(page.locator('text=编辑')).toBeVisible();
    await expect(page.locator('text=删除')).toBeVisible();
  });

  test('Admin Choice Question Create Page - Should display Chinese text', async ({ page }) => {
    // 登录管理员账户
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin');
    await page.click('button[type="submit"]');
    
    // 等待登录成功并跳转
    await page.waitForURL('**/admin/dashboard');
    
    // 导航到选择题创建页面
    await page.goto('http://localhost:8080/admin/choice-question/create');
    await page.waitForLoadState('networkidle');
    
    // 验证页面标题是否为中文
    await expect(page.locator('text=创建选择题')).toBeVisible();
    
    // 验证表单标签是否为中文
    await expect(page.locator('text=题目类型')).toBeVisible();
    await expect(page.locator('text=选择题目类型')).toBeVisible();
    await expect(page.locator('text=单选题')).toBeVisible();
    await expect(page.locator('text=多选题')).toBeVisible();
    await expect(page.locator('text=选择或创建标签')).toBeVisible();
    await expect(page.locator('text=解析')).toBeVisible();
    await expect(page.locator('text=添加选项')).toBeVisible();
    
    // 验证没有英文硬编码文本
    await expect(page.locator('text=Create Choice Question')).not.toBeVisible();
    await expect(page.locator('text=Select or create tags')).not.toBeVisible();
    await expect(page.locator('text=Add Option')).not.toBeVisible();
  });

  test('Admin Contest List Page - Should display Chinese text', async ({ page }) => {
    // 登录管理员账户
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin');
    await page.click('button[type="submit"]');
    
    // 等待登录成功并跳转
    await page.waitForURL('**/admin/dashboard');
    
    // 导航到比赛列表页面
    await page.goto('http://localhost:8080/admin/contest');
    await page.waitForLoadState('networkidle');
    
    // 验证页面标题和表头是否为中文
    await expect(page.locator('text=比赛列表')).toBeVisible();
    await expect(page.locator('text=关键词')).toBeVisible();
    await expect(page.locator('text=ID')).toBeVisible();
    await expect(page.locator('text=标题')).toBeVisible();
    await expect(page.locator('text=规则类型')).toBeVisible();
    await expect(page.locator('text=比赛类型')).toBeVisible();
    await expect(page.locator('text=开始时间')).toBeVisible();
    await expect(page.locator('text=结束时间')).toBeVisible();
    await expect(page.locator('text=创建时间')).toBeVisible();
    await expect(page.locator('text=创建者')).toBeVisible();
    await expect(page.locator('text=状态')).toBeVisible();
    await expect(page.locator('text=可见')).toBeVisible();
    await expect(page.locator('text=操作')).toBeVisible();
    
    // 验证操作按钮是否为中文
    await expect(page.locator('text=编辑')).toBeVisible();
    await expect(page.locator('text=问题')).toBeVisible();
    await expect(page.locator('text=公告')).toBeVisible();
    await expect(page.locator('text=下载已接受的提交')).toBeVisible();
    
    // 验证确定按钮是否为中文
    await expect(page.locator('text=确定')).toBeVisible();
    
    // 验证没有英文硬编码文本
    await expect(page.locator('text=Contest List')).not.toBeVisible();
    await expect(page.locator('text=Keywords')).not.toBeVisible();
    await expect(page.locator('text=Rule Type')).not.toBeVisible();
    await expect(page.locator('text=Contest Type')).not.toBeVisible();
  });

  test('Admin Contest Create Page - Should display Chinese text', async ({ page }) => {
    // 登录管理员账户
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin');
    await page.click('button[type="submit"]');
    
    // 等待登录成功并跳转
    await page.waitForURL('**/admin/dashboard');
    
    // 导航到比赛创建页面
    await page.goto('http://localhost:8080/admin/contest/create');
    await page.waitForLoadState('networkidle');
    
    // 验证页面标题是否为中文
    await expect(page.locator('text=创建比赛')).toBeVisible();
    
    // 验证没有英文硬编码文本
    await expect(page.locator('text=Create Contest')).not.toBeVisible();
  });

  test('Admin Problem Create Page - Should display Chinese text', async ({ page }) => {
    // 登录管理员账户
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin');
    await page.click('button[type="submit"]');
    
    // 等待登录成功并跳转
    await page.waitForURL('**/admin/dashboard');
    
    // 导航到问题创建页面
    await page.goto('http://localhost:8080/admin/problem/create');
    await page.waitForLoadState('networkidle');
    
    // 验证样例相关文本是否为中文
    await expect(page.locator('text=样例')).toBeVisible();
    await expect(page.locator('text=删除')).toBeVisible();
    
    // 验证没有英文硬编码文本
    await expect(page.locator('text=Sample')).not.toBeVisible();
    await expect(page.locator('text=Delete')).not.toBeVisible();
  });

  test('Comprehensive Localization Check - No English hardcoded text should be visible', async ({ page }) => {
    // 登录管理员账户
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin');
    await page.click('button[type="submit"]');
    
    // 等待登录成功并跳转
    await page.waitForURL('**/admin/dashboard');
    
    const pagesToCheck = [
      'http://localhost:8080/admin/problems',
      'http://localhost:8080/admin/choice-questions',
      'http://localhost:8080/admin/choice-question/create',
      'http://localhost:8080/admin/contest',
      'http://localhost:8080/admin/contest/create'
    ];
    
    for (const url of pagesToCheck) {
      await page.goto(url);
      await page.waitForLoadState('networkidle');
      
      // 检查常见的英文硬编码文本是否不存在
      const englishTexts = [
        'Create Choice Question',
        'Edit Choice Question', 
        'Select or create tags',
        'Add Option',
        'Contest List',
        'Keywords',
        'Rule Type',
        'Contest Type',
        'Create Contest',
        'Edit Contest',
        'Sample',
        'Delete'
      ];
      
      for (const text of englishTexts) {
        await expect(page.locator(`text=${text}`)).not.toBeVisible();
      }
    }
  });
});