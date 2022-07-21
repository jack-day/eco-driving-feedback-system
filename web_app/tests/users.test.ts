import request from 'supertest';
import express from 'express';
import nock from 'nock';
import createJwt from './helpers/auth';
import pool from '../src/db';
import api from '../src/api';

const app = express();
app.use('/api', api);

describe('Users API Endpoints', () => {
    // Setup
    // ------------------------------------------
    const mockUserID = 'user_one';
    let jwt: string;
    let jwtWithoutAccount: string;
    
    beforeAll(async () => {
        jwt = await createJwt(mockUserID);
        jwtWithoutAccount = await createJwt('no-account');
    });

    afterAll(() => {
        nock.cleanAll();
        pool.end();
    });

    afterEach(async () => {
        await pool.query('DELETE FROM usr');
    });


    // POST /users/
    // ------------------------------------------
    describe('POST /users/', () => {
        it('inserts new user into database', async () => {
            const response = await request(app)
                .post('/api/users')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(201);

            const { rows } = await pool.query(
                'SELECT * FROM usr WHERE auth0_user_id = $1',
                [mockUserID]
            );
            expect(rows).toHaveLength(1);
            expect(rows[0]).toHaveProperty('usr_id');
            expect(rows[0].auth0_user_id).toBe(mockUserID);
        });

        it('responds with 400 when user already exists', async () => {
            await pool.query(
                'INSERT INTO usr (auth0_user_id) VALUES ($1)',
                [mockUserID]
            );

            const response = await request(app)
                .post('/api/users')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(400);
            expect(response.text).toBe('User already exists');
        });

        it('responds with 401 when not given a valid token', async () => {
            const response = await request(app)
                .post('/api/users')
                .set('Authorization', `Bearer `)
                .send();
            expect(response.statusCode).toBe(401);
        });
    });


    // DELETE /myself/
    // ------------------------------------------
    describe('DELETE /myself/', () => {
        it('deletes the user from the database', async () => {
            await pool.query(
                'INSERT INTO usr (auth0_user_id) VALUES ($1)',
                [mockUserID]
            );
            
            const response = await request(app)
                .delete('/api/myself')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);

            const { rows } = await pool.query('SELECT * FROM usr');
            expect(rows).toHaveLength(0);
        });

        it('responds with 401 when not given a valid token', async () => {
            const response = await request(app)
                .delete('/api/myself')
                .set('Authorization', `Bearer `)
                .send();
            expect(response.statusCode).toBe(401);
        });

        it('responds with 401 when user is not registered', async () => {
            const response = await request(app)
                .delete('/api/myself')
                .set('Authorization', `Bearer ${jwtWithoutAccount}`)
                .send();
            expect(response.statusCode).toBe(401);
        });
    });


    // GET /myself/registered
    // ------------------------------------------
    describe('GET /myself/registered', () => {
        it('responds with 200 for a registered user', async () => {
            await pool.query(
                'INSERT INTO usr (auth0_user_id) VALUES ($1)',
                [mockUserID]
            );

            const response = await request(app)
                .get('/api/myself/registered')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
        });

        it('responds with 204 for an unregistered user', async () => {
            const response = await request(app)
                .get('/api/myself/registered')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(204);
        });

        it('responds with 401 when not given a valid token', async () => {
            const response = await request(app)
                .get('/api/myself/registered')
                .set('Authorization', `Bearer `)
                .send();
            expect(response.statusCode).toBe(401);
        });
    });
});
