const webpack = require('webpack');
const path = require('path')
// eslint-disable-next-line prefer-destructuring
const resolve = path.resolve;
const HTMLPlugin = require('html-webpack-plugin');
const UglifyJSWebpackPlguin  = require('uglifyjs-webpack-plugin')

module.exports = {
  entry:'./public/index.tsx',
  output: {
    filename: '[name].min.js',
    publicPath: '/',
    path: resolve(process.cwd(), 'dist/'),
  },
  target: 'web',
  resolve: {
    extensions: ['.ts', '.js', '.tsx', '.jsx'],
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            babelrc: true,
          },
        },
      }, {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'ts-loader'
        },
      }, {
        test: /\.(css)$/,
        exclude: /node_modules/,
        use: [
          'style-loader',
          {
            loader: 'css-loader',
            options: {
              modules: true,
            },
          },
        ]
      }, {
            test: /\.s[ac]ss$/i,
            exclude: /node_modules/,
            use: [
              // Creates `style` nodes from JS strings
              'style-loader',
              // Translates CSS into CommonJS
              'css-loader',
              // Compiles Sass to CSS
              'sass-loader',
            ],
        }, {
            test: /\.(png|jpg|gif)$/,
            use: [
                {
                    loader: 'file-loader'
                }
            ]
        }
    ]
  },
  plugins: [
    new webpack.optimize.AggressiveMergingPlugin(),
    new HTMLPlugin({
      template: './public/index.html',
      favicon: './public/static/handshake_favicon.png'
    })
  ],
  devtool: 'source-map',
  devServer: {
    contentBase: './dist',
    port: 8080,
    historyApiFallback: true
  }
};
