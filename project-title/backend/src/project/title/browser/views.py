"""
Browser views for project.title
"""
from Products.Five import BrowserView
from zope.interface import Interface


class OAuthRedirectView(BrowserView):
    """
    View that provides OAuth redirect functionality for Volto integration.
    """
    
    def __call__(self):
        """
        Returns JavaScript that redirects users from Classic UI to Volto
        after OAuth authentication.
        """
        js_content = """
        <script type="text/javascript">
        // OAuth Redirect Handler for Volto Frontend
        (function() {
            // Check if user came from OAuth and should be redirected to Volto
            var shouldRedirect = false;
            
            // Check if this is a post-OAuth landing (user is authenticated)
            var isAuthenticated = document.body.classList.contains('userrole-authenticated') ||
                                document.body.classList.contains('userrole-member') ||
                                document.querySelector('.personal-tools a[href*="logout"]');
            
            // Check if there's OAuth return URL in sessionStorage
            var oauthReturnUrl = sessionStorage.getItem('oauth_return_url');
            
            // Check if URL suggests OAuth flow
            var fromOAuth = window.location.href.includes('authomatic') ||
                           document.referrer.includes('accounts.google.com') ||
                           sessionStorage.getItem('oauth_in_progress');
            
            if (isAuthenticated && (oauthReturnUrl || fromOAuth)) {
                console.log('OAuth login detected, redirecting to Volto frontend...');
                
                // Clear OAuth indicators
                sessionStorage.removeItem('oauth_return_url');
                sessionStorage.removeItem('oauth_in_progress');
                
                // Redirect to Volto
                var voltoUrl = oauthReturnUrl || 'http://localhost:3000/';
                if (voltoUrl.includes('localhost:8080')) {
                    voltoUrl = voltoUrl.replace('localhost:8080', 'localhost:3000');
                }
                
                setTimeout(function() {
                    window.location.href = voltoUrl;
                }, 500); // Small delay to ensure page is loaded
            }
        })();
        </script>
        """
        
        self.request.response.setHeader('Content-Type', 'text/html')
        return js_content 