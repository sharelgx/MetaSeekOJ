// 在webpack配置中添加字体处理规则
module.exports = {
  module: {
    rules: [
      {
        test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/,
        loader: 'url-loader',
        options: {
          limit: 10000,
          name: 'fonts/[name].[hash:7].[ext]',
          publicPath: '/static/'
        }
      }
    ]
  }
}
