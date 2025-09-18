// 检查面包屑导航的JavaScript测试脚本

// 等待页面加载完成
window.addEventListener('load', function() {
    console.log('页面加载完成，开始检查面包屑导航...');
    
    // 等待Vue应用初始化
    setTimeout(function() {
        checkBreadcrumbNavigation();
    }, 3000);
});

function checkBreadcrumbNavigation() {
    console.log('=== 面包屑导航检查开始 ===');
    
    // 检查面包屑导航元素是否存在
    const breadcrumbSection = document.querySelector('.breadcrumb-section');
    const breadcrumbNav = document.querySelector('.breadcrumb-nav');
    
    console.log('面包屑区域元素:', breadcrumbSection);
    console.log('面包屑导航元素:', breadcrumbNav);
    
    if (breadcrumbSection) {
        console.log('✓ 面包屑区域存在');
        console.log('面包屑区域内容:', breadcrumbSection.innerHTML);
        
        // 检查是否有v-if条件阻止显示
        const style = window.getComputedStyle(breadcrumbSection);
        console.log('面包屑区域样式 - display:', style.display);
        console.log('面包屑区域样式 - visibility:', style.visibility);
        
        if (breadcrumbNav) {
            console.log('✓ 面包屑导航存在');
            console.log('面包屑导航内容:', breadcrumbNav.innerHTML);
        } else {
            console.log('✗ 面包屑导航不存在');
        }
    } else {
        console.log('✗ 面包屑区域不存在');
    }
    
    // 检查Vue实例和数据
    if (window.Vue && window.Vue.version) {
        console.log('Vue版本:', window.Vue.version);
        
        // 尝试获取Vue实例
        const app = document.querySelector('#app').__vue__;
        if (app) {
            console.log('Vue应用实例存在');
            
            // 查找TopicPracticeDetail组件
            const findComponent = (component, name) => {
                if (component.$options.name === name) {
                    return component;
                }
                for (let child of component.$children) {
                    const found = findComponent(child, name);
                    if (found) return found;
                }
                return null;
            };
            
            const topicComponent = findComponent(app, 'TopicPracticeDetail');
            if (topicComponent) {
                console.log('✓ TopicPracticeDetail组件找到');
                console.log('组件breadcrumb数据:', topicComponent.breadcrumb);
                console.log('组件currentCategory数据:', topicComponent.currentCategory);
                console.log('组件loading状态:', topicComponent.loading);
            } else {
                console.log('✗ TopicPracticeDetail组件未找到');
            }
        }
    }
    
    console.log('=== 面包屑导航检查结束 ===');
}

// 导出检查函数供控制台使用
window.checkBreadcrumbNavigation = checkBreadcrumbNavigation;