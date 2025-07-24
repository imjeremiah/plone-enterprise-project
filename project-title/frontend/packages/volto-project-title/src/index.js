import LoginComponent from './components/Login';
import StandardsWidget from './components/StandardsWidget';
import SeatingChartView from './components/Views/SeatingChartView';
import RandomStudentPicker from './components/RandomPicker/RandomStudentPicker';

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
  
  // Initialize views object if it doesn't exist
  if (!config.views) {
    config.views = {};
  }
  if (!config.views.contentTypesViews) {
    config.views.contentTypesViews = {};
  }
  
  // Register SeatingChart view for classroom management
  config.views.contentTypesViews.SeatingChart = SeatingChartView;
  
  // Add random picker route for standalone access
  config.addonRoutes = [
    {
      path: '/login',
      component: LoginComponent,
      exact: true,
    },
    {
      path: '/random-picker',
      component: RandomStudentPicker,
      exact: true,
    },
    ...(config.addonRoutes || []),
  ];
  
  // Register RandomStudentPicker as a reusable component
  if (!config.components) {
    config.components = {};
  }
  config.components.RandomStudentPicker = RandomStudentPicker;
  
  console.log('✅ Custom Login component registered');
  console.log('✅ Standards Widget registered for educational content');
  console.log('✅ SeatingChart view registered for classroom management');
  console.log('✅ Random Student Picker component registered');

  return config;
};

export default applyConfig;
