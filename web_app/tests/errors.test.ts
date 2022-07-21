import { jest } from '@jest/globals';
import request from 'supertest';
import express, { ErrorRequestHandler } from 'express';
import { handleErrors, AppError, handleClientErrors, ClientError } from '../src/errors';

// handleErrors
// ----------------------------------------------
describe('handleErrors', () => {
    const handler = jest.fn();
    const consoleErrorSpy = jest.spyOn(global.console, 'error');
    const exitSpy = jest.spyOn(process, 'exit');

    const app = express();
    app.get('/', handler);
    app.use(handleErrors);

    it('responds with 500 when an error occurs', async () => {
        consoleErrorSpy.mockImplementationOnce(() => null);
        handler.mockImplementation(() => { throw new Error(); });

        const response = await request(app).get('/').send();
        expect(response.statusCode).toBe(500);
        expect(consoleErrorSpy).toHaveBeenCalled();
    });

    it('terminates the process if the error is fatal', async () => {
        consoleErrorSpy.mockImplementationOnce(() => null);
        exitSpy.mockImplementationOnce(
            (() => null) as jest.MockedFunction<typeof process.exit>);
        
        handler.mockImplementation(() => {
            throw new AppError({ isFatal: true });
        });

        const response = await request(app).get('/').send();
        expect(response.statusCode).toBe(500);
        expect(consoleErrorSpy).toHaveBeenCalled();
        expect(exitSpy).toHaveBeenCalledWith(5);
    });
});


// ClientError
// ----------------------------------------------
describe('ClientError', () => {
    it('sets httpCode if given', () => {
        const err = new ClientError({ httpCode: 405 });
        expect(err.httpCode).toBe(405);
    });

    it('defaults httpCode to 400 if not given', () => {
        const err = new ClientError();
        expect(err.httpCode).toBe(400);
    });

    it('throws error when given a status code under 400', () => {
        expect(() => {
            new ClientError({ httpCode: 399 });
        }).toThrowError('Invalid HTTP response status code, must be a 4xx client error response code');
    });

    it('throws error when given a status code above 499', () => {
        expect(() => {
            new ClientError({ httpCode: 500 });
        }).toThrowError('Invalid HTTP response status code, must be a 4xx client error response code');
    });
});


// handleClientErrors
// ----------------------------------------------
describe('handleClientErrors', () => {
    const handler = jest.fn();
    const mockErrorHandler = jest.fn(((err, req, res, next) => {  /* eslint-disable-line @typescript-eslint/no-unused-vars */
        res.sendStatus(550);
    }) as ErrorRequestHandler);

    const app = express();
    app.get('/', handler, handleClientErrors);
    app.use(mockErrorHandler);

    it('responds with 400 when a default ClientError is thrown', async () => {
        handler.mockImplementation(() => { throw new ClientError(); });
        const response = await request(app).get('/').send();
        expect(response.statusCode).toBe(400);
    });

    it('responds with set httpCode when an ClientError is thrown', async () => {
        handler.mockImplementation(() => {
            throw new ClientError({ httpCode: 410 });
        });
        const response = await request(app).get('/').send();
        expect(response.statusCode).toBe(410);
    });

    it('responds with set message when an ClientError is thrown', async () => {
        handler.mockImplementation(() => {
            throw new ClientError({ message: 'test' });
        });
        const response = await request(app).get('/').send();
        expect(response.statusCode).toBe(400);
        expect(response.text).toBe('test');
    });

    it('passes any non-ClientError errors to the next middleware', async () => {
        const err = new Error();
        handler.mockImplementation(() => { throw err; });
        const response = await request(app).get('/').send();
        expect(response.statusCode).toBe(550);
        expect(mockErrorHandler).toHaveBeenCalledWith(
            err,
            expect.any(express.request.constructor),
            expect.any(express.response.constructor),
            expect.any(Function)
        );
    });
});
