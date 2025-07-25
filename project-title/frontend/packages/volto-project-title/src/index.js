import LoginComponent from './components/Login';
import StandardsWidget from './components/StandardsWidget';
import SeatingChartView from './components/Views/SeatingChartView';
import RandomStudentPicker from './components/RandomPicker/RandomStudentPicker';
import HallPassManager from './components/HallPass/HallPassManager';
import HallPassManagerRoute from './components/HallPass/HallPassManagerRoute';
import LessonTimer from './components/Timer/LessonTimer';
import TimerPage from './components/Timer/TimerPage';
import SubstitutePage from './components/SubstituteFolder/SubstitutePage';
import TeacherDashboard from './components/Dashboard/TeacherDashboard';

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
  
  // Register HallPass view for digital hall pass management
  config.views.contentTypesViews.HallPass = HallPassManager;
  
  // Add standalone routes for classroom management tools
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
    {
      path: '/hall-pass-manager',
      component: HallPassManagerRoute,
      exact: true,
    },
    {
      path: '/timer',
      component: TimerPage,
      exact: true,
    },
    {
      path: '/substitute-folder',
      component: SubstitutePage,
      exact: true,
    },
    {
      path: '/dashboard',
      component: TeacherDashboard,
      exact: true,
    },
    ...(config.addonRoutes || []),
  ];
  
  // Register classroom management components as reusable
  if (!config.components) {
    config.components = {};
  }
  config.components.RandomStudentPicker = RandomStudentPicker;
  config.components.HallPassManager = HallPassManager;
  config.components.LessonTimer = LessonTimer;
  
  console.log('✅ Custom Login component registered');
  console.log('✅ Standards Widget registered for educational content');
  console.log('✅ SeatingChart view registered for classroom management');
  console.log('✅ Random Student Picker component registered');
  console.log('✅ Digital Hall Pass Manager component registered');
  console.log('✅ Lesson Timer tool registered for classroom activities');
  console.log('✅ Substitute Folder Generator registered for emergency preparation');
  console.log('✅ Teacher Dashboard registered for real-time classroom management');

  return config;
};

export default applyConfig;
