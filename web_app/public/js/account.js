/** @module */
import initCoreUI from './modules/coreUI.js';
import { authorize, signOut } from './modules/auth0.js';

const el = {};

/** Initialise the 'Delete account permamently?' dialog */
function initDeleteDialog() {
    const deleteBtn = document.querySelector('#delete-account');
    const dialog = document.querySelector('#verify-delete-dialog');
    const cancelBtn = document.querySelector('#verify-delete-cancel');
    el.verifyInput = document.querySelector('#verify-delete');
    el.confirmDeleteBtn = document.querySelector('#verify-delete-confirm');

    deleteBtn.addEventListener('click', () => {
        dialog.onanimationend = () => {
            dialog.classList.remove('fade-in');
            dialog.onanimationend = null;
        };
        dialog.classList.add('fade-in');
        dialog.show();
    });

    cancelBtn.addEventListener('click', () => {
        dialog.onanimationend = () => {
            dialog.close();
            dialog.classList.remove('fade-out');
            dialog.onanimationend = null;
            el.verifyInput.value = '';
            el.confirmDeleteBtn.disabled = true;
        };
        dialog.classList.add('fade-out');
    });
}

/** Delete account through API  */
async function deleteAccount(token) {
    const response = await fetch('/api/myself/', {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });

    if (response.ok) {
        signOut();
    } else {
        throw new Error('Failed to delete account');
    }
}

/** Initialise event listeners for account deletion elements */
function initDeleteAccount(accessToken) {
    const errorMsg = document.querySelector('#verify-delete-dialog > section > p.error');

    el.verifyInput.addEventListener('input', () => {
        if (el.verifyInput.value === 'DELETE') {
            el.confirmDeleteBtn.disabled = false;
        } else {
            el.confirmDeleteBtn.disabled = true;
        }
    });

    el.confirmDeleteBtn.addEventListener('click', async () => {
        const confirmDeleteBtnOrigText = el.confirmDeleteBtn.textContent;
        try {
            el.confirmDeleteBtn.textContent = 'Deleting Account...';
            await deleteAccount(accessToken);
            errorMsg.classList.add('hide');
        } catch (err) {
            console.error(err);
            el.confirmDeleteBtn.textContent = confirmDeleteBtnOrigText;
            errorMsg.classList.remove('hide');
        }
    });
}


// Init
// ----------------------------------------------
async function init() {
    initCoreUI();
    initDeleteDialog();
    const token = await authorize();
    initDeleteAccount(token);
}

window.addEventListener('load', init);
