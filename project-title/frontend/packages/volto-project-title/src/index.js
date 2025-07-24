import LoginComponent from './components/Login';
import StandardsWidget from './components/StandardsWidget';

const applyConfig = (config) => {
  console.log('🚀 Edu Plone addon loading...');
  
  config.settings.isMultilingual = false;
  config.settings.supportedLanguages = ['en'];
  config.settings.defaultLanguage = 'en';

  // Override the login route in Volto
  config.addonRoutes = [
    {
      path: '/login',
      component: LoginComponent,
      exact: true,
    },
    ...(config.addonRoutes || []),
  ];
  
  // Initialize widgets object if it doesn't exist
  if (!config.widgets) {
    config.widgets = {};
  }
  if (!config.widgets.widget) {
    config.widgets.widget = {};
  }
  
  // Register Standards Widget for educational content
  config.widgets.widget.aligned_standards = StandardsWidget;
  
  console.log('✅ Custom Login component registered');
  console.log('✅ Standards Widget registered for educational content');

  return config;
};

export default applyConfig;
