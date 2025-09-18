const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    console.log('正在访问选择题页面...');
    await page.goto('http://localhost:8080/choice-questions', { waitUntil: 'networkidle' });
    
    // 等待页面加载
    await page.waitForTimeout(3000);
    
    // 检查页面标题
    const title = await page.title();
    console.log('页面标题:', title);
    
    // 检查是否有JavaScript错误
    const errors = [];
    page.on('pageerror', error => {
      errors.push(error.message);
    });
    
    // 检查控制台错误
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // 等待一段时间收集错误
    await page.waitForTimeout(2000);
    
    // 检查页面内容
    const bodyText = await page.textContent('body');
    console.log('页面是否包含选择题相关内容:', bodyText.includes('选择题') || bodyText.includes('Choice') || bodyText.includes('Question'));
    
    // 检查Vue应用是否加载
    const vueApp = await page.evaluate(() => {
      return window.Vue !== undefined || document.querySelector('#app') !== null;
    });
    console.log('Vue应用是否加载:', vueApp);
    
    // 检查API请求
    const apiRequests = [];
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        apiRequests.push(request.url());
      }
    });
    
    // 等待API请求
    await page.waitForTimeout(3000);
    
    console.log('\n=== 测试结果 ===');
    console.log('页面标题:', title);
    console.log('JavaScript错误数量:', errors.length);
    if (errors.length > 0) {
      console.log('JavaScript错误:', errors);
    }
    console.log('控制台错误数量:', consoleErrors.length);
    if (consoleErrors.length > 0) {
      console.log('控制台错误:', consoleErrors);
    }
    console.log('API请求数量:', apiRequests.length);
    if (apiRequests.length > 0) {
      console.log('API请求:', apiRequests);
    }
    
    // 截图保存
    await page.screenshot({ path: 'choice-questions-screenshot.png', fullPage: true });
    console.log('页面截图已保存为 choice-questions-screenshot.png');
    
  } catch (error) {
    console.error('测试过程中出现错误:', error.message);
  } finally {
    await browser.close();
  }
})();