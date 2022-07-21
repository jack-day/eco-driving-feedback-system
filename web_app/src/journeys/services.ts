import { ClientError } from '../errors';
import { journeyNoID, getJourneysOpts } from './types';
import * as db from './data_access';

/** Gets journeys */
export async function getJourneys(
    auth0UserID: string, opts: getJourneysOpts = {}
) {
    return await db.selectJourneys(auth0UserID, opts);
}

/** Creates a new journey */
export async function createJourney(auth0UserID: string, journey: journeyNoID) {
    return await db.insertJourney(auth0UserID, journey);
}

/** Get a journey */
export async function getJourney(auth0UserID: string, journeyID: number) {
    return await db.selectJourney(auth0UserID, journeyID);
}

/** Check a journey exists */
export async function journeyExists(auth0UserID: string, journeyID: number) {
    return await db.journeyExists(auth0UserID, journeyID);
}

/** Update a journey */
export async function updateJourney(
    auth0UserID: string, journeyID: number, journey: journeyNoID
) {
    const exists = await journeyExists(auth0UserID, journeyID);
    if (exists) {
        await db.updateJourney(auth0UserID, journeyID, journey);
    } else {
        throw new ClientError({
            httpCode: 404,
            message: 'Journey does not exist',
        });
    }
}
