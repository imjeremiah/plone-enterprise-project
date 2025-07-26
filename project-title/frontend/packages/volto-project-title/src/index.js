import SeatingChartView from './components/Views/SeatingChartView';
import SeatingChartsPage from './components/Views/SeatingChartsPage';
import HallPassManager from './components/HallPass/HallPassManager';
import CustomHomepage from './components/Home/CustomHomepage';
import RandomStudentPicker from './components/RandomPicker/RandomStudentPicker';
import HallPassManagerRoute from './components/HallPass/HallPassManagerRoute';
import TimerPage from './components/Timer/TimerPage';
import SubstitutePage from './components/SubstituteFolder/SubstitutePage';
import TeacherDashboard from './components/Dashboard/TeacherDashboard';
import ClassroomToolsWidget from './components/Dashboard/widgets/ClassroomToolsWidget';

const applyConfig = (config) => {
  console.log('🚀 Edu Plone addon loading...');

  config.settings.isMultilingual = false;
  config.settings.supportedLanguages = ['en'];
  config.settings.defaultLanguage = 'en';

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

  // Register custom homepage with classroom tools
  config.views.contentTypesViews['Plone Site'] = CustomHomepage;

  // Add standalone routes for classroom management tools
  config.addonRoutes = [
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
    {
      path: '/seating-charts',
      component: SeatingChartsPage,
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
  config.components.ClassroomToolsWidget = ClassroomToolsWidget;

  // Simplified logging - only show completion
  console.log('✅ Edu Plone classroom management tools initialized');
  console.log('🎛️ Dashboard available at /dashboard');

  return config;
};

export default applyConfig;
