/**
 * @module CoreUI
 * @description Functionality for all the core UI elements, such as the account menu.
 */
import { signOut } from './auth0.js';

/** Initialse the account menu */
function initAccountMenu() {
    const accountIcon = document.querySelector('#account svg');
    const accountMenu = document.querySelector('#account-menu');
    accountIcon.addEventListener('click', () => {
        accountMenu.classList.toggle('hide');
    });

    const signOutBtn = document.querySelector('#sign-out');
    signOutBtn.addEventListener('click', () => signOut());

    document.addEventListener('click', (e) => {
        if (
            e.target !== accountMenu &&
            e.target !== accountIcon &&
            e.target.parentElement !== accountMenu &&
            e.target.parentElement !== accountIcon &&
            !accountMenu.classList.contains('hide')
        ) {
            accountMenu.classList.add('hide');
        }
    });
}

/** Initialse all core UI elements */
export default function initCoreUI() {
    initAccountMenu();
}
