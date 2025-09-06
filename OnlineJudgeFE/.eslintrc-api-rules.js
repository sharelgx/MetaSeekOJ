/**
 * ESLint自定义规则 - API一致性检查
 * 在开发时实时检查API调用的一致性
 */

module.exports = {
  rules: {
    // 检查废弃的API调用
    'no-deprecated-api': {
      meta: {
        type: 'problem',
        docs: {
          description: '禁止使用废弃的API方法',
          category: 'Best Practices'
        },
        fixable: 'code',
        schema: []
      },
      create(context) {
        // 废弃API映射
        const deprecatedApis = {
          'getChoiceQuestionCategories': 'getCategoryList',
          'getChoiceQuestionTags': 'getTagList',
          'getExamPaperCategories': 'getCategoryList'
        }

        return {
          MemberExpression(node) {
            // 检查 api.methodName() 调用
            if (node.object.name === 'api' && 
                node.property.type === 'Identifier' &&
                deprecatedApis[node.property.name]) {
              
              const recommendedMethod = deprecatedApis[node.property.name]
              
              context.report({
                node,
                message: `使用了废弃的API方法 '${node.property.name}'，建议使用 '${recommendedMethod}'`,
                fix(fixer) {
                  return fixer.replaceText(node.property, recommendedMethod)
                }
              })
            }
          }
        }
      }
    },

    // 强制使用API映射配置
    'prefer-api-mapping': {
      meta: {
        type: 'suggestion',
        docs: {
          description: '建议使用API映射配置统一管理API调用',
          category: 'Best Practices'
        },
        schema: []
      },
      create(context) {
        let hasApiImport = false
        let hasApiMappingImport = false
        const apiCalls = []

        return {
          ImportDeclaration(node) {
            // 检查是否导入了API
            if (node.source.value.includes('api')) {
              hasApiImport = true
            }
            // 检查是否导入了API映射
            if (node.source.value.includes('api-mapping')) {
              hasApiMappingImport = true
            }
          },

          MemberExpression(node) {
            // 收集API调用
            if (node.object.name === 'api' && 
                node.property.type === 'Identifier') {
              apiCalls.push(node)
            }
          },

          'Program:exit'() {
            // 如果有API调用但没有使用API映射，给出建议
            if (hasApiImport && apiCalls.length > 0 && !hasApiMappingImport) {
              context.report({
                node: apiCalls[0],
                message: '建议使用 @/utils/api-mapping 统一管理API调用，提高代码一致性'
              })
            }
          }
        }
      }
    },

    // 检查API调用参数一致性
    'api-call-consistency': {
      meta: {
        type: 'problem',
        docs: {
          description: '检查API调用的参数一致性',
          category: 'Possible Errors'
        },
        schema: []
      },
      create(context) {
        const apiCallPatterns = new Map()

        return {
          CallExpression(node) {
            // 检查 api.methodName() 调用
            if (node.callee.type === 'MemberExpression' &&
                node.callee.object.name === 'api' &&
                node.callee.property.type === 'Identifier') {
              
              const methodName = node.callee.property.name
              const argCount = node.arguments.length
              
              if (apiCallPatterns.has(methodName)) {
                const previousArgCount = apiCallPatterns.get(methodName)
                if (previousArgCount !== argCount) {
                  context.report({
                    node,
                    message: `API方法 '${methodName}' 的参数数量不一致，之前调用使用了 ${previousArgCount} 个参数，当前使用了 ${argCount} 个参数`
                  })
                }
              } else {
                apiCallPatterns.set(methodName, argCount)
              }
            }
          }
        }
      }
    }
  }
}