module.exports = {
  // 测试环境
  testEnvironment: 'jsdom',
  
  // 根目录
  rootDir: '../',
  
  // 测试文件匹配模式
  testMatch: [
    '**/tests/unit/**/*.spec.(js|jsx|ts|tsx)',
    '**/__tests__/*.(js|jsx|ts|tsx)'
  ],
  
  // 模块文件扩展名
  moduleFileExtensions: [
    'js',
    'json'
  ],
  
  // 模块名映射
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^~/(.*)$': '<rootDir>/$1'
  },
  
  // 转换器配置（最小化）
  transform: {
    '.+\\.(css|styl|less|sass|scss|svg|png|jpg|ttf|woff|woff2)$': 'jest-transform-stub'
  },
  
  // 忽略转换的模块
  transformIgnorePatterns: [
    'node_modules/(?!(element-ui|vue-router|vuex)/)'
  ],
  
  // 测试URL
  testURL: 'http://localhost/',
  
  // 覆盖率收集
  collectCoverageFrom: [
    'src/**/*.{js,vue}',
    '!src/main.js',
    '!src/router/index.js',
    '!**/node_modules/**'
  ],
  
  // 覆盖率输出目录
  coverageDirectory: '<rootDir>/tests/coverage',
  
  // 设置文件
  setupFilesAfterEnv: [
    '<rootDir>/tests/setup.js'
  ],
  
  // 全局变量
  globals: {
    'vue-jest': {
      babelConfig: false,
      hideStyleWarn: true,
      experimentalCSSCompile: true
    }
  },
  
  // 清除模拟
  clearMocks: true,
  
  // 详细输出
  verbose: true
};