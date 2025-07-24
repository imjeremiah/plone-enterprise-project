/**
 * OAuth Redirect Handler for Volto Frontend
 * 
 * This script automatically redirects users from Classic UI to Volto
 * after successful OAuth authentication.
 */

// Check if user came from OAuth and redirect to Volto
(function() {
    // Check if we're on the Classic UI after OAuth
    if (window.location.href.includes('localhost:8080/Plone') && 
        !window.location.href.includes('@@authomatic-handler')) {
        
        // Check if there's a stored return URL or if user just logged in
        const oauthReturnUrl = sessionStorage.getItem('oauth_return_url');
        const isJustLoggedIn = document.body.textContent.includes('admin') || 
                              document.querySelector('.userrole-authenticated');
        
        if (oauthReturnUrl || isJustLoggedIn) {
            console.log('OAuth login detected, redirecting to Volto...');
            
            // Clear the stored URL
            sessionStorage.removeItem('oauth_return_url');
            
            // Redirect to Volto frontend
            const voltoUrl = oauthReturnUrl || 'http://localhost:3000';
            window.location.href = voltoUrl.replace('localhost:8080', 'localhost:3000');
        }
    }
})(); 