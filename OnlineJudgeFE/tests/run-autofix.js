#!/usr/bin/env node

const AutoFixer = require('./auto-fix');
const fs = require('fs');
const path = require('path');

async function runDiagnostics() {
  console.log('=== Frontend Admin Module Diagnostics ===\n');
  
  // 1. 检查文件是否存在
  const filesToCheck = [
    '../src/pages/admin/router.js',
    '../src/pages/admin/components/SideMenu.vue',
    '../src/pages/admin/api.js',
    '../src/pages/admin/views/choice-question/ChoiceQuestion.vue',
    '../src/pages/admin/views/choice-question/ChoiceQuestionList.vue',
    '../src/i18n/admin/zh-CN.js',
    '../src/i18n/admin/en-US.js'
  ];
  
  console.log('1. File Existence Check:');
  for (const file of filesToCheck) {
    const fullPath = path.join(__dirname, file);
    const exists = fs.existsSync(fullPath);
    console.log(`   ${exists ? '✓' : '✗'} ${file}`);
    
    if (!exists && file.includes('choice-question')) {
      console.log(`     Missing choice question component: ${file}`);
    }
  }
  
  console.log('\n2. Router Configuration Check:');
  const routerPath = path.join(__dirname, '../src/pages/admin/router.js');
  if (fs.existsSync(routerPath)) {
    const routerContent = fs.readFileSync(routerPath, 'utf8');
    const hasChoiceRoutes = routerContent.includes('choice-question');
    const hasChoiceImports = routerContent.includes('ChoiceQuestion');
    
    console.log(`   ${hasChoiceRoutes ? '✓' : '✗'} Choice question routes configured`);
    console.log(`   ${hasChoiceImports ? '✓' : '✗'} Choice question components imported`);
    
    if (!hasChoiceRoutes || !hasChoiceImports) {
      console.log('     Router needs configuration updates');
    }
  } else {
    console.log('   ✗ Router file not found');
  }
  
  console.log('\n3. Side Menu Configuration Check:');
  const menuPath = path.join(__dirname, '../src/pages/admin/components/SideMenu.vue');
  if (fs.existsSync(menuPath)) {
    const menuContent = fs.readFileSync(menuPath, 'utf8');
    const hasChoiceMenu = menuContent.includes('choice-question');
    
    console.log(`   ${hasChoiceMenu ? '✓' : '✗'} Choice question menu items configured`);
    
    if (!hasChoiceMenu) {
      console.log('     Side menu needs choice question items');
    }
  } else {
    console.log('   ✗ SideMenu file not found');
  }
  
  console.log('\n4. API Configuration Check:');
  const apiPath = path.join(__dirname, '../src/pages/admin/api.js');
  if (fs.existsSync(apiPath)) {
    const apiContent = fs.readFileSync(apiPath, 'utf8');
    const hasChoiceAPI = apiContent.includes('getChoiceQuestions');
    
    console.log(`   ${hasChoiceAPI ? '✓' : '✗'} Choice question API methods configured`);
    
    if (!hasChoiceAPI) {
      console.log('     API needs choice question methods');
    }
  } else {
    console.log('   ✗ API file not found');
  }
  
  console.log('\n5. I18n Configuration Check:');
  const zhPath = path.join(__dirname, '../src/i18n/admin/zh-CN.js');
  const enPath = path.join(__dirname, '../src/i18n/admin/en-US.js');
  
  if (fs.existsSync(zhPath)) {
    const zhContent = fs.readFileSync(zhPath, 'utf8');
    const hasZhTranslations = zhContent.includes('Choice_Question');
    console.log(`   ${hasZhTranslations ? '✓' : '✗'} Chinese translations configured`);
  } else {
    console.log('   ✗ Chinese i18n file not found');
  }
  
  if (fs.existsSync(enPath)) {
    const enContent = fs.readFileSync(enPath, 'utf8');
    const hasEnTranslations = enContent.includes('Choice_Question');
    console.log(`   ${hasEnTranslations ? '✓' : '✗'} English translations configured`);
  } else {
    console.log('   ✗ English i18n file not found');
  }
}

async function main() {
  try {
    // 运行诊断
    await runDiagnostics();
    
    console.log('\n=== Running Auto-Fix ===\n');
    
    // 运行自动修复
    const results = await AutoFixer.runAllFixes();
    
    console.log('\n=== Auto-Fix Results ===');
    console.log('Routes fixed:', results.routes ? '✓' : '✗');
    console.log('Side menu fixed:', results.sideMenu ? '✓' : '✗');
    console.log('API fixed:', results.api ? '✓' : '✗');
    console.log('I18n fixed:', results.i18n ? '✓' : '✗');
    
    const hasChanges = Object.values(results).some(result => result === true);
    
    if (hasChanges) {
      console.log('\n⚠️  Changes were made. Please restart the frontend server for changes to take effect.');
      console.log('   Run: npm run dev');
    } else {
      console.log('\n✓ No changes needed. All configurations are already in place.');
    }
    
    console.log('\n=== Post-Fix Verification ===\n');
    
    // 重新运行诊断
    await runDiagnostics();
    
    console.log('\n=== Recommendations ===');
    console.log('1. Access the admin interface at: http://localhost:8080/admin/');
    console.log('2. Login with username: root, password: rootroot');
    console.log('3. Check if Problem and Choice Question modules appear in the sidebar');
    console.log('4. If modules are still missing, check browser console for JavaScript errors');
    console.log('5. Verify backend API endpoints are accessible at: http://localhost:8000/api/');
    
  } catch (error) {
    console.error('Error running auto-fix:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { runDiagnostics, main };