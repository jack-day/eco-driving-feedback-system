import request from 'supertest';
import express from 'express';
import nock from 'nock';
import createJwt from './helpers/auth';
import pool from '../src/db';
import { insertUser } from '../src/users/data_access';
import { insertScores } from '../src/scores/data_access';
import { scores } from '../src/scores/types';
import api from '../src/api';

const app = express();
app.use('/api', api);

describe('Scores API Endpoints', () => {
    // Setup
    // ------------------------------------------
    const mockAuth0UserID = 'scores_user';
    let jwt: string;
    let jwtWithoutAccount: string;
    let mockUserID: number;
    
    beforeAll(async () => {
        jwt = await createJwt(mockAuth0UserID);
        mockUserID = await insertUser(mockAuth0UserID);
        jwtWithoutAccount = await createJwt('no-account');
    });

    afterAll(async () => {
        await pool.query('DELETE FROM usr');
        nock.cleanAll();
        pool.end();
    });

    
    // GET /scores/
    // ------------------------------------------
    describe('GET /scores/', () => {
        // Setup
        // --------------------------------------
        const now = new Date();
        const mockScores: scores = {
            calculatedAt: now.toISOString(),
            ecoDriving: 1,
            drivAccSmoothness: 2,
            startAccSmoothness: 3,
            decSmoothness: 4,
            gsiAdh: 5,
            speedLimitAdh: 6,
            motorwaySpeed: 7,
            idleDuration: 8,
            journeyIdlePct: 9,
            journeyDistance: 10,
        };

        const mockScoresOld: scores = {
            calculatedAt: new Date(new Date().setDate(
                now.getDate() - 5)).toISOString(),
            ecoDriving: 1,
            drivAccSmoothness: 2,
            startAccSmoothness: 3,
            decSmoothness: 4,
            gsiAdh: 5,
        };

        beforeAll(async () => {
            await insertScores(mockAuth0UserID, mockScores);
            await insertScores(mockAuth0UserID, mockScoresOld);
        });

        afterAll(async () => {
            await pool.query('DELETE FROM scores');
        });


        // Tests
        // --------------------------------------
        it("responds with all of the user's scores", async () => {
            const response = await request(app)
                .get('/api/scores')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toStrictEqual([mockScores, mockScoresOld]);
        });

        it.each([
            ['ecoDriving'],
            ['drivAccSmoothness'],
            ['startAccSmoothness'],
            ['decSmoothness'],
            ['gsiAdh'],
            ['speedLimitAdh'],
            ['motorwaySpeed'],
            ['idleDuration'],
            ['journeyIdlePct'],
            ['journeyDistance'],
        ])('responds only with score of type given in query parameters', async (
            type: string
        ) => {
            const expectedScores: Record<string, any> = {
                calculatedAt: mockScores.calculatedAt };
            const expectedScoresOld: Record<string, any> = {
                calculatedAt: mockScoresOld.calculatedAt };

            let typeVal;
            if ((typeVal = (mockScores as Record<string, any>)[type])) {
                expectedScores[type] = typeVal;
            }

            let typeValOld;
            if ((typeValOld = (mockScoresOld as Record<string, any>)[type])) {
                expectedScoresOld[type] = typeValOld;
            }

            const response = await request(app)
                .get(`/api/scores?type=${type}`)
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toStrictEqual([
                expectedScores, expectedScoresOld,
            ]);
        });

        it('responds with scores within the limit', async () => {
            const response = await request(app)
                .get('/api/scores?limit=2')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toStrictEqual([mockScores, mockScoresOld]);
        });

        it('responds with scores, excluding scores over the row limit', async () => {
            const response = await request(app)
                .get('/api/scores?limit=1')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toStrictEqual([mockScores]);
        });

        it('responds with scores up to and on the given max days ago', async () => {
            const response = await request(app)
                .get('/api/scores?maxDaysAgo=5')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toStrictEqual([mockScores, mockScoresOld]);
        });
        
        it('responds with scores, excluding scores over the given max days ago', async () => {
            const response = await request(app)
                .get('/api/scores?maxDaysAgo=4')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toStrictEqual([mockScores]);
        });

        it.each([
            ['-1', 1], ['1.1', 1], ['a', 1], ['false', 1], ['', 2],
        ])('responds with 400 when type query parameter is invalid', async (
            type: string, expectedErrorCount: number
        ) => {
            const response = await request(app)
                .get(`/api/scores?type=${type}`)
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(400);
            expect(response.body.errors).toHaveLength(expectedErrorCount);
        });

        it.each([
            ['-1'], ['1.1'], ['a'], ['false'], [''],
        ])('responds with 400 when limit query parameter is invalid', async (
            maxDaysAgo: string
        ) => {
            const response = await request(app)
                .get(`/api/scores?limit=${maxDaysAgo}`)
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(400);
            expect(response.body.errors).toHaveLength(1);
        });

        it.each([
            ['-1'], ['1.1'], ['a'], ['false'], [''],
        ])('responds with 400 when maxDaysAgo query parameter is invalid', async (
            maxDaysAgo: string
        ) => {
            const response = await request(app)
                .get(`/api/scores?maxDaysAgo=${maxDaysAgo}`)
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(400);
            expect(response.body.errors).toHaveLength(1);
        });

        it('responds with 401 when not given a valid token', async () => {
            const response = await request(app)
                .get('/api/scores')
                .set('Authorization', `Bearer `)
                .send();
            expect(response.statusCode).toBe(401);
        });
                
        it('responds with 401 when user is not registered', async () => {
            const response = await request(app)
                .get('/api/scores')
                .set('Authorization', `Bearer ${jwtWithoutAccount}`)
                .send();
            expect(response.statusCode).toBe(401);
        });
    });


    // POST /scores/
    // ------------------------------------------
    describe('POST /scores/', () => {
        afterEach(async () => {
            await pool.query('DELETE FROM scores');
        });

        it.each([
            [{ calculatedAt: '2022-01-01T10:00:00.000Z', ecoDriving: 10 }],
            [{
                calculatedAt: '2022-01-01T10:00:00.000Z',
                ecoDriving: 1,
                drivAccSmoothness: 2,
                startAccSmoothness: 3,
                decSmoothness: 4,
                gsiAdh: 5,
                speedLimitAdh: 6,
                motorwaySpeed: 7,
                idleDuration: 8,
                journeyIdlePct: 9,
                journeyDistance: 10,
            }],
        ])('inserts new scores into database', async (body: scores) => {
            const response = await request(app)
                .post('/api/scores')
                .set('Authorization', `Bearer ${jwt}`)
                .send(body);
            expect(response.statusCode).toBe(201);

            const { rows } = await pool.query(
                'SELECT * FROM scores WHERE usr_id = $1',
                [mockUserID]
            );
            expect(rows).toHaveLength(1);
            expect(rows[0]).toStrictEqual({
                usr_id: mockUserID,
                calculated_at: new Date(body.calculatedAt),
                eco_driving: body.ecoDriving,
                driv_acc_smoothness: body.drivAccSmoothness ?? null,
                start_acc_smoothness: body.startAccSmoothness ?? null,
                dec_smoothness: body.decSmoothness ?? null,
                gsi_adh: body.gsiAdh ?? null,
                speed_limit_adh: body.speedLimitAdh ?? null,
                motorway_speed: body.motorwaySpeed ?? null,
                idle_duration: body.idleDuration ?? null,
                journey_idle_pct: body.journeyIdlePct ?? null,
                journey_distance: body.journeyDistance ?? null,
            });
        });

        it.each([
            [{}, 2],
            [{ calculatedAt: '2022-01-01T10:00:00.000Z' }, 1],
            [{ ecoDriving: 0 }, 1],
            [{
                calculatedAt: '2022-01-01T10:00:00.000Z',
                ecoDriving: -1,
                drivAccSmoothness: -1,
                startAccSmoothness: -1,
                decSmoothness: -1,
                gsiAdh: -1,
                speedLimitAdh: -1,
                motorwaySpeed: -1,
                idleDuration: -1,
                journeyIdlePct: -1,
                journeyDistance: -1,
            }, 10],
            [{
                calculatedAt: '2022-01-01T10:00:00.000Z',
                ecoDriving: 101,
                drivAccSmoothness: 101,
                startAccSmoothness: 101,
                decSmoothness: 101,
                gsiAdh: 101,
                speedLimitAdh: 101,
                motorwaySpeed: 101,
                idleDuration: 101,
                journeyIdlePct: 101,
                journeyDistance: 101,
            }, 10],
            [{
                calculatedAt: '',
                ecoDriving: '101',
                drivAccSmoothness: '101',
                startAccSmoothness: '101',
                decSmoothness: '101',
                gsiAdh: '101',
                speedLimitAdh: '101',
                motorwaySpeed: '101',
                idleDuration: '101',
                journeyIdlePct: '101',
                journeyDistance: '101',
            }, 11],
        ])('responds with 400 when body does not pass validation', async (
            body: Record<string, any>, exprectedErrCount: number
        ) => {
            const response = await request(app)
                .post('/api/scores')
                .set('Authorization', `Bearer ${jwt}`)
                .send(body);
            expect(response.statusCode).toBe(400);
            expect(response.body.errors.length).toBe(exprectedErrCount);
        });

        it('responds with 400 and error message when scores with same calculate time already exist', async () => {
            const body = {
                calculatedAt: '2022-01-01T10:00:00.000Z',
                ecoDriving: 10,
            };

            const firstResponse = await request(app)
                .post('/api/scores')
                .set('Authorization', `Bearer ${jwt}`)
                .send(body);
            expect(firstResponse.statusCode).toBe(201);

            const secondResponse = await request(app)
                .post('/api/scores')
                .set('Authorization', `Bearer ${jwt}`)
                .send(body);
            expect(secondResponse.statusCode).toBe(400);
            expect(secondResponse.text).toBe(
                'Scores calculated at that time already exist');
        });
        
        it('responds with 401 when not given a valid token', async () => {
            const response = await request(app)
                .post('/api/scores')
                .set('Authorization', `Bearer `)
                .send({ prop: 'wrong' });
            expect(response.statusCode).toBe(401);
        });
                
        it('responds with 401 when user is not registered', async () => {
            const response = await request(app)
                .post('/api/scores')
                .set('Authorization', `Bearer ${jwtWithoutAccount}`)
                .send({ prop: 'wrong' });
            expect(response.statusCode).toBe(401);
        });
    });
});
