const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: {
    app: './src/pages/oj/index.js',
    admin: './src/pages/admin/index.js'
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].js',
    publicPath: '/'
  },
  resolve: {
    extensions: ['.js', '.vue', '.json'],
    alias: {
      'vue$': 'vue/dist/vue.esm.js',
      '@': path.resolve(__dirname, 'src'),
      '@oj': path.resolve(__dirname, 'src/pages/oj'),
      '@admin': path.resolve(__dirname, 'src/pages/admin')
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
        test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
        loader: 'url-loader',
        options: {
          limit: 10000,
          name: 'img/[name].[hash:7].[ext]'
        }
      },
      {
        test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/,
        loader: 'url-loader',
        options: {
          limit: 10000,
          name: 'fonts/[name].[hash:7].[ext]'
        }
      },
      {
        test: /\.css$/,
        use: ['vue-style-loader', 'css-loader']
      },
      {
        test: /\.less$/,
        use: ['vue-style-loader', 'css-loader', 'less-loader']
      }
    ]
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: '"development"'
      }
    }),
    new HtmlWebpackPlugin({
      filename: 'index.html',
      template: './src/pages/oj/index.html',
      inject: true,
      chunks: ['app']
    }),
    new HtmlWebpackPlugin({
      filename: 'admin/index.html',
      template: './src/pages/admin/index.html',
      inject: true,
      chunks: ['admin']
    })
  ],
  devServer: {
    port: 8080,
    host: '0.0.0.0',
    historyApiFallback: {
      rewrites: [
        { from: /^\/admin/, to: '/admin/index.html' },
        { from: /./, to: '/index.html' }
      ]
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8086',
        changeOrigin: true
      },
      '/public': {
        target: 'http://localhost:8086',
        changeOrigin: true
      }
    }
  }
};