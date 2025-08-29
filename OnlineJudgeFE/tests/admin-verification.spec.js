const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

// 测试报告生成器
class TestReporter {
  constructor() {
    this.results = {
      timestamp: new Date().toISOString(),
      tests: [],
      summary: {
        total: 0,
        passed: 0,
        failed: 0,
        issues: []
      }
    };
  }

  addTest(name, status, details = {}) {
    this.results.tests.push({
      name,
      status,
      details,
      timestamp: new Date().toISOString()
    });
    
    this.results.summary.total++;
    if (status === 'passed') {
      this.results.summary.passed++;
    } else {
      this.results.summary.failed++;
      this.results.summary.issues.push({ test: name, ...details });
    }
  }

  generateReport() {
    const reportPath = path.join(__dirname, '../test-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(this.results, null, 2));
    
    // 生成可读的文本报告
    const textReportPath = path.join(__dirname, '../test-report.txt');
    let textReport = `=== Frontend Admin Module Test Report ===\n`;
    textReport += `Generated: ${this.results.timestamp}\n\n`;
    
    textReport += `Summary:\n`;
    textReport += `  Total Tests: ${this.results.summary.total}\n`;
    textReport += `  Passed: ${this.results.summary.passed}\n`;
    textReport += `  Failed: ${this.results.summary.failed}\n\n`;
    
    textReport += `Test Results:\n`;
    this.results.tests.forEach(test => {
      const status = test.status === 'passed' ? '✓' : '✗';
      textReport += `  ${status} ${test.name}\n`;
      if (test.details.error) {
        textReport += `    Error: ${test.details.error}\n`;
      }
      if (test.details.screenshot) {
        textReport += `    Screenshot: ${test.details.screenshot}\n`;
      }
    });
    
    if (this.results.summary.issues.length > 0) {
      textReport += `\nIssues Found:\n`;
      this.results.summary.issues.forEach((issue, index) => {
        textReport += `  ${index + 1}. ${issue.test}\n`;
        if (issue.error) {
          textReport += `     ${issue.error}\n`;
        }
      });
    }
    
    textReport += `\nRecommendations:\n`;
    textReport += `  1. Access admin interface at: http://localhost:8080/admin/\n`;
    textReport += `  2. Login with username: root, password: rootroot\n`;
    textReport += `  3. Verify Problem and Choice Question modules in sidebar\n`;
    textReport += `  4. Check browser console for JavaScript errors\n`;
    textReport += `  5. Ensure backend API is running at: http://localhost:8000\n`;
    
    fs.writeFileSync(textReportPath, textReport);
    
    console.log('\n' + textReport);
    console.log(`\nDetailed reports saved to:`);
    console.log(`  JSON: ${reportPath}`);
    console.log(`  Text: ${textReportPath}`);
    
    return this.results;
  }
}

const reporter = new TestReporter();

test.describe('Admin Interface Verification Tests', () => {
  test.beforeEach(async ({ page }) => {
    // 设置页面超时
    page.setDefaultTimeout(10000);
  });

  test('should load admin login page', async ({ page }) => {
    try {
      await page.goto('/admin/login');
      await expect(page).toHaveTitle(/Online Judge/);
      
      // 检查登录表单元素
      const usernameInput = page.locator('input[type="text"], input[placeholder*="用户名"], input[placeholder*="username"]');
      const passwordInput = page.locator('input[type="password"], input[placeholder*="密码"], input[placeholder*="password"]');
      const loginButton = page.locator('button[type="submit"], button:has-text("登录"), button:has-text("Login")');
      
      await expect(usernameInput).toBeVisible();
      await expect(passwordInput).toBeVisible();
      await expect(loginButton).toBeVisible();
      
      reporter.addTest('Admin login page loads', 'passed', {
        url: page.url(),
        title: await page.title()
      });
    } catch (error) {
      reporter.addTest('Admin login page loads', 'failed', {
        error: error.message,
        url: page.url()
      });
      throw error;
    }
  });

  test('should login successfully', async ({ page }) => {
    try {
      await page.goto('/admin/login');
      
      // 尝试多种可能的选择器
      const usernameSelectors = [
        'input[name="username"]',
        'input[type="text"]',
        'input[placeholder*="用户名"]',
        'input[placeholder*="username"]',
        '.el-input__inner[type="text"]'
      ];
      
      const passwordSelectors = [
        'input[name="password"]',
        'input[type="password"]',
        'input[placeholder*="密码"]',
        'input[placeholder*="password"]',
        '.el-input__inner[type="password"]'
      ];
      
      const buttonSelectors = [
        'button[type="submit"]',
        'button:has-text("登录")',
        'button:has-text("Login")',
        '.el-button--primary'
      ];
      
      let usernameInput, passwordInput, loginButton;
      
      // 查找用户名输入框
      for (const selector of usernameSelectors) {
        try {
          usernameInput = page.locator(selector).first();
          if (await usernameInput.isVisible({ timeout: 1000 })) break;
        } catch (e) { continue; }
      }
      
      // 查找密码输入框
      for (const selector of passwordSelectors) {
        try {
          passwordInput = page.locator(selector).first();
          if (await passwordInput.isVisible({ timeout: 1000 })) break;
        } catch (e) { continue; }
      }
      
      // 查找登录按钮
      for (const selector of buttonSelectors) {
        try {
          loginButton = page.locator(selector).first();
          if (await loginButton.isVisible({ timeout: 1000 })) break;
        } catch (e) { continue; }
      }
      
      if (!usernameInput || !passwordInput || !loginButton) {
        throw new Error('Could not find login form elements');
      }
      
      await usernameInput.fill('root');
      await passwordInput.fill('rootroot');
      await loginButton.click();
      
      // 等待登录完成，检查URL变化或页面内容
      await page.waitForTimeout(2000);
      
      const currentUrl = page.url();
      const isLoggedIn = currentUrl.includes('/admin') && !currentUrl.includes('/login');
      
      if (!isLoggedIn) {
        // 检查是否有错误消息
        const errorMessage = await page.locator('.el-message--error, .error-message, .alert-danger').textContent().catch(() => null);
        throw new Error(`Login failed. Current URL: ${currentUrl}. Error: ${errorMessage || 'Unknown'}`);
      }
      
      reporter.addTest('Admin login successful', 'passed', {
        finalUrl: currentUrl
      });
    } catch (error) {
      reporter.addTest('Admin login successful', 'failed', {
        error: error.message,
        url: page.url()
      });
      throw error;
    }
  });

  test('should display admin dashboard with sidebar', async ({ page }) => {
    try {
      // 先登录
      await page.goto('/admin/login');
      
      const usernameInput = page.locator('input[type="text"], .el-input__inner[type="text"]').first();
      const passwordInput = page.locator('input[type="password"], .el-input__inner[type="password"]').first();
      const loginButton = page.locator('button[type="submit"], .el-button--primary').first();
      
      await usernameInput.fill('root');
      await passwordInput.fill('rootroot');
      await loginButton.click();
      
      await page.waitForTimeout(3000);
      
      // 检查侧边栏是否存在
      const sidebar = page.locator('.el-menu, .sidebar, nav');
      await expect(sidebar).toBeVisible();
      
      // 检查是否有菜单项
      const menuItems = page.locator('.el-menu-item, .menu-item, nav a');
      const menuCount = await menuItems.count();
      
      if (menuCount === 0) {
        throw new Error('No menu items found in sidebar');
      }
      
      reporter.addTest('Admin dashboard with sidebar', 'passed', {
        menuItemsCount: menuCount,
        url: page.url()
      });
    } catch (error) {
      reporter.addTest('Admin dashboard with sidebar', 'failed', {
        error: error.message,
        url: page.url()
      });
      throw error;
    }
  });

  test('should display Problem module in sidebar', async ({ page }) => {
    try {
      // 登录并导航到admin页面
      await page.goto('/admin/login');
      
      const usernameInput = page.locator('input[type="text"], .el-input__inner[type="text"]').first();
      const passwordInput = page.locator('input[type="password"], .el-input__inner[type="password"]').first();
      const loginButton = page.locator('button[type="submit"], .el-button--primary').first();
      
      await usernameInput.fill('root');
      await passwordInput.fill('rootroot');
      await loginButton.click();
      
      await page.waitForTimeout(3000);
      
      // 检查Problem模块
      const problemSelectors = [
        'text=Problem',
        'text=问题',
        '[data-test="problem-menu"]',
        'a[href*="problem"]',
        '.el-menu-item:has-text("Problem")',
        '.el-menu-item:has-text("问题")'
      ];
      
      let problemFound = false;
      let problemElement;
      
      for (const selector of problemSelectors) {
        try {
          problemElement = page.locator(selector).first();
          if (await problemElement.isVisible({ timeout: 2000 })) {
            problemFound = true;
            break;
          }
        } catch (e) { continue; }
      }
      
      if (!problemFound) {
        // 获取所有菜单项用于调试
        const allMenuItems = await page.locator('.el-menu-item, .menu-item').allTextContents();
        throw new Error(`Problem module not found in sidebar. Available menu items: ${allMenuItems.join(', ')}`);
      }
      
      reporter.addTest('Problem module in sidebar', 'passed', {
        found: true,
        url: page.url()
      });
    } catch (error) {
      reporter.addTest('Problem module in sidebar', 'failed', {
        error: error.message,
        url: page.url()
      });
      throw error;
    }
  });

  test('should display Choice Question module in sidebar', async ({ page }) => {
    try {
      // 登录并导航到admin页面
      await page.goto('/admin/login');
      
      const usernameInput = page.locator('input[type="text"], .el-input__inner[type="text"]').first();
      const passwordInput = page.locator('input[type="password"], .el-input__inner[type="password"]').first();
      const loginButton = page.locator('button[type="submit"], .el-button--primary').first();
      
      await usernameInput.fill('root');
      await passwordInput.fill('rootroot');
      await loginButton.click();
      
      await page.waitForTimeout(3000);
      
      // 检查Choice Question模块
      const choiceSelectors = [
        'text=Choice Question',
        'text=选择题',
        '[data-test="choice-question-menu"]',
        'a[href*="choice-question"]',
        '.el-menu-item:has-text("Choice Question")',
        '.el-menu-item:has-text("选择题")'
      ];
      
      let choiceFound = false;
      let choiceElement;
      
      for (const selector of choiceSelectors) {
        try {
          choiceElement = page.locator(selector).first();
          if (await choiceElement.isVisible({ timeout: 2000 })) {
            choiceFound = true;
            break;
          }
        } catch (e) { continue; }
      }
      
      if (!choiceFound) {
        // 获取所有菜单项用于调试
        const allMenuItems = await page.locator('.el-menu-item, .menu-item').allTextContents();
        throw new Error(`Choice Question module not found in sidebar. Available menu items: ${allMenuItems.join(', ')}`);
      }
      
      reporter.addTest('Choice Question module in sidebar', 'passed', {
        found: true,
        url: page.url()
      });
    } catch (error) {
      reporter.addTest('Choice Question module in sidebar', 'failed', {
        error: error.message,
        url: page.url()
      });
      throw error;
    }
  });

  test('should verify API endpoints accessibility', async ({ page }) => {
    try {
      // 检查后端API是否可访问
      const apiEndpoints = [
        'http://localhost:8000/api/',
        'http://localhost:8000/api/admin/',
        'http://localhost:8000/api/problem/',
        'http://localhost:8000/api/plugin/choice/'
      ];
      
      const results = [];
      
      for (const endpoint of apiEndpoints) {
        try {
          const response = await page.request.get(endpoint);
          results.push({
            endpoint,
            status: response.status(),
            accessible: response.status() < 500
          });
        } catch (error) {
          results.push({
            endpoint,
            status: 'error',
            accessible: false,
            error: error.message
          });
        }
      }
      
      const accessibleCount = results.filter(r => r.accessible).length;
      
      if (accessibleCount === 0) {
        throw new Error('No API endpoints are accessible');
      }
      
      reporter.addTest('API endpoints accessibility', 'passed', {
        results,
        accessibleCount,
        totalCount: apiEndpoints.length
      });
    } catch (error) {
      reporter.addTest('API endpoints accessibility', 'failed', {
        error: error.message
      });
      throw error;
    }
  });

  test.afterAll(async () => {
    // 生成测试报告
    reporter.generateReport();
  });
});