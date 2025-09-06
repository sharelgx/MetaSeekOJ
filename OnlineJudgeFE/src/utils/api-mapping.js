/**
 * API接口映射配置
 * 用于统一管理API方法名称，防止接口调用不一致的问题
 * 
 * 使用方式：
 * import { getApiMethod } from '@/utils/api-mapping'
 * const apiMethod = getApiMethod('categories.list')
 * 
 * 或者直接使用映射对象：
 * import { API_MAPPING } from '@/utils/api-mapping'
 * const method = API_MAPPING.categories.list
 */

// API接口映射配置
export const API_MAPPING = {
  // 分类相关API
  categories: {
    list: 'getChoiceQuestionCategories',       // 获取分类列表 - 修复为实际API方法名
    create: 'createChoiceQuestionCategory',     // 创建分类
    update: 'updateChoiceQuestionCategory',     // 更新分类
    delete: 'deleteChoiceQuestionCategory'      // 删除分类
  },
  
  // 选择题相关API
  choiceQuestions: {
    list: 'getChoiceQuestions',                 // 获取选择题列表
    detail: 'getChoiceQuestion',                // 获取选择题详情
    create: 'createChoiceQuestion',             // 创建选择题
    update: 'updateChoiceQuestion',             // 更新选择题
    delete: 'deleteChoiceQuestion',             // 删除选择题
    submit: 'submitChoiceQuestion',             // 提交选择题答案
    import: 'importChoiceQuestions',            // 批量导入选择题
    export: 'exportChoiceQuestions'             // 导出选择题
  },
  
  // 题目相关API（通用）
  questions: {
    import: 'importQuestions'                   // 批量导入题目（通用）
  },
  
  // 试卷相关API
  examPapers: {
    list: 'getExamPaperList',                   // 获取试卷列表
    detail: 'getExamPaper',                     // 获取试卷详情
    create: 'createExamPaper',                  // 创建试卷
    update: 'updateExamPaper',                  // 更新试卷
    delete: 'deleteExamPaper',                  // 删除试卷
    import: 'importExamPapers',                 // 批量导入试卷
    export: 'exportExamPapers'                  // 导出试卷
  },
  
  // 标签相关API
  tags: {
    list: 'getTagList',                         // 获取标签列表
    create: 'createChoiceQuestionTag',          // 创建标签（选择题）
    update: 'updateTag',                        // 更新标签
    delete: 'deleteTag'                         // 删除标签
  },
  
  // 用户相关API
  users: {
    list: 'getUserList',                        // 获取用户列表
    detail: 'getUser',                          // 获取用户详情
    create: 'createUser',                       // 创建用户
    update: 'updateUser',                       // 更新用户
    delete: 'deleteUser'                        // 删除用户
  },
  
  // 统计相关API
  statistics: {
    overview: 'getStatisticsOverview',          // 获取统计概览
    questions: 'getQuestionStatistics',        // 获取题目统计
    papers: 'getPaperStatistics',              // 获取试卷统计
    users: 'getUserStatistics'                 // 获取用户统计
  }
}

// 已废弃的API方法名映射（用于兼容性检查）
export const DEPRECATED_API_MAPPING = {
  'getChoiceQuestionCategories': 'getCategoryList',  // 选择题分类 -> 统一分类接口
  'getChoiceQuestionTags': 'getTagList',             // 选择题标签 -> 统一标签接口
  'getExamPaperCategories': 'getCategoryList'        // 试卷分类 -> 统一分类接口
}

/**
 * 获取API方法名
 * @param {string} path - API路径，如 'categories.list'
 * @returns {string} API方法名
 */
export function getApiMethod(path) {
  const keys = path.split('.')
  let current = API_MAPPING
  
  for (const key of keys) {
    if (current[key]) {
      current = current[key]
    } else {
      console.warn(`API mapping not found for path: ${path}`)
      return null
    }
  }
  
  return current
}

/**
 * 检查API方法是否已废弃
 * @param {string} methodName - API方法名
 * @returns {string|null} 如果已废弃，返回推荐的新方法名；否则返回null
 */
export function checkDeprecatedApi(methodName) {
  return DEPRECATED_API_MAPPING[methodName] || null
}

/**
 * 验证API方法是否存在于映射中
 * @param {string} methodName - API方法名
 * @returns {boolean} 是否存在
 */
export function validateApiMethod(methodName) {
  const allMethods = []
  
  // 收集所有有效的API方法名
  function collectMethods(obj) {
    for (const key in obj) {
      if (typeof obj[key] === 'string') {
        allMethods.push(obj[key])
      } else if (typeof obj[key] === 'object') {
        collectMethods(obj[key])
      }
    }
  }
  
  collectMethods(API_MAPPING)
  return allMethods.includes(methodName)
}

/**
 * 获取所有API方法的列表（用于开发调试）
 * @returns {Array} 所有API方法名的数组
 */
export function getAllApiMethods() {
  const methods = []
  
  function collectMethods(obj, prefix = '') {
    for (const key in obj) {
      if (typeof obj[key] === 'string') {
        methods.push({
          path: prefix + key,
          method: obj[key]
        })
      } else if (typeof obj[key] === 'object') {
        collectMethods(obj[key], prefix + key + '.')
      }
    }
  }
  
  collectMethods(API_MAPPING)
  return methods
}

/**
 * 简单的API调用验证函数
 * @param {string} methodName - API方法名
 * @param {Object} params - API参数
 * @returns {boolean} 验证结果
 */
export function validateApiCall(methodName, params = {}) {
  if (process.env.NODE_ENV === 'development') {
    console.log(`API调用验证: ${methodName}`, params)
  }
  return true
}

// 开发环境下的API一致性检查
if (process.env.NODE_ENV === 'development') {
  // 检查是否有重复的API方法名
  const allMethods = getAllApiMethods()
  const methodNames = allMethods.map(item => item.method)
  const duplicates = methodNames.filter((item, index) => methodNames.indexOf(item) !== index)
  
  if (duplicates.length > 0) {
    console.warn('发现重复的API方法名:', duplicates)
  }
  
  // 输出API映射信息（仅在开发环境）
  console.log('API映射配置已加载，共', allMethods.length, '个API方法')
}

export default API_MAPPING