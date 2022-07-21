import Joi from 'joi';
import PromiseRouter from 'express-promise-router';
import { requireAccount } from '../auth';
import { json, validateQueryParams, validateBody } from '../validation';
import { scoresGet, scoresPost } from './controllers';

// Validation Schemas
// ----------------------------------------------
const queryParamSchema = Joi.object({
    type: Joi.string().valid(
        'ecoDriving',
        'drivAccSmoothness',
        'startAccSmoothness',
        'decSmoothness',
        'gsiAdh',
        'speedLimitAdh',
        'motorwaySpeed',
        'idleDuration',
        'journeyIdlePct',
        'journeyDistance'
    ),
    limit: Joi.string().regex(/^\d+$/),
    maxDaysAgo: Joi.string().regex(/^\d+$/),
}).options({ allowUnknown: true });

const bodySchema = Joi.object({
    calculatedAt: Joi.date().iso().required(),
    ecoDriving: Joi.number().integer().min(0).max(100).required(),
    drivAccSmoothness: Joi.number().integer().min(0).max(100),
    startAccSmoothness: Joi.number().integer().min(0).max(100),
    decSmoothness: Joi.number().integer().min(0).max(100),
    gsiAdh: Joi.number().integer().min(0).max(100),
    speedLimitAdh: Joi.number().integer().min(0).max(100),
    motorwaySpeed: Joi.number().integer().min(0).max(100),
    idleDuration: Joi.number().integer().min(0).max(100),
    journeyIdlePct: Joi.number().integer().min(0).max(100),
    journeyDistance: Joi.number().integer().min(0).max(100),
});

// Routes
// ----------------------------------------------
const router = PromiseRouter();

router.use(requireAccount, json());
router.get('/scores/', validateQueryParams(queryParamSchema), scoresGet);
router.post('/scores/', validateBody(bodySchema), scoresPost);

export default router;
