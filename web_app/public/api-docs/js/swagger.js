/**
 * @module Swagger-API-docs
 * @description Updates swagger's authorization with the user's current Auth0
 * access token. If they are not logged in, the authorize button will redirect
 * them to the Auth0 login.
 */
import { auth0, initAuth0, signIn } from '/js/modules/auth0.js';


// Elements
// ----------------------------------------------
/** Clear all event listeners from an element */
function clearEventListeners(elem) {
    elem.replaceWith(elem.cloneNode(true));
}

/**
 * Clear all event listeners from the authorize button and api path lock icons
 * to disable swagger's default authorization dialog
 */
function clearAuthBtnEventListeners() {
    const authBtn = document.querySelector('.auth-wrapper > .authorize');
    const authIconBtns = document.querySelectorAll('.authorization__btn');
    clearEventListeners(authBtn);
    authIconBtns.forEach(clearEventListeners);
}

/** Switch the authorize button lock icons to locked */
function lockAuthBtns() {
    const authBtn = document.querySelector('.auth-wrapper > .authorize');
    const authBtnSvgUse = authBtn.querySelector('svg use');
    authBtnSvgUse.setAttribute('href', '#locked');
    authBtnSvgUse.setAttribute('xlink:href', '#locked');

    const authIconBtns = document.querySelectorAll('.authorization__btn');
    for (const btn of authIconBtns) {
        const svgUse = btn.querySelector('svg use');
        svgUse.setAttribute('href', '#locked');
        svgUse.setAttribute('xlink:href', '#locked');
        clearEventListeners(btn);
    }
}


// Authorization
// ----------------------------------------------
/** Authorize swagger with the user's Auth0 access token */
async function authorizeSwagger() {
    const token = await auth0.getTokenSilently();
    ui.preauthorizeApiKey('OAuth2Bearer', `Bearer ${token}`); // eslint-disable-line no-undef
}


// Init
// ----------------------------------------------
async function init() {
    await initAuth0();
    const isAuthenticated = await auth0.isAuthenticated();

    if (isAuthenticated) {
        authorizeSwagger();
        lockAuthBtns();
    } else {
        clearAuthBtnEventListeners();
        const authBtn = document.querySelector('.auth-wrapper > .authorize');        
        authBtn.addEventListener('click', () => signIn({
            redirectURL: window.location.href,
        }));
    }
}

window.addEventListener('load', init);
