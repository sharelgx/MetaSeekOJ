const puppeteer = require('puppeteer');

async function testAdminPage() {
  let browser;
  try {
    console.log('启动浏览器...');
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    // 监听控制台消息
    const consoleMessages = [];
    page.on('console', msg => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text()
      });
    });
    
    // 监听页面错误
    const pageErrors = [];
    page.on('pageerror', error => {
      pageErrors.push(error.message);
    });
    
    // 监听网络请求失败
    const failedRequests = [];
    page.on('requestfailed', request => {
      failedRequests.push({
        url: request.url(),
        failure: request.failure().errorText
      });
    });
    
    console.log('访问管理页面...');
    await page.goto('http://localhost:8080/admin/', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    // 等待页面加载
    await page.waitForTimeout(3000);
    
    console.log('\n=== 测试结果 ===');
    console.log('页面标题:', await page.title());
    
    if (pageErrors.length > 0) {
      console.log('\n页面错误:');
      pageErrors.forEach(error => console.log('- ', error));
    } else {
      console.log('\n✓ 没有页面错误');
    }
    
    if (failedRequests.length > 0) {
      console.log('\n网络请求失败:');
      failedRequests.forEach(req => {
        console.log(`- ${req.url}: ${req.failure}`);
      });
    } else {
      console.log('\n✓ 所有网络请求成功');
    }
    
    // 检查控制台错误
    const errors = consoleMessages.filter(msg => msg.type === 'error');
    const warnings = consoleMessages.filter(msg => msg.type === 'warning');
    
    if (errors.length > 0) {
      console.log('\n控制台错误:');
      errors.forEach(error => console.log('- ', error.text));
    } else {
      console.log('\n✓ 没有控制台错误');
    }
    
    if (warnings.length > 0) {
      console.log('\n控制台警告:');
      warnings.forEach(warning => console.log('- ', warning.text));
    }
    
    // 检查页面是否包含预期内容
    const bodyText = await page.evaluate(() => document.body.innerText);
    if (bodyText.includes('OnlineJudge') || bodyText.includes('管理') || bodyText.includes('Admin')) {
      console.log('\n✓ 页面内容正常');
    } else {
      console.log('\n⚠ 页面内容可能异常');
    }
    
    console.log('\n=== 测试完成 ===');
    
  } catch (error) {
    console.error('测试失败:', error.message);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

testAdminPage();