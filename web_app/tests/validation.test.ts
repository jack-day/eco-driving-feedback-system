import { jest } from '@jest/globals';
import request from 'supertest';
import express, { Handler } from 'express';
import Joi from 'joi';
import {
    json,
    validateParams,
    validateQueryParams,
    validateBody
} from '../src/validation';

const app = express();
const handler = jest.fn(((req, res) => res.sendStatus(200)) as Handler);

// json
// ----------------------------------------------
describe('json', () => {
    app.post('/json', json(), handler); // Setup route

    it('passes to next function when body json is valid', async () => {
        const response = await request(app)
            .post('/json')
            .type('json')
            .send('{"prop": 0}');
        expect(handler).toHaveBeenCalled();
        expect(response.statusCode).toBe(200);
    });

    it('responds with 400 when there is a syntax error in body json', async () => {
        const response = await request(app)
            .post('/json')
            .type('json')
            .send("{'prop': 0}");
        expect(response.statusCode).toBe(400);
        expect(response.text).toBe("Unexpected token ' in JSON at position 1");
    });
});


// validateParams
// ----------------------------------------------
describe('validateParams', () => {
    // Setup
    // ------------------------------------------
    let schema: Joi.AnySchema;

    const validateParamsMock = ((req, res, next) => {
        validateParams(schema)(req, res, next);
    }) as Handler;

    app.get('/validateParams/:param', validateParamsMock, handler);


    // Tests
    // ------------------------------------------
    it('passes to next function when req params matches schema', async () => {
        schema = Joi.object({ param: Joi.string().length(4) });
        const response = await request(app).get('/validateParams/test').send();
        expect(handler).toHaveBeenCalled();
        expect(response.statusCode).toBe(200);
    });
    
    it('responds with 404 when req params not matching schema', async () => {
        schema = Joi.object({ param: Joi.string().length(6) });
        const response = await request(app).get('/validateParams/test').send();
        expect(response.statusCode).toBe(404);
    });
});


// validateQueryParams
// ----------------------------------------------
describe('validateQueryParams', () => {
    // Setup
    // ------------------------------------------
    let schema: Joi.AnySchema;
    app.get('/validateQueryParams', json(), (req, res, next) => {
        validateQueryParams(schema)(req, res, next);
    }, handler);


    // Tests
    // ------------------------------------------
    it('passes to next function when req query params match schema', async () => {
        schema = Joi.object({ query: Joi.string().length(4).required() });
        const response = await request(app)
            .get('/validateQueryParams?query=test');
        expect(handler).toHaveBeenCalled();
        expect(response.statusCode).toBe(200);
    });
    
    it('responds with 400 and errors when req query params not matching schema', async () => {
        schema = Joi.object({ query: Joi.string().length(4).required() });
        const response = await request(app)
            .get('/validateQueryParams?query=bad');
        expect(response.statusCode).toBe(400);
        expect(response.body.errors).toHaveLength(1);
    });

    it('responds with errors for each object schema when using joi.alternatives()', async () => {
        schema = Joi.alternatives().try(
            Joi.object({ query: Joi.string().email().required() }),
            Joi.object({ query: Joi.string().isoDate().required() })
        );

        const response = await request(app)
            .get('/validateQueryParams?query=bad');
        expect(response.statusCode).toBe(400);
        expect(response.body.errors).toHaveLength(3);
        expect(response.body.errors[0])
            .toBe('request query parameters does not match any of the allowed schemas');
        expect(response.body.errors[1])
            .toBe('schema 0 failed because "query" must be a valid email');
        expect(response.body.errors[2])
            .toBe('schema 1 failed because "query" must be in iso format');
    });
});


// validateBody
// ----------------------------------------------
describe('validateBody', () => {
    // Setup
    // ------------------------------------------
    let schema: Joi.AnySchema;
    app.post('/validateBody', json(), (req, res, next) => {
        validateBody(schema)(req, res, next);
    }, handler);


    // Tests
    // ------------------------------------------
    it('passes to next function when req body matches schema', async () => {
        schema = Joi.object({
            prop: Joi.number().greater(0).required(),
        });

        const response = await request(app)
            .post('/validateBody')
            .send({ prop: 1 });
        expect(handler).toHaveBeenCalled();
        expect(response.statusCode).toBe(200);
    });
    
    it('responds with 400 and errors when req body not matching schema', async () => {
        schema = Joi.object({
            prop: Joi.number().greater(0).required(),
        });

        const response = await request(app)
            .post('/validateBody')
            .send({ prop: 0 });
        expect(response.statusCode).toBe(400);
        expect(response.body.errors).toHaveLength(1);
    });

    it(`replaces '"value"' with 'request body' in error messages`, async () => {
        schema = Joi.boolean().required();
        const response = await request(app)
            .post('/validateBody')
            .send({});
        expect(response.statusCode).toBe(400);
        expect(response.body.errors)
            .toStrictEqual(['request body must be a boolean']);
    });

    it('responds with single type error when type does not match any joi.alternatives()', async () => {
        schema = Joi.alternatives().try(
            Joi.boolean().required(),
            Joi.number().required()
        );

        const response = await request(app)
            .post('/validateBody')
            .send({});
        expect(response.statusCode).toBe(400);
        expect(response.body.errors).toHaveLength(1);
    });

    it('responds with errors for each object schema when using joi.alternatives()', async () => {
        schema = Joi.alternatives().try(
            Joi.object({ prop: Joi.boolean().required() }),
            Joi.object({ prop: Joi.number().required() })
        );

        const response = await request(app)
            .post('/validateBody')
            .send({ prop: 'wrong' });
        expect(response.statusCode).toBe(400);
        expect(response.body.errors).toHaveLength(3);
        expect(response.body.errors[0])
            .toBe('request body does not match any of the allowed schemas');
        expect(response.body.errors[1])
            .toBe('schema 0 failed because "prop" must be a boolean');
        expect(response.body.errors[2])
            .toBe('schema 1 failed because "prop" must be a number');
    });
});
