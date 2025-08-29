import { mount, createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import ElementUI from 'element-ui'
import QuestionEditor from '@/components/QuestionEditor.vue'

const localVue = createLocalVue()
localVue.use(Vuex)
localVue.use(ElementUI)

describe('QuestionEditor.vue', () => {
  let wrapper
  let store
  let actions
  let getters

  beforeEach(() => {
    actions = {
      getCategories: jest.fn(),
      getTags: jest.fn()
    }

    getters = {
      categories: () => [
        { id: 1, name: '数学', description: '数学相关题目' },
        { id: 2, name: '物理', description: '物理相关题目' }
      ],
      tags: () => [
        { id: 1, name: '代数', color: '#FF5722' },
        { id: 2, name: '几何', color: '#2196F3' }
      ]
    }

    store = new Vuex.Store({
      modules: {
        choiceQuestion: {
          namespaced: true,
          actions,
          getters
        }
      }
    })

    wrapper = mount(QuestionEditor, {
      localVue,
      store,
      propsData: {
        question: null,
        mode: 'create'
      }
    })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.question-editor').exists()).toBe(true)
  })

  it('initializes with default form data', () => {
    expect(wrapper.vm.form.title).toBe('')
    expect(wrapper.vm.form.content).toBe('')
    expect(wrapper.vm.form.question_type).toBe('single')
    expect(wrapper.vm.form.options).toEqual(['', '', '', ''])
    expect(wrapper.vm.form.correct_answer).toEqual([])
    expect(wrapper.vm.form.difficulty).toBe('easy')
    expect(wrapper.vm.form.score).toBe(10)
  })

  it('loads question data in edit mode', async () => {
    const question = {
      id: 1,
      title: '1+1等于多少？',
      content: '请选择正确答案',
      question_type: 'single',
      options: ['1', '2', '3', '4'],
      correct_answer: [1],
      difficulty: 'easy',
      score: 10,
      category: 1,
      tags: [1]
    }

    wrapper = mount(QuestionEditor, {
      localVue,
      store,
      propsData: {
        question,
        mode: 'edit'
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.vm.form.title).toBe('1+1等于多少？')
    expect(wrapper.vm.form.content).toBe('请选择正确答案')
    expect(wrapper.vm.form.options).toEqual(['1', '2', '3', '4'])
    expect(wrapper.vm.form.correct_answer).toEqual([1])
  })

  it('validates required fields', async () => {
    const submitButton = wrapper.find('.submit-btn')
    await submitButton.trigger('click')

    await wrapper.vm.$nextTick()

    // 检查表单验证
    expect(wrapper.vm.$refs.form.validate).toBeDefined()
  })

  it('adds new option', async () => {
    const addButton = wrapper.find('.add-option-btn')
    await addButton.trigger('click')

    expect(wrapper.vm.form.options.length).toBe(5)
    expect(wrapper.vm.form.options[4]).toBe('')
  })

  it('removes option', async () => {
    // 先添加一个选项
    wrapper.vm.form.options.push('新选项')
    await wrapper.vm.$nextTick()

    const removeButtons = wrapper.findAll('.remove-option-btn')
    await removeButtons.at(4).trigger('click')

    expect(wrapper.vm.form.options.length).toBe(4)
  })

  it('handles single choice selection', async () => {
    wrapper.vm.form.question_type = 'single'
    await wrapper.vm.$nextTick()

    const radioButton = wrapper.find('input[type="radio"][value="1"]')
    await radioButton.setChecked()

    expect(wrapper.vm.form.correct_answer).toEqual([1])
  })

  it('handles multiple choice selection', async () => {
    wrapper.vm.form.question_type = 'multiple'
    await wrapper.vm.$nextTick()

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    await checkboxes.at(0).setChecked()
    await checkboxes.at(2).setChecked()

    expect(wrapper.vm.form.correct_answer).toContain(0)
    expect(wrapper.vm.form.correct_answer).toContain(2)
  })

  it('validates minimum options count', () => {
    wrapper.vm.form.options = ['选项1', '选项2']
    
    const isValid = wrapper.vm.validateOptions()
    expect(isValid).toBe(false)
  })

  it('validates correct answer selection', () => {
    wrapper.vm.form.question_type = 'single'
    wrapper.vm.form.correct_answer = []
    
    const isValid = wrapper.vm.validateCorrectAnswer()
    expect(isValid).toBe(false)
  })

  it('emits save event with form data', async () => {
    wrapper.vm.form = {
      title: '测试题目',
      content: '测试内容',
      question_type: 'single',
      options: ['A', 'B', 'C', 'D'],
      correct_answer: [0],
      difficulty: 'easy',
      score: 10,
      category: 1,
      tags: [1]
    }

    await wrapper.vm.handleSave()

    expect(wrapper.emitted('save')).toBeTruthy()
    expect(wrapper.emitted('save')[0][0]).toEqual(wrapper.vm.form)
  })

  it('emits cancel event', async () => {
    const cancelButton = wrapper.find('.cancel-btn')
    await cancelButton.trigger('click')

    expect(wrapper.emitted('cancel')).toBeTruthy()
  })

  it('resets form data', () => {
    wrapper.vm.form.title = '测试标题'
    wrapper.vm.form.content = '测试内容'
    
    wrapper.vm.resetForm()
    
    expect(wrapper.vm.form.title).toBe('')
    expect(wrapper.vm.form.content).toBe('')
  })

  it('handles rich text editor changes', async () => {
    const richTextEditor = wrapper.find('.rich-text-editor')
    const newContent = '<p>新的题目内容</p>'
    
    await richTextEditor.vm.$emit('input', newContent)
    
    expect(wrapper.vm.form.content).toBe(newContent)
  })

  it('displays preview correctly', async () => {
    wrapper.vm.form = {
      title: '预览题目',
      content: '预览内容',
      question_type: 'single',
      options: ['选项A', '选项B', '选项C', '选项D'],
      correct_answer: [0]
    }

    const previewButton = wrapper.find('.preview-btn')
    await previewButton.trigger('click')

    await wrapper.vm.$nextTick()

    expect(wrapper.vm.showPreview).toBe(true)
    expect(wrapper.find('.question-preview').exists()).toBe(true)
  })

  it('handles category selection', async () => {
    const categorySelect = wrapper.find('.category-select')
    await categorySelect.vm.$emit('change', 2)

    expect(wrapper.vm.form.category).toBe(2)
  })

  it('handles tag selection', async () => {
    const tagSelect = wrapper.find('.tag-select')
    await tagSelect.vm.$emit('change', [1, 2])

    expect(wrapper.vm.form.tags).toEqual([1, 2])
  })

  it('validates score range', () => {
    wrapper.vm.form.score = -5
    const isValid = wrapper.vm.validateScore()
    expect(isValid).toBe(false)

    wrapper.vm.form.score = 150
    const isValid2 = wrapper.vm.validateScore()
    expect(isValid2).toBe(false)

    wrapper.vm.form.score = 50
    const isValid3 = wrapper.vm.validateScore()
    expect(isValid3).toBe(true)
  })
})