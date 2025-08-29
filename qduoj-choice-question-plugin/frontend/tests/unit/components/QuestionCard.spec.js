import { mount, createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import ElementUI from 'element-ui'
import QuestionCard from '@/components/QuestionCard.vue'

const localVue = createLocalVue()
localVue.use(Vuex)
localVue.use(ElementUI)

describe('QuestionCard.vue', () => {
  let wrapper
  let store
  let actions

  const mockQuestion = {
    id: 1,
    title: '1+1等于多少？',
    content: '请选择正确答案',
    question_type: 'single',
    options: ['1', '2', '3', '4'],
    correct_answer: [1],
    difficulty: 'easy',
    score: 10,
    category: {
      id: 1,
      name: '数学'
    },
    tags: [
      { id: 1, name: '代数', color: '#FF5722' }
    ]
  }

  beforeEach(() => {
    actions = {
      submitAnswer: jest.fn().mockResolvedValue({
        is_correct: true,
        score: 10,
        correct_answer: [1]
      })
    }

    store = new Vuex.Store({
      modules: {
        choiceQuestion: {
          namespaced: true,
          actions
        }
      }
    })

    wrapper = mount(QuestionCard, {
      localVue,
      store,
      propsData: {
        question: mockQuestion,
        mode: 'practice'
      }
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.question-card').exists()).toBe(true)
    expect(wrapper.find('.question-title').text()).toBe('1+1等于多少？')
    expect(wrapper.find('.question-content').exists()).toBe(true)
  })

  it('displays question options', () => {
    const options = wrapper.findAll('.option-item')
    expect(options.length).toBe(4)
    expect(options.at(0).text()).toContain('1')
    expect(options.at(1).text()).toContain('2')
    expect(options.at(2).text()).toContain('3')
    expect(options.at(3).text()).toContain('4')
  })

  it('displays question metadata', () => {
    expect(wrapper.find('.difficulty').text()).toContain('简单')
    expect(wrapper.find('.score').text()).toContain('10')
    expect(wrapper.find('.category').text()).toContain('数学')
  })

  it('displays question tags', () => {
    const tags = wrapper.findAll('.question-tag')
    expect(tags.length).toBe(1)
    expect(tags.at(0).text()).toBe('代数')
  })

  it('handles single choice selection', async () => {
    const radioButton = wrapper.find('input[type="radio"][value="1"]')
    await radioButton.setChecked()

    expect(wrapper.vm.userAnswer).toEqual([1])
  })

  it('handles multiple choice selection', async () => {
    const multipleQuestion = {
      ...mockQuestion,
      question_type: 'multiple',
      correct_answer: [0, 2]
    }

    wrapper = mount(QuestionCard, {
      localVue,
      store,
      propsData: {
        question: multipleQuestion,
        mode: 'practice'
      }
    })

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    await checkboxes.at(0).setChecked()
    await checkboxes.at(2).setChecked()

    expect(wrapper.vm.userAnswer).toContain(0)
    expect(wrapper.vm.userAnswer).toContain(2)
  })

  it('submits answer correctly', async () => {
    wrapper.vm.userAnswer = [1]
    
    const submitButton = wrapper.find('.submit-btn')
    await submitButton.trigger('click')

    expect(actions.submitAnswer).toHaveBeenCalledWith(
      expect.any(Object),
      {
        questionId: 1,
        userAnswer: [1],
        timeSpent: expect.any(Number)
      }
    )
  })

  it('shows result after submission', async () => {
    wrapper.vm.userAnswer = [1]
    
    await wrapper.vm.submitAnswer()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.showResult).toBe(true)
    expect(wrapper.vm.result.is_correct).toBe(true)
    expect(wrapper.find('.result-section').exists()).toBe(true)
  })

  it('displays correct answer in result', async () => {
    wrapper.vm.userAnswer = [0] // 错误答案
    actions.submitAnswer.mockResolvedValueOnce({
      is_correct: false,
      score: 0,
      correct_answer: [1]
    })
    
    await wrapper.vm.submitAnswer()
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.correct-answer').exists()).toBe(true)
    expect(wrapper.find('.correct-answer').text()).toContain('正确答案')
  })

  it('tracks time spent', async () => {
    const startTime = Date.now()
    wrapper.vm.startTime = startTime
    
    // 模拟经过一些时间
    jest.spyOn(Date, 'now').mockReturnValue(startTime + 30000) // 30秒后
    
    await wrapper.vm.submitAnswer()
    
    expect(wrapper.vm.timeSpent).toBeGreaterThan(0)
  })

  it('prevents multiple submissions', async () => {
    wrapper.vm.userAnswer = [1]
    
    await wrapper.vm.submitAnswer()
    await wrapper.vm.submitAnswer() // 第二次提交
    
    expect(actions.submitAnswer).toHaveBeenCalledTimes(1)
  })

  it('validates answer before submission', async () => {
    // 没有选择答案
    wrapper.vm.userAnswer = []
    
    const submitButton = wrapper.find('.submit-btn')
    await submitButton.trigger('click')
    
    expect(actions.submitAnswer).not.toHaveBeenCalled()
    expect(wrapper.find('.error-message').exists()).toBe(true)
  })

  it('shows loading state during submission', async () => {
    wrapper.vm.userAnswer = [1]
    
    // 模拟异步提交
    const submitPromise = wrapper.vm.submitAnswer()
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.submitting).toBe(true)
    expect(wrapper.find('.submit-btn').attributes('loading')).toBeDefined()
    
    await submitPromise
    
    expect(wrapper.vm.submitting).toBe(false)
  })

  it('handles submission error', async () => {
    wrapper.vm.userAnswer = [1]
    actions.submitAnswer.mockRejectedValueOnce(new Error('网络错误'))
    
    await wrapper.vm.submitAnswer()
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.submitting).toBe(false)
    expect(wrapper.find('.error-message').exists()).toBe(true)
  })

  it('resets answer', async () => {
    wrapper.vm.userAnswer = [1]
    wrapper.vm.showResult = true
    
    const resetButton = wrapper.find('.reset-btn')
    await resetButton.trigger('click')
    
    expect(wrapper.vm.userAnswer).toEqual([])
    expect(wrapper.vm.showResult).toBe(false)
    expect(wrapper.vm.result).toBeNull()
  })

  it('shows explanation in review mode', async () => {
    const questionWithExplanation = {
      ...mockQuestion,
      explanation: '因为1+1=2，所以正确答案是选项B。'
    }

    wrapper = mount(QuestionCard, {
      localVue,
      store,
      propsData: {
        question: questionWithExplanation,
        mode: 'review'
      }
    })

    expect(wrapper.find('.explanation').exists()).toBe(true)
    expect(wrapper.find('.explanation').text()).toContain('因为1+1=2')
  })

  it('disables interaction in review mode', () => {
    wrapper = mount(QuestionCard, {
      localVue,
      store,
      propsData: {
        question: mockQuestion,
        mode: 'review'
      }
    })

    const radioButtons = wrapper.findAll('input[type="radio"]')
    radioButtons.wrappers.forEach(radio => {
      expect(radio.attributes('disabled')).toBeDefined()
    })

    expect(wrapper.find('.submit-btn').exists()).toBe(false)
  })

  it('emits events correctly', async () => {
    wrapper.vm.userAnswer = [1]
    
    await wrapper.vm.submitAnswer()
    
    expect(wrapper.emitted('answer-submitted')).toBeTruthy()
    expect(wrapper.emitted('answer-submitted')[0][0]).toEqual({
      questionId: 1,
      userAnswer: [1],
      result: expect.any(Object)
    })
  })

  it('formats time display correctly', () => {
    wrapper.vm.timeSpent = 125 // 2分5秒
    
    const formattedTime = wrapper.vm.formatTime(125)
    expect(formattedTime).toBe('2:05')
  })

  it('calculates progress correctly', () => {
    wrapper.vm.userAnswer = [1, 2] // 选择了2个选项
    
    const progress = wrapper.vm.getProgress()
    expect(progress).toBeGreaterThan(0)
  })
})