/**
 * Helper to generate mock JWT tokens and mock the server verifying
 * them. Allows tests to be authenticated without the need to communicate with
 * Auth0. Modified from: https://github.com/auth0/node-oauth2-jwt-bearer/blob/6907844d19d7cd1334ba0517c36ee31962ebdc8c/packages/access-token-jwt/test/helpers.ts,
 * which is used in the tests of express-oauth2-jwt-bearer.
 */
import { SignJWT, generateKeyPair, exportJWK } from 'jose';
import nock from 'nock';
import config from '../../src/config';

const now = Math.round(Date.now() / 1000);
const day = 60 * 60 * 24;

interface CreateJWTOptions {
    payload?: { [key: string]: any };
    issuer?: string;
    audience?: string;
    jwksUri?: string;
    discoveryUri?: string;
    kid?: string;
    iat?: number;
    exp?: number;
}

/** Generates a mock JWT and mock issuer server to pass authentication */
export default async function createJwt(subject: string, {
    payload = {},
    issuer = config.auth.domain,
    audience = config.auth.audience,
    jwksUri = '/.well-known/jwks.json',
    discoveryUri = '/.well-known/openid-configuration',
    iat = now,
    exp = now + day,
    kid = 'kid',
}: CreateJWTOptions = {}) {
    const { publicKey, privateKey } = await generateKeyPair('RS256');
    const publicJwk = await exportJWK(publicKey);

    nock(issuer)
        .persist()
        .get(jwksUri)
        .reply(200, () => {
            return { keys: [{ kid, ...publicJwk }] };
        })
        .get(discoveryUri)
        .reply(200, () => {
            return {
                issuer,
                jwks_uri: (issuer + jwksUri).replace('//.well-known', '/.well-known'),
            };
        });

    return new SignJWT(payload)
        .setProtectedHeader({ alg: 'RS256', typ: 'JWT', kid })
        .setIssuer(issuer)
        .setSubject(subject)
        .setAudience(audience)
        .setIssuedAt(iat)
        .setExpirationTime(exp)
        .sign(privateKey);
}
