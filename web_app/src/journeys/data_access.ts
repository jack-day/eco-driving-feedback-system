import { QueryResult } from 'pg';
import pool from '../db';
import { removeNullishProps } from '../utils';
import { journey, journeyNoID, getJourneysOpts } from './types';

// Helpers
// ----------------------------------------------
/** Rounds a number to ndigits precision after the decimal point */
function round(num: number | null | undefined, ndigits: number) {
    if (num == undefined) return undefined;
    const multiplier = 10 ** ndigits;
    return Math.round(num * multiplier) / multiplier;
}


// Insert
// ----------------------------------------------
/**
 * Inserts a new journey
 * @returns Journey ID
 */
export async function insertJourney(auth0UserID: string, journey: journeyNoID) {
    const { rows }: QueryResult<{ journey_id: number }> = await pool.query(
        `INSERT INTO journey
        (usr_id, start_time, end_time, distance, idle_secs, gsi_adh)
        VALUES (
            (SELECT usr_id FROM usr WHERE auth0_user_id = $1),
            $2, $3, $4, $5, $6
        ) RETURNING journey_id`,
        [
            auth0UserID,
            journey.start,
            journey.end,
            round(journey.distance, 1),
            journey.idleSecs,
            round(journey.gsiAdh, 2),
        ]
    );
    return rows[0].journey_id;
}


// Select
// ----------------------------------------------
/** Selects journeys */
export async function selectJourneys(
    auth0UserID: string, opts: getJourneysOpts = {}
): Promise<journey[]> {
    let query = `
        SELECT
            journey_id as "journeyID",
            start_time as "start",
            end_time as "end",
            distance as "distance",
            idle_secs as "idleSecs",
            gsi_adh as "gsiAdh"
        FROM journey j
        INNER JOIN usr u ON u.usr_id=j.usr_id
        WHERE u.auth0_user_id = $1
        ORDER BY end_time DESC NULLS LAST
        LIMIT $2`;
    const values: any[] = [auth0UserID, opts.limit || null];
    
    if (opts.offset) {
        query += ' OFFSET $3';
        values.push(opts.offset);
    }

    const { rows }: QueryResult<journey> = await pool.query(query, values);
    return rows.map(row => removeNullishProps(row));
}

/** Selects a journey */
export async function selectJourney(
    auth0UserID: string, journeyID: number
): Promise<journey | undefined> {
    const { rows }: QueryResult<journey> = await pool.query(
        `SELECT
            journey_id as "journeyID",
            start_time as "start",
            end_time as "end",
            distance as "distance",
            idle_secs as "idleSecs",
            gsi_adh as "gsiAdh"
        FROM journey j
        INNER JOIN usr u ON u.usr_id=j.usr_id
        WHERE u.auth0_user_id = $1 AND journey_id = $2`,
        [auth0UserID, journeyID]
    );
    return rows[0] ? removeNullishProps(rows[0]) : undefined;
}


// Update
// ----------------------------------------------
/** Updates a journey */
export async function updateJourney(
    auth0UserID: string, journeyID: number, journey: journeyNoID
) {
    await pool.query(
        `UPDATE journey SET
            start_time = $3,
            end_time = $4,
            distance = $5,
            idle_secs = $6,
            gsi_adh = $7
        WHERE usr_id = (SELECT usr_id FROM usr WHERE auth0_user_id = $1) AND
        journey_id = $2`,
        [
            auth0UserID,
            journeyID,
            journey.start,
            journey.end,
            round(journey.distance, 1),
            journey.idleSecs,
            round(journey.gsiAdh, 2),
        ]
    );
}


// Exists
// ----------------------------------------------
/** Check a journey exists */
export async function journeyExists(auth0UserID: string, journeyID: number) {
    const { rows } = await pool.query(
        `SELECT journey_id FROM journey
        WHERE usr_id = (SELECT usr_id FROM usr WHERE auth0_user_id = $1) AND
        journey_id = $2`,
        [auth0UserID, journeyID]
    );
    return rows.length === 1;
}
