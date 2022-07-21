/** @module */
import { auth0, initAuth0, signIn, removeAuthLoader, checkRegistered } from './modules/auth0.js';

/** Redirect users who are already signed in and registered */
async function redirectSignedIn() {
    await initAuth0();

    const isAuthenticated = await auth0.isAuthenticated();
    if (isAuthenticated) {

        const token = await auth0.getTokenSilently();
        const registered = await checkRegistered(token);
        if (registered) {
            window.location = window.location.origin;
        } else {
            removeAuthLoader();
        }
    } else {
        removeAuthLoader();
    }
}

async function init() {
    if (window.location.hash === '#auth-error') {
        const authError = document.querySelector('#auth-error');
        authError.classList.remove('hide');
        window.location.hash = '';
    }

    await redirectSignedIn();

    const signInBtn = document.querySelector('#sign-in');
    signInBtn.addEventListener('click', () => signIn({ registerUser: true }));
}

window.addEventListener('load', init);
