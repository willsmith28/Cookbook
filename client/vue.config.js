module.exports = {
  devServer: {
    clientLogLevel: "debug",
    disableHostCheck: true,
    host: "0.0.0.0",
    hot: true,
    liveReload: true,
    open: false,
    overlay: true,
    port: 8080,
    public: "localhost:1337",
    watchOptions: {
      aggregateTimeout: 300,
      ignored: /node_modules/,
      poll: 1000
    }
  }
};
