<template>
  <div class="statistics-chart">
    <div class="chart-header">
      <h4>
        <Icon type="ios-analytics" />
        {{ title }}
      </h4>
      <div class="chart-controls" v-if="showControls">
        <ButtonGroup size="small">
          <Button 
            v-for="type in chartTypes" 
            :key="type.value"
            :type="currentChartType === type.value ? 'primary' : 'default'"
            @click="changeChartType(type.value)"
          >
            <Icon :type="type.icon" />
            {{ type.label }}
          </Button>
        </ButtonGroup>
      </div>
    </div>
    
    <div class="chart-content">
      <!-- 概览卡片 -->>
      <div class="overview-cards" v-if="showOverview">
        <div class="stat-card" v-for="stat in overviewStats" :key="stat.key">
          <div class="stat-icon" :style="{ backgroundColor: stat.color }">
            <Icon :type="stat.icon" color="#fff" size="20" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
          <div class="stat-trend" v-if="stat.trend">
            <Icon 
              :type="stat.trend > 0 ? 'ios-trending-up' : 'ios-trending-down'" 
              :color="stat.trend > 0 ? '#19be6b' : '#ed4014'"
              size="16"
            />
            <span :style="{ color: stat.trend > 0 ? '#19be6b' : '#ed4014' }">
              {{ Math.abs(stat.trend) }}%
            </span>
          </div>
        </div>
      </div>
      
      <!-- 图表容器 -->>
      <div class="chart-container">
        <!-- 饼图 -->>
        <div v-if="currentChartType === 'pie'" class="pie-chart">
          <div class="chart-wrapper">
            <div ref="pieChart" class="chart-canvas"></div>
          </div>
          <div class="chart-legend">
            <div 
              v-for="(item, index) in pieData" 
              :key="index"
              class="legend-item"
            >
              <div class="legend-color" :style="{ backgroundColor: item.color }"></div>
              <span class="legend-label">{{ item.name }}</span>
              <span class="legend-value">{{ item.value }}</span>
              <span class="legend-percent">({{ item.percent }}%)</span>
            </div>
          </div>
        </div>
        
        <!-- 柱状图 -->>
        <div v-if="currentChartType === 'bar'" class="bar-chart">
          <div ref="barChart" class="chart-canvas"></div>
        </div>
        
        <!-- 折线图 -->>
        <div v-if="currentChartType === 'line'" class="line-chart">
          <div ref="lineChart" class="chart-canvas"></div>
        </div>
        
        <!-- 表格视图 -->>
        <div v-if="currentChartType === 'table'" class="table-view">
          <Table 
            :columns="tableColumns"
            :data="tableData"
            size="small"
            :show-header="true"
          />
        </div>
      </div>
      
      <!-- 加载状态 -->>
      <div v-if="loading" class="loading-state">
        <Spin size="large">
          <Icon type="ios-loading" size="18" class="spin-icon" />
          <div>加载统计数据中...</div>
        </Spin>
      </div>
      
      <!-- 空状态 -->>
      <div v-if="!loading && isEmpty" class="empty-state">
        <Icon type="ios-stats" size="48" color="#c5c8ce" />
        <p>暂无统计数据</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatisticsChart',
  props: {
    title: {
      type: String,
      default: '统计图表'
    },
    data: {
      type: Object,
      default: () => ({})
    },
    chartType: {
      type: String,
      default: 'pie'
    },
    showControls: {
      type: Boolean,
      default: true
    },
    showOverview: {
      type: Boolean,
      default: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      currentChartType: this.chartType,
      chartTypes: [
        { value: 'pie', label: '饼图', icon: 'ios-pie' },
        { value: 'bar', label: '柱状图', icon: 'ios-stats' },
        { value: 'line', label: '折线图', icon: 'ios-trending-up' },
        { value: 'table', label: '表格', icon: 'ios-list' }
      ],
      colors: ['#2d8cf0', '#19be6b', '#ff9900', '#ed4014', '#9b59b6', '#1abc9c', '#34495e', '#f39c12']
    }
  },
  
  computed: {
    isEmpty() {
      return !this.data || Object.keys(this.data).length === 0
    },
    
    overviewStats() {
      if (!this.data.overview) return []
      
      return [
        {
          key: 'total',
          label: '总题目数',
          value: this.data.overview.total || 0,
          icon: 'ios-document',
          color: '#2d8cf0',
          trend: this.data.overview.totalTrend
        },
        {
          key: 'answered',
          label: '已答题目',
          value: this.data.overview.answered || 0,
          icon: 'ios-checkmark-circle',
          color: '#19be6b',
          trend: this.data.overview.answeredTrend
        },
        {
          key: 'correct',
          label: '答对题目',
          value: this.data.overview.correct || 0,
          icon: 'ios-thumbs-up',
          color: '#ff9900',
          trend: this.data.overview.correctTrend
        },
        {
          key: 'accuracy',
          label: '正确率',
          value: this.data.overview.accuracy ? `${this.data.overview.accuracy}%` : '0%',
          icon: 'ios-analytics',
          color: '#9b59b6',
          trend: this.data.overview.accuracyTrend
        }
      ]
    },
    
    pieData() {
      if (!this.data.pie) return []
      
      const total = this.data.pie.reduce((sum, item) => sum + item.value, 0)
      
      return this.data.pie.map((item, index) => ({
        ...item,
        color: this.colors[index % this.colors.length],
        percent: total > 0 ? Math.round((item.value / total) * 100) : 0
      }))
    },
    
    tableColumns() {
      if (!this.data.table || !this.data.table.columns) return []
      return this.data.table.columns
    },
    
    tableData() {
      if (!this.data.table || !this.data.table.data) return []
      return this.data.table.data
    }
  },
  
  watch: {
    data: {
      handler() {
        this.$nextTick(() => {
          this.renderChart()
        })
      },
      deep: true
    },
    
    currentChartType() {
      this.$nextTick(() => {
        this.renderChart()
      })
    }
  },
  
  mounted() {
    this.$nextTick(() => {
      this.renderChart()
    })
  },
  
  methods: {
    changeChartType(type) {
      this.currentChartType = type
      this.$emit('chart-type-change', type)
    },
    
    renderChart() {
      if (this.loading || this.isEmpty) return
      
      switch (this.currentChartType) {
        case 'pie':
          this.renderPieChart()
          break
        case 'bar':
          this.renderBarChart()
          break
        case 'line':
          this.renderLineChart()
          break
      }
    },
    
    renderPieChart() {
      // 简单的CSS饼图实现
      const container = this.$refs.pieChart
      if (!container || !this.pieData.length) return
      
      container.innerHTML = ''
      
      // 创建饼图
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
      svg.setAttribute('width', '200')
      svg.setAttribute('height', '200')
      svg.setAttribute('viewBox', '0 0 200 200')
      
      let currentAngle = 0
      const centerX = 100
      const centerY = 100
      const radius = 80
      
      this.pieData.forEach((item, index) => {
        const angle = (item.percent / 100) * 360
        const startAngle = currentAngle
        const endAngle = currentAngle + angle
        
        const x1 = centerX + radius * Math.cos((startAngle * Math.PI) / 180)
        const y1 = centerY + radius * Math.sin((startAngle * Math.PI) / 180)
        const x2 = centerX + radius * Math.cos((endAngle * Math.PI) / 180)
        const y2 = centerY + radius * Math.sin((endAngle * Math.PI) / 180)
        
        const largeArcFlag = angle > 180 ? 1 : 0
        
        const pathData = [
          `M ${centerX} ${centerY}`,
          `L ${x1} ${y1}`,
          `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
          'Z'
        ].join(' ')
        
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
        path.setAttribute('d', pathData)
        path.setAttribute('fill', item.color)
        path.setAttribute('stroke', '#fff')
        path.setAttribute('stroke-width', '2')
        
        svg.appendChild(path)
        currentAngle += angle
      })
      
      container.appendChild(svg)
    },
    
    renderBarChart() {
      // 简单的CSS柱状图实现
      const container = this.$refs.barChart
      if (!container || !this.data.bar) return
      
      container.innerHTML = ''
      
      const chartDiv = document.createElement('div')
      chartDiv.className = 'simple-bar-chart'
      
      const maxValue = Math.max(...this.data.bar.map(item => item.value))
      
      this.data.bar.forEach((item, index) => {
        const barContainer = document.createElement('div')
        barContainer.className = 'bar-container'
        
        const bar = document.createElement('div')
        bar.className = 'bar'
        bar.style.height = `${(item.value / maxValue) * 100}%`
        bar.style.backgroundColor = this.colors[index % this.colors.length]
        
        const label = document.createElement('div')
        label.className = 'bar-label'
        label.textContent = item.name
        
        const value = document.createElement('div')
        value.className = 'bar-value'
        value.textContent = item.value
        
        barContainer.appendChild(bar)
        barContainer.appendChild(label)
        barContainer.appendChild(value)
        chartDiv.appendChild(barContainer)
      })
      
      container.appendChild(chartDiv)
    },
    
    renderLineChart() {
      // 简单的CSS折线图实现
      const container = this.$refs.lineChart
      if (!container || !this.data.line) return
      
      container.innerHTML = ''
      
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
      svg.setAttribute('width', '100%')
      svg.setAttribute('height', '200')
      svg.setAttribute('viewBox', '0 0 400 200')
      
      const data = this.data.line
      const maxValue = Math.max(...data.map(item => item.value))
      const stepX = 380 / (data.length - 1)
      
      let pathData = ''
      
      data.forEach((item, index) => {
        const x = 10 + index * stepX
        const y = 180 - (item.value / maxValue) * 160
        
        if (index === 0) {
          pathData += `M ${x} ${y}`
        } else {
          pathData += ` L ${x} ${y}`
        }
        
        // 添加数据点
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
        circle.setAttribute('cx', x)
        circle.setAttribute('cy', y)
        circle.setAttribute('r', '4')
        circle.setAttribute('fill', '#2d8cf0')
        svg.appendChild(circle)
      })
      
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
      path.setAttribute('d', pathData)
      path.setAttribute('stroke', '#2d8cf0')
      path.setAttribute('stroke-width', '2')
      path.setAttribute('fill', 'none')
      
      svg.appendChild(path)
      container.appendChild(svg)
    }
  }
}
</script>

<style scoped>
.statistics-chart {
  background: #fff;
  border: 1px solid #e8eaec;
  border-radius: 8px;
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f8f9;
  border-bottom: 1px solid #e8eaec;
}

.chart-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #17233d;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-content {
  padding: 20px;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #17233d;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: #808695;
  margin-top: 4px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.chart-container {
  min-height: 300px;
}

.pie-chart {
  display: flex;
  align-items: center;
  gap: 40px;
}

.chart-wrapper {
  flex-shrink: 0;
}

.chart-canvas {
  width: 200px;
  height: 200px;
}

.chart-legend {
  flex: 1;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-label {
  flex: 1;
  color: #17233d;
}

.legend-value {
  font-weight: 600;
  color: #2d8cf0;
}

.legend-percent {
  color: #808695;
}

/* 简单柱状图样式 */
.simple-bar-chart {
  display: flex;
  align-items: end;
  gap: 16px;
  height: 200px;
  padding: 20px 0;
}

.bar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  height: 100%;
}

.bar {
  width: 40px;
  min-height: 4px;
  border-radius: 2px 2px 0 0;
  margin-bottom: 8px;
}

.bar-label {
  font-size: 12px;
  color: #808695;
  text-align: center;
  margin-bottom: 4px;
}

.bar-value {
  font-size: 14px;
  font-weight: 600;
  color: #17233d;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #808695;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #c5c8ce;
}

.empty-state p {
  margin: 12px 0 0 0;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .overview-cards {
    grid-template-columns: 1fr;
  }
  
  .pie-chart {
    flex-direction: column;
    gap: 20px;
  }
  
  .simple-bar-chart {
    gap: 8px;
  }
  
  .bar {
    width: 30px;
  }
}
</style>