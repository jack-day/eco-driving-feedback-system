import { QueryResult } from 'pg';
import pool from '../db';
import { removeNullishProps } from '../utils';
import { scores, getScoresOpts } from './types';

/** Returns the columns to be retrieved by selectScores */
function selectScoresCols(type?: string) {
    switch (type) {
        case 'ecoDriving':
            return 'eco_driving as "ecoDriving"';
        case 'drivAccSmoothness':
            return 'driv_acc_smoothness as "drivAccSmoothness"';
        case 'startAccSmoothness':
            return 'start_acc_smoothness as "startAccSmoothness"';
        case 'decSmoothness':
            return 'dec_smoothness as "decSmoothness"';
        case 'gsiAdh':
            return 'gsi_adh as "gsiAdh"';
        case 'speedLimitAdh':
            return 'speed_limit_adh as "speedLimitAdh"';
        case 'motorwaySpeed':
            return 'motorway_speed as "motorwaySpeed"';
        case 'idleDuration':
            return 'idle_duration as "idleDuration"';
        case 'journeyIdlePct':
            return 'journey_idle_pct as "journeyIdlePct"';
        case 'journeyDistance':
            return 'journey_distance as "journeyDistance"';
        default:
            return `eco_driving as "ecoDriving",
            driv_acc_smoothness as "drivAccSmoothness",
            start_acc_smoothness as "startAccSmoothness",
            dec_smoothness as "decSmoothness",
            gsi_adh as "gsiAdh",
            speed_limit_adh as "speedLimitAdh",
            motorway_speed as "motorwaySpeed",
            idle_duration as "idleDuration",
            journey_idle_pct as "journeyIdlePct",
            journey_distance as "journeyDistance"`;
    }
}

/** Selects scores */
export async function selectScores(
    auth0UserID: string, opts: getScoresOpts = {}
): Promise<scores[]> {
    const values: any[] = [auth0UserID, opts.limit || null];
    let query = `
        SELECT
            calculated_at as "calculatedAt",
            ${selectScoresCols(opts.type)}
        FROM scores s
        INNER JOIN usr u ON u.usr_id=s.usr_id
        WHERE u.auth0_user_id = $1
        AND calculated_at <= NOW()::date + interval '1 day'`;
    
    if (opts.maxDaysAgo) {
        // Get scores calculated since 00:00 on each day
        query += " AND calculated_at >= NOW()::date - interval '1 day' * $3";
        values.push(opts.maxDaysAgo);
    }

    query += ' ORDER BY calculated_at DESC LIMIT $2';

    const { rows }: QueryResult<scores> = await pool.query(query, values);
    return rows.map(row => removeNullishProps(row));
}


/** Inserts new scores */
export async function insertScores(auth0UserID: string, scores: scores) {
    await pool.query(
        `INSERT INTO scores (
            usr_id,
            calculated_at,
            eco_driving,
            driv_acc_smoothness,
            start_acc_smoothness,
            dec_smoothness,
            gsi_adh,
            speed_limit_adh,
            motorway_speed,
            idle_duration,
            journey_idle_pct,
            journey_distance
        ) VALUES (
            (SELECT usr_id FROM usr WHERE auth0_user_id = $1),
            $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
        )`,
        [
            auth0UserID,
            scores.calculatedAt,
            scores.ecoDriving,
            scores.drivAccSmoothness,
            scores.startAccSmoothness,
            scores.decSmoothness,
            scores.gsiAdh,
            scores.speedLimitAdh,
            scores.motorwaySpeed,
            scores.idleDuration,
            scores.journeyIdlePct,
            scores.journeyDistance,
        ]
    );
}
