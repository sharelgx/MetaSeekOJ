#!/usr/bin/env node

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

// 简单的HTTP请求函数
function makeRequest(url, timeout = 5000) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const client = urlObj.protocol === 'https:' ? https : http;
    
    const req = client.request({
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname + urlObj.search,
      method: 'GET',
      timeout: timeout
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        resolve({
          status: res.statusCode,
          headers: res.headers,
          data: data
        });
      });
    });
    
    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
    
    req.end();
  });
}

// 测试报告生成器
class SimpleReporter {
  constructor() {
    this.results = {
      timestamp: new Date().toISOString(),
      tests: [],
      summary: {
        total: 0,
        passed: 0,
        failed: 0
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
    }
  }

  generateReport() {
    const reportPath = path.join(__dirname, '../simple-test-report.txt');
    let report = `=== Simple Frontend Verification Report ===\n`;
    report += `Generated: ${this.results.timestamp}\n\n`;
    
    report += `Summary:\n`;
    report += `  Total Tests: ${this.results.summary.total}\n`;
    report += `  Passed: ${this.results.summary.passed}\n`;
    report += `  Failed: ${this.results.summary.failed}\n\n`;
    
    report += `Test Results:\n`;
    this.results.tests.forEach(test => {
      const status = test.status === 'passed' ? '✓' : '✗';
      report += `  ${status} ${test.name}\n`;
      if (test.details.error) {
        report += `    Error: ${test.details.error}\n`;
      }
      if (test.details.status) {
        report += `    Status: ${test.details.status}\n`;
      }
      if (test.details.url) {
        report += `    URL: ${test.details.url}\n`;
      }
    });
    
    report += `\nNext Steps:\n`;
    report += `  1. Open browser and navigate to: http://localhost:8080/admin/\n`;
    report += `  2. Login with username: root, password: rootroot\n`;
    report += `  3. Check if Problem and Choice Question modules appear in sidebar\n`;
    report += `  4. If modules are missing, check browser console for errors\n`;
    report += `  5. Verify backend API is accessible at: http://localhost:8000/api/\n`;
    
    fs.writeFileSync(reportPath, report);
    console.log(report);
    console.log(`\nReport saved to: ${reportPath}`);
    
    return this.results;
  }
}

async function runVerification() {
  const reporter = new SimpleReporter();
  
  console.log('=== Running Simple Frontend Verification ===\n');
  
  // 1. 检查前端服务是否运行
  try {
    const response = await makeRequest('http://localhost:8080/');
    if (response.status === 200) {
      reporter.addTest('Frontend server accessibility', 'passed', {
        status: response.status,
        url: 'http://localhost:8080/'
      });
    } else {
      reporter.addTest('Frontend server accessibility', 'failed', {
        status: response.status,
        url: 'http://localhost:8080/'
      });
    }
  } catch (error) {
    reporter.addTest('Frontend server accessibility', 'failed', {
      error: error.message,
      url: 'http://localhost:8080/'
    });
  }
  
  // 2. 检查admin页面是否可访问
  try {
    const response = await makeRequest('http://localhost:8080/admin/');
    if (response.status === 200) {
      reporter.addTest('Admin page accessibility', 'passed', {
        status: response.status,
        url: 'http://localhost:8080/admin/'
      });
    } else {
      reporter.addTest('Admin page accessibility', 'failed', {
        status: response.status,
        url: 'http://localhost:8080/admin/'
      });
    }
  } catch (error) {
    reporter.addTest('Admin page accessibility', 'failed', {
      error: error.message,
      url: 'http://localhost:8080/admin/'
    });
  }
  
  // 3. 检查后端API是否运行
  try {
    const response = await makeRequest('http://localhost:8000/api/');
    if (response.status < 500) {
      reporter.addTest('Backend API accessibility', 'passed', {
        status: response.status,
        url: 'http://localhost:8000/api/'
      });
    } else {
      reporter.addTest('Backend API accessibility', 'failed', {
        status: response.status,
        url: 'http://localhost:8000/api/'
      });
    }
  } catch (error) {
    reporter.addTest('Backend API accessibility', 'failed', {
      error: error.message,
      url: 'http://localhost:8000/api/'
    });
  }
  
  // 4. 检查选择题API端点
  try {
    const response = await makeRequest('http://localhost:8000/api/plugin/choice/');
    if (response.status < 500) {
      reporter.addTest('Choice Question API endpoint', 'passed', {
        status: response.status,
        url: 'http://localhost:8000/api/plugin/choice/'
      });
    } else {
      reporter.addTest('Choice Question API endpoint', 'failed', {
        status: response.status,
        url: 'http://localhost:8000/api/plugin/choice/'
      });
    }
  } catch (error) {
    reporter.addTest('Choice Question API endpoint', 'failed', {
      error: error.message,
      url: 'http://localhost:8000/api/plugin/choice/'
    });
  }
  
  // 5. 检查文件配置
  const configChecks = [
    {
      name: 'Router configuration',
      file: '../src/pages/admin/router.js',
      check: (content) => content.includes('choice-question') && content.includes('ChoiceQuestion')
    },
    {
      name: 'Side menu configuration',
      file: '../src/pages/admin/components/SideMenu.vue',
      check: (content) => content.includes('choice-question')
    },
    {
      name: 'API configuration',
      file: '../src/pages/admin/api.js',
      check: (content) => content.includes('getChoiceQuestions')
    },
    {
      name: 'Chinese i18n',
      file: '../src/i18n/admin/zh-CN.js',
      check: (content) => content.includes('Choice_Question')
    },
    {
      name: 'English i18n',
      file: '../src/i18n/admin/en-US.js',
      check: (content) => content.includes('Choice_Question')
    }
  ];
  
  for (const config of configChecks) {
    try {
      const filePath = path.join(__dirname, config.file);
      if (fs.existsSync(filePath)) {
        const content = fs.readFileSync(filePath, 'utf8');
        const isConfigured = config.check(content);
        
        reporter.addTest(config.name, isConfigured ? 'passed' : 'failed', {
          file: config.file,
          configured: isConfigured
        });
      } else {
        reporter.addTest(config.name, 'failed', {
          file: config.file,
          error: 'File not found'
        });
      }
    } catch (error) {
      reporter.addTest(config.name, 'failed', {
        file: config.file,
        error: error.message
      });
    }
  }
  
  // 生成报告
  const results = reporter.generateReport();
  
  // 返回结果
  return results;
}

if (require.main === module) {
  runVerification().then(results => {
    const success = results.summary.failed === 0;
    process.exit(success ? 0 : 1);
  }).catch(error => {
    console.error('Verification failed:', error);
    process.exit(1);
  });
}

module.exports = { runVerification };