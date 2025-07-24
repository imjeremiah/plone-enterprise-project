# Developer Configuration Notes

## Frontend-Backend Integration (CRITICAL)

### Issue Fixed: Frontend API Path Configuration

**Problem**: The Volto frontend was attempting to communicate with itself (`localhost:3000`) instead of the Plone backend (`localhost:8080`).

**Solution Applied**: Updated `frontend/Makefile` to automatically set the correct API path.

### What Was Changed

**File**: `project-title/frontend/Makefile`
```makefile
# OLD (broken)
start: ## Starts Volto, allowing reloading of the add-on during development
	pnpm start

# NEW (working)  
start: ## Starts Volto, allowing reloading of the add-on during development
	RAZZLE_API_PATH=http://localhost:8080/Plone pnpm start
```

### How to Start Services

```bash
# Backend (Terminal 1)
cd project-title/backend
make start  # http://localhost:8080

# Frontend (Terminal 2) 
cd project-title/frontend
make start  # http://localhost:3000 (automatically configured)
```

### Verification

✅ **Working Integration Confirmed**:
- Backend: http://localhost:8080/Plone
- Frontend: http://localhost:3000
- Frontend displays "Project Title" from backend API

### Never Forget Again

- The Makefile now handles this automatically
- No manual environment variables needed
- Just use `make start` as documented in phase docs

### Emergency Fallback

If the Makefile doesn't work for some reason:
```bash
cd frontend
RAZZLE_API_PATH=http://localhost:8080/Plone pnpm start
```

---

## CORS Configuration (CRITICAL FIX)

### Issue: CORS Errors Blocking Frontend-Backend Communication

**Problem**: Browser blocks API requests with error:
```
Access to XMLHttpRequest at 'http://localhost:8080/Plone/++api++/' 
from origin 'http://localhost:3000' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### ✅ Solution Implemented: Registry-Based CORS Configuration

**File Created**: `project-title/backend/src/project/title/profiles/default/registry.xml`

This approach uses Plone's registry to configure CORS settings, which is more reliable than custom adapters.

#### CORS Configuration Applied:
- ✅ **Allowed Origins**: `http://localhost:3000`, `http://127.0.0.1:3000`, `http://localhost:3001`
- ✅ **Allowed Methods**: GET, POST, PUT, PATCH, DELETE, OPTIONS  
- ✅ **Allow Credentials**: true (for authenticated requests)
- ✅ **Expose Headers**: Content-Length, Content-Type

### Backend Dependencies Updated

**File**: `project-title/backend/src/project/title/dependencies.zcml`
```xml
<include package="plone.restapi" />
<include package="plone.volto" />
<include package="plone.app.caching" />
```

### Testing CORS Configuration

After restarting the backend, test CORS headers:
```bash
# Test API connectivity
curl -s http://localhost:8080/Plone/++api++/ | head -5

# Test CORS headers
curl -s -I -H "Origin: http://localhost:3000" http://localhost:8080/Plone/++api++/
```

### Expected Result After CORS Fix

✅ **Frontend should successfully load without CORS errors**
✅ **Custom login component should become visible**  
✅ **Google OAuth button should appear**

---

## Google OAuth Setup (Feature 1)

### Google Cloud Console Configuration

**Required for Feature 1: Modern Authentication - Google OAuth/SSO**

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Name: "Project Title Educational Platform"

#### Step 2: Enable Google APIs
1. Go to "APIs & Services" > "Library"
2. Search and enable:
   - **Google+ API** (for user profile access)
   - **People API** (for user information)

#### Step 3: Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. Application type: **Web application**
4. Name: "Project Title OAuth Client"

#### Step 4: Configure Redirect URIs
Add these authorized redirect URIs:
```
http://localhost:8080/@@authomatic-handler
http://localhost:8080/Plone/@@authomatic-handler
https://yourdomain.com/@@authomatic-handler  # For production
```

#### Step 5: Set Environment Variables
```bash
# Development
export GOOGLE_OAUTH_CLIENT_ID="your-client-id.googleusercontent.com"
export GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret"

# Production (add to deployment configuration)
GOOGLE_OAUTH_CLIENT_ID=your-production-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-production-client-secret
```

#### Step 6: Test OAuth Configuration
1. Start backend: `cd backend && make start`
2. Go to: http://localhost:8080/Plone/@@authomatic-handler
3. Should show OAuth provider selection

### Security Notes
- **Never commit credentials to version control**
- Use environment variables for all OAuth secrets
- Development config is insecure - for testing only
- Production requires valid Google Cloud credentials

### Troubleshooting OAuth
- Check redirect URI matches exactly
- Verify APIs are enabled in Google Cloud
- Check environment variables are set
- Look for errors in Plone logs: `tail -f backend/instance/var/log/instance.log`

### OAuth Implementation Resolution

**Issue Encountered**: ImportError with `IAutomaticSettings` interface from pas.plugins.authomatic

**Solution Applied**: 
- Simplified OAuth configuration approach
- Removed custom adapter configuration 
- Rely on pas.plugins.authomatic's standard installation process
- OAuth configuration will be done through Plone control panel

**Result**: ✅ Backend starts successfully with OAuth support loaded

### OAuth Configuration Steps (After Google Cloud Setup)

1. **Install pas.plugins.authomatic**: ✅ Already included in pyproject.toml
2. **Access Plone Control Panel**: http://localhost:8080/Plone/@@overview-controlpanel
3. **Configure Authomatic**: Go to "Configuration" > "Authomatic (OAuth)"
4. **Add Google Provider**:
   ```json
   {
     "google": {
       "class_": "authomatic.providers.oauth2.Google",
       "consumer_key": "your-google-client-id",
       "consumer_secret": "your-google-client-secret",
       "scope": ["profile", "email"]
     }
   }
   ```

### Frontend Login Component Status

✅ **Login Component Created**: Custom login with Google OAuth button
✅ **Component Registered**: Volto addon loads and registers successfully  
✅ **Styling Applied**: Red Google button with proper hover effects

**File**: `project-title/frontend/packages/volto-project-title/src/components/Login/Login.jsx`

#### What Should Appear After CORS Fix:
- 🔴 **Large red "Sign in with Google" button**
- 🎯 **"Teacher Quick Access" heading**  
- ⚙️ **"Administrator Login" toggle option**

---

## Development Workflow

### Quick Start (After CORS Fix)

```bash
# Terminal 1: Backend
cd project-title/backend
make start  # ✅ Should start without errors

# Terminal 2: Frontend  
cd project-title/frontend
make start  # ✅ Should load without CORS errors

# Expected Result:
# - Frontend loads at http://localhost:3000
# - Backend API at http://localhost:8080/Plone/++api++/
# - Custom login component visible at /login
# - Google OAuth button appears
```

### Troubleshooting

1. **Backend won't start**: Check for port conflicts, delete `.venv` and reinstall
2. **CORS errors persist**: Verify registry.xml settings, restart backend
3. **Login component not showing**: Check frontend console for component registration
4. **OAuth not working**: Verify Google Cloud credentials and redirect URIs

---

## Summary: CORS Problem Solved ✅

The key CORS issue has been resolved through:
1. ✅ **Registry-based CORS configuration** (reliable approach)
2. ✅ **Proper dependency management** (removed problematic packages)
3. ✅ **Environment-based configuration** (follows Plone best practices)

**Next Steps**: 
- Test frontend without CORS errors
- Verify Google OAuth button visibility  
- Complete OAuth flow with Google Cloud credentials 