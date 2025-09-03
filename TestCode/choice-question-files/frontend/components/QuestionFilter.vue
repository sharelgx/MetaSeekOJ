<template>
  <div class="question-filter">
    <Card :bordered="false" class="filter-card">
      <div class="filter-header">
        <div class="filter-title">
          <Icon type="ios-funnel" />
          <span>筛选条件</span>
        </div>
        <div class="filter-actions">
          <Button 
            type="text" 
            size="small" 
            @click="toggleExpanded"
            class="expand-btn"
          >
            <Icon :type="expanded ? 'ios-arrow-up' : 'ios-arrow-down'" />
            {{ expanded ? '收起' : '展开' }}
          </Button>
          <Button 
            type="text" 
            size="small" 
            @click="resetFilters"
            :disabled="!hasActiveFilters"
          >
            <Icon type="ios-refresh" />
            重置
          </Button>
        </div>
      </div>
      
      <div class="filter-content" v-show="expanded">
        <Row :gutter="16">
          <!-- 关键词搜索 -->
          <Col :xs="24" :sm="12" :md="8" :lg="6">
            <div class="filter-item">
              <label class="filter-label">关键词</label>
              <Input
                v-model="localFilters.keyword"
                placeholder="搜索题目标题或内容"
                clearable
                @on-change="handleFilterChange"
              >
                <Icon type="ios-search" slot="prefix" />
              </Input>
            </div>
          </Col>
          
          <!-- 分类筛选 -->
          <Col :xs="24" :sm="12" :md="8" :lg="6">
            <div class="filter-item">
              <label class="filter-label">分类</label>
              <Select
                v-model="localFilters.category"
                placeholder="选择分类"
                clearable
                @on-change="handleFilterChange"
              >
                <Option 
                  v-for="category in categories" 
                  :key="category.id" 
                  :value="category.id"
                >
                  {{ category.name }}
                </Option>
              </Select>
            </div>
          </Col>
          
          <!-- 标签筛选 -->
          <Col :xs="24" :sm="12" :md="8" :lg="6">
            <div class="filter-item">
              <label class="filter-label">标签</label>
              <Select
                v-model="localFilters.tags"
                placeholder="选择标签"
                multiple
                clearable
                @on-change="handleFilterChange"
              >
                <Option 
                  v-for="tag in tags" 
                  :key="tag.id" 
                  :value="tag.id"
                >
                  {{ tag.name }}
                </Option>
              </Select>
            </div>
          </Col>
          
          <!-- 难度筛选 -->
          <Col :xs="24" :sm="12" :md="8" :lg="6">
            <div class="filter-item">
              <label class="filter-label">难度</label>
              <Select
                v-model="localFilters.difficulty"
                placeholder="选择难度"
                clearable
                @on-change="handleFilterChange"
              >
                <Option 
                  v-for="difficulty in difficulties" 
                  :key="difficulty.value" 
                  :value="difficulty.value"
                >
                  <span :class="`difficulty-${difficulty.value}`">
                    {{ difficulty.label }}
                  </span>
                </Option>
              </Select>
            </div>
          </Col>
          
          <!-- 题型筛选 -->
          <Col :xs="24" :sm="12" :md="8" :lg="6">
            <div class="filter-item">
              <label class="filter-label">题型</label>
              <Select
                v-model="localFilters.questionType"
                placeholder="选择题型"
                clearable
                @on-change="handleFilterChange"
              >
                <Option 
                  v-for="type in questionTypes" 
                  :key="type.value" 
                  :value="type.value"
                >
                  {{ type.label }}
                </Option>
              </Select>
            </div>
          </Col>
          
          <!-- 分值范围 -->
          <Col :xs="24" :sm="12" :md="8" :lg="6">
            <div class="filter-item">
              <label class="filter-label">分值范围</label>
              <div class="score-range">
                <InputNumber
                  v-model="localFilters.minScore"
                  placeholder="最小值"
                  :min="0"
                  :max="localFilters.maxScore || 100"
                  size="small"
                  @on-change="handleFilterChange"
                />
                <span class="range-separator">-</span>
                <InputNumber
                  v-model="localFilters.maxScore"
                  placeholder="最大值"
                  :min="localFilters.minScore || 0"
                  :max="100"
                  size="small"
                  @on-change="handleFilterChange"
                />
              </div>
            </div>
          </Col>
          
          <!-- 状态筛选 -->
          <Col :xs="24" :sm="12" :md="8" :lg="6">
            <div class="filter-item">
              <label class="filter-label">答题状态</label>
              <Select
                v-model="localFilters.status"
                placeholder="选择状态"
                clearable
                @on-change="handleFilterChange"
              >
                <Option value="unanswered">未答题</Option>
                <Option value="correct">答对</Option>
                <Option value="incorrect">答错</Option>
                <Option value="partial">部分正确</Option>
              </Select>
            </div>
          </Col>
          
          <!-- 公开性筛选 -->
          <Col :xs="24" :sm="12" :md="8" :lg="6">
            <div class="filter-item">
              <label class="filter-label">公开性</label>
              <RadioGroup 
                v-model="localFilters.visible" 
                @on-change="handleFilterChange"
                size="small"
              >
                <Radio :label="null">全部</Radio>
                <Radio :label="true">公开</Radio>
                <Radio :label="false">私有</Radio>
              </RadioGroup>
            </div>
          </Col>
        </Row>
        
        <!-- 高级筛选 -->
        <div class="advanced-filters" v-if="showAdvanced">
          <Divider orientation="left" size="small">高级筛选</Divider>
          
          <Row :gutter="16">
            <!-- 创建时间范围 -->
            <Col :xs="24" :sm="12" :md="8">
              <div class="filter-item">
                <label class="filter-label">创建时间</label>
                <DatePicker
                  v-model="localFilters.dateRange"
                  type="daterange"
                  placeholder="选择时间范围"
                  format="yyyy-MM-dd"
                  @on-change="handleFilterChange"
                  style="width: 100%"
                />
              </div>
            </Col>
            
            <!-- 答题人数范围 -->
            <Col :xs="24" :sm="12" :md="8">
              <div class="filter-item">
                <label class="filter-label">答题人数</label>
                <div class="score-range">
                  <InputNumber
                    v-model="localFilters.minAnswerCount"
                    placeholder="最小人数"
                    :min="0"
                    size="small"
                    @on-change="handleFilterChange"
                  />
                  <span class="range-separator">-</span>
                  <InputNumber
                    v-model="localFilters.maxAnswerCount"
                    placeholder="最大人数"
                    :min="localFilters.minAnswerCount || 0"
                    size="small"
                    @on-change="handleFilterChange"
                  />
                </div>
              </div>
            </Col>
            
            <!-- 正确率范围 -->
            <Col :xs="24" :sm="12" :md="8">
              <div class="filter-item">
                <label class="filter-label">正确率 (%)</label>
                <Slider
                  v-model="localFilters.accuracyRange"
                  range
                  :min="0"
                  :max="100"
                  :step="5"
                  show-input
                  @on-change="handleFilterChange"
                />
              </div>
            </Col>
          </Row>
        </div>
        
        <!-- 筛选操作按钮 -->
        <div class="filter-footer">
          <div class="filter-summary">
            <span v-if="hasActiveFilters" class="active-filters-count">
              已应用 {{ activeFiltersCount }} 个筛选条件
            </span>
          </div>
          
          <div class="filter-buttons">
            <Button 
              type="text" 
              size="small" 
              @click="toggleAdvanced"
            >
              <Icon :type="showAdvanced ? 'ios-arrow-up' : 'ios-arrow-down'" />
              {{ showAdvanced ? '收起高级筛选' : '展开高级筛选' }}
            </Button>
            
            <Button 
              type="primary" 
              size="small" 
              @click="applyFilters"
              :loading="applying"
            >
              <Icon type="ios-search" />
              应用筛选
            </Button>
          </div>
        </div>
      </div>
    </Card>
    
    <!-- 活跃筛选条件标签 -->
    <div class="active-filters" v-if="hasActiveFilters && !expanded">
      <div class="active-filters-header">
        <span>当前筛选:</span>
        <Button type="text" size="small" @click="resetFilters">
          <Icon type="ios-close" />
          清除全部
        </Button>
      </div>
      
      <div class="filter-tags">
        <Tag 
          v-for="filter in activeFilterTags" 
          :key="filter.key"
          closable
          @on-close="removeFilter(filter.key)"
          :color="filter.color"
        >
          {{ filter.label }}: {{ filter.value }}
        </Tag>
      </div>
    </div>
  </div>
</template>

<script>
import utils from '@/utils/utils'
const { debounce } = utils

export default {
  name: 'QuestionFilter',
  
  props: {
    filters: {
      type: Object,
      default: () => ({})
    },
    categories: {
      type: Array,
      default: () => []
    },
    tags: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    autoApply: {
      type: Boolean,
      default: true
    }
  },
  
  data() {
    return {
      expanded: false,
      showAdvanced: false,
      applying: false,
      
      localFilters: {
        keyword: '',
        category: null,
        tags: [],
        difficulty: null,
        questionType: null,
        minScore: null,
        maxScore: null,
        status: null,
        visible: null,
        dateRange: [],
        minAnswerCount: null,
        maxAnswerCount: null,
        accuracyRange: [0, 100]
      },
      
      difficulties: [
        { value: 'Low', label: '简单' },
        { value: 'Mid', label: '中等' },
        { value: 'High', label: '困难' }
      ],
      
      questionTypes: [
        { value: 'single', label: '单选题' },
        { value: 'multiple', label: '多选题' },
        { value: 'judge', label: '判断题' },
        { value: 'fill', label: '填空题' }
      ]
    }
  },
  
  computed: {
    hasActiveFilters() {
      return this.activeFiltersCount > 0
    },
    
    activeFiltersCount() {
      let count = 0
      
      if (this.localFilters.keyword) count++
      if (this.localFilters.category) count++
      if (this.localFilters.tags && this.localFilters.tags.length) count++
      if (this.localFilters.difficulty) count++
      if (this.localFilters.questionType) count++
      if (this.localFilters.minScore !== null || this.localFilters.maxScore !== null) count++
      if (this.localFilters.status) count++
      if (this.localFilters.visible !== null) count++
      if (this.localFilters.dateRange && this.localFilters.dateRange.length) count++
      if (this.localFilters.minAnswerCount !== null || this.localFilters.maxAnswerCount !== null) count++
      if (this.localFilters.accuracyRange[0] > 0 || this.localFilters.accuracyRange[1] < 100) count++
      
      return count
    },
    
    activeFilterTags() {
      const tags = []
      
      if (this.localFilters.keyword) {
        tags.push({
          key: 'keyword',
          label: '关键词',
          value: this.localFilters.keyword,
          color: 'blue'
        })
      }
      
      if (this.localFilters.category) {
        const category = this.categories.find(c => c.id === this.localFilters.category)
        tags.push({
          key: 'category',
          label: '分类',
          value: category ? category.name : this.localFilters.category,
          color: 'green'
        })
      }
      
      if (this.localFilters.tags && this.localFilters.tags.length) {
        const tagNames = this.localFilters.tags.map(tagId => {
          const tag = this.tags.find(t => t.id === tagId)
          return tag ? tag.name : tagId
        }).join(', ')
        
        tags.push({
          key: 'tags',
          label: '标签',
          value: tagNames,
          color: 'purple'
        })
      }
      
      if (this.localFilters.difficulty) {
        const difficulty = this.difficulties.find(d => d.value === this.localFilters.difficulty)
        tags.push({
          key: 'difficulty',
          label: '难度',
          value: difficulty ? difficulty.label : this.localFilters.difficulty,
          color: 'orange'
        })
      }
      
      if (this.localFilters.questionType) {
        const type = this.questionTypes.find(t => t.value === this.localFilters.questionType)
        tags.push({
          key: 'questionType',
          label: '题型',
          value: type ? type.label : this.localFilters.questionType,
          color: 'cyan'
        })
      }
      
      return tags
    }
  },
  
  watch: {
    filters: {
      handler(newFilters) {
        this.localFilters = { ...this.localFilters, ...newFilters }
      },
      deep: true,
      immediate: true
    }
  },
  
  created() {
    // 创建防抖的筛选处理函数
    this.debouncedFilterChange = debounce(this.emitFilterChange, 500)
  },
  
  methods: {
    toggleExpanded() {
      this.expanded = !this.expanded
    },
    
    toggleAdvanced() {
      this.showAdvanced = !this.showAdvanced
    },
    
    handleFilterChange() {
      if (this.autoApply) {
        this.debouncedFilterChange()
      }
    },
    
    emitFilterChange() {
      this.$emit('filter-change', { ...this.localFilters })
    },
    
    applyFilters() {
      this.applying = true
      
      setTimeout(() => {
        this.emitFilterChange()
        this.applying = false
      }, 300)
    },
    
    resetFilters() {
      this.localFilters = {
        keyword: '',
        category: null,
        tags: [],
        difficulty: null,
        questionType: null,
        minScore: null,
        maxScore: null,
        status: null,
        visible: null,
        dateRange: [],
        minAnswerCount: null,
        maxAnswerCount: null,
        accuracyRange: [0, 100]
      }
      
      this.emitFilterChange()
      this.$emit('filter-reset')
    },
    
    removeFilter(key) {
      switch (key) {
        case 'keyword':
          this.localFilters.keyword = ''
          break
        case 'category':
          this.localFilters.category = null
          break
        case 'tags':
          this.localFilters.tags = []
          break
        case 'difficulty':
          this.localFilters.difficulty = null
          break
        case 'questionType':
          this.localFilters.questionType = null
          break
      }
      
      this.emitFilterChange()
    }
  }
}
</script>

<style scoped>
.question-filter {
  margin-bottom: 16px;
}

.filter-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.filter-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #17233d;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

.expand-btn {
  color: #2d8cf0;
}

.filter-content {
  padding: 20px 16px 16px;
}

.filter-item {
  margin-bottom: 16px;
}

.filter-label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #515a6e;
}

.score-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-separator {
  color: #c5c8ce;
  font-size: 12px;
}

.advanced-filters {
  margin-top: 20px;
  padding-top: 16px;
}

.filter-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.filter-summary {
  flex: 1;
}

.active-filters-count {
  font-size: 13px;
  color: #2d8cf0;
  font-weight: 500;
}

.filter-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
}

.active-filters {
  margin-top: 12px;
  padding: 12px 16px;
  background: #f8f8f9;
  border-radius: 6px;
  border: 1px solid #e8eaec;
}

.active-filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #515a6e;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 难度样式 */
.difficulty-Low {
  color: #19be6b;
}

.difficulty-Mid {
  color: #ff9900;
}

.difficulty-High {
  color: #ed4014;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .filter-footer {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .filter-buttons {
    justify-content: space-between;
  }
  
  .active-filters-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
}
</style>