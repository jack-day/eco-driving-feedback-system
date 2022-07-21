import pg from 'pg';
import { ClientError } from '../errors';
import { scores, getScoresOpts } from './types';
import * as db from './data_access';

/** Get scores */
export async function getScores(auth0UserID: string, opts: getScoresOpts={}) {
    return await db.selectScores(auth0UserID, opts);
}

/** Add scores */
export async function addScores(auth0UserID: string, scores: scores) {
    try {
        await db.insertScores(auth0UserID, scores);
    } catch (err) {
        if (err instanceof pg.DatabaseError && err.code === '23505') {
            throw new ClientError({
                message: 'Scores calculated at that time already exist',
            });
        } else {
            throw err;
        }
    }
}
