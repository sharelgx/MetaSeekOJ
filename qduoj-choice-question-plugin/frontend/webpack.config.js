const path = require('path')
const { VueLoaderPlugin } = require('vue-loader')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin')

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production'
  
  return {
    entry: {
      'plugin-entry': './plugin-entry.js'
    },
    
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: isProduction ? '[name].[contenthash].js' : '[name].js',
      chunkFilename: isProduction ? '[name].[contenthash].chunk.js' : '[name].chunk.js',
      clean: true,
      library: {
        name: 'ChoiceQuestionPlugin',
        type: 'umd',
        export: 'default'
      },
      globalObject: 'this'
    },
    
    resolve: {
      extensions: ['.js', '.vue', '.json'],
      alias: {
        '@': path.resolve(__dirname, 'src'),
        'vue$': 'vue/dist/vue.esm.js'
      }
    },
    
    externals: {
      // 这些依赖由主应用提供，不打包到插件中
      'vue': {
        commonjs: 'vue',
        commonjs2: 'vue',
        amd: 'vue',
        root: 'Vue'
      },
      'vue-router': {
        commonjs: 'vue-router',
        commonjs2: 'vue-router',
        amd: 'vue-router',
        root: 'VueRouter'
      },
      'vuex': {
        commonjs: 'vuex',
        commonjs2: 'vuex',
        amd: 'vuex',
        root: 'Vuex'
      },
      'element-ui': {
        commonjs: 'element-ui',
        commonjs2: 'element-ui',
        amd: 'element-ui',
        root: 'ELEMENT'
      },
      'axios': {
        commonjs: 'axios',
        commonjs2: 'axios',
        amd: 'axios',
        root: 'axios'
      }
    },
    
    module: {
      rules: [
        {
          test: /\.vue$/,
          loader: 'vue-loader'
        },
        {
          test: /\.js$/,
          loader: 'babel-loader',
          exclude: /node_modules/
        },
        {
          test: /\.css$/,
          use: [
            isProduction ? MiniCssExtractPlugin.loader : 'vue-style-loader',
            'css-loader'
          ]
        },
        {
          test: /\.scss$/,
          use: [
            isProduction ? MiniCssExtractPlugin.loader : 'vue-style-loader',
            'css-loader',
            'sass-loader'
          ]
        },
        {
          test: /\.(png|jpe?g|gif|svg)$/i,
          type: 'asset',
          parser: {
            dataUrlCondition: {
              maxSize: 8 * 1024 // 8kb
            }
          },
          generator: {
            filename: 'images/[name].[hash:8][ext]'
          }
        },
        {
          test: /\.(woff2?|eot|ttf|otf)$/i,
          type: 'asset/resource',
          generator: {
            filename: 'fonts/[name].[hash:8][ext]'
          }
        }
      ]
    },
    
    plugins: [
      new VueLoaderPlugin(),
      
      ...(isProduction ? [
        new MiniCssExtractPlugin({
          filename: '[name].[contenthash].css',
          chunkFilename: '[name].[contenthash].chunk.css'
        })
      ] : []),
      
      // 开发环境下生成HTML文件用于测试
      ...(!isProduction ? [
        new HtmlWebpackPlugin({
          template: path.resolve(__dirname, 'public/index.html'),
          filename: 'index.html',
          inject: true
        })
      ] : [])
    ],
    
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
      },
      
      ...(isProduction && {
        minimize: true,
        sideEffects: false
      })
    },
    
    devServer: {
      static: {
        directory: path.join(__dirname, 'public')
      },
      compress: true,
      port: 8080,
      hot: true,
      open: true,
      historyApiFallback: true,
      client: {
        overlay: {
          errors: true,
          warnings: false
        }
      }
    },
    
    devtool: isProduction ? 'source-map' : 'eval-cheap-module-source-map',
    
    performance: {
      hints: isProduction ? 'warning' : false,
      maxEntrypointSize: 512000,
      maxAssetSize: 512000
    },
    
    stats: {
      colors: true,
      modules: false,
      children: false,
      chunks: false,
      chunkModules: false
    }
  }
}