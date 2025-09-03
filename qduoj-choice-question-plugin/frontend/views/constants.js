// 选择题相关常量定义

// 难度选择
export const DIFFICULTY_CHOICES = [
  { value: 'easy', label: '简单', color: 'success' },
  { value: 'medium', label: '中等', color: 'warning' },
  { value: 'hard', label: '困难', color: 'error' }
]

// 题型选择
export const QUESTION_TYPE_CHOICES = [
  { value: 'single', label: '单选题' },
  { value: 'multiple', label: '多选题' }
]

// 排序选项
export const ORDER_BY_CHOICES = [
  { value: '-create_time', label: '创建时间（新到旧）' },
  { value: 'create_time', label: '创建时间（旧到新）' },
  { value: 'difficulty', label: '难度（低到高）' },
  { value: '-difficulty', label: '难度（高到低）' },
  { value: 'score', label: '分值（低到高）' },
  { value: '-score', label: '分值（高到低）' }
]

// 默认标签颜色
export const DEFAULT_TAG_COLORS = [
  'blue', 'green', 'red', 'yellow', 'pink', 'magenta', 
  'volcano', 'orange', 'gold', 'lime', 'cyan', 'geekblue', 'purple'
]

// API 状态码
export const API_STATUS = {
  SUCCESS: 'success',
  ERROR: 'error'
}

// 分页配置
export const PAGINATION_CONFIG = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100]
}