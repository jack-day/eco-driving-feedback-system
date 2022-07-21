/**
 * @module
 * @description API request validation middleware.
 */
import { AnySchema, ValidationErrorItem } from 'joi';
import { Handler, json as expressJSON } from 'express';

/**
 * Returns middleware that wraps express.json to catch thrown syntax errors and
 * respond with a 400 status code
 */
export function json(): Handler {
    return (req, res, next) => {
        expressJSON()(req, res, (err) => {
            if (err && err instanceof SyntaxError) {
                res.status(400).send(err.message);
            } else {
                next(err);
            }
        });
    };
}

/**
 * Returns error messages for each alternative schema in a joi.alternatives() schema
 * @param value - The value to be validated
 * @param schema - The schema to validate to the value against
 * @param valueLbl - The label to replace "value" in any returned errors
 */
function alternativesErrors(value: any, schema: AnySchema, valueLbl: string) {
    const errors: ValidationErrorItem[] = [{
        message: `${valueLbl} does not match any of the allowed schemas`,
        path: [],
        type: 'alternatives.match',
    }];
    
    for (let i = 0; i < schema.$_terms.matches.length; i++) {
        const altSchema: AnySchema = schema.$_terms.matches[i].schema;
        const { error } = altSchema.validate(value, { abortEarly: false });

        if (error) {
            for (const err of error.details) {
                err.message = `schema ${i} failed because ${err.message}`;
                errors.push(err);
            }
        }
    }

    return errors;
}

interface ValidateOptions {
    val: any;
    schema: AnySchema;
    valLabel?: string;
    httpCode?: number;
    sendErrors?: boolean
}

/**
 * Returns middleware to validate a value against a given schema
 * @param val - The value to be validated
 * @param schema - The schema to validate to the value against
 * @param valLabel - The label to replace "value" in any returned errors
 * @param httpCode - The HTTP response status code to respond with
 * @param sendErrors - Whether to respond with validation errors
 */
function validate({
    val, schema, valLabel = 'value', httpCode = 400, sendErrors = true,
}: ValidateOptions): Handler {
    return (req, res, next) => {
        const { error } = schema.validate(val, { abortEarly: false });

        if (error === undefined) {
            next();
        } else if (sendErrors) {
            if (error && error.details[0].type === 'alternatives.match') {
                error.details = alternativesErrors(val, schema, valLabel);
            }

            res.status(httpCode).json({
                errors: error.details.map(err => {
                    return err.message.replace('"value"', valLabel);
                }),
            });
        } else {
            res.sendStatus(httpCode);
        }
    };
}

/** Returns middleware to validate the request params to ensure it matches a given schema */
export function validateParams(schema: AnySchema): Handler {
    return (req, res, next) => {
        validate({
            val: req.params,
            schema,
            httpCode: 404,
            sendErrors: false,
        })(req, res, next);
    };
}

/** Returns middleware to validate the request params to ensure it matches a given schema */
export function validateQueryParams(schema: AnySchema): Handler {
    return (req, res, next) => {
        validate({
            val: req.query,
            schema,
            valLabel: 'request query parameters',
        })(req, res, next);
    };
}

/** Returns middleware to validate the request body to ensure it matches a given schema */
export function validateBody(schema: AnySchema): Handler {
    return (req, res, next) => {
        validate({
            val: req.body,
            schema,
            valLabel: 'request body',
        })(req, res, next);
    };
}
