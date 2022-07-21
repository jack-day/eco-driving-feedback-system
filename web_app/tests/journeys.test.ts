import request from 'supertest';
import express from 'express';
import nock from 'nock';
import createJwt from './helpers/auth';
import pool from '../src/db';
import { insertUser } from '../src/users/data_access';
import { insertJourney } from '../src/journeys/data_access';
import { journey, journeyNoID } from '../src/journeys/types';
import api from '../src/api';

// Re-used Test Data
// ----------------------------------------------
const validJourneys: journeyNoID[][] = [
    [{
        start: '2022-01-01T10:00:00.000Z',
        end: '2022-01-01T10:00:01.000Z',
        distance: 0,
        idleSecs: 1,
    }],
    [{
        start: '2022-01-01T10:00:00.000Z',
        end: '2022-01-01T10:00:01.000Z',
        distance: 0,
        idleSecs: 1,
        gsiAdh: 2,
    }],
];

const invalidJourneys: Record<string, any>[][] = [
    [{}],
    [{ start: '2022-01-01T10:00:00.000Z' }],
    [{ end: '2022-01-01T11:00:00.000Z' }],
    [{ idleSecs: 0 }],
    [{ distance: 0 }],
    [{ gsiAdh: 0 }],
    [{
        start: '2022-01-01T10:00:00.000Z',
        end: '2022-01-01T11:00:00.000Z',
    }],
    [{
        start: '2022-01-01T10:00:00.000Z',
        distance: 0,
    }],
    [{
        start: '2022-01-01T10:00:00.000Z',
        idleSecs: 0,
    }],
    [{
        end: '2022-01-01T11:00:00.000Z',
        distance: 0,
    }],
    [{
        end: '2022-01-01T11:00:00.000Z',
        idleSecs: 0,
    }],
    [{
        distance: 0,
        idleSecs: 0,
    }],
    [{
        start: '2022-01-01T10:00:00.000Z',
        end: '2022-01-01T11:00:00.000Z',
        distance: 0,
    }],
    [{
        start: '2022-01-01T10:00:00.000Z',
        end: '2022-01-01T11:00:00.000Z',
        idleSecs: 0,
    }],
    [{
        start: '2022-01-01T10:00:00.000Z',
        end: '2022-01-01T10:00:00.000Z',
        distance: 0,
        idleSecs: 0,
    }],
    [{
        start: '2022-01-01T10:00:00.000Z',
        end: '2022-01-01T11:00:00.000Z',
        distance: -1,
        idleSecs: 0,
    }],
    [{
        start: '2022-01-01T10:00:00.000Z',
        end: '2022-01-01T11:00:00.000Z',
        distance: 0,
        idleSecs: -1,
    }],
    [{
        start: '2022-01-01T10:00:00.000Z',
        end: '2022-01-01T11:00:00.000Z',
        distance: 0,
        idleSecs: 0,
        gsiAdh: -1,
    }],
    [{
        start: '2022-01-01T10:00:00.000Z',
        end: '2022-01-01T11:00:00.000Z',
        distance: 0,
        idleSecs: 0,
        gsiAdh: 101,
    }],
];


// Setup
// ----------------------------------------------
const app = express();
app.use('/api', api);


// Tests
// ----------------------------------------------
describe('Journeys API Endpoints', () => {
    // Setup
    // ------------------------------------------
    const mockAuth0UserID = 'journey_user';
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


    // GET /journeys/:journeyID
    // ------------------------------------------
    describe('GET /journeys/:journeyID', () => {
        // Setup
        // --------------------------------------
        const mockJourneys = [
            {
                journeyID: 0,
                start: '2022-01-01T10:00:00.000Z',
                end: '2022-01-01T11:00:00.000Z',
                distance: 1,
                idleSecs: 2,
                gsiAdh: 3,
            },
            {
                journeyID: 1,
                start: '2022-01-01T08:00:00.000Z',
                end: '2022-01-01T09:00:00.000Z',
                distance: 1,
                idleSecs: 2,
            },
            {
                journeyID: 2,
                start: '2022-01-01T08:00:00.000Z',
                end: '2022-01-01T09:00:00.000Z',
                distance: 2,
                idleSecs: 1,
            },
        ];

        beforeAll(async () => {
            for (const mockJourney of mockJourneys) {
                mockJourney.journeyID = await insertJourney(
                    mockAuth0UserID, mockJourney
                );
            }
        });

        afterAll(async () => {
            await pool.query('DELETE FROM journey');
        });


        // Tests
        // --------------------------------------
        it('responds with stored journeys', async () => {
            const response = await request(app)
                .get('/api/journeys/')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toStrictEqual(mockJourneys);
        });

        it('responds with journeys within a given limit', async () => {
            const response = await request(app)
                .get('/api/journeys?limit=3')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toStrictEqual(mockJourneys);
        });

        it('excludes journeys over a given limit', async () => {
            const response = await request(app)
                .get('/api/journeys?limit=1')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toStrictEqual([mockJourneys[0]]);
        });

        it('responds with journeys after a given offset', async () => {
            const response = await request(app)
                .get('/api/journeys?offset=2')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toStrictEqual([mockJourneys[2]]);
        });

        test('limit and offest query parameters work together', async () => {
            const response = await request(app)
                .get('/api/journeys?limit=1&offset=1')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toStrictEqual([mockJourneys[1]]);
        });

        it("doesn't include the More-Entries header when limit is not given", async () => {
            const response = await request(app)
                .get('/api/journeys?offset=1')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toHaveLength(2);
            expect(response.headers['more-entries']).toBeUndefined();
        });

        it('responds with the More-Entries header set to true when more are available', async () => {
            const response = await request(app)
                .get('/api/journeys?limit=1')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toHaveLength(1);
            expect(response.headers['more-entries']).toBe('true');
        });

        it('responds with the More-Entries header set to false when no more are available', async () => {
            const response = await request(app)
                .get('/api/journeys?limit=1&offset=2')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toHaveLength(1);
            expect(response.headers['more-entries']).toBe('false');
        });

        it.each([
            ['-1'], ['1.1'], ['a'], ['false'], [''],
        ])('responds with 400 when limit query parameter is invalid', async (
            limit: string
        ) => {
            const response = await request(app)
                .get(`/api/journeys?limit=${limit}`)
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(400);
            expect(response.body.errors).toHaveLength(1);
        });

        it.each([
            ['-1'], ['1.1'], ['a'], ['false'], [''],
        ])('responds with 400 when offset query parameter is invalid', async (
            offset: string
        ) => {
            const response = await request(app)
                .get(`/api/journeys?offset=${offset}`)
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(400);
            expect(response.body.errors).toHaveLength(1);
        });

        it('responds with 401 when not given a valid token', async () => {
            const response = await request(app)
                .get('/api/journeys/')
                .set('Authorization', `Bearer `)
                .send();
            expect(response.statusCode).toBe(401);
        });

        it('responds with 401 when user is not registered', async () => {
            const response = await request(app)
                .get('/api/journeys/')
                .set('Authorization', `Bearer ${jwtWithoutAccount}`)
                .send();
            expect(response.statusCode).toBe(401);
        });
    });

    
    // POST /journeys/
    // ------------------------------------------
    describe('POST /journeys/', () => {
        beforeAll(async () => {
            // Start sequence functions for the session
            await pool.query(`SELECT nextval(
                pg_get_serial_sequence('journey', 'journey_id'))`);
        });

        afterEach(async () => {
            await pool.query('DELETE FROM journey');
        });

        it.each(
            validJourneys
        )('inserts new journey into database and returns journeyID', async (body: journeyNoID) => {
            const { rows: journeyIDRows } = await pool.query(`SELECT currval(
                pg_get_serial_sequence('journey', 'journey_id'))`);
            const expectedJourneyID: number = journeyIDRows[0].currval + 1;

            const response = await request(app)
                .post('/api/journeys')
                .set('Authorization', `Bearer ${jwt}`)
                .send(body);
            expect(response.statusCode).toBe(201);
            expect(response.body).toStrictEqual({ id: expectedJourneyID });

            const { rows } = await pool.query(
                'SELECT * FROM journey WHERE usr_id = $1',
                [mockUserID]
            );
            expect(rows).toHaveLength(1);
            expect(rows[0]).toStrictEqual({
                journey_id: expectedJourneyID,
                usr_id: mockUserID,
                start_time: body.start ? new Date(body.start) : null,
                end_time: body.end ? new Date(body.end) : null,
                distance: body.distance ?? null,
                idle_secs: body.idleSecs ?? null,
                gsi_adh: body.gsiAdh ?? null,
            });
        });

        it.each(
            invalidJourneys
        )('responds with 400 when body does not pass validation', async (body) => {
            const response = await request(app)
                .post('/api/journeys')
                .set('Authorization', `Bearer ${jwt}`)
                .send(body);
            expect(response.statusCode).toBe(400);
        });

        it('responds with 401 when not given a valid token', async () => {
            const response = await request(app)
                .post('/api/journeys')
                .set('Authorization', `Bearer `)
                .send({ prop: 'wrong' });
            expect(response.statusCode).toBe(401);
        });

        it('responds with 401 when user is not registered', async () => {
            const response = await request(app)
                .post('/api/journeys')
                .set('Authorization', `Bearer ${jwtWithoutAccount}`)
                .send({ prop: 'wrong' });
            expect(response.statusCode).toBe(401);
        });
    });


    // GET /journeys/:journeyID
    // ------------------------------------------
    describe('GET /journeys/:journeyID', () => {
        // Setup
        // --------------------------------------
        const mockJourney = {
            journeyID: 0,
            start: '2022-01-01T10:00:00.000Z',
            end: '2022-01-01T11:00:00.000Z',
            distance: 1,
            idleSecs: 2,
            gsiAdh: 3,
        };

        beforeAll(async () => {
            mockJourney.journeyID = await insertJourney(
                mockAuth0UserID, mockJourney
            );
        });

        afterAll(async () => {
            await pool.query('DELETE FROM journey');
        });


        // Tests
        // --------------------------------------
        it('responds with journey data for an existing journey', async () => {
            const response = await request(app)
                .get(`/api/journeys/${mockJourney.journeyID}`)
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toStrictEqual(mockJourney);
        });

        it('removes null values from response object', async () => {
            const journey: journey = {...mockJourney};
            delete journey.gsiAdh;
            journey.journeyID = await insertJourney(
                mockAuth0UserID, journey
            );

            const response = await request(app)
                .get(`/api/journeys/${journey.journeyID}`)
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(200);
            expect(response.body).toStrictEqual(journey);
        });

        it.each([
            ['a'],
            ['-1'],
            ['1.0'],
            ['1a'],
            ['a1'],
        ])('responds with 404 for an invalid journeyID', async (journeyID) => {
            const response = await request(app)
                .get(`/api/journeys/${journeyID}`)
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(404);
        });

        it('responds with 401 when not given a valid token', async () => {
            const response = await request(app)
                .get(`/api/journeys/${mockJourney.journeyID}`)
                .set('Authorization', `Bearer `)
                .send();
            expect(response.statusCode).toBe(401);
        });

        it('responds with 401 when user is not registered', async () => {
            const response = await request(app)
                .get(`/api/journeys/${mockJourney.journeyID}`)
                .set('Authorization', `Bearer ${jwtWithoutAccount}`)
                .send();
            expect(response.statusCode).toBe(401);
        });

        it('responds with 404 for a non-existent journey', async () => {
            const response = await request(app)
                .get('/api/journeys/0')
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(404);
        });
    });

    
    // PUT /journeys/:journeyID
    // ------------------------------------------
    describe('PUT /journeys/:journeyID', () => {
        // Setup
        // --------------------------------------
        let mockJourneyID: number;

        beforeAll(async () => {
            mockJourneyID = await insertJourney(mockAuth0UserID, {
                start: '2022-01-01T10:00:00.000Z',
                end: '2022-01-01T11:00:00.000Z',
                distance: 1,
                idleSecs: 2,
                gsiAdh: 3,
            });
        });

        afterAll(async () => {
            await pool.query('DELETE FROM journey');
        });


        // Tests
        // --------------------------------------
        it.each(
            validJourneys
        )('updates journey with body data', async (body: journeyNoID) => {
            const response = await request(app)
                .put(`/api/journeys/${mockJourneyID}`)
                .set('Authorization', `Bearer ${jwt}`)
                .send(body);
            expect(response.statusCode).toBe(204);

            const { rows } = await pool.query(
                'SELECT * FROM journey WHERE usr_id = $1',
                [mockUserID]
            );
            expect(rows).toHaveLength(1);
            expect(rows[0]).toStrictEqual({
                journey_id: mockJourneyID,
                usr_id: mockUserID,
                start_time: body.start ? new Date(body.start) : null,
                end_time: body.end ? new Date(body.end) : null,
                distance: body.distance ?? null,
                idle_secs: body.idleSecs ?? null,
                gsi_adh: body.gsiAdh ?? null,
            });
        });

        it.each([
            ['a'],
            ['-1'],
            ['1.0'],
            ['1a'],
            ['a1'],
        ])('responds with 404 for an invalid journeyID', async (journeyID) => {
            const response = await request(app)
                .put(`/api/journeys/${journeyID}`)
                .set('Authorization', `Bearer ${jwt}`)
                .send();
            expect(response.statusCode).toBe(404);
        });

        it.each(
            invalidJourneys
        )('responds with 400 when body does not pass validation', async (body) => {
            const response = await request(app)
                .put(`/api/journeys/${mockJourneyID}`)
                .set('Authorization', `Bearer ${jwt}`)
                .send(body);
            expect(response.statusCode).toBe(400);
        });

        it('responds with 401 when not given a valid token', async () => {
            const response = await request(app)
                .put(`/api/journeys/${mockJourneyID}`)
                .set('Authorization', `Bearer `)
                .send({ prop: 'wrong' });
            expect(response.statusCode).toBe(401);
        });

        it('responds with 401 when user is not registered', async () => {
            const response = await request(app)
                .put(`/api/journeys/${mockJourneyID}`)
                .set('Authorization', `Bearer ${jwtWithoutAccount}`)
                .send({ prop: 'wrong' });
            expect(response.statusCode).toBe(401);
        });

        it('responds with 404 for a non-existent journey', async () => {
            const response = await request(app)
                .put('/api/journeys/0')
                .set('Authorization', `Bearer ${jwt}`)
                .send({
                    start: '2022-01-01T10:00:00.000Z',
                    end: '2022-01-01T11:00:00.000Z',
                    distance: 1,
                    idleSecs: 2,
                    gsiAdh: 3,
                });
            expect(response.statusCode).toBe(404);
        });
    });
});
