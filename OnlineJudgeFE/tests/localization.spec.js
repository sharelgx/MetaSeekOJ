const { test, expect } = require('@playwright/test');

// 测试配置
const BASE_URL = 'http://localhost:8080';
const ADMIN_URL = 'http://localhost:8080/admin';

// 等待页面加载完成的辅助函数
async function waitForPageLoad(page) {
  try {
    await page.waitForLoadState('domcontentloaded', { timeout: 10000 });
    await page.waitForTimeout(2000); // 等待 Vue 组件渲染完成
  } catch (error) {
    console.log('页面加载超时，继续执行测试:', error.message);
  }
}

// 检查页面是否包含中文文本的辅助函数
function containsChinese(text) {
  return /[\u4e00-\u9fff]/.test(text);
}

// 检查页面是否包含英文硬编码文本的辅助函数
function containsEnglishHardcode(text) {
  const englishPatterns = [
    /\bCreate\b/,
    /\bEdit\b/,
    /\bDelete\b/,
    /\bAuthor\b/,
    /\bOperation\b/,
    /\bVisible\b/,
    /\bStatus\b/,
    /\bTitle\b/,
    /\bDescription\b/,
    /\bSample\b/,
    /\bContest List\b/,
    /\bProblem List\b/,
    /\bChoice Question\b/
  ];
  return englishPatterns.some(pattern => pattern.test(text));
}

test.describe('OJ 前端汉化测试', () => {
  test.beforeEach(async ({ page }) => {
    // 设置浏览器语言为中文
    await page.setExtraHTTPHeaders({
      'Accept-Language': 'zh-CN,zh;q=0.9'
    });
  });

  test('OJ 主页汉化检查', async ({ page }) => {
    await page.goto(`${BASE_URL}/index.html`);
    await waitForPageLoad(page);
    
    // 检查页面标题
    const title = await page.title();
    console.log('OJ 主页标题:', title);
    
    // 检查整个页面的文本内容
    const pageText = await page.textContent('body');
    console.log('页面包含中文:', containsChinese(pageText));
    console.log('页面包含英文硬编码:', containsEnglishHardcode(pageText));
    
    // 截图保存
    await page.screenshot({ path: 'tests/screenshots/oj-home.png', fullPage: true });
  });

  test('OJ 问题列表页面汉化检查', async ({ page }) => {
    await page.goto(`${BASE_URL}/problem`);
    await waitForPageLoad(page);
    
    // 检查表格标题
    const tableHeaders = await page.locator('th, .table-header').allTextContents();
    console.log('问题列表表格标题:', tableHeaders);
    
    // 检查是否有英文硬编码
    const pageText = await page.textContent('body');
    console.log('问题列表页面包含英文硬编码:', containsEnglishHardcode(pageText));
    
    await page.screenshot({ path: 'tests/screenshots/oj-problems.png', fullPage: true });
  });

  test('OJ 比赛列表页面汉化检查', async ({ page }) => {
    await page.goto(`${BASE_URL}/contest`);
    await waitForPageLoad(page);
    
    const pageText = await page.textContent('body');
    console.log('比赛列表页面包含中文:', containsChinese(pageText));
    console.log('比赛列表页面包含英文硬编码:', containsEnglishHardcode(pageText));
    
    await page.screenshot({ path: 'tests/screenshots/oj-contests.png', fullPage: true });
  });

  test('OJ 排行榜页面汉化检查', async ({ page }) => {
    await page.goto(`${BASE_URL}/rank`);
    await waitForPageLoad(page);
    
    const pageText = await page.textContent('body');
    console.log('排行榜页面包含中文:', containsChinese(pageText));
    console.log('排行榜页面包含英文硬编码:', containsEnglishHardcode(pageText));
    
    await page.screenshot({ path: 'tests/screenshots/oj-rank.png', fullPage: true });
  });

  test('管理员登录页面汉化检查', async ({ page }) => {
    await page.goto(`${ADMIN_URL}/login`);
    await waitForPageLoad(page);
    
    const pageText = await page.textContent('body');
    console.log('管理员登录页面包含中文:', containsChinese(pageText));
    console.log('管理员登录页面包含英文硬编码:', containsEnglishHardcode(pageText));
    
    await page.screenshot({ path: 'tests/screenshots/admin-login.png', fullPage: true });
  });

  test('管理员主页汉化检查', async ({ page }) => {
    await page.goto(ADMIN_URL);
    await waitForPageLoad(page);
    
    const pageText = await page.textContent('body');
    console.log('管理员主页包含中文:', containsChinese(pageText));
    console.log('管理员主页包含英文硬编码:', containsEnglishHardcode(pageText));
    
    await page.screenshot({ path: 'tests/screenshots/admin-home.png', fullPage: true });
  });

  test('检查控制台是否有 i18n 相关错误', async ({ page }) => {
    const consoleMessages = [];
    const errors = [];
    
    page.on('console', msg => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text()
      });
    });
    
    page.on('pageerror', error => {
      errors.push(error.message);
    });
    
    await page.goto(BASE_URL);
    await waitForPageLoad(page);
    
    // 检查控制台消息中是否有 i18n 相关的警告或错误
    const i18nMessages = consoleMessages.filter(msg => 
      msg.text.includes('i18n') || 
      msg.text.includes('translation') || 
      msg.text.includes('undefined') ||
      msg.text.includes('m.undefined')
    );
    
    console.log('控制台 i18n 相关消息:', i18nMessages);
    console.log('页面错误:', errors);
    
    // 如果有 i18n 相关的错误，测试应该失败
    const hasI18nErrors = i18nMessages.some(msg => msg.type === 'error') || 
                         errors.some(error => error.includes('i18n') || error.includes('translation'));
    
    expect(hasI18nErrors).toBeFalsy();
  });

  test('语言切换功能测试', async ({ page }) => {
    await page.goto(BASE_URL);
    await waitForPageLoad(page);
    
    // 尝试找到语言切换按钮
    const langSwitcher = page.locator('[data-testid="lang-switcher"], .lang-switch, .language-selector');
    
    if (await langSwitcher.count() > 0) {
      console.log('找到语言切换器');
      
      // 记录切换前的页面文本
      const beforeText = await page.textContent('body');
      
      // 尝试切换到英文
      await langSwitcher.click();
      await waitForPageLoad(page);
      
      // 记录切换后的页面文本
      const afterText = await page.textContent('body');
      
      console.log('语言切换前后文本是否不同:', beforeText !== afterText);
      
      await page.screenshot({ path: 'tests/screenshots/lang-switch-test.png', fullPage: true });
    } else {
      console.log('未找到语言切换器');
    }
  });
});