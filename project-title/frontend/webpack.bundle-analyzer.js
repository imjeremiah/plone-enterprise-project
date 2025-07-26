/**
 * Webpack Bundle Analyzer Configuration for Phase 4 Performance Optimization
 * 
 * This configuration adds bundle analysis capabilities to help identify:
 * - Large dependencies that can be code-split
 * - Duplicate modules across chunks
 * - Optimization opportunities
 * - Bundle size trends over time
 */

const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const path = require('path');

const bundleAnalyzerConfig = (config) => {
  // Only add analyzer in analyze mode
  if (process.env.BUNDLE_ANALYZE === 'true') {
    config.plugins = config.plugins || [];
    
    config.plugins.push(
      new BundleAnalyzerPlugin({
        analyzerMode: 'static',
        reportFilename: path.resolve(__dirname, 'build/bundle-report.html'),
        defaultSizes: 'gzip',
        openAnalyzer: false,
        generateStatsFile: true,
        statsFilename: path.resolve(__dirname, 'build/bundle-stats.json'),
        logLevel: 'info'
      })
    );
    
    // Optimize for analysis
    config.optimization = {
      ...config.optimization,
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          // Vendor chunk for third-party libraries
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 20
          },
          // Volto core chunk
          volto: {
            test: /[\\/]node_modules[\\/]@plone[\\/]volto[\\/]/,
            name: 'volto-core',
            chunks: 'all',
            priority: 30
          },
          // Classroom management components
          classroom: {
            test: /[\\/]packages[\\/]volto-project-title[\\/]src[\\/]components[\\/]/,
            name: 'classroom-components',
            chunks: 'all',
            priority: 10
          },
          // Dashboard specific chunk
          dashboard: {
            test: /[\\/]packages[\\/]volto-project-title[\\/]src[\\/]components[\\/]Dashboard[\\/]/,
            name: 'dashboard',
            chunks: 'all',
            priority: 15
          },
          // Semantic UI components (often large)
          semanticui: {
            test: /[\\/]node_modules[\\/]semantic-ui-react[\\/]/,
            name: 'semantic-ui',
            chunks: 'all',
            priority: 25
          }
        }
      }
    };
  }
  
  return config;
};

module.exports = bundleAnalyzerConfig; 