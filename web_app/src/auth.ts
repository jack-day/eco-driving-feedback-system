/**
 * @module 
 * @description API authentication and authorisation middleware.
 */
import { Request, AuthedRequest, Response, NextFunction } from 'express';
import { auth, AuthResult, JWTPayload, UnauthorizedError } from 'express-oauth2-jwt-bearer';
import config from './config';
import { userExists } from './users/services';

const checkJwt = auth({
    audience: config.auth.audience,
    issuerBaseURL: `https://${config.auth.domain}`,
});

/**
 * Requires authentication in the request
 * - Will return a 401 if a valid JWT bearer token is not provided.
 * - Will return a 500 if a subject is not set within the JWT payload
 */
export async function requireAuth(
    req: Request, res: Response, next: NextFunction
) {
    await checkJwt(req, res, (err) => {
        if (!err) {
            // Check the request JWT has a set subject in it's payload
            if (req.auth && req.auth.payload && req.auth.payload.sub) {
                next();
            } else {
                next(new Error(
                    'Authenticated request does not contain a payload with a subject'
                ));
            }
        } else {
            if (err instanceof UnauthorizedError) {
                res.sendStatus(err.statusCode);
            } else {
                next(err);
            }
        }
    });
}

export interface RequireAuthResult extends Omit<AuthResult, 'payload'> {
    payload: Omit<JWTPayload, 'sub'> & { sub: string }
}

/**
 * Requires the request user to be authenticated and have an account 
 * - Will return a 401 if a valid JWT bearer token is not provided or an account
 *   does not exist corresponding with the Auth0 id_token given in the valid JWT
 * - Will return a 500 if a subject is not set within the JWT payload
 */
export async function requireAccount(
    req: Request, res: Response, next: NextFunction
) {
    await requireAuth(req, res, async (err) => {
        if (!err) {
            const authedReq = req as AuthedRequest;
            const exists = await userExists(authedReq.auth.payload.sub);
            if (exists) {
                next();
            } else {
                res.sendStatus(401);
            }
        } else {
            next(err);
        }
    });
}
