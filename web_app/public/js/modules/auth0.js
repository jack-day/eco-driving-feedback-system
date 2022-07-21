/**
 * @module Auth0
 * @description Manages Auth0 authentication and authorisation using the
 * [Auth0 Single Page App SDK]{@link https://auth0.com/docs/libraries/auth0-single-page-app-sdk}.
 */
/** Auth0 client object ({@link https://auth0.github.io/auth0-spa-js/classes/auth0client.html}) */
export let auth0;

// Loader
// ----------------------------------------------
/** Display an error on the auth loader screen */
export function authLoaderError() {
    const authLoader = document.querySelector('#auth-loader');
    const authLoaderCircle = authLoader.querySelector('svg');
    authLoaderCircle.remove();
    
    const errorMsg = document.createElement('p');
    errorMsg.textContent = 'An error has occurred during authentication.';
    authLoader.classList.add('error');
    authLoader.append(errorMsg);
}

/** Remove the auth loader screen */
export function removeAuthLoader() {
    const authLoader = document.querySelector('#auth-loader');
    if (authLoader) authLoader.remove();
}


// Authentication
// ----------------------------------------------
/** Fetch auth0 config from server */
async function fetchAuthConfig() {
    const response = await fetch('/auth/config');
    if (response.ok) {
        return response.json();
    } else {
        authLoaderError();
        throw Error('Failed to fetch auth config');
    }
}

/** Initialise the Auth0 client object */
export async function initAuth0() {
    const config = await fetchAuthConfig();
    auth0 = await createAuth0Client({ // eslint-disable-line no-undef
        domain: config.domain,
        client_id: config.clientID,
        redirect_uri: config.callbackURL,
        audience: config.audience,
        scope: config.scope,
        advancedOptions: {
            defaultScope: null,
        },
    });
}

/**
 * Sign in event handler to login with Auth0
 * @param {Object} opts Sign in options
 * @param {string} opts.redirectURL - URL to be redirected to from /auth/callback after a successful login
 * @param {boolean} opts.registerUser Whether to attempt to register the user
 */
export async function signIn({ redirectURL, registerUser }) {
    await auth0.loginWithRedirect({
        appState: {
            target: redirectURL || window.location.origin,
            registerUser: registerUser || false,
        },
    });
}

/**
 * Sign user out of Auth0
 * @param {boolean} indicateError - Whether to indicate an authentication error when redirected
 */
export function signOut(indicateError = false) {
    let returnTo = window.location.origin + '/login';
    if (indicateError) returnTo += '#auth-error';
    auth0.logout({ returnTo });
}

/**
 * Check if the user is registered
 * @param {string} token - User's Auth0 access token
 */
export async function checkRegistered(token) {
    const response = await fetch('/api/myself/registered', {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });

    if (response.status === 200) {
        return true;
    } else if (response.status === 204) {
        return false;
    } else {
        authLoaderError();
        throw Error("Failed to fetch the user's registration status");
    }
}

/**
 * Check user authorisation, redirect to login page if not authenticated
 * @param {Object} opts Authorization options
 * @param {boolean} opts.keepLoader Whether to keep the loader when succesfully authorized
 * @returns {Promise<string>} API access token
 */
export async function authorize({ keepLoader = false } = {}) {
    await initAuth0();

    const isAuthenticated = await auth0.isAuthenticated();
    if (!isAuthenticated) {
        window.location = window.location.origin + '/login';
    }

    const token = await auth0.getTokenSilently();
    const registered = await checkRegistered(token);
    if (registered) {
        if (!keepLoader) removeAuthLoader();
        return token;
    } else {
        signOut();
    }
}
