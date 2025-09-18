/**
 * API验证工具
 * 用于在开发时检查API调用的一致性，防止使用错误的API方法名
 */

import { checkDeprecatedApi, validateApiMethod, getAllApiMethods } from './api-mapping'

/**
 * API调用拦截器
 * 在开发环境下检查API方法的使用情况
 */
class ApiValidator {
  constructor() {
    this.usedMethods = new Set()
    this.deprecatedUsage = new Map()
    this.invalidMethods = new Set()
    this.enabled = process.env.NODE_ENV === 'development'
  }

  /**
   * 验证API方法调用
   * @param {string} methodName - API方法名
   * @param {string} filePath - 调用文件路径（可选）
   */
  validateCall(methodName, filePath = 'unknown') {
    if (!this.enabled) return

    this.usedMethods.add(methodName)

    // 检查是否为废弃的API
    const recommendedMethod = checkDeprecatedApi(methodName)
    if (recommendedMethod) {
      const usage = this.deprecatedUsage.get(methodName) || []
      usage.push(filePath)
      this.deprecatedUsage.set(methodName, usage)
      
      console.warn(
        `⚠️  使用了废弃的API方法: ${methodName}\n` +
        `   推荐使用: ${recommendedMethod}\n` +
        `   调用位置: ${filePath}`
      )
    }

    // 检查是否为无效的API方法
    if (!validateApiMethod(methodName) && !recommendedMethod) {
      this.invalidMethods.add(methodName)
      console.error(
        `❌ 使用了未定义的API方法: ${methodName}\n` +
        `   调用位置: ${filePath}\n` +
        `   请检查API映射配置`
      )
    }
  }

  /**
   * 生成API使用报告
   */
  generateReport() {
    if (!this.enabled) return

    console.group('📊 API使用情况报告')
    
    console.log(`总共使用了 ${this.usedMethods.size} 个不同的API方法`)
    
    if (this.deprecatedUsage.size > 0) {
      console.group('⚠️  废弃API使用情况')
      for (const [method, files] of this.deprecatedUsage) {
        console.log(`${method}: ${files.length} 次调用`)
        files.forEach(file => console.log(`  - ${file}`))
      }
      console.groupEnd()
    }
    
    if (this.invalidMethods.size > 0) {
      console.group('❌ 无效API方法')
      this.invalidMethods.forEach(method => {
        console.log(`- ${method}`)
      })
      console.groupEnd()
    }
    
    console.groupEnd()
  }

  /**
   * 获取建议的API方法
   * @param {string} searchTerm - 搜索词
   * @returns {Array} 匹配的API方法列表
   */
  suggestApiMethods(searchTerm) {
    const allMethods = getAllApiMethods()
    const suggestions = allMethods.filter(item => 
      item.method.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.path.toLowerCase().includes(searchTerm.toLowerCase())
    )
    
    return suggestions.map(item => ({
      method: item.method,
      path: item.path,
      description: `使用路径: ${item.path}`
    }))
  }
}

// 创建全局验证器实例
const apiValidator = new ApiValidator()

/**
 * 创建API代理，自动验证API调用
 * @param {Object} apiObject - 原始API对象
 * @param {string} filePath - 调用文件路径
 * @returns {Proxy} 代理后的API对象
 */
export function createApiProxy(apiObject, filePath = 'unknown') {
  if (!apiValidator.enabled) {
    return apiObject
  }

  return new Proxy(apiObject, {
    get(target, prop) {
      const value = target[prop]
      
      if (typeof value === 'function') {
        // 验证API方法调用
        apiValidator.validateCall(prop, filePath)
        
        return function(...args) {
          return value.apply(target, args)
        }
      }
      
      return value
    }
  })
}

/**
 * 手动验证API方法
 * @param {string} methodName - API方法名
 * @param {string} filePath - 调用文件路径
 */
export function validateApiCall(methodName, filePath = 'unknown') {
  apiValidator.validateCall(methodName, filePath)
}

/**
 * 生成API使用报告
 */
export function generateApiReport() {
  apiValidator.generateReport()
}

/**
 * 获取API方法建议
 * @param {string} searchTerm - 搜索词
 * @returns {Array} 建议列表
 */
export function getApiSuggestions(searchTerm) {
  return apiValidator.suggestApiMethods(searchTerm)
}

/**
 * 检查文件中的API使用情况
 * @param {string} fileContent - 文件内容
 * @param {string} filePath - 文件路径
 */
export function checkFileApiUsage(fileContent, filePath) {
  if (!apiValidator.enabled) return

  // 匹配API调用模式
  const apiCallPattern = /api\.(\w+)\s*\(/g
  const importPattern = /import.*api.*from/g
  
  let match
  const foundMethods = new Set()
  
  // 检查是否导入了API
  if (!importPattern.test(fileContent)) {
    return // 如果没有导入API，跳过检查
  }
  
  // 查找所有API调用
  while ((match = apiCallPattern.exec(fileContent)) !== null) {
    const methodName = match[1]
    if (!foundMethods.has(methodName)) {
      foundMethods.add(methodName)
      apiValidator.validateCall(methodName, filePath)
    }
  }
}

// 在开发环境下，定期生成报告
if (process.env.NODE_ENV === 'development') {
  // 页面卸载时生成报告
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', () => {
      apiValidator.generateReport()
    })
    
    // 定期检查（每5分钟）
    setInterval(() => {
      if (apiValidator.usedMethods.size > 0) {
        apiValidator.generateReport()
      }
    }, 5 * 60 * 1000)
  }
}

export default apiValidator