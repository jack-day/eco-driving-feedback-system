import { QueryResult } from 'pg';
import pool from '../db';

/** Check if a user already exists */
export async function userExists(auth0UserID: string) {
    const { rows } = await pool.query(
        'SELECT usr_id FROM usr WHERE auth0_user_id = $1',
        [auth0UserID]
    );
    return rows.length === 1;
}

/**
 * Inserts a new user into 
 * @returns User ID
 */
export async function insertUser(auth0UserID: string) {
    const { rows }: QueryResult<{ usr_id: number }> = await pool.query(
        'INSERT INTO usr (auth0_user_id) VALUES ($1) RETURNING usr_id',
        [auth0UserID]
    );
    return rows[0].usr_id;
}

/** Deletes a user from usr */
export async function deleteUser(auth0UserID: string) {
    await pool.query(
        'DELETE FROM usr WHERE auth0_user_id = $1',
        [auth0UserID]
    );
}
