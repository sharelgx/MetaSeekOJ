import { mount, createLocalVue } from '@vue/test-utils'
import VueRouter from 'vue-router'
import Vuex from 'vuex'
import ElementUI from 'element-ui'
import Practice from '@/views/Practice.vue'

const localVue = createLocalVue()
localVue.use(VueRouter)
localVue.use(Vuex)
localVue.use(ElementUI)

describe('Practice.vue', () => {
  let wrapper
  let store
  let router
  let actions
  let getters
  let mutations

  const mockQuestions = [
    {
      id: 1,
      title: '1+1等于多少？',
      content: '请选择正确答案',
      question_type: 'single',
      options: ['1', '2', '3', '4'],
      correct_answer: [1],
      difficulty: 'easy',
      score: 10,
      category: { id: 1, name: '数学' }
    },
    {
      id: 2,
      title: '2+2等于多少？',
      content: '请选择正确答案',
      question_type: 'single',
      options: ['2', '3', '4', '5'],
      correct_answer: [2],
      difficulty: 'easy',
      score: 10,
      category: { id: 1, name: '数学' }
    }
  ]

  const mockCategories = [
    { id: 1, name: '数学', description: '数学相关题目' },
    { id: 2, name: '物理', description: '物理相关题目' }
  ]

  beforeEach(() => {
    actions = {
      getQuestions: jest.fn().mockResolvedValue({
        results: mockQuestions,
        count: 2
      }),
      getCategories: jest.fn().mockResolvedValue(mockCategories),
      submitAnswer: jest.fn().mockResolvedValue({
        is_correct: true,
        score: 10
      }),
      generatePracticeSet: jest.fn().mockResolvedValue(mockQuestions)
    }

    getters = {
      questions: () => mockQuestions,
      categories: () => mockCategories,
      loading: () => false,
      currentQuestion: () => mockQuestions[0]
    }

    mutations = {
      SET_CURRENT_QUESTION: jest.fn(),
      SET_PRACTICE_MODE: jest.fn(),
      RESET_PRACTICE: jest.fn()
    }

    store = new Vuex.Store({
      modules: {
        choiceQuestion: {
          namespaced: true,
          actions,
          getters,
          mutations
        }
      }
    })

    router = new VueRouter({
      routes: [
        { path: '/practice', name: 'Practice' },
        { path: '/practice/:id', name: 'PracticeQuestion' }
      ]
    })

    wrapper = mount(Practice, {
      localVue,
      store,
      router
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.practice-page').exists()).toBe(true)
  })

  it('loads questions on mount', () => {
    expect(actions.getQuestions).toHaveBeenCalled()
    expect(actions.getCategories).toHaveBeenCalled()
  })

  it('displays practice mode selection', () => {
    expect(wrapper.find('.practice-modes').exists()).toBe(true)
    expect(wrapper.find('.mode-random').exists()).toBe(true)
    expect(wrapper.find('.mode-category').exists()).toBe(true)
    expect(wrapper.find('.mode-difficulty').exists()).toBe(true)
  })

  it('handles random practice mode', async () => {
    const randomModeButton = wrapper.find('.mode-random')
    await randomModeButton.trigger('click')

    expect(wrapper.vm.practiceMode).toBe('random')
    expect(actions.generatePracticeSet).toHaveBeenCalledWith(
      expect.any(Object),
      { mode: 'random', count: 10 }
    )
  })

  it('handles category practice mode', async () => {
    const categoryModeButton = wrapper.find('.mode-category')
    await categoryModeButton.trigger('click')

    await wrapper.vm.$nextTick()

    expect(wrapper.vm.practiceMode).toBe('category')
    expect(wrapper.find('.category-selector').exists()).toBe(true)
  })

  it('handles difficulty practice mode', async () => {
    const difficultyModeButton = wrapper.find('.mode-difficulty')
    await difficultyModeButton.trigger('click')

    await wrapper.vm.$nextTick()

    expect(wrapper.vm.practiceMode).toBe('difficulty')
    expect(wrapper.find('.difficulty-selector').exists()).toBe(true)
  })

  it('starts practice session', async () => {
    wrapper.vm.practiceMode = 'random'
    wrapper.vm.practiceCount = 5

    const startButton = wrapper.find('.start-practice-btn')
    await startButton.trigger('click')

    expect(wrapper.vm.practiceStarted).toBe(true)
    expect(wrapper.vm.currentQuestionIndex).toBe(0)
    expect(wrapper.find('.question-container').exists()).toBe(true)
  })

  it('navigates between questions', async () => {
    wrapper.vm.practiceStarted = true
    wrapper.vm.practiceQuestions = mockQuestions
    wrapper.vm.currentQuestionIndex = 0

    await wrapper.vm.$nextTick()

    const nextButton = wrapper.find('.next-question-btn')
    await nextButton.trigger('click')

    expect(wrapper.vm.currentQuestionIndex).toBe(1)
  })

  it('handles previous question navigation', async () => {
    wrapper.vm.practiceStarted = true
    wrapper.vm.practiceQuestions = mockQuestions
    wrapper.vm.currentQuestionIndex = 1

    await wrapper.vm.$nextTick()

    const prevButton = wrapper.find('.prev-question-btn')
    await prevButton.trigger('click')

    expect(wrapper.vm.currentQuestionIndex).toBe(0)
  })

  it('disables previous button on first question', async () => {
    wrapper.vm.practiceStarted = true
    wrapper.vm.currentQuestionIndex = 0

    await wrapper.vm.$nextTick()

    const prevButton = wrapper.find('.prev-question-btn')
    expect(prevButton.attributes('disabled')).toBeDefined()
  })

  it('disables next button on last question', async () => {
    wrapper.vm.practiceStarted = true
    wrapper.vm.practiceQuestions = mockQuestions
    wrapper.vm.currentQuestionIndex = mockQuestions.length - 1

    await wrapper.vm.$nextTick()

    const nextButton = wrapper.find('.next-question-btn')
    expect(nextButton.attributes('disabled')).toBeDefined()
  })

  it('shows finish button on last question', async () => {
    wrapper.vm.practiceStarted = true
    wrapper.vm.practiceQuestions = mockQuestions
    wrapper.vm.currentQuestionIndex = mockQuestions.length - 1

    await wrapper.vm.$nextTick()

    expect(wrapper.find('.finish-practice-btn').exists()).toBe(true)
  })

  it('tracks practice progress', () => {
    wrapper.vm.practiceQuestions = mockQuestions
    wrapper.vm.currentQuestionIndex = 1
    wrapper.vm.answeredQuestions = [0]

    const progress = wrapper.vm.practiceProgress
    expect(progress.current).toBe(2)
    expect(progress.total).toBe(2)
    expect(progress.answered).toBe(1)
    expect(progress.percentage).toBe(100)
  })

  it('handles answer submission', async () => {
    wrapper.vm.practiceStarted = true
    wrapper.vm.practiceQuestions = mockQuestions
    wrapper.vm.currentQuestionIndex = 0

    await wrapper.vm.handleAnswerSubmitted({
      questionId: 1,
      userAnswer: [1],
      result: { is_correct: true, score: 10 }
    })

    expect(wrapper.vm.answeredQuestions).toContain(0)
    expect(wrapper.vm.practiceResults[0]).toEqual({
      questionId: 1,
      userAnswer: [1],
      result: { is_correct: true, score: 10 }
    })
  })

  it('calculates practice statistics', () => {
    wrapper.vm.practiceResults = [
      { result: { is_correct: true, score: 10 } },
      { result: { is_correct: false, score: 0 } },
      { result: { is_correct: true, score: 15 } }
    ]

    const stats = wrapper.vm.practiceStatistics
    expect(stats.totalQuestions).toBe(3)
    expect(stats.correctCount).toBe(2)
    expect(stats.incorrectCount).toBe(1)
    expect(stats.totalScore).toBe(25)
    expect(stats.accuracy).toBe(66.67)
  })

  it('finishes practice session', async () => {
    wrapper.vm.practiceStarted = true
    wrapper.vm.practiceResults = [
      { result: { is_correct: true, score: 10 } },
      { result: { is_correct: false, score: 0 } }
    ]

    const finishButton = wrapper.find('.finish-practice-btn')
    await finishButton.trigger('click')

    expect(wrapper.vm.practiceFinished).toBe(true)
    expect(wrapper.find('.practice-summary').exists()).toBe(true)
  })

  it('shows practice summary', async () => {
    wrapper.vm.practiceFinished = true
    wrapper.vm.practiceResults = [
      { result: { is_correct: true, score: 10 } },
      { result: { is_correct: false, score: 0 } }
    ]

    await wrapper.vm.$nextTick()

    expect(wrapper.find('.practice-summary').exists()).toBe(true)
    expect(wrapper.find('.total-score').text()).toContain('10')
    expect(wrapper.find('.accuracy-rate').text()).toContain('50')
  })

  it('restarts practice', async () => {
    wrapper.vm.practiceFinished = true

    const restartButton = wrapper.find('.restart-practice-btn')
    await restartButton.trigger('click')

    expect(wrapper.vm.practiceStarted).toBe(false)
    expect(wrapper.vm.practiceFinished).toBe(false)
    expect(wrapper.vm.currentQuestionIndex).toBe(0)
    expect(wrapper.vm.practiceResults).toEqual([])
    expect(wrapper.vm.answeredQuestions).toEqual([])
  })

  it('handles practice settings', async () => {
    const settingsButton = wrapper.find('.practice-settings-btn')
    await settingsButton.trigger('click')

    expect(wrapper.vm.showSettings).toBe(true)
    expect(wrapper.find('.practice-settings').exists()).toBe(true)
  })

  it('validates practice configuration', () => {
    wrapper.vm.practiceMode = 'category'
    wrapper.vm.selectedCategory = null

    const isValid = wrapper.vm.validatePracticeConfig()
    expect(isValid).toBe(false)

    wrapper.vm.selectedCategory = 1
    const isValid2 = wrapper.vm.validatePracticeConfig()
    expect(isValid2).toBe(true)
  })

  it('handles empty question set', async () => {
    actions.generatePracticeSet.mockResolvedValueOnce([])

    wrapper.vm.practiceMode = 'random'
    await wrapper.vm.startPractice()

    expect(wrapper.find('.no-questions-message').exists()).toBe(true)
    expect(wrapper.vm.practiceStarted).toBe(false)
  })

  it('handles loading state', async () => {
    getters.loading = () => true

    wrapper = mount(Practice, {
      localVue,
      store,
      router
    })

    expect(wrapper.find('.loading-spinner').exists()).toBe(true)
  })

  it('handles error state', async () => {
    actions.getQuestions.mockRejectedValueOnce(new Error('网络错误'))

    wrapper = mount(Practice, {
      localVue,
      store,
      router
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.find('.error-message').exists()).toBe(true)
  })

  it('saves practice progress', () => {
    wrapper.vm.practiceResults = [
      { result: { is_correct: true, score: 10 } }
    ]

    wrapper.vm.savePracticeProgress()

    const savedProgress = JSON.parse(localStorage.getItem('practice_progress'))
    expect(savedProgress).toBeDefined()
    expect(savedProgress.results.length).toBe(1)
  })

  it('loads saved practice progress', () => {
    const savedProgress = {
      mode: 'random',
      results: [{ result: { is_correct: true, score: 10 } }],
      currentIndex: 1
    }
    localStorage.setItem('practice_progress', JSON.stringify(savedProgress))

    wrapper.vm.loadPracticeProgress()

    expect(wrapper.vm.practiceMode).toBe('random')
    expect(wrapper.vm.practiceResults.length).toBe(1)
    expect(wrapper.vm.currentQuestionIndex).toBe(1)
  })
})