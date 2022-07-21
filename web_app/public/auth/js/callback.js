/** @module */
import { auth0, initAuth0, authLoaderError, signOut } from '/js/modules/auth0.js';

async function registerUser() {
    const token = await auth0.getTokenSilently();
    const response = await fetch('/api/users', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });
    
    if (!response.ok && response.status !== 400) {
        throw new Error('Error occured attempting to register user');
    }
}

/** Handle users redirected from Auth0 authentication */
async function handleAuth0Redirect() {
    const isAuthenticated = await auth0.isAuthenticated();
    if (isAuthenticated) window.location.origin;
  
    const query = window.location.search;
    if (query.includes('state=')) {
        if (query.includes('code=')) {
            try {
                const result = await auth0.handleRedirectCallback();
                if (result.appState.registerUser) await registerUser();
                window.location = result.appState.target;
            } catch (e) {
                console.error(e);
                authLoaderError();
                signOut(true);
            }
        } else if (query.includes('error=')) {
            authLoaderError();
            signOut(true);
        }
    }
}

async function init() {
    await initAuth0();
    await handleAuth0Redirect();
}

window.addEventListener('load', init);
