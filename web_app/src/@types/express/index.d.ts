/* eslint-disable */
import { ParsedQs } from 'qs';
import * as core from 'express-serve-static-core';
import { RequireAuthResult } from '../../auth.js';

/*
After authenticating the user's access token, we know that their
authentication data has definetly been added to the express request by
express-oauth2-jwt-bearer. Thus, to use the auth property without handling
if it exists on the req object, an authenticated request interface has been made
where 'auth' is set as a non-optional property on the request object. Some extra
care needs to be taken than just to extend Express' Request interface due to
express-serve-static-core (core type definitions for Express) also referencing
the default Request interface in some of it's types. 
*/

declare module 'express-serve-static-core' {
    // Create the authenticated request interface
    interface AuthedRequest<P, ResBody, ReqBody, ReqQuery, Locals> extends Request<P, ResBody, ReqBody, ReqQuery, Locals> {
        auth: RequireAuthResult
    }

    // Add AuthedRequest as a request type to router request handler functions
    interface IRouterMatcher<
        T,
        Method extends 'all' | 'get' | 'post' | 'put' | 'delete' | 'patch' | 'options' | 'head' = any
    > {
        <
            P = ParamsDictionary,
            ResBody = any,
            ReqBody = any,
            ReqQuery = ParsedQs,
            Locals extends Record<string, any> = Record<string, any>
        >(
            path: PathParams,
            ...handlers: Array<(
                req: AuthedRequest<P, ResBody, ReqBody, ReqQuery, Locals>,
                res: Response<ResBody, Locals>,
                next: NextFunction,
            ) => void>
        ): T;
    }
}

// Add AuthedRequest to the global express object
declare global {
    namespace Express {
        /** Authenticated request */
        interface AuthedRequest<
            P = core.ParamsDictionary,
            ResBody = any,
            ReqBody = any,
            ReqQuery = core.Query,
            Locals extends Record<string, any> = Record<string, any>
        > extends core.AuthedRequest<P, ResBody, ReqBody, ReqQuery, Locals> {}
    }
}

// Export AuthedRequest under express
declare module 'express' {
    /** Authenticated request */
    export interface AuthedRequest<
        P = core.ParamsDictionary,
        ResBody = any,
        ReqBody = any,
        ReqQuery = core.Query,
        Locals extends Record<string, any> = Record<string, any>
    > extends core.AuthedRequest<P, ResBody, ReqBody, ReqQuery, Locals> {}    
}    
