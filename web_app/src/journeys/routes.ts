import Joi from 'joi';
import PromiseRouter from 'express-promise-router';
import { requireAccount } from '../auth';
import { json, validateParams, validateQueryParams, validateBody } from '../validation';
import { journeysGet, journeysPost, journeyGet, journeysPut } from './controllers';

// Validation Schemas
// ----------------------------------------------
const paramsSchema = Joi.object({
    journeyID: Joi.string().regex(/^\d+$/),
});

const queryParamSchema = Joi.object({
    limit: Joi.string().regex(/^\d+$/),
    offset: Joi.string().regex(/^\d+$/),
}).options({ allowUnknown: true });

const bodySchema = Joi.object({
    start: Joi.date().iso().required(),
    end: Joi.date().iso().greater(Joi.ref('start')).required(),
    distance: Joi.number().min(0).required(),
    idleSecs: Joi.number().integer().min(0).required(),
    gsiAdh: Joi.number().min(0).max(100),
});


// Routes
// ----------------------------------------------
const router = PromiseRouter();

router.use(requireAccount, json());
router.get('/journeys/', validateQueryParams(queryParamSchema), journeysGet);
router.post('/journeys/', validateBody(bodySchema), journeysPost);
router.get('/journeys/:journeyID', validateParams(paramsSchema), journeyGet);
router.put('/journeys/:journeyID',
    validateParams(paramsSchema), validateBody(bodySchema), journeysPut);

export default router;
