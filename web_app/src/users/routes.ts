import PromiseRouter from 'express-promise-router';
import { requireAuth, requireAccount } from '../auth';
import { usersPost, myselfDelete, myselfRegistered } from './controllers';

const router = PromiseRouter();

router.post('/users/', requireAuth, usersPost);
router.delete('/myself', requireAccount, myselfDelete);
router.get('/myself/registered', requireAuth, myselfRegistered);

export default router;
