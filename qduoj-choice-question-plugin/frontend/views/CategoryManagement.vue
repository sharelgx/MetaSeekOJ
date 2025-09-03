<template>
  <div class="category-management">
    <!-- 页面标题和操作按钮 -->
    <div class="page-header">
      <h2>分类管理</h2>
      <div class="header-actions">
        <Button type="primary" icon="ios-add" @click="showCreateModal">
          新建分类
        </Button>
        <Button icon="ios-refresh" @click="refresh">刷新</Button>
      </div>
    </div>
    
    <!-- 分类树形结构 -->
    <Card>
      <div slot="title">
        <Icon type="ios-folder" />
        分类树
      </div>
      <div slot="extra">
        <ButtonGroup>
          <Button 
            :type="viewMode === 'tree' ? 'primary' : 'default'"
            @click="viewMode = 'tree'"
            size="small"
          >
            <Icon type="ios-git-network" />
            树形视图
          </Button>
          <Button 
            :type="viewMode === 'list' ? 'primary' : 'default'"
            @click="viewMode = 'list'"
            size="small"
          >
            <Icon type="ios-list" />
            列表视图
          </Button>
        </ButtonGroup>
      </div>
      
      <!-- 树形视图 -->
      <div v-if="viewMode === 'tree'" class="tree-view">
        <Tree
          :data="categoryTree"
          :render="renderTreeNode"
          :load-data="loadData"
          show-checkbox
          @on-select-change="onTreeSelect"
          @on-check-change="onTreeCheck"
        />
      </div>
      
      <!-- 列表视图 -->
      <div v-else class="list-view">
        <Table
          :columns="columns"
          :data="categoryList"
          :loading="loading"
          row-key="id"
          @on-row-click="onRowClick"
        />
      </div>
    </Card>
    
    <!-- 分类详情面板 -->
    <Card v-if="selectedCategory" class="detail-panel">
      <div slot="title">
        <Icon type="ios-information-circle" />
        分类详情
      </div>
      <div slot="extra">
        <ButtonGroup>
          <Button 
            type="primary" 
            size="small" 
            @click="editCategory(selectedCategory)"
          >
            编辑
          </Button>
          <Button 
            type="warning" 
            size="small" 
            @click="moveCategory(selectedCategory)"
          >
            移动
          </Button>
          <Button 
            type="error" 
            size="small" 
            @click="deleteCategory(selectedCategory)"
          >
            删除
          </Button>
        </ButtonGroup>
      </div>
      
      <Row :gutter="16">
        <Col :span="12">
          <div class="detail-item">
            <label>分类名称：</label>
            <span>{{ selectedCategory.name }}</span>
          </div>
          <div class="detail-item">
            <label>父分类：</label>
            <span>{{ selectedCategory.parent_name || '根分类' }}</span>
          </div>
          <div class="detail-item">
            <label>排序：</label>
            <span>{{ selectedCategory.sort_order }}</span>
          </div>
          <div class="detail-item">
            <label>状态：</label>
            <Tag :color="selectedCategory.is_enabled ? 'success' : 'default'">
              {{ selectedCategory.is_enabled ? '启用' : '禁用' }}
            </Tag>
          </div>
        </Col>
        <Col :span="12">
          <div class="detail-item">
            <label>题目数量：</label>
            <span>{{ selectedCategory.question_count }}</span>
          </div>
          <div class="detail-item">
            <label>创建时间：</label>
            <span>{{ formatDate(selectedCategory.create_time) }}</span>
          </div>
          <div class="detail-item">
            <label>更新时间：</label>
            <span>{{ formatDate(selectedCategory.last_update_time) }}</span>
          </div>
        </Col>
      </Row>
      
      <div class="detail-item" v-if="selectedCategory.description">
        <label>描述：</label>
        <div class="description">{{ selectedCategory.description }}</div>
      </div>
      
      <!-- 分类统计 -->
      <div class="category-stats" v-if="categoryStats">
        <h4>统计信息</h4>
        <Row :gutter="16">
          <Col :span="6">
            <Statistic title="总提交数" :value="categoryStats.total_submissions" />
          </Col>
          <Col :span="6">
            <Statistic title="正确提交" :value="categoryStats.correct_submissions" />
          </Col>
          <Col :span="6">
            <Statistic title="正确率" :value="categoryStats.acceptance_rate" suffix="%" />
          </Col>
          <Col :span="6">
            <Statistic title="平均难度" :value="categoryStats.average_difficulty" :precision="1" />
          </Col>
        </Row>
      </div>
    </Card>
    
    <!-- 批量操作面板 -->
    <Card v-if="selectedCategories.length > 0" class="batch-panel">
      <div slot="title">
        <Icon type="ios-checkmark-circle" />
        批量操作 (已选择 {{ selectedCategories.length }} 个分类)
      </div>
      <div class="batch-actions">
        <Button type="success" @click="batchEnable">批量启用</Button>
        <Button type="warning" @click="batchDisable">批量禁用</Button>
        <Button type="primary" @click="batchMove">批量移动</Button>
        <Button type="error" @click="batchDelete">批量删除</Button>
      </div>
    </Card>
    
    <!-- 新建/编辑分类模态框 -->
    <Modal
      v-model="categoryModal"
      :title="isEdit ? '编辑分类' : '新建分类'"
      @on-ok="submitCategory"
      @on-cancel="resetCategoryForm"
    >
      <Form ref="categoryForm" :model="categoryForm" :rules="categoryRules" :label-width="80">
        <FormItem label="分类名称" prop="name">
          <Input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </FormItem>
        
        <FormItem label="父分类" prop="parent">
          <Cascader
            v-model="categoryForm.parent"
            :data="parentCategoryOptions"
            :load-data="loadParentCategories"
            placeholder="选择父分类（可选）"
            clearable
          />
        </FormItem>
        
        <FormItem label="排序" prop="sort_order">
          <InputNumber 
            v-model="categoryForm.sort_order" 
            :min="0" 
            :max="9999"
            placeholder="排序值，数字越小越靠前"
          />
        </FormItem>
        
        <FormItem label="状态">
          <Switch v-model="categoryForm.is_enabled">
            <span slot="open">启用</span>
            <span slot="close">禁用</span>
          </Switch>
        </FormItem>
        
        <FormItem label="描述" prop="description">
          <Input 
            v-model="categoryForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="分类描述（可选）"
          />
        </FormItem>
      </Form>
    </Modal>
    
    <!-- 移动分类模态框 -->
    <Modal
      v-model="moveModal"
      title="移动分类"
      @on-ok="submitMove"
      @on-cancel="resetMoveForm"
    >
      <Form :label-width="80">
        <FormItem label="当前分类">
          <Input :value="moveForm.current_name" readonly />
        </FormItem>
        
        <FormItem label="目标父分类">
          <Cascader
            v-model="moveForm.target_parent"
            :data="parentCategoryOptions"
            :load-data="loadParentCategories"
            placeholder="选择目标父分类"
            clearable
          />
        </FormItem>
        
        <FormItem label="新排序">
          <InputNumber 
            v-model="moveForm.new_sort_order" 
            :min="0" 
            :max="9999"
            placeholder="新的排序值"
          />
        </FormItem>
      </Form>
    </Modal>
  </div>
</template>

<script>
import api from '../api'
import { formatDate } from '../utils/date'

export default {
  name: 'CategoryManagement',
  data() {
    return {
      loading: false,
      viewMode: 'tree', // tree | list
      
      // 分类数据
      categoryTree: [],
      categoryList: [],
      selectedCategory: null,
      selectedCategories: [],
      categoryStats: null,
      
      // 模态框
      categoryModal: false,
      moveModal: false,
      isEdit: false,
      
      // 表单数据
      categoryForm: {
        name: '',
        parent: null,
        sort_order: 0,
        is_enabled: true,
        description: ''
      },
      
      moveForm: {
        category_id: null,
        current_name: '',
        target_parent: null,
        new_sort_order: 0
      },
      
      // 父分类选项
      parentCategoryOptions: [],
      
      // 表格列定义
      columns: [
        {
          title: 'ID',
          key: 'id',
          width: 60
        },
        {
          title: '分类名称',
          key: 'name',
          minWidth: 150,
          render: (h, params) => {
            const level = params.row.level || 0
            const indent = level * 20
            return h('div', {
              style: {
                paddingLeft: `${indent}px`
              }
            }, [
              h('Icon', {
                props: {
                  type: 'ios-folder',
                  size: 16
                },
                style: {
                  marginRight: '8px',
                  color: '#2d8cf0'
                }
              }),
              params.row.name
            ])
          }
        },
        {
          title: '父分类',
          key: 'parent_name',
          width: 120,
          render: (h, params) => {
            return h('span', params.row.parent_name || '根分类')
          }
        },
        {
          title: '题目数',
          key: 'question_count',
          width: 80,
          sortable: true
        },
        {
          title: '排序',
          key: 'sort_order',
          width: 80,
          sortable: true
        },
        {
          title: '状态',
          key: 'is_enabled',
          width: 80,
          render: (h, params) => {
            return h('Tag', {
              props: {
                color: params.row.is_enabled ? 'success' : 'default'
              }
            }, params.row.is_enabled ? '启用' : '禁用')
          }
        },
        {
          title: '创建时间',
          key: 'create_time',
          width: 150,
          render: (h, params) => {
            return h('span', this.formatDate(params.row.create_time))
          }
        },
        {
          title: '操作',
          key: 'action',
          width: 150,
          render: (h, params) => {
            return h('div', [
              h('Button', {
                props: {
                  type: 'primary',
                  size: 'small'
                },
                style: {
                  marginRight: '5px'
                },
                on: {
                  click: () => {
                    this.editCategory(params.row)
                  }
                }
              }, '编辑'),
              h('Button', {
                props: {
                  type: 'error',
                  size: 'small'
                },
                on: {
                  click: () => {
                    this.deleteCategory(params.row)
                  }
                }
              }, '删除')
            ])
          }
        }
      ],
      
      // 表单验证规则
      categoryRules: {
        name: [
          { required: true, message: '请输入分类名称', trigger: 'blur' },
          { min: 1, max: 50, message: '分类名称长度在1到50个字符', trigger: 'blur' }
        ]
      }
    }
  },
  mounted() {
    this.init()
  },
  methods: {
    async init() {
      await this.loadCategories()
      await this.loadParentCategoryOptions()
    },
    
    async loadCategories() {
      this.loading = true
      try {
        const res = await api.getCategoryList()
        const categories = res.data.results || res.data
        
        // 构建树形结构
        this.categoryTree = this.buildCategoryTree(categories)
        
        // 构建列表结构（带层级信息）
        this.categoryList = this.buildCategoryList(categories)
      } catch (error) {
        this.$Message.error('加载分类失败')
      } finally {
        this.loading = false
      }
    },
    
    buildCategoryTree(categories) {
      const categoryMap = {}
      const rootCategories = []
      
      // 创建分类映射
      categories.forEach(category => {
        categoryMap[category.id] = {
          ...category,
          title: category.name,
          expand: true,
          children: []
        }
      })
      
      // 构建树形结构
      categories.forEach(category => {
        if (category.parent) {
          const parent = categoryMap[category.parent]
          if (parent) {
            parent.children.push(categoryMap[category.id])
          }
        } else {
          rootCategories.push(categoryMap[category.id])
        }
      })
      
      return rootCategories
    },

    buildCascaderOptions(categories) {
      const categoryMap = {}
      const rootOptions = []
      
      // 创建分类映射
      categories.forEach(category => {
        categoryMap[category.id] = {
          value: category.id,
          label: category.name,
          children: []
        }
      })
      
      // 构建树形结构
      categories.forEach(category => {
        if (category.parent) {
          const parent = categoryMap[category.parent]
          if (parent) {
            parent.children.push(categoryMap[category.id])
          }
        } else {
          rootOptions.push(categoryMap[category.id])
        }
      })
      
      return rootOptions
    },
    
    buildCategoryList(categories) {
      const categoryMap = {}
      const result = []
      
      // 创建分类映射
      categories.forEach(category => {
        categoryMap[category.id] = {
          ...category,
          children: []
        }
      })
      
      // 构建父子关系
      categories.forEach(category => {
        if (category.parent) {
          const parent = categoryMap[category.parent]
          if (parent) {
            parent.children.push(categoryMap[category.id])
          }
        }
      })
      
      // 递归展开为列表
      const flatten = (items, level = 0) => {
        items.forEach(item => {
          result.push({
            ...item,
            level
          })
          if (item.children && item.children.length > 0) {
            flatten(item.children, level + 1)
          }
        })
      }
      
      const rootCategories = categories.filter(c => !c.parent)
      flatten(rootCategories.map(c => categoryMap[c.id]))
      
      return result
    },
    
    async loadParentCategoryOptions() {
      // 加载父分类选项，用于级联选择器
      try {
        const res = await api.getCategoryList()
        this.parentCategoryOptions = this.buildCascaderOptions(res.data.results || res.data)
      } catch (error) {
        console.error('加载父分类选项失败:', error)
      }
    },
    
    buildCascaderOptions(categories) {
      const categoryMap = {}
      const rootOptions = []
      
      // 创建分类映射
      categories.forEach(category => {
        categoryMap[category.id] = {
          value: category.id,
          label: category.name,
          children: []
        }
      })
      
      // 构建层级结构
      categories.forEach(category => {
        if (category.parent) {
          const parent = categoryMap[category.parent]
          if (parent) {
            parent.children.push(categoryMap[category.id])
          }
        } else {
          rootOptions.push(categoryMap[category.id])
        }
      })
      
      return rootOptions
    },
    
    renderTreeNode(h, { root, node, data }) {
      return h('span', {
        style: {
          display: 'inline-block',
          width: '100%'
        }
      }, [
        h('span', [
          h('Icon', {
            props: {
              type: 'ios-folder',
              size: 16
            },
            style: {
              marginRight: '8px',
              color: '#2d8cf0'
            }
          }),
          h('span', data.title)
        ]),
        h('span', {
          style: {
            float: 'right',
            marginRight: '32px'
          }
        }, [
          h('Tag', {
            props: {
              color: data.is_enabled ? 'success' : 'default',
              size: 'small'
            }
          }, data.is_enabled ? '启用' : '禁用'),
          h('span', {
            style: {
              marginLeft: '8px',
              color: '#999'
            }
          }, `${data.question_count} 题`)
        ])
      ])
    },
    
    onTreeSelect(selectedKeys, { selected, selectedNodes, node, event }) {
      if (selectedNodes.length > 0) {
        this.selectedCategory = selectedNodes[0]
        this.loadCategoryStats(this.selectedCategory.id)
      }
    },
    
    onTreeCheck(checkedKeys, { checked, checkedNodes, node, event }) {
      this.selectedCategories = checkedNodes
    },
    
    onRowClick(row) {
      this.selectedCategory = row
      this.loadCategoryStats(row.id)
    },
    
    async loadCategoryStats(categoryId) {
      try {
        const res = await api.getCategoryStats(categoryId)
        this.categoryStats = res.data
      } catch (error) {
        console.error('加载分类统计失败:', error)
      }
    },
    
    showCreateModal() {
      this.isEdit = false
      this.categoryModal = true
      this.resetCategoryForm()
    },
    
    editCategory(category) {
      this.isEdit = true
      this.categoryModal = true
      this.categoryForm = {
        id: category.id,
        name: category.name,
        parent: category.parent,
        sort_order: category.sort_order,
        is_enabled: category.is_enabled,
        description: category.description || ''
      }
    },
    
    async submitCategory() {
      try {
        await this.$refs.categoryForm.validate()
        
        if (this.isEdit) {
          await api.updateCategory(this.categoryForm.id, this.categoryForm)
          this.$Message.success('分类更新成功')
        } else {
          await api.createCategory(this.categoryForm)
          this.$Message.success('分类创建成功')
        }
        
        this.categoryModal = false
        this.loadCategories()
      } catch (error) {
        if (error.fields) {
          // 表单验证错误
          return false
        }
        this.$Message.error(this.isEdit ? '分类更新失败' : '分类创建失败')
      }
    },
    
    resetCategoryForm() {
      this.categoryForm = {
        name: '',
        parent: null,
        sort_order: 0,
        is_enabled: true,
        description: ''
      }
      if (this.$refs.categoryForm) {
        this.$refs.categoryForm.resetFields()
      }
    },
    
    moveCategory(category) {
      this.moveForm = {
        category_id: category.id,
        current_name: category.name,
        target_parent: category.parent,
        new_sort_order: category.sort_order
      }
      this.moveModal = true
    },
    
    async submitMove() {
      try {
        await api.updateCategory(this.moveForm.category_id, {
          parent: this.moveForm.target_parent,
          sort_order: this.moveForm.new_sort_order
        })
        
        this.$Message.success('分类移动成功')
        this.moveModal = false
        this.loadCategories()
      } catch (error) {
        this.$Message.error('分类移动失败')
      }
    },
    
    resetMoveForm() {
      this.moveForm = {
        category_id: null,
        current_name: '',
        target_parent: null,
        new_sort_order: 0
      }
    },
    
    deleteCategory(category) {
      this.$Modal.confirm({
        title: '确认删除',
        content: `确定要删除分类 "${category.name}" 吗？此操作不可恢复。`,
        onOk: async () => {
          try {
            await api.deleteCategory(category.id)
            this.$Message.success('分类删除成功')
            this.loadCategories()
            if (this.selectedCategory && this.selectedCategory.id === category.id) {
              this.selectedCategory = null
              this.categoryStats = null
            }
          } catch (error) {
            this.$Message.error('分类删除失败')
          }
        }
      })
    },
    
    batchEnable() {
      this.batchUpdateStatus(true)
    },
    
    batchDisable() {
      this.batchUpdateStatus(false)
    },
    
    async batchUpdateStatus(enabled) {
      const action = enabled ? '启用' : '禁用'
      this.$Modal.confirm({
        title: `批量${action}`,
        content: `确定要${action}选中的 ${this.selectedCategories.length} 个分类吗？`,
        onOk: async () => {
          try {
            const categoryIds = this.selectedCategories.map(c => c.id)
            await api.batchUpdateCategories({
              category_ids: categoryIds,
              is_enabled: enabled
            })
            
            this.$Message.success(`批量${action}成功`)
            this.selectedCategories = []
            this.loadCategories()
          } catch (error) {
            this.$Message.error(`批量${action}失败`)
          }
        }
      })
    },
    
    batchMove() {
      // 实现批量移动逻辑
      this.$Message.info('批量移动功能开发中')
    },
    
    batchDelete() {
      this.$Modal.confirm({
        title: '批量删除',
        content: `确定要删除选中的 ${this.selectedCategories.length} 个分类吗？此操作不可恢复。`,
        onOk: async () => {
          try {
            const categoryIds = this.selectedCategories.map(c => c.id)
            await api.batchDeleteCategories({ category_ids: categoryIds })
            
            this.$Message.success('批量删除成功')
            this.selectedCategories = []
            this.loadCategories()
          } catch (error) {
            this.$Message.error('批量删除失败')
          }
        }
      })
    },
    
    refresh() {
      this.selectedCategory = null
      this.selectedCategories = []
      this.categoryStats = null
      this.loadCategories()
    },

    loadParentCategories(item, callback) {
      // 动态加载父分类选项
      setTimeout(() => {
        const children = this.categoryTree
          .filter(cat => cat.parent === item.value)
          .map(cat => ({
            value: cat.id,
            label: cat.name,
            loading: false
          }))
        callback(children)
      }, 100)
    },

    formatDate(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.category-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.tree-view {
  min-height: 400px;
}

.list-view {
  min-height: 400px;
}

.detail-panel {
  margin-top: 20px;
}

.detail-item {
  margin-bottom: 12px;
  display: flex;
  align-items: flex-start;
}

.detail-item label {
  font-weight: bold;
  color: #666;
  min-width: 80px;
  margin-right: 8px;
}

.description {
  flex: 1;
  padding: 8px;
  background: #f8f8f9;
  border-radius: 4px;
  color: #666;
  line-height: 1.5;
}

.category-stats {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e8eaec;
}

.category-stats h4 {
  margin-bottom: 16px;
  color: #333;
}

.batch-panel {
  margin-top: 20px;
}

.batch-actions {
  display: flex;
  gap: 8px;
}
</style>