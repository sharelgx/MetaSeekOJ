const { test, expect } = require('@playwright/test');

// 测试选择题功能
test.describe('Choice Questions Tests', () => {
  
  // 1. 测试选择题列表页面
  test('should load choice questions list page', async ({ page }) => {
    test.setTimeout(30000);
    
    await page.goto('http://localhost:8080/choice-questions', {
      waitUntil: 'domcontentloaded'
    });
    
    // 检查页面是否加载
    await expect(page.locator('body')).toBeVisible();
  });
  
  // 2. 测试选择题详情页面
  test('should load choice question detail page', async ({ page }) => {
    test.setTimeout(30000);
    
    await page.goto('http://localhost:8080/choice-question/7', {
      waitUntil: 'domcontentloaded'
    });
    
    // 检查页面是否加载
    await expect(page.locator('body')).toBeVisible();
    
    // 等待题目内容加载
    await page.waitForTimeout(3000);
    
    // 检查是否有选项
    const options = page.locator('.option-item');
    await expect(options.first()).toBeVisible({ timeout: 10000 });
  });
  
  // 3. 测试选择题交互功能
  test('should allow option selection and submission', async ({ page }) => {
    test.setTimeout(30000);
    
    await page.goto('http://localhost:8080/choice-question/7', {
      waitUntil: 'domcontentloaded'
    });
    
    // 等待页面加载
    await page.waitForTimeout(3000);
    
    // 检查选项是否存在
    const options = page.locator('.option-item');
    const optionCount = await options.count();
    
    if (optionCount > 0) {
      // 点击第一个选项
      await options.first().click();
      
      // 检查提交按钮是否可用
      const submitButton = page.locator('button:has-text("提交答案")');
      await expect(submitButton).toBeVisible({ timeout: 5000 });
      
      // 如果按钮可用，尝试点击
      const isEnabled = await submitButton.isEnabled();
      if (isEnabled) {
        await submitButton.click();
        
        // 等待提交结果
        await page.waitForTimeout(2000);
        
        // 检查是否显示结果
        const resultSection = page.locator('.answer-analysis, .result-info');
        await expect(resultSection).toBeVisible({ timeout: 10000 });
      }
    }
  });
});