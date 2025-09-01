const fs = require('fs');
const path = require('path');

// 从 check-problem-keys.js 的输出中提取的缺失键列表
const missingKeysInAdmin = [
  'Add_Sample', 'Code_Template', 'Compile', 'Delete', 'Description', 'Difficulty',
  'Display_ID', 'IOMode', 'Input', 'InputFileName', 'Language', 'Memory_limit',
  'New_Tag', 'Output', 'OutputFileName', 'SPJ_Code', 'SPJ_language', 'Sample',
  'Sample_Input', 'Sample_Output', 'Score', 'ShareSubmission', 'Special_Judge',
  'Tags', 'Time_Limit', 'Title', 'Upload_Test_Case', 'Visible', 'Input_Samples',
  'Output_Samples', 'Hint', 'Source', 'High', 'Mid', 'Low', 'Save', 'Cancel',
  'Reset', 'Option', 'Author', 'ID', 'Type', 'Problem_List', 'Choice_Question'
];

// 读取 oj 翻译文件
const ojZhCNPath = path.join(__dirname, 'src/i18n/oj/zh-CN.js');
const ojEnUSPath = path.join(__dirname, 'src/i18n/oj/en-US.js');

function extractKeysFromFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const keyRegex = /([A-Za-z_][A-Za-z0-9_]*):.*?['"`]/g;
  const keys = new Set();
  let match;
  
  while ((match = keyRegex.exec(content)) !== null) {
    keys.add(match[1]);
  }
  
  return keys;
}

const ojZhCNKeys = extractKeysFromFile(ojZhCNPath);
const ojEnUSKeys = extractKeysFromFile(ojEnUSPath);

console.log('=== 检查缺失键是否在 OJ 翻译文件中存在 ===\n');

const foundInOJ = [];
const stillMissing = [];

missingKeysInAdmin.forEach(key => {
  if (ojZhCNKeys.has(key) && ojEnUSKeys.has(key)) {
    foundInOJ.push(key);
  } else {
    stillMissing.push(key);
  }
});

console.log(`在 OJ 翻译文件中找到的键 (${foundInOJ.length}):`);
foundInOJ.forEach(key => console.log(`  - ${key}`));

console.log(`\n仍然缺失的键 (${stillMissing.length}):`);
stillMissing.forEach(key => console.log(`  - ${key}`));

console.log('\n=== 分析结果 ===');
console.log(`总共缺失键: ${missingKeysInAdmin.length}`);
console.log(`在 OJ 中找到: ${foundInOJ.length}`);
console.log(`仍需添加到 admin: ${stillMissing.length}`);

if (foundInOJ.length > 0) {
  console.log('\n建议: Problem.vue 可能需要同时访问 admin 和 oj 命名空间的翻译键');
}