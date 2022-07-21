import pg from 'pg';
import { ClientError } from '../errors';
import * as db from './data_access';

/** Checks if a user exists */
export async function userExists(auth0UserID: string) {
    return await db.userExists(auth0UserID);
}

/** Creates a new user */
export async function createUser(auth0UserID: string) {
    try {
        await db.insertUser(auth0UserID);
    } catch (err) {
        if (err instanceof pg.DatabaseError && err.code === '23505') {
            throw new ClientError({ message: 'User already exists' });
        } else {
            throw err;
        }
    }
}

/** Deletes a user */
export async function deleteUser(auth0UserID: string) {
    return await db.deleteUser(auth0UserID);
}
