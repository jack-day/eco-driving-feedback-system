/**
 * @module
 * @description Contains the app's error objects for improved error handling
 * and error handling middleware to handle errors encoutered by Express.
 */
import { Request, Response, NextFunction } from 'express';

/** Centralized app error object */
export class AppError extends Error {
    public readonly httpCode?: number;
    /** Whether the application must terminate due to the error  */
    public readonly isFatal?: boolean;

    constructor(opts: {
        message?: string;
        httpCode?: number;
        isFatal?: boolean;
    }) {
        super(opts.message); // 'Error' breaks prototype chain here
        Object.setPrototypeOf(this, new.target.prototype); // restore prototype chain

        this.httpCode = opts.httpCode;
        this.isFatal = opts.isFatal;

        Error.captureStackTrace(this);
    }
}

/** API client-side error object  */
export class ClientError extends AppError {
    public readonly httpCode: number;

    constructor(opts: { message?: string; httpCode?: number; } = {}) {
        if (opts.httpCode && (opts.httpCode < 400 || opts.httpCode >= 500)) {
            throw Error('Invalid HTTP response status code, must be a 4xx client error response code');
        }

        super({ message: opts.message, isFatal: false });
        this.httpCode = opts.httpCode || 400;
    }
}

/** Error handler middleware to handle client errors */
export function handleClientErrors(
    err: Error,
    req: Request,
    res: Response,
    next: NextFunction /* eslint-disable-line @typescript-eslint/no-unused-vars */
) {
    if (err instanceof ClientError) {
        res.status(err.httpCode).send(err.message);
    } else {
        next(err);
    }
}

/** Error handler middleware to handle any errors */
export function handleErrors(
    err: Error,
    req: Request,
    res: Response,
    next: NextFunction /* eslint-disable-line @typescript-eslint/no-unused-vars */
) {
    res.sendStatus(500);
    console.error(`[${new Date().toISOString()}][ERROR]`, err);
    if (err instanceof AppError && err.isFatal == true) {
        process.exit(5);
    }
}
