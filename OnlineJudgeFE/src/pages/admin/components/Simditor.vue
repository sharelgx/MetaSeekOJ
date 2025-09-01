<template>
  <textarea ref="editor"></textarea>
</template>

<script>
  import Simditor from 'tar-simditor'
  import 'tar-simditor/styles/simditor.css'
  import $ from 'jquery'
  import './simditor-file-upload'
  import 'tar-simditor-markdown'
  import 'tar-simditor-markdown/styles/simditor-markdown.css'
  import hljs from 'highlight.js'
  import 'highlight.js/styles/default.css'
  import katex from 'katex'
  import 'katex/dist/katex.min.css'

  export default {
    name: 'Simditor',
    props: {
      toolbar: {
        type: Array,
        default: () => ['title', 'bold', 'italic', 'underline', 'fontScale', 'color', 'ol', 'ul', '|', 'blockquote', 'code', 'link', 'table', 'image', 'uploadfile', 'hr', '|', 'indent', 'outdent', 'alignment', '|', 'markdown']
      },
      value: {
        type: String,
        default: ''
      }
    },
    data () {
      return {
        editor: null,
        currentValue: this.value
      }
    },
    mounted () {
      this.editor = new Simditor({
        textarea: this.$refs.editor,
        toolbar: this.toolbar,
        pasteImage: true,
        markdown: false,
        upload: {
          url: '/api/admin/upload_image/',
          params: null,
          fileKey: 'image',
          connectionCount: 3,
          leaveConfirm: this.$i18n.t('m.Uploading_is_in_progress')
        },
        allowedStyles: {
          span: ['color']
        },
        image: {
          defaultWidth: 200
        }
      })
      this.editor.on('valuechanged', (e, src) => {
        this.currentValue = this.editor.getValue()
        this.resizeImages()
        this.highlightCode()
        this.renderMath()
      })
      this.editor.on('decorate', (e, src) => {
        this.currentValue = this.editor.getValue()
        this.resizeImages()
        this.highlightCode()
        this.renderMath()
      })

      this.editor.setValue(this.value)
      // 初始化时调整已有图片尺寸和代码高亮
      this.$nextTick(() => {
        this.resizeImages()
        this.highlightCode()
        this.renderMath()
      })
    },
    methods: {
      resizeImages () {
        if (this.editor && this.editor.body) {
          const images = this.editor.body.find('img')
          images.each((index, img) => {
            const $img = $(img)
            if (!$img.attr('data-resized')) {
              // 设置图片最大宽度为400px，高度自适应
              $img.removeAttr('width') // 移除固定宽度
              $img.removeAttr('height') // 移除固定高度
              $img.css({
                'max-width': '400px',
                'width': 'auto',
                'height': 'auto' // 高度自适应
              })
              $img.attr('data-resized', 'true')
            }
          })
        }
      },
      highlightCode () {
        if (this.editor && this.editor.body) {
          const codeBlocks = this.editor.body.find('pre code')
          codeBlocks.each((index, block) => {
            const $block = $(block)
            if (!$block.attr('data-highlighted')) {
              try {
                // 使用新版本的highlight.js API
                if (hljs.highlightElement) {
                  hljs.highlightElement(block)
                } else {
                  // 兼容旧版本
                  hljs.highlightBlock(block)
                }
                $block.attr('data-highlighted', 'true')
              } catch (error) {
                console.warn('代码高亮失败:', error)
              }
            }
          })
        }
      },
      renderMath () {
        if (this.editor && this.editor.body) {
          // 渲染行内数学公式 $...$
          const inlineMathRegex = /\$([^$]+)\$/g
          // 渲染块级数学公式 $$...$$
          const blockMathRegex = /\$\$([^$]+)\$\$/g
          
          const content = this.editor.body.html()
          let newContent = content
          
          try {
            // 处理块级数学公式
            newContent = newContent.replace(blockMathRegex, (match, formula) => {
              try {
                const rendered = katex.renderToString(formula.trim(), {
                  displayMode: true,
                  throwOnError: false
                })
                return `<div class="katex-block">${rendered}</div>`
              } catch (error) {
                console.warn('块级数学公式渲染失败:', formula, error)
                return match
              }
            })
            
            // 处理行内数学公式
            newContent = newContent.replace(inlineMathRegex, (match, formula) => {
              try {
                const rendered = katex.renderToString(formula.trim(), {
                  displayMode: false,
                  throwOnError: false
                })
                return `<span class="katex-inline">${rendered}</span>`
              } catch (error) {
                console.warn('行内数学公式渲染失败:', formula, error)
                return match
              }
            })
            
            if (newContent !== content) {
              this.editor.body.html(newContent)
            }
          } catch (error) {
            console.warn('数学公式渲染失败:', error)
          }
        }
      }
    },
    watch: {
      'value' (val) {
        if (this.currentValue !== val) {
          this.currentValue = val
          this.editor.setValue(val)
        }
      },
      'currentValue' (newVal, oldVal) {
        if (newVal !== oldVal) {
          this.$emit('change', newVal)
          this.$emit('input', newVal)
        }
      }
    }
  }
</script>

<style lang="less" scoped>
  // 代码高亮样式优化
  /deep/ pre {
    background-color: #f8f8f8;
    border: 1px solid #e1e1e8;
    border-radius: 4px;
    padding: 12px;
    margin: 10px 0;
    overflow-x: auto;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.4;
    
    code {
      background: transparent;
      border: none;
      padding: 0;
      color: inherit;
      font-family: inherit;
    }
  }
  
  /deep/ code {
    background-color: #f1f1f1;
    border: 1px solid #e1e1e8;
    border-radius: 3px;
    padding: 2px 4px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 13px;
    color: #c7254e;
  }
  
  // 高亮主题样式调整
  /deep/ .hljs {
    background: #f8f8f8 !important;
    color: #333 !important;
  }
  
  /deep/ .hljs-keyword {
    color: #0000ff !important;
    font-weight: bold;
  }
  
  /deep/ .hljs-string {
    color: #008000 !important;
  }
  
  /deep/ .hljs-comment {
    color: #008000 !important;
    font-style: italic;
  }
  
  /deep/ .hljs-number {
    color: #ff0000 !important;
  }
  
  /deep/ .hljs-built_in,
  /deep/ .hljs-type {
    color: #0000ff !important;
  }
</style>
