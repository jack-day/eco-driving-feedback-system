import { jest } from '@jest/globals';
import request from 'supertest';
import express, { Handler } from 'express';
import nock from 'nock';
import createJwt from './helpers/auth';
import pool from '../src/db';
import { requireAuth, requireAccount } from '../src/auth';

const app = express();
const handler = jest.fn(((req, res) => res.sendStatus(250)) as Handler);
app.get('/requireAuth', requireAuth, handler);
app.get('/requireAccount', requireAccount, handler);

describe('Auth Middleware', () => {
    const mockUserID = 'auth_user';
    let jwt: string;
    
    beforeAll(async () => {
        jwt = await createJwt(mockUserID);
    });

    afterAll(() => {
        nock.cleanAll();
        pool.end();
    });


    describe('requireAuth', () => {
        it('calls next middleware function when given valid token', async () => {
            const response = await request(app)
                .get('/requireAuth')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(handler).toHaveBeenCalled();
            expect(response.statusCode).toBe(250);
        });

        it('responds with 401 when not given a valid token', async () => {
            const response = await request(app)
                .get('/requireAuth')
                .set('Authorization', `Bearer `)
                .send();
            expect(response.statusCode).toBe(401);
        });
    });


    describe('requireAccount', () => {
        it("responds with 401 when user isn't registered", async () => {
            const response = await request(app)
                .get('/requireAccount')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(401);
        });
    });
});