      const currentIndex = siblings.findIndex(item => item.id === category.id)
      
      if (currentIndex < siblings.length - 1) {
        const nextItem = siblings[currentIndex + 1]
        this.swapSortOrder(category, nextItem)
      }
    },
    
    // 获取同级分类
    getSiblings(category) {
      if (!category.parent) {
        return this.treeCategories
      } else {
        const parent = this.flatCategories.find(cat => cat.id === category.parent)
        return parent ? parent.children : []
      }
    },
    
    // 交换两个分类的排序顺序
    async swapSortOrder(cat1, cat2) {
      try {
        const temp = cat1.sort_order
        cat1.sort_order = cat2.sort_order
        cat2.sort_order = temp
        
        await this.updateCategoryOrder([
          { id: cat1.id, sort_order: cat1.sort_order },
          { id: cat2.id, sort_order: cat2.sort_order }
        ])
        
        this.treeCategories = this.buildTree(this.categories)
        this.$forceUpdate()
        
      } catch (error) {
        console.error('交换排序失败:', error)
        this.$message.error('调整顺序失败')
      }
    },
    
    // 手动更新排序
    async updateManualOrder() {
      if (!this.selectedCategoryData) return
      
      try {
        await this.updateCategoryOrder([{
          id: this.selectedCategoryData.id,
          sort_order: this.manualOrder
        }])
        
        this.selectedCategoryData.sort_order = this.manualOrder
        this.treeCategories = this.buildTree(this.categories)
        this.$forceUpdate()
        
        this.$message.success(this.$t('m.Sort_Order_Updated'))
      } catch (error) {
        console.error('更新排序失败:', error)
        this.$message.error(this.$t('m.Update_Sort_Failed'))
      }
    },
    
    // 检查是否可以上移
    canMoveUp(category) {
      const siblings = this.getSiblings(category)
      const currentIndex = siblings.findIndex(item => item.id === category.id)
      return currentIndex > 0
    },
    
    // 检查是否可以下移
    canMoveDown(category) {
      const siblings = this.getSiblings(category)
      const currentIndex = siblings.findIndex(item => item.id === category.id)
      return currentIndex < siblings.length - 1
    },
    
    // 更新分类排序的API调用
    async updateCategoryOrder(updates) {
      try {
        if (api.batchUpdateCategoryOrder) {
          await api.batchUpdateCategoryOrder(updates)
        } else {
          for (const update of updates) {
            await api.updateChoiceQuestionCategory(update.id, {
              sort_order: update.sort_order
            })
            // 更新本地数据
            const localCategory = this.categories.find(cat => cat.id === update.id)
            if (localCategory) {
              localCategory.sort_order = update.sort_order
            }
          }
        }
      } catch (error) {
        console.error('更新分类排序失败:', error)
        throw error
      }
    },
    
    // 保存排序结果
    async saveSortOrder() {
      try {
        const updates = this.flatCategories.map(cat => ({
          id: cat.id,
          sort_order: cat.sort_order || 0
        }))
        
        await this.updateCategoryOrder(updates)
        this.$message.success(this.$t('m.Sort_Order_Saved'))
      } catch (error) {
        console.error('保存排序失败:', error)
        this.$message.error(this.$t('m.Save_Sort_Failed'))
      }
    },
    
    // 其他现有方法
    toggleExpand(nodeId) {
      if (this.expandedNodes.has(nodeId)) {
        this.expandedNodes.delete(nodeId)
      } else {
        this.expandedNodes.add(nodeId)
      }
      this.$forceUpdate()
    },
    
    selectCategory(categoryId) {
      this.selectedCategory = categoryId
    },
    
    expandAll() {
      this.expandedNodes = new Set(this.flatCategories.map(cat => cat.id))
      this.$forceUpdate()
    },
    
    collapseAll() {
      this.expandedNodes.clear()
      this.$forceUpdate()
    },
    
    handleCreateCategory(parentId = null) {
      this.editingCategory = null
      // 为新分类设置合理的默认排序值
      const siblings = parentId ? 
        this.flatCategories.filter(cat => cat.parent === parentId) :
        this.treeCategories
      const maxOrder = siblings.length > 0 ? 
        Math.max(...siblings.map(cat => cat.sort_order || 0)) : 0
      
      this.categoryForm = {
        name: '',
        description: '',
        parent: parentId,
        sort_order: maxOrder + 10
      }
      this.showCreateModal = true
    },
    
    editCategory(category) {
      this.editingCategory = category
      this.categoryForm = {
        name: category.name,
        description: category.description || '',
        parent: category.parent,
        sort_order: category.sort_order || 0
      }
      this.showCreateModal = true
    },
    
    async deleteCategory(category) {
      const confirm = await this.$confirm(
        `确定要删除分类 "${category.name}" 吗？`, 
        '确认删除', 
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).catch(() => false)
      
      if (confirm) {
        try {
          await api.deleteChoiceQuestionCategory(category.id)
          this.$message.success('删除成功')
          this.getCategories()
          
          if (this.selectedCategory === category.id) {
            this.selectedCategory = null
          }
        } catch (err) {
          this.$message.error('删除失败')
          console.error(err)
        }
      }
    },
    
    async handleSubmit() {
      const valid = await this.$refs.categoryForm.validate().catch(() => false)
      if (!valid) return
      
      this.submitting = true
      try {
        if (this.editingCategory) {
          await api.updateChoiceQuestionCategory(this.editingCategory.id, this.categoryForm)
          this.$message.success('更新成功')
        } else {
          await api.createChoiceQuestionCategory(this.categoryForm)
          this.$message.success('创建成功')
        }
        this.showCreateModal = false
        this.getCategories()
      } catch (err) {
        this.$message.error(this.editingCategory ? '更新失败' : '创建失败')
        console.error(err)
      } finally {
        this.submitting = false
      }
    },
    
    resetForm() {
      this.editingCategory = null
      this.categoryForm = {
        name: '',
        description: '',
        parent: null,
        sort_order: 0
      }
      this.$refs.categoryForm && this.$refs.categoryForm.resetFields()
    },
    
    getParentName(parentId) {
      if (!parentId) return null
      const parent = this.flatCategories.find(cat => cat.id === parentId)
      return parent ? parent.name : null
    },

    getChildrenCount(categoryId) {
      return this.categories.filter(cat => cat.parent === categoryId).length
    },

    handleSearch() {
      if (this.searchTimer) {
        clearTimeout(this.searchTimer)
      }
      
      this.searchTimer = setTimeout(() => {
        if (this.searchTerm && !this.sortMode) {
          this.expandMatchingNodes()
        }
      }, 300)
    },

    expandMatchingNodes() {
      const expandIds = new Set()
      
      const checkAndExpand = (nodes) => {
        nodes.forEach(node => {
          const matches = node.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
            (node.description && node.description.toLowerCase().includes(this.searchTerm.toLowerCase()))
          
          if (matches) {
            let parent = this.categories.find(cat => cat.id === node.parent)
            while (parent) {
              expandIds.add(parent.id)
              parent = this.categories.find(cat => cat.id === parent.parent)
            }
          }
          
          if (node.children && node.children.length > 0) {
            checkAndExpand(node.children)
          }
        })
      }
      
      checkAndExpand(this.treeCategories)
      
      expandIds.forEach(id => this.expandedNodes.add(id))
      this.$forceUpdate()
    },

    handleImport() {
      this.$message.info('导入功能开发中...')
    },

    handleExport() {
      this.$message.info('导出功能开发中...')
    },

    handleBatchManage() {
      this.$message.info('批量管理功能开发中...')
    }
  }
}
</script>

<style scoped>
.category-management {
  background-color: #f5f7fa;
}

.header-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.main-content {
  padding: 0;
}

.tree-panel, .details-panel, .quick-actions, .sort-help {
  background: white;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  margin-bottom: 16px;
}

.tree-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding: 16px 20px 0;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 16px;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.sort-mode-tip {
  background: #e6f7ff;
  color: #1890ff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.tree-container {
  min-height: 400px;
  padding: 0 20px 20px;
}

.tree-content {
  padding-top: 8px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #c0c4cc;
}

.empty-state p {
  margin: 12px 0 0 0;
  font-size: 14px;
}

.tree-node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.tree-node-content:hover {
  background-color: #f5f7fa;
}

.tree-node-content.selected {
  background-color: #ecf5ff;
  border-left: 3px solid #409eff;
}

.tree-node-content.sort-mode {
  cursor: move;
}

.tree-node-content.dragging {
  opacity: 0.5;
}

.tree-node-content.drag-over-top {
  border-top: 2px solid #409eff;
}

.tree-node-content.drag-over-middle {
  background-color: #e6f7ff;
}

.tree-node-content.drag-over-bottom {
  border-bottom: 2px solid #409eff;
}

.drag-handle {
  color: #909399;
  cursor: move;
  padding: 2px;
  transition: color 0.2s ease;
}

.drag-handle:hover {
  color: #409eff;
}

.expand-button {
  width: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.expand-btn {
  padding: 0;
  width: 20px;
  height: 20px;
  border: none;
  background: none;
}

.expand-placeholder {
  width: 20px;
  height: 20px;
}

.folder-icon {
  flex-shrink: 0;
}

.folder-icon-style {
  font-size: 18px;
  color: #409eff;
}

.document-icon-style {
  font-size: 16px;
  color: #909399;
}

.node-info {
  flex: 1;
  cursor: pointer;
}

.node-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2px;
}

.node-name {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.node-badges {
  display: flex;
  gap: 4px;
  align-items: center;
}

.question-count, .sort-order {
  margin-left: 4px;
}

.node-description {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
  margin-top: 2px;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.tree-node-content:hover .node-actions {
  opacity: 1;
}

.action-btn {
  padding: 4px !important;
  margin: 0 2px;
  border-radius: 4px;
}

.action-btn.success:hover {
  background-color: #f0f9ff;
  color: #67c23a;
}

.action-btn.primary:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.action-btn.danger:hover {
  background-color: #fef0f0;
  color: #f56c6c;
}

.tree-children {
  border-left: 1px solid #ebeef5;
  margin-left: 20px;
  animation: slideDown 0.2s ease;
}

.details-panel, .quick-actions, .sort-help {
  padding: 20px;
}

.panel-header {
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 20px;
}

.panel-title {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
}

.details-content {
  padding: 4px 0;
}

.detail-item {
  margin-bottom: 16px;
}

.detail-item label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 4px;
}

.detail-item p {
  margin: 0;
  color: #303133;
  font-size: 14px;
  line-height: 1.4;
}

.detail-actions {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.detail-actions .el-button {
  margin-right: 8px;
  margin-bottom: 8px;
}

.sort-actions {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.sort-controls {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.manual-order {
  display: flex;
  align-items: center;
  gap: 8px;
}

.manual-order label {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
}

.no-selection {
  text-align: center;
  padding: 40px 20px;
  color: #c0c4cc;
}

.no-selection p {
  margin: 12px 0 0 0;
  font-size: 14px;
}

.quick-action-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: #fafafa;
  color: #606266;
  font-size: 14px;
  transition: all 0.2s ease;
}

.quick-action-btn:hover {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.quick-action-btn i {
  margin-right: 8px;
  font-size: 16px;
}

.help-content {
  padding: 8px 0;
}

.help-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 13px;
  color: #606266;
}

.help-item i {
  color: #909399;
  width: 16px;
  text-align: center;
}

.form-help-text {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.dialog-footer {
  text-align: right;
}

.dialog-footer .el-button {
  margin-left: 8px;
}

/* 动画效果 */
.tree-node-wrapper {
  transition: all 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .tree-toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .toolbar-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .header-buttons {
    flex-direction: column;
    gap: 8px;
    width: 100%;
  }
  
  .header-buttons .el-button {
    width: 100%;
  }
  
  .tree-node-content {
    padding: 10px 8px;
  }
  
  .node-actions {
    opacity: 1; /* 在移动端始终显示操作按钮 */
  }
  
  .sort-controls {
    flex-direction: column;
    gap: 8px;
  }
  
  .manual-order {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .manual-order label {
    margin-bottom: 4px;
  }
  
  /* 移动端列布局改为垂直堆叠 */
  .main-content .el-col {
    margin-bottom: 16px;
  }
  
  .sort-mode-tip {
    font-size: 11px;
    padding: 2px 6px;
  }
}

/* 搜索框样式 */
.search-section .el-input__inner {
  border-radius: 20px;
}

.search-section .el-input__prefix {
  left: 12px;
}

.search-section .el-input--prefix .el-input__inner {
  padding-left: 35px;
}

/* 排序模式下的特殊样式 */
.sort-mode .tree-node-content {
  border: 1px dashed #d9d9d9;
  margin: 2px 0;
}

.sort-mode .tree-node-content:hover {
  border-color: #409eff;
}

/* 拖拽状态动画 */
.tree-node-content.dragging {
  transform: rotate(2deg);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* 更好的拖拽指示器 */
.tree-node-content.drag-over-top::before {
  content: '';
  position: absolute;
  top: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #409eff;
  border-radius: 1px;
}

.tree-node-content.drag-over-bottom::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #409eff;
  border-radius: 1px;
}
</style>
