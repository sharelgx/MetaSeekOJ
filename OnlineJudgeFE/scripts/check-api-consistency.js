#!/usr/bin/env node
/**
 * API一致性检查工具
 * 用于检查整个项目中API调用的一致性
 */

const fs = require('fs')
const path = require('path')

// 简单的颜色输出函数（不依赖chalk）
const colors = {
  blue: (text) => `\x1b[34m${text}\x1b[0m`,
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  gray: (text) => `\x1b[90m${text}\x1b[0m`,
  bold: {
    blue: (text) => `\x1b[1m\x1b[34m${text}\x1b[0m`
  }
}

// 模拟API映射配置（因为无法直接require ES6模块）
const API_MAPPING = {
  categories: {
    list: 'getCategoryList',
    create: 'createCategory',
    update: 'updateCategory',
    delete: 'deleteCategory'
  },
  choiceQuestions: {
    list: 'getChoiceQuestions',
    detail: 'getChoiceQuestion',
    create: 'createChoiceQuestion',
    update: 'updateChoiceQuestion',
    delete: 'deleteChoiceQuestion',
    submit: 'submitChoiceQuestion',
    import: 'importChoiceQuestions',
    export: 'exportChoiceQuestions'
  },
  questions: {
    import: 'importChoiceQuestions'
  },
  examPapers: {
    list: 'getExamPaperList',
    detail: 'getExamPaper',
    create: 'createExamPaper',
    update: 'updateExamPaper',
    delete: 'deleteExamPaper',
    import: 'importExamPapers',
    export: 'exportExamPapers'
  },
  tags: {
    list: 'getTagList',
    create: 'createChoiceQuestionTag',
    update: 'updateTag',
    delete: 'deleteTag'
  },
  users: {
    list: 'getUserList',
    detail: 'getUser',
    create: 'createUser',
    update: 'updateUser',
    delete: 'deleteUser'
  },
  statistics: {
    overview: 'getStatisticsOverview',
    questions: 'getQuestionStatistics',
    papers: 'getPaperStatistics',
    users: 'getUserStatistics'
  }
}

const DEPRECATED_API_MAPPING = {
  'getChoiceQuestionCategories': 'getCategoryList',
  'getChoiceQuestionTags': 'getTagList',
  'getExamPaperCategories': 'getCategoryList'
}

class ApiConsistencyChecker {
  constructor() {
    this.issues = {
      deprecated: new Map(),
      invalid: new Set(),
      inconsistent: new Map(),
      unused: new Set()
    }
    
    this.usedMethods = new Set()
    this.allValidMethods = this.getAllValidMethods()
  }

  getAllValidMethods() {
    const methods = new Set()
    
    function collectMethods(obj) {
      for (const key in obj) {
        if (typeof obj[key] === 'string') {
          methods.add(obj[key])
        } else if (typeof obj[key] === 'object') {
          collectMethods(obj[key])
        }
      }
    }
    
    collectMethods(API_MAPPING)
    return methods
  }

  checkProject(projectRoot = process.cwd()) {
    console.log(colors.blue('🔍 开始检查API一致性...'))
    console.log(colors.gray(`项目路径: ${projectRoot}`))
    
    const srcDir = path.join(projectRoot, 'src')
    if (!fs.existsSync(srcDir)) {
      console.error(colors.red('❌ 未找到src目录'))
      return
    }

    this.scanDirectory(srcDir)
    this.generateReport()
  }

  scanDirectory(dir) {
    const files = fs.readdirSync(dir)
    
    for (const file of files) {
      const filePath = path.join(dir, file)
      const stat = fs.statSync(filePath)
      
      if (stat.isDirectory()) {
        // 跳过node_modules等目录
        if (!['node_modules', 'dist', 'build', '.git'].includes(file)) {
          this.scanDirectory(filePath)
        }
      } else if (stat.isFile()) {
        // 检查Vue和JS文件
        const ext = path.extname(file)
        if (['.vue', '.js', '.ts'].includes(ext)) {
          this.checkFile(filePath)
        }
      }
    }
  }

  checkFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8')
      this.analyzeFileContent(content, filePath)
    } catch (error) {
      console.warn(colors.yellow(`⚠️  无法读取文件 ${filePath}: ${error.message}`))
    }
  }

  analyzeFileContent(content, filePath) {
    // 检查是否导入了API
    const importPattern = /import.*api.*from/gi
    if (!importPattern.test(content)) {
      return // 如果没有导入API，跳过检查
    }

    // 匹配API调用模式
    const apiCallPattern = /api\.(\w+)\s*\(/g
    const foundMethods = new Set()
    
    let match
    while ((match = apiCallPattern.exec(content)) !== null) {
      const methodName = match[1]
      if (!foundMethods.has(methodName)) {
        foundMethods.add(methodName)
        this.usedMethods.add(methodName)
        this.validateApiCall(methodName, filePath)
      }
    }

    // 检查API映射配置的使用
    const mappingUsage = /getApiMethod|validateApiCall|createApiProxy/.test(content)
    if (foundMethods.size > 0 && !mappingUsage) {
      const inconsistentUsage = this.issues.inconsistent.get('未使用API映射配置') || []
      inconsistentUsage.push(filePath)
      this.issues.inconsistent.set('未使用API映射配置', inconsistentUsage)
    }
  }

  validateApiCall(methodName, filePath) {
    // 检查是否为废弃的API
    if (DEPRECATED_API_MAPPING[methodName]) {
      const usage = this.issues.deprecated.get(methodName) || []
      usage.push(filePath)
      this.issues.deprecated.set(methodName, usage)
      return
    }

    // 检查是否为无效的API方法
    if (!this.allValidMethods.has(methodName)) {
      this.issues.invalid.add(`${methodName} (${path.relative(process.cwd(), filePath)})`)
    }
  }

  generateReport() {
    console.log('\n' + '='.repeat(60))
    console.log(colors.bold.blue('📊 API一致性检查报告'))
    console.log('='.repeat(60))

    const hasIssues = this.issues.deprecated.size > 0 || 
                     this.issues.invalid.size > 0 || 
                     this.issues.inconsistent.size > 0

    if (!hasIssues) {
      console.log(colors.green('\n✅ 恭喜！未发现API一致性问题'))
      console.log(colors.gray(`共检查了 ${this.usedMethods.size} 个不同的API方法`))
      return
    }

    // 统计信息
    console.log(colors.blue(`\n📈 统计信息:`))
    console.log(`  - 使用的API方法数量: ${this.usedMethods.size}`)
    console.log(`  - 废弃API使用: ${this.issues.deprecated.size}`)
    console.log(`  - 无效API方法: ${this.issues.invalid.size}`)
    console.log(`  - 不一致使用: ${this.issues.inconsistent.size}`)

    // 报告废弃API使用情况
    if (this.issues.deprecated.size > 0) {
      console.log(colors.yellow('\n⚠️  废弃API使用情况:'))
      for (const [method, files] of this.issues.deprecated) {
        const recommendedMethod = DEPRECATED_API_MAPPING[method]
        console.log(colors.yellow(`\n  ${method} -> 建议使用: ${recommendedMethod}`))
        files.forEach(file => {
          const relativePath = path.relative(process.cwd(), file)
          console.log(colors.gray(`    - ${relativePath}`))
        })
      }
    }

    // 报告无效API方法
    if (this.issues.invalid.size > 0) {
      console.log(colors.red('\n❌ 无效API方法:'))
      this.issues.invalid.forEach(item => {
        console.log(colors.red(`  - ${item}`))
      })
    }

    // 报告不一致的API使用
    if (this.issues.inconsistent.size > 0) {
      console.log(colors.yellow('\n🔄 不一致的API使用:'))
      for (const [issue, files] of this.issues.inconsistent) {
        console.log(colors.yellow(`\n  ${issue}:`))
        files.forEach(file => {
          const relativePath = path.relative(process.cwd(), file)
          console.log(colors.gray(`    - ${relativePath}`))
        })
      }
    }

    // 建议
    console.log(colors.blue('\n💡 修复建议:'))
    if (this.issues.deprecated.size > 0) {
      console.log('  1. 将废弃的API方法替换为推荐的方法')
    }
    if (this.issues.invalid.size > 0) {
      console.log('  2. 检查无效的API方法名，确保在API映射配置中定义')
    }
    if (this.issues.inconsistent.size > 0) {
      console.log('  3. 在文件中导入并使用 @/utils/api-mapping 统一管理API调用')
    }
    
    console.log(colors.blue('\n📚 参考文档:'))
    console.log('  - API映射配置: src/utils/api-mapping.js')
    console.log('  - API验证工具: src/utils/api-validator.js')
    
    console.log('\n' + '='.repeat(60))
    
    // 如果有严重问题，返回错误码
    if (this.issues.invalid.size > 0) {
      process.exit(1)
    }
  }
}

// 命令行使用
if (require.main === module) {
  const checker = new ApiConsistencyChecker()
  const projectRoot = process.argv[2] || process.cwd()
  checker.checkProject(projectRoot)
}

module.exports = ApiConsistencyChecker