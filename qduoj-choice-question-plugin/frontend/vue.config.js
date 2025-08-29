const path = require('path')

module.exports = {
  // 基础路径
  publicPath: process.env.NODE_ENV === 'production' ? '/static/plugins/choice-question/' : '/',
  
  // 输出目录
  outputDir: 'dist',
  
  // 静态资源目录
  assetsDir: 'static',
  
  // 是否在构建生产包时生成 sourceMap 文件
  productionSourceMap: process.env.NODE_ENV !== 'production',
  
  // 配置webpack
  configureWebpack: {
    // 入口文件
    entry: {
      app: './plugin-entry.js'
    },
    
    // 外部依赖，不打包到插件中
    externals: {
      'vue': 'Vue',
      'vue-router': 'VueRouter',
      'vuex': 'Vuex',
      'element-ui': 'ELEMENT',
      'axios': 'axios',
      'lodash': '_',
      'moment': 'moment'
    },
    
    // 输出配置
    output: {
      library: 'ChoiceQuestionPlugin',
      libraryTarget: 'umd',
      libraryExport: 'default',
      globalObject: 'this'
    },
    
    // 解析配置
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        'components': path.resolve(__dirname, 'src/components'),
        'views': path.resolve(__dirname, 'src/views'),
        'utils': path.resolve(__dirname, 'src/utils'),
        'api': path.resolve(__dirname, 'src/api'),
        'store': path.resolve(__dirname, 'src/store'),
        'assets': path.resolve(__dirname, 'src/assets')
      }
    },
    
    // 优化配置
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 10
          },
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'all',
            priority: 5,
            reuseExistingChunk: true
          }
        }
      }
    }
  },
  
  // 链式操作webpack配置
  chainWebpack: config => {
    // 移除默认的HTML插件（插件不需要HTML文件）
    if (process.env.NODE_ENV === 'production') {
      config.plugins.delete('html')
      config.plugins.delete('preload')
      config.plugins.delete('prefetch')
    }
    
    // 配置文件加载器
    config.module
      .rule('images')
      .test(/\.(png|jpe?g|gif|svg)(\?.*)?$/)
      .use('url-loader')
      .loader('url-loader')
      .options({
        limit: 8192,
        name: 'img/[name].[hash:8].[ext]'
      })
    
    config.module
      .rule('fonts')
      .test(/\.(woff2?|eot|ttf|otf)(\?.*)?$/)
      .use('url-loader')
      .loader('url-loader')
      .options({
        limit: 8192,
        name: 'fonts/[name].[hash:8].[ext]'
      })
    
    // 配置别名
    config.resolve.alias
      .set('@', path.resolve(__dirname, 'src'))
      .set('components', path.resolve(__dirname, 'src/components'))
      .set('views', path.resolve(__dirname, 'src/views'))
      .set('utils', path.resolve(__dirname, 'src/utils'))
      .set('api', path.resolve(__dirname, 'src/api'))
      .set('store', path.resolve(__dirname, 'src/store'))
      .set('assets', path.resolve(__dirname, 'src/assets'))
    
    // 开发环境配置
    if (process.env.NODE_ENV === 'development') {
      // 开启source map
      config.devtool('eval-cheap-module-source-map')
    }
    
    // 生产环境配置
    if (process.env.NODE_ENV === 'production') {
      // 压缩配置
      config.optimization.minimize(true)
      
      // 移除console
      config.optimization
        .minimizer('terser')
        .tap(args => {
          args[0].terserOptions.compress.drop_console = true
          args[0].terserOptions.compress.drop_debugger = true
          return args
        })
    }
  },
  
  // CSS相关配置
  css: {
    // 是否提取CSS到单独文件
    extract: process.env.NODE_ENV === 'production',
    
    // 是否开启CSS source map
    sourceMap: process.env.NODE_ENV !== 'production',
    
    // CSS预处理器配置
    loaderOptions: {
      scss: {
        // 全局SCSS变量
        additionalData: `@import "@/assets/styles/variables.scss";`
      },
      
      postcss: {
        plugins: [
          require('autoprefixer')({
            overrideBrowserslist: [
              '> 1%',
              'last 2 versions',
              'not dead'
            ]
          })
        ]
      }
    }
  },
  
  // 开发服务器配置
  devServer: {
    port: 8080,
    host: '0.0.0.0',
    https: false,
    open: true,
    hot: true,
    
    // 代理配置
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        logLevel: 'debug'
      }
    },
    
    // 覆盖配置
    overlay: {
      warnings: false,
      errors: true
    },
    
    // 静态文件服务
    static: {
      directory: path.join(__dirname, 'public'),
      publicPath: '/'
    }
  },
  
  // 插件配置
  pluginOptions: {
    // 自定义插件选项
    'choice-question': {
      version: '1.0.0',
      description: 'QDUOJ选择题插件'
    }
  },
  
  // 并行处理
  parallel: require('os').cpus().length > 1,
  
  // PWA配置（如果需要）
  pwa: {
    name: 'QDUOJ选择题插件',
    themeColor: '#409EFF',
    msTileColor: '#000000',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black',
    
    workboxPluginMode: 'InjectManifest',
    workboxOptions: {
      swSrc: 'src/sw.js'
    }
  },
  
  // 国际化配置
  pluginOptions: {
    i18n: {
      locale: 'zh-CN',
      fallbackLocale: 'en',
      localeDir: 'locales',
      enableInSFC: true
    }
  }
}