import { Router } from 'express';
import users from './users/routes';
import journeys from './journeys/routes';
import scores from './scores/routes';
import { handleClientErrors } from './errors';

const api = Router();

api.use(users);
api.use(journeys);
api.use(scores);
api.use(handleClientErrors);

export default api;
