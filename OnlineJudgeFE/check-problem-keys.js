const fs = require('fs');
const path = require('path');

// 读取 Problem.vue 文件
const problemVuePath = path.join(__dirname, 'src/pages/admin/views/problem/Problem.vue');
const problemVueContent = fs.readFileSync(problemVuePath, 'utf8');

// 提取所有翻译键
const translationKeyRegex = /\$t\('m\.([^']+)'/g;
const keys = [];
let match;

while ((match = translationKeyRegex.exec(problemVueContent)) !== null) {
  keys.push(match[1]);
}

// 去重并排序
const uniqueKeys = [...new Set(keys)].sort();

console.log('Problem.vue 中使用的翻译键:');
uniqueKeys.forEach(key => {
  console.log(`  ${key}`);
});

console.log(`\n总共找到 ${uniqueKeys.length} 个唯一的翻译键`);

// 检查翻译文件中是否存在这些键
const adminZhCNPath = path.join(__dirname, 'src/i18n/admin/zh-CN.js');
const adminEnUSPath = path.join(__dirname, 'src/i18n/admin/en-US.js');

function loadTranslationFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  // 匹配 export const m = { ... }
  const exportMatch = content.match(/export const m\s*=\s*({[\s\S]*})/);
  if (exportMatch) {
    try {
      const objStr = exportMatch[1];
      return eval('(' + objStr + ')');
    } catch (e) {
      console.error(`解析 ${filePath} 失败:`, e.message);
      return {};
    }
  }
  return {};
}

const zhCNTranslations = loadTranslationFile(adminZhCNPath);
const enUSTranslations = loadTranslationFile(adminEnUSPath);

console.log('\n检查缺失的翻译键:');
const missingInZhCN = [];
const missingInEnUS = [];

uniqueKeys.forEach(key => {
  if (!zhCNTranslations[key]) {
    missingInZhCN.push(key);
  }
  if (!enUSTranslations[key]) {
    missingInEnUS.push(key);
  }
});

if (missingInZhCN.length > 0) {
  console.log('\n中文翻译文件中缺失的键:');
  missingInZhCN.forEach(key => console.log(`  ${key}`));
} else {
  console.log('\n✅ 中文翻译文件中没有缺失的键');
}

if (missingInEnUS.length > 0) {
  console.log('\n英文翻译文件中缺失的键:');
  missingInEnUS.forEach(key => console.log(`  ${key}`));
} else {
  console.log('\n✅ 英文翻译文件中没有缺失的键');
}